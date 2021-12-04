import logging
import requests
from config import USERS_COLLECTION, STEAM_API_KEY


logger = logging.getLogger(__name__)


def get_or_create(db, steam_id: int):
    if db.find(USERS_COLLECTION, {'steam_id': steam_id}):
        # update user info
        pass
    else:
        db.insert(USERS_COLLECTION,
        {
            'steam_id': steam_id,
            'subscribed': False,
            'subscription_expires': '',
        })
        logger.info(f'Добавлен новый пользователь с steam_id {steam_id}')
    try:
        user_info = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}").json()
        user_info = user_info['response']['players'][0]
        db.update(USERS_COLLECTION, {'steam_id': steam_id}, {'profile': user_info['profileurl'], 'avatar': user_info['avatarfull'], 'name': user_info['personaname']})
    except Exception as e:
        logger.error(f'Ошибка получения данных о пользователе Steam по API: {e}')
    return db.find(USERS_COLLECTION, {'steam_id': steam_id})