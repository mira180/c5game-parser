import logging
import os
from sys import platform
from dotenv import load_dotenv
import json

load_dotenv('.env')

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('selenium').setLevel('CRITICAL')
logging.basicConfig(
        level='DEBUG',
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%H:%M:%S")


UPDATED_TIME_FORMAT = os.getenv('UPDATED_TIME_FORMAT', r'%Y-%m-%d %H:%M:%S')
ITEMS_COLLECTION = os.getenv('ITEMS_COLLECTION', 'items')
USERS_COLLECTION = os.getenv('USERS_COLLECTION', 'users')
PROXY_FILE = os.getenv('PROXY_FILE', 'proxy.txt')
UPDATE_THREADS = int(os.getenv('UPDATE_THREADS', '150'))
BUILD_THREADS = int(os.getenv('BUILD_THREADS', '150'))
if platform == 'win32':
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver.exe'))
elif platform == 'linux':
    CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', os.path.join(os.path.abspath(os.getcwd()), 'webdriver/chromedriver'))

DB_NAME = os.getenv('DB_NAME', 'c5game_parser')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '27017'))
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_AUTH_SOURCE = os.getenv('DB_AUTH_SOURCE', 'admin')
DATE_FORMAT = os.getenv('DATE_FORMAT', r'%Y-%m-%d %H:%M:%S')
EXCHANGER_API_KEY = os.getenv('EXCHANGER_API_KEY')
STEAM_API_KEY = os.getenv('STEAM_API_KEY')
UPDATE_THREADS = int(os.getenv('UPDATE_THREADS', '100'))
UPDATE_INTERVAL = float(os.getenv('UPDATE_INTERVAL', '15'))
UPDATER_HOST = os.getenv('UPDATER_HOST', '127.0.0.1')
UPDATER_PORT = int(os.getenv('UPDATER_PORT', '44400'))

class FlaskConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', '`\xc8d*J(@\xbc/t\x12\x8ei\x06^\xeb^\xd0\xbb\xd2y\xa7\x99E')
    TEMPLATES_AUTO_RELOAD = True
    MONGODB_SETTINGS = {
        'db': DB_NAME,
        'host': DB_HOST,
        'port': DB_PORT,
        'username': DB_USERNAME,
        'password': DB_PASSWORD,
        'authentication_source': DB_AUTH_SOURCE
    }
    MERCHANT_ID = int(os.getenv('MERCHANT_ID'))
    MERCHANT_SECRET_1 = os.getenv('MERCHANT_SECRET_1')
    MERCHANT_SECRET_2 = os.getenv('MERCHANT_SECRET_2')
    PRICE_PER_MONTH = float(os.getenv('PRICE_PER_MONTH'))
    PRICE_CURRENCY = os.getenv('PRICE_CURRENCY')
    MERCHANT_ALLOWED_IP_ADDRESSES = json.loads(os.getenv('MERCHANT_ALLOWED_IP_ADDRESSES'))
    DATE_FORMAT = DATE_FORMAT