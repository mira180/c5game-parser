import requests
from config import UPDATER_HOST, UPDATER_PORT
import logging

logger = logging.getLogger(__name__)

def get_statistics_from_updater():
    try:
        return requests.get(f'http://{UPDATER_HOST}:{UPDATER_PORT}').json()
    except Exception as e:
        logger.debug(f'Не удалось получить статистику от updater ({UPDATER_HOST}:{UPDATER_PORT}): {e}')
    return {}, {}