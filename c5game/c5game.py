from datetime import datetime
from lxml import etree
import logging
import threading
import queue
import time

from constants import Game, Platform
from config import ITEMS_COLLECTION, UPDATED_TIME_FORMAT, BUILD_THREADS
import steam
import utils

from .config import REQUEST_HEADERS

logger = logging.getLogger(__name__)

class Parser:

    def __init__(self, base_url: str = 'https://www.c5game.com', use_proxy=False):
        self.base_url = base_url
        self.use_proxy = use_proxy
        self.steam_parser = steam.Parser(use_proxy=use_proxy)

    def get_item_by_id(self, item_id: int, game: Game, update_steam=False) -> dict:
        logger.info(f'Получение предмета по item_id: {item_id}, game: {game.name}, update_steam: {update_steam}')

        if game == Game.DOTA:
            get_url = f'/dota/item/index.html?item_id={item_id}&type=S'
        elif game == Game.CSGO:
            get_url = f'/csgo/{item_id}/S.html'
        else:
            get_url = f'/market/item/index.html?item_id={item_id}&appid=&type=S'

        return self.get_item_by_url(self, self.base_url + get_url, update_steam=update_steam)

    def get_item_by_url(self, url: str, update_steam=False) -> dict:
    
        try:
            logger.info(f'Получение предмета по URL: {url}')
            r = utils.request(url, headers=REQUEST_HEADERS, use_proxy=self.use_proxy)

            if r.status_code == 200:
                dom = etree.HTML(r.text)
                item = {
                    Platform.STEAM.name: {
                        'url': utils.clean_steam_url(dom.xpath("//div[@class='sale-item-info']//div[@class='hero']//div[contains(@class, 'steamUrl')]/a/@href")[0]),
                    },
                    Platform.C5GAME.name: {
                        'url': url,
                        'name': dom.xpath("//div[@class='sale-item-info']//div[@class='name']/span[1]/text()")[0].strip(),
                        'lowest_sell_order': {
                            'cny': float(dom.xpath("//div[@class='sale-item-info']//div[@class='hero']/span[2]/text()")[0].strip()),
                            'usd': float(dom.xpath("//div[@class='sale-item-info']//div[@class='hero']/span[3]/text()")[0].strip()[4:-1])
                        },
                        #'sell_count': int(dom.xpath("//span[@id='J_SellCount']/text()")[0]),
                        'image': dom.xpath("//div[contains(@class, 'sale-item-img')]/img/@src")[0].split('?')[0],
                        'updated_at': datetime.now().strftime(UPDATED_TIME_FORMAT),
                    }
                }

                if update_steam:
                    logger.debug('Обновление предмета Steam')
                    item[Platform.STEAM.name].update(self.steam_parser.get_item_by_url(item[Platform.STEAM.name]['url']))

                logger.info(f"Получили предмет {item[Platform.C5GAME.name]['name']}")
                return item
            
            elif r.status_code == 404:
                logger.warning(f'Предмет с URL {url} не найден')
                
            else:
                logger.warning(f'Ошибка получения информации о предмете с URL {url}, статус: {r.status_code}')
        
        except Exception as e:
            logger.error(f'Ошибка получения информации о предмете c URL {url}: {e}')

        return {}

class Builder:
    
    def __init__(self, db, use_proxy=False, base_url='https://www.c5game.com'):
        self.db = db
        self.use_proxy = use_proxy
        self.base_url = base_url
        self.parser = Parser(use_proxy=use_proxy)

    def build_database(self, games: list, start_page: int = 1, max_pages: int = 0):
        try:
            logger.info(f'Создаем базу данных для {Platform.C5GAME.name}')
            driver = self._get_webdriver()
            self._login(driver)
            
            def getter():
                while True:
                    try:
                        url, game = get_queue.get(timeout=0.1)
                        self.add_item(url, game)
                    except queue.Empty:
                        if exit_event.is_set():
                            logger.debug('Выходим из потока')
                            break
                    except Exception as e:
                        logger.warning(f'Ошибка в потоке во время обновления предмета: {e}')
                        break

            get_queue = queue.Queue()
            threads = []
            exit_event = threading.Event()
            for _ in range(BUILD_THREADS):
                t = threading.Thread(target=getter)
                t.daemon=True
                threads.append(t)
                t.start()

            for game in games:

                if Game.CSGO == game:
                    driver.get(f'{self.base_url}/csgo/default/result.html?page={start_page}')

                elif Game.DOTA == game:
                    driver.get(f'{self.base_url}/dota.html?page={start_page}')
                
                elif Game.Z1 == game:
                    driver.get(f'{self.base_url}/market.html?appid=433850&page={start_page}')
                
                elif Game.RUST == game:
                    driver.get(f'{self.base_url}/market.html?appid=252490&page={start_page}')

                elif Game.STEAM == game:
                    driver.get(f'{self.base_url}/market.html?appid=753&page={start_page}')

                elif Game.PAYDAY2 == game:
                    driver.get(f'{self.base_url}/market.html?appid=218620&page={start_page}')
                
                elif Game.TF2 == game:
                    driver.get(f'{self.base_url}/market.html?appid=440&page={start_page}')

                retry = False
                pages_counter = max_pages
                while True:

                    logger.info(f'Текущая страница: {driver.current_url}')

                    if max_pages:
                        pages_counter -= 1
                        if pages_counter < 0:
                            logger.info(f'Достигли максимума страниц: {max_pages}')
                            break

                    if driver.current_url == self.base_url + '/login.html':
                        logger.warning('Пользователь не авторизован')
                        self._login(driver)
                    else:
                        try:
                            for url in driver.find_elements_by_xpath("//li[@class='selling']/p[@class='name']/a"):
                                get_queue.put((url.get_attribute('href'), game))
                            next_page = driver.find_element_by_xpath("//li[contains(@class, 'next')]/a")
                            if next_page.get_attribute('href') != driver.current_url:
                                logger.info('Переходим на следующую страницу')
                                next_page.click()
                                retry = False
                            else:
                                logger.info('Закончили перебор всех страниц')
                                break
                        except Exception as e:
                            logger.error(f'Ошибка во время перебора страницы {driver.current_url}: {e}')
                            if not retry:
                                logger.debug('Обновляем страницу...')
                                driver.refresh()
                                retry = True
                            else:
                                logger.warning('Не смогли перебрать страницу из-за ошибки, завершаем перебор...')
                                break
            
            exit_event.set()
            for t in threads:
                t.join()

            logger.info(f'Построили базу данных для {Platform.C5GAME.name} для игр {games}')
            
            driver.quit()

        except Exception as e:
            logger.error(f'Не смогли построить базу данных для {Platform.C5GAME.name}, так как произошла ошибка: {e}')
            raise

    
    def add_item(self, url: str, game: Game):
        item = self.parser.get_item_by_url(url, update_steam=False)
        if item:
            item['game'] = game.name
            if self.db.find(ITEMS_COLLECTION, {Platform.STEAM.name + '.url': item[Platform.STEAM.name]['url']}):
                logger.info(f"Обновлен предмет с URL {item[Platform.STEAM.name]['url']}")
                self.db.update(ITEMS_COLLECTION, {Platform.STEAM.name + '.url': item[Platform.STEAM.name]['url']}, {Platform.C5GAME.name: item[Platform.C5GAME.name]})
            else:
                logger.info(f"Добавлен новый предмет с URL {item[Platform.STEAM.name]['url']}")
                self.db.insert(ITEMS_COLLECTION, item)
        else:
            logger.warning(f'Не смогли получить информацию о предмете с URL {url}')

    def _get_webdriver(self):
        try:
            driver = utils.get_webdriver()
            logger.debug('Получили веб-драйвер')
            return driver
        except:
            logger.error('Ошибка получения веб-драйвера')
            raise

    def _login(self, driver) -> bool:
        try:
            logger.debug('Пытаемся авторизоваться на сайте')
            driver.get(self.base_url + '/login.html')
            input('Авторизуйтесь на сайте, после чего нажмите ENTER...')
        except:
            logger.error('Ошибка во время авторизации')
            raise
        
