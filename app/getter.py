import threading
import logging
from datetime import datetime
from constants import Platform
import requests
from lxml import etree
import re
import urllib.parse
import time
import queue
from db import Database
from config import DATE_FORMAT, DB_NAME
import random

logger = logging.getLogger(__name__)
db = Database(db_name=DB_NAME)

class Proxy(object):

    def __init__(self, proxy_file='proxy.txt'):
        self.proxies = [l.strip() for l in open(proxy_file)]

    def get(self):
        #logger.debug(f"Получаем прокси, current_time: {current_time}")
        proxy = random.choice(self.proxies)
        logger.debug(f"Нашли свободный прокси {proxy}")
        return { 'http': proxy, 'https': proxy }

class Getter(object):

    def __init__(self):
        self.proxy = Proxy()
    
    def get(self):
        raise NotImplementedError
    
    def _get_proxies(self):
        try:
            if self.proxy:
                return self.proxy.get()
        except:
            pass
        return {}

    def _get_headers(self):
        return {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

class SteamGetter(Getter):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.platform = Platform.STEAM

    def get(self, url):
        try:
            r = requests.get(url, headers=self._get_headers(), proxies=self._get_proxies())
            item_nameid = int(re.findall(r'Market_LoadOrderSpread\(\s*[0-9]+\s*\)', r.text)[0][len('Market_LoadOrderSpread('):-1].strip())
            appid = re.sub('\D', '', urllib.parse.unquote(url.split('/')[-2]))
            market_hash_name = url.split('/')[-1]
        except Exception as e:
            logger.debug(f'Слишком много запросов? ({r.status_code}) - {url}')
            raise
        # нужно распараллелить
        orders_histogram = requests.get(
            f'https://steamcommunity.com/market/itemordershistogram?language=en&currency=1&item_nameid={item_nameid}',
            headers=self._get_headers(),
            proxies=self._get_proxies()
        ).json()
        price_overview = requests.get(
            f'https://steamcommunity.com/market/priceoverview/?appid={appid}&currency=1&market_hash_name={market_hash_name}',
            headers=self._get_headers(),
            proxies=self._get_proxies()
        ).json()
        updated = {
            'name': urllib.parse.unquote(url.split('/')[-1]),
            'lowest_sell_order': int(orders_histogram['lowest_sell_order']) / 100 if orders_histogram['lowest_sell_order'] else None,
            'highest_buy_order': int(orders_histogram['highest_buy_order']) / 100 if orders_histogram['highest_buy_order'] else None,
            'volume': int(re.sub('\D', '', price_overview['volume'])) if price_overview and 'volume' in price_overview else None,
            'median_price': float(re.sub('\D', '', price_overview['median_price'])) if price_overview and 'median_price' in price_overview else None
        }
        return updated
        

class C5gameGetter(Getter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.platform = Platform.C5GAME

    def get(self, url):
        r = requests.get(url, headers=self._get_headers(), proxies=self._get_proxies())
        dom = etree.HTML(r.text)
        updated = {
            'lowest_sell_order': float(dom.xpath("//div[@class='sale-item-info']//div[@class='hero']/span[3]/text()")[0].strip()[4:-1]),
            #'sell_count': int(dom.xpath("//span[@id='J_SellCount']/text()")[0])
        }
        return updated

class Updater:

    def __init__(self, platforms, threads=100, interval=15):
        self.platforms = platforms
        self.threads = threads
        self.interval = interval
        self.started = False
        self._c5game_getter = C5gameGetter()
        self._steam_getter = SteamGetter()
        self.statistics = {}
        self.last_statistics = {}

    def start(self):
        if not self.started:
            self.started = True
            for platform in self.platforms:
                if platform in Platform:
                    logger.debug(f"Создаем поток для {platform.name}")
                    threading.Thread(target=self._update, args=(platform, ), daemon=True).start()
    
    def _update(self, platform):

        def get_C5GAME(item):
            try:
                logger.debug(f"Обновляем предмет для C5GAME: {item['C5GAME']['url']}")
                updated = self._c5game_getter.get(item['C5GAME']['url'])
                item['C5GAME'].update({
                    'updated': datetime.utcnow().strftime(DATE_FORMAT),
                    'lowest_sell_order': updated['lowest_sell_order']
                })
                db.update('item', {'_id': item['_id']}, { 'C5GAME': item['C5GAME'] })
                logger.debug("Обновили предмет C5GAME")
                self.statistics['C5GAME']['success'] += 1
            except Exception as e:
                logger.debug(f"Ошибка обновления предмета для C5GAME: {e}")
                self.statistics['C5GAME']['errors'] += 1
                pass

        def get_STEAM(item):
            try:
                logger.debug(f"Обновляем предмет для STEAM: {item['STEAM']['url']}")
                updated = self._steam_getter.get(item['STEAM']['url'])
                item['STEAM'].update({
                    'name': updated['name'],
                    'updated': datetime.utcnow().strftime(DATE_FORMAT),
                    'lowest_sell_order': updated['lowest_sell_order'],
                    'highest_buy_order': updated['highest_buy_order'],
                    'volume': updated['volume'],
                    'median_price': updated['median_price']
                })
                db.update('item', {'_id': item['_id']}, { 'STEAM': item['STEAM'] })
                logger.debug("Обновили предмет STEAM")
                self.statistics['STEAM']['success'] += 1
            except Exception as e:
                logger.debug(f"Ошибка обновления предмета для STEAM: {e}")
                self.statistics['STEAM']['errors'] += 1
                pass

        def getter(q, interval):
            while True:
                item = q.get()
                if platform is Platform.C5GAME:
                    get_C5GAME(item)
                elif platform is Platform.STEAM:
                    get_STEAM(item)
                q.task_done()
                time.sleep(interval)

        q = queue.Queue()
        interval = self.interval

        for _ in range(self.threads):
            threading.Thread(target=getter, args=(q, interval), daemon=True).start()

        logger.debug(f"Запустили {self.threads} потоков")

        while True:
            self.statistics[platform.name] = {
                'errors': 0,
                'success': 0,
                'started': datetime.utcnow().strftime(DATE_FORMAT)
            }
            for item in db.find('item', {}, multiple=True):
                q.put(item)
            q.join()
            self.statistics[platform.name]['ended'] = datetime.utcnow().strftime(DATE_FORMAT)
            self.last_statistics[platform.name] = self.statistics[platform.name]
            logger.debug(f"Сделали полный круг обновления: {platform.name}")
            logger.debug(f"Статистика для {platform.name}: {self.statistics[platform.name]['errors']} ошибок, {self.statistics[platform.name]['success']} успешно, заняло {self.last_statistics[platform.name]['passed'] / 60} мин.")