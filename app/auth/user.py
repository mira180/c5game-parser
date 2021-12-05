from app.models import User
import logging
import requests
from datetime import datetime
from config import STEAM_API_KEY, DATE_FORMAT


logger = logging.getLogger(__name__)


def create_user(steam_id: int):
    User(steam_id=steam_id, registered=datetime.now().strftime(DATE_FORMAT)).save()
    return update_user(steam_id)

def update_user(steam_id: int):
    user = User.objects(steam_id=steam_id).first()
    user.update(last_login=datetime.now().strftime(DATE_FORMAT))
    try:
        steam = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}").json()['response']['players'][0]
        user.update(profile=steam['profileurl'], avatar=steam['avatarfull'], name=steam['personaname'])
    except Exception as e:
        logger.error(f'Ошибка обновления данных о пользователе: {e}')
    return User.objects(steam_id=steam_id).first()