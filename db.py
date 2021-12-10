import pymongo
import logging

logger = logging.getLogger(__name__)

class Database:

    def __init__(self, uri='mongodb://localhost:27017', db_name='test'):
        #logger.info(f'Подключение к базе данных: {uri}')
        client = pymongo.MongoClient(uri)
        self.db = client[db_name]
        
    def insert(self, collection_name, data):
        """
        Добавление новой записи в коллекцию
        """
        #logger.debug(f'Добавление новой записи в коллекцию {collection_name}: {data}')
        collection = self.db[collection_name]
        return collection.insert_one(data).inserted_id
    
    def find(self, collection_name, elements, multiple=False):
        """
        Поиск по коллекции
        """
        #logger.debug(f'Поиск в коллекции {collection_name} по фильтру: {elements}')
        collection = self.db[collection_name]
        if multiple:
            results = collection.find(elements)
            return [r for r in results]
        else:
            return collection.find_one(elements)
        
    def update(self, collection_name, query_elements, new_values):
        """
        Изменение записи в коллекции
        """
        #logger.debug(f'Изменение записи в коллекции {collection_name}, где {query_elements} -> {new_values}')
        collection = self.db[collection_name]
        collection.update_one(query_elements, {'$set': new_values})

    def delete(self, collection_name, query):
        """
        Удаление записи из коллекции
        """
        #logger.debug(f'Удаление записи в коллекции {collection_name} по фильтру: {query}')
        collection = self.db[collection_name]
        collection.delete_one(query)