import re
import logging
from lxml import etree
import urllib.parse
import re
from datetime import datetime

from config import UPDATED_TIME_FORMAT
import utils

logger = logging.getLogger(__name__)

class Parser:

    def __init__(self, base_url: str = 'https://steamcommunity.com/market', use_proxy=False):
        self.base_url = base_url
        self.use_proxy = use_proxy

    def get_item_by_url(self, url: str, language: str = 'english', currency: int = 1) -> dict:
        try:
            logger.info(f'Получение предмета по URL: {url}')
            r = utils.request(url, use_proxy=self.use_proxy)
            if r.status_code == 200:
                item_nameid = int(re.findall(r'Market_LoadOrderSpread\(\s*[0-9]+\s*\)', r.text)[0][len('Market_LoadOrderSpread('):-1].strip())
                appid = re.sub('\D', '', urllib.parse.unquote(url.split('/')[-2]))
                market_hash_name = url.split('/')[-1]
                orders_histogram = self.get_item_orders_histogram(item_nameid, language, currency)
                logger.debug(f'Получили orders_histogram: {orders_histogram}')
                price_overview = self.get_item_price_overview(appid, market_hash_name, currency)
                logger.debug(f'Получили price_overview: {price_overview}')
                item = {
                    'url': url,
                    'name': urllib.parse.unquote(url.split('/')[-1]),
                    'updated_at': datetime.now().strftime(UPDATED_TIME_FORMAT),
                }
                if price_overview:
                    if 'volume' in price_overview:
                        item['volume'] = int(price_overview['volume'])
                if orders_histogram:
                    if 'lowest_sell_order' in orders_histogram:
                        item['lowest_sell_order'] = int(orders_histogram['lowest_sell_order']) / 100
                    if 'highest_buy_order' in orders_histogram:
                        item['highest_buy_order'] = int(orders_histogram['highest_buy_order']) / 100
                logger.info(f"Получили предмет {item['name']}")
                return item
            else:
                logger.warning(f'Не смог получить информацию о предмете, запрос по URL {url} вернул код: {r.status_code}')
        except Exception as e:
            logger.error(f'Ошибка во время получения информации о предмете по URL {url}: {e}')
        return {}
            

    def get_item_orders_histogram(self, item_nameid: int, language: str = 'english', currency: int = 1) -> dict:
        try:
            r = utils.request(f'{self.base_url}/itemordershistogram?language={language}&currency={currency}&item_nameid={item_nameid}', use_proxy=self.use_proxy)
            if r.status_code == 200:
                return r.json()
            else:
                logger.warning(f'Не смог получить order_histogram для предмета {item_nameid}, запрос вернул код: {r.status_code}')
        except Exception as e:
            logger.error(f'Ошибка во время получения orders_histogram для предмета {item_nameid}: {e}')
        return {}

    def get_item_price_overview(self, appid: int, market_hash_name: str, currency: int = 1) -> dict:
        try:
            r = utils.request(f'{self.base_url}/priceoverview/?appid={appid}&currency={currency}&market_hash_name={market_hash_name}', use_proxy=self.use_proxy)
            if r.status_code == 200:
                return r.json()
            else:
                logger.warning(f'Не смог получить price_overview для предмета (appid: {appid}, market_hash_name: {market_hash_name}), запрос вернул код: {r.status_code}')
        except Exception as e:
            logger.error(f'Ошибка во время получения price_overview для предмета (appid: {appid}, market_hash_name: {market_hash_name}): {e}')
        return {}
