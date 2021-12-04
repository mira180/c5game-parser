import logging
import requests
from lxml import etree
from time import sleep
import random
import re

from selenium import webdriver

from constants import Game
from config import CHROMEDRIVER_PATH, PROXY_FILE

logger = logging.getLogger(__name__)

def get_random_proxy(proxy_file = PROXY_FILE):
    try:
        logger.debug('Получение случайного прокси')
        with open(proxy_file) as pf:
            proxy_list = [line.strip() for line in pf]
            random_proxy = random.choice(proxy_list)
            logger.debug(f'Вернули случайный прокси: {random_proxy}')
            return random_proxy
    except Exception as e:
        logger.error(f'Ошибка получения случайного прокси: {e}')

def request(url: str, headers: dict = None, retry: bool = True, interval: int = 5, use_proxy = False, max_retries: int = 5):
    retries_counter = 0
    while True:
        try:
            retries_counter += 1
            if retries_counter > max_retries:
                logger.warning(f'Превышено максимальное количество запросов к URL: {url}')
                break
            logger.debug(f'Выполняем запрос к URL: {url}')
            params = {
                'url': url,
                'timeout': 20,
            }
            if headers:
                params['headers'] = headers
            if use_proxy:
                random_proxy = get_random_proxy()
                params['proxies'] = {
                    'http': random_proxy,
                    'https': random_proxy
                }
            r = requests.get(**params)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                logger.warning(f'Запрос к URL {url} вернул статус 404')
                return r
        except Exception as e:
            logger.error(f'Ошибка во время запроса к URL {url}: {e}')
        if not retry:
            return r
        logger.debug(f'Повторная попытка запроса к URL {url} через {interval} секунд')
        sleep(interval)

def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en-US')
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    return driver

def get_item_list(game: Game) -> list:
    try:
        logger.info(f'Получение списка предметов для {game.name}')
        items = []
        if game == Game.CSGO:
            get_url = 'https://counterstrike.fandom.com/wiki/Skins/List'
            r = requests.get(get_url)
            if r.status_code == 200:
                dom = etree.HTML(r.text)
                for row in dom.xpath("//tbody/tr"):
                    item_info = row.xpath("td/a/text()|td/span/text()")
                    if item_info:
                        item = {
                            'collection': item_info[0],
                            'weapon': item_info[1],
                            'skin': item_info[2].replace('*', '').strip(),
                            'quality': item_info[3]
                        }
                        items.append(item)
                logger.debug(f'Получен список предметов для {game.name}')
                return items
                        
            else:
                logger.warning(f'Не удалось получить список предметов по URL {get_url}, статус: {r.status_code}')
    except Exception as e:
        logger.warning(f'Ошибка получения списка предметов: {e}')
    return []

def clean_steam_url(url: str) -> str:
    url_split = url.split('/')
    url_split[-2] = re.sub('\D', '', url_split[-2])
    return '/'.join(url_split)