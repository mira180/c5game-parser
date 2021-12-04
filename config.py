import logging
import os
from sys import platform

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('selenium').setLevel('CRITICAL')
logging.basicConfig(
        level='INFO',
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%H:%M:%S")

UPDATED_TIME_FORMAT = os.getenv('UPDATED_TIME_FORMAT', r'%Y-%m-%d %H:%M:%S')
SUBSCRIPTION_TIME_FORMAT = os.getenv('SUBSCRIPTION_TIME_FORMAT', r'%d.%m.%Y')
ITEMS_COLLECTION = os.getenv('ITEMS_COLLECTION', 'items')
USERS_COLLECTION = os.getenv('USERS_COLLECTION', 'users')
PROXY_FILE = os.getenv('PROXY_FILE', 'proxy.txt')
UPDATE_THREADS = int(os.getenv('UPDATE_THREADS', '150'))
BUILD_THREADS = int(os.getenv('BUILD_THREADS', '150'))
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
EXCHANGER_API_KEY = os.getenv('EXCHANGER_API_KEY')
if platform == 'win32':
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver.exe'))
elif platform == 'linux':
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver'))

class FlaskConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', '`\xc8d*J(@\xbc/t\x12\x8ei\x06^\xeb^\xd0\xbb\xd2y\xa7\x99E')
    TEMPLATES_AUTO_RELOAD = True