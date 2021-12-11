import requests
from constants import Game
from db import Database
from config import DB_AUTH_SOURCE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
import logging
from proxy import Proxy

logger = logging.getLogger(__name__)

db = Database(uri=f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?authSource={DB_AUTH_SOURCE}', db_name=DB_NAME)

def build(games):

    proxy = Proxy()

    for game in games:

        if game is Game.CSGO:
            url = 'https://market.csgo.com/ajax/name/all/all/all/{page}/56/0;500000/all/all/all?sd=desc&lang=en'
            base_url = 'https://market.csgo.com/item'
            steam_url = 'https://steamcommunity.com/market/listings/730/{name}'
        
        elif game is Game.DOTA:
            url = 'https://market.dota2.net/ajax/name/all/all/all/{page}/56/0;500000/all/all?sd=desc&lang=en'
            base_url = 'https://market.dota2.net/item'
            steam_url = 'https://steamcommunity.com/market/listings/570/{name}'

        elif game is Game.RUST:
            url = 'https://rust.tm/ajax/name/all/all/all/{page}/56/0;500000/all/all?sd=desc&lang=en'
            base_url = 'https://rust.tm/item'
            steam_url = 'https://steamcommunity.com/market/listings/252490/{name}'

        elif game is Game.TF2:
            url = 'https://tf2.tm/ajax/name/all/all/all/{page}/56/0;500000/all/all/-1/-1/all?sd=desc&lang=en'
            base_url = 'https://tf2.tm/item'
            steam_url = 'https://steamcommunity.com/market/listings/440/{name}'
        
        else:
            continue
        
        logger.debug(f'Строим для {game.name}')
        page = 1
        stats = {
            'new': 0,
            'updated': 0,
            'passed': 0
        }
        while True:
            try:
                logger.debug(f'Страница {page}')
                r = requests.get(url.format(page=page), proxies=proxy.get())
                for record in r.json()[0]:
                    new = {
                        'url': f'{base_url}/{record[0]}-{record[1]}-{record[2]}',
                        'updated': ''
                    }
                    new_steam = {
                        'url': steam_url.format(name=record[2]),
                        'updated': ''
                    }
                    item = db.find('item', {'STEAM.url': new_steam['url']})
                    if item:
                        if 'MARKETTM' in item:
                            logger.debug(f"Нашли предмет с MARKETTM, пропускаем")
                            stats['passed'] += 1
                        else:
                            db.update('item', {'STEAM.url': new_steam['url']}, {'MARKETTM': new})
                            logger.debug(f"Добавили MARKETTM к предмету: {new_steam['url']}")
                            stats['updated'] += 1
                    else:
                        db.insert('item', {'game': game.name, 'STEAM': new_steam, 'MARKETTM': new})
                        logger.debug(f"Создали новый предмет: {new_steam['url']}")
                        stats['new'] += 1
                page += 1
            except Exception as e:
                logger.debug(f"Ошибка: {e}\nПоследний статус запроса: {r.status_code}\nПоследняя страница: {page}")
                break
    
        logger.debug(f"Статистика для {game.name}: добавлено: {stats['new']}, обновлено: {stats['updated']}, пропущено: {stats['passed']}")