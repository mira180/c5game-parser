import logging
from bson.objectid import ObjectId
import time
from typing import Union
import queue
import threading

from constants import Game, Platform
from config import ITEMS_COLLECTION, UPDATE_THREADS

import steam
import c5game

logger = logging.getLogger(__name__)

class Updater:

    def __init__(self, db, use_proxy=False):
        self.db = db
        self.use_proxy = use_proxy
        self.steam_parser = steam.Parser(use_proxy=use_proxy)
        self.c5game_parser = c5game.Parser(use_proxy=use_proxy)
        self.c5game_builder = c5game.Builder(db, use_proxy=use_proxy)

    def build_database(self, platforms: list, games: list):

        if Platform.C5GAME in platforms:
            self.c5game_builder.build_database(games)

    def update_item(self, _id: Union[str, ObjectId], platforms: list) -> dict:

        try:
            logger.info(f'Обновление предмета {_id} для платформ {platforms}')
            if isinstance(_id, str):
                _id = ObjectId(_id)
            item = self.db.find(ITEMS_COLLECTION, {'_id': _id})
            if item:
                threads = []

                if Platform.STEAM in platforms:
                    def update():
                        if Platform.STEAM.name in item:
                            updated = self.steam_parser.get_item_by_url(item[Platform.STEAM.name]['url'])
                            if updated:
                                self.db.update(ITEMS_COLLECTION, {'_id': _id}, {Platform.STEAM.name: updated})
                                logger.debug(f'Обновили предмет для {Platform.STEAM.name}')
                        else:
                            logger.warning(f'Не смогли обновить предмет {_id} для платформы {Platform.STEAM.name}, так как предмета нет на этой платформе')
                    t = threading.Thread(target=update)
                    t.start()
                    threads.append(t)

                if Platform.C5GAME in platforms:
                    def update():
                        if Platform.C5GAME.name in item:
                            updated = self.c5game_parser.get_item_by_url(item[Platform.C5GAME.name]['url'])
                            if updated:
                                self.db.update(ITEMS_COLLECTION, {'_id': _id}, {Platform.C5GAME.name: updated[Platform.C5GAME.name]})
                                logger.debug(f'Обновили предмет для {Platform.C5GAME.name}')
                        else:
                            logger.warning(f'Не смогли обновить предмет {_id} для платформы {Platform.C5game.name}, так как предмета нет на этой платформе')
                    t = threading.Thread(target=update)
                    t.start()
                    threads.append(t)
                
                for t in threads:
                    t.join()

                item = self.db.find(ITEMS_COLLECTION, {'_id': _id})
                
                return item

            else:
                logger.warning(f'Невозможно обновить предмет {_id}, предмета с таким _id нет в базе данных')

        except Exception as e:
            logger.warning(f'Ошибка во время обновления предмета {_id}: {e}')
        
        return {}

    def update_all(self, games: list, platforms: list):

        try:

            def updater():
                while True:
                    try:
                        item, platforms = update_queue.get(False)
                        self.update_item(item['_id'], platforms)
                    except queue.Empty:
                        logger.debug('Поток завершает работу, так как в очередь пуста')
                        break
                    except Exception as e:
                        logger.warning(f'Ошибка в потоке во время обновления предмета: {e}')
                        break

            logger.info(f'Обновление всех предметов для игр {games}, для платформ {platforms}')
            update_queue = queue.Queue()
            threads = []
            start_time = time.time()
            for game in games:
                for item in self.db.find(ITEMS_COLLECTION, {'game': game.name}, multiple=True):
                    logger.debug(f'Помещаем в очередь обновлений: {(item, platforms)}')
                    update_queue.put((item, platforms))
            
            for _ in range(UPDATE_THREADS):
                t = threading.Thread(target=updater)
                t.daemon = True
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join()

            elapsed_time = time.time() - start_time
            logger.info(f'Обновили все предметы для игр {games}, для платформ {platforms}, потрачено времени: {elapsed_time:.2f} секунд')

        except Exception as e:
            logger.error(f'Ошибка в время обновления всех предметов для игр {games}, для платформ {platforms}: {e}')