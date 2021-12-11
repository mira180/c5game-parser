import random
import logging

logger = logging.getLogger(__name__)

class Proxy(object):

    def __init__(self, proxy_file='proxy.txt'):
        self.proxies = [l.strip() for l in open(proxy_file)]

    def get(self):
        #logger.debug(f"Получаем прокси, current_time: {current_time}")
        proxy = random.choice(self.proxies)
        logger.debug(f"Нашли свободный прокси {proxy}")
        return { 'http': proxy, 'https': proxy }