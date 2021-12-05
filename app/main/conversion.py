from flask import jsonify
import requests
import time
import logging

logger = logging.getLogger(__name__)

class ConversionRates:

    def __init__(self, api_key, interval = 86400):
        self.api_key = api_key
        self.interval = interval
        self.latest = {}
    
    def get(self):
        if not self.latest or time.time() - self.latest['updated_at'] > self.interval:
            if self.latest:
                logger.info(time.time() - self.latest['updated_at'])
            return self.update()
        return jsonify(self.latest)

    def update(self):
        try:
            latest = requests.get(f'https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD').json()
            self.latest = {
                'updated_at': int(time.time()),
                'base_code': latest['base_code'],
                'conversion_rates': latest['conversion_rates']
            }
        except:
            logger.warning('Ошибка получения курсов валют')
        return jsonify(self.latest)