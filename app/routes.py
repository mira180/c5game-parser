from flask import render_template, redirect, request, url_for, g, session
from flask_openid import OpenID
from app import app

import json
import requests
import logging
import time
from datetime import datetime

from .user import get_or_create
from db import Database
from config import ITEMS_COLLECTION, USERS_COLLECTION, SUBSCRIPTION_TIME_FORMAT, EXCHANGER_API_KEY
from constants import Platform, Game, fee, steam_id_re


logger = logging.getLogger(__name__)
db = Database()
oid = OpenID(app, '/tmp', safe_roots=[])


@app.route('/')
@app.route('/index')
def index():
    return redirect('/dota')

@app.route('/dota')
@app.route('/csgo')
@app.route('/tf2')
@app.route('/z1')
@app.route('/rust')
@app.route('/steam')
@app.route('/payday2')
def table():
    if request.path == '/dota':
        game = Game.DOTA.name
    elif request.path == '/csgo':
        game = Game.CSGO.name
    elif request.path == '/tf2':
        game = Game.TF2.name
    elif request.path == '/z1':
        game = Game.Z1.name
    elif request.path == '/rust':
        game = Game.RUST.name
    elif request.path == '/steam':
        game = Game.STEAM.name
    elif request.path == '/payday2':
        game = Game.PAYDAY2.name
    first_platform = request.args.get('first_platform', Platform.C5GAME.name)
    second_platform = request.args.get('second_platform', Platform.STEAM.name)
    subscribed = g.user is not None and g.user['subscribed']
    platforms = {}
    for platform in Platform:
        platforms[platform.name] = {
            'name': platform.name,
            'logo': f'/static/images/{platform.name}_logo.png',
            'short': platform.name[:2]
        }
    for platform in [first_platform, second_platform]:
        if platform not in platforms:
            raise Exception(f"Неизвестная платформа: {platform}")
    items = []
    for item in db.find(ITEMS_COLLECTION, {'game': game, first_platform: { '$exists': True },  second_platform: { '$exists': True }}, multiple=True):
        try:
            nitem = {}
            nitem['name'] = item[Platform.STEAM.name]['name']
            for platform in platforms:
                if platform in item:
                    try:
                        nitem_platform = {}

                        if platform == Platform.C5GAME.name:
                            nitem_platform['price'] = item[platform]['lowest_sell_order']['usd']
                        
                        elif platform == Platform.STEAM.name:
                            nitem_platform['price'] = item[platform]['lowest_sell_order']
                            if 'volume' in item[platform]:
                                nitem_platform['volume'] = item[platform]['volume']
                        
                        nitem_platform['url'] = item[platform]['url']
                        nitem_platform['updated_at'] = item[platform]['updated_at']
                        nitem[platform] = nitem_platform
                    except:
                        pass

            if not subscribed:
                if nitem[first_platform]['price'] > 1.0 or nitem[second_platform]['price'] > 1.0:
                    raise Exception("Для получения предмета требуется подписка")

            nitem[first_platform]['diff'] = round((nitem[second_platform]['price'] / fee[second_platform][game] / nitem[first_platform]['price'] - 1) * 100, 2)
            nitem[second_platform]['diff'] = round((nitem[first_platform]['price'] / fee[first_platform][game] / nitem[second_platform]['price'] - 1) * 100, 2)
            items.append(nitem)
        except:
            pass

    return render_template('table.html', first_platform=first_platform, second_platform=second_platform, platforms=platforms, items=items)

@app.route('/account')
def account():
    if g.user is not None:
        return render_template('account.html')
    else:
        return redirect('/login')

@app.route('/get_conversion_rates')
def get_conversion_rates():
    try:
        with open('latest.txt', 'r') as lf:
            latest = json.loads(lf.read())
        if time.time() - latest['updated_at'] > 86400:
            try:
                logger.info('Обновляем курсы валют')
                latest_ = requests.get('https://v6.exchangerate-api.com/v6/{EXCHANGER_API_KEY}/latest/USD').json()
                if latest_['result'] == 'success':
                    latest['updated_at'] = latest_['time_last_update_unix']
                    latest['base_code'] = latest_['base_code']
                    latest['conversion_rates'] = latest_['conversion_rates']
                    with open('latest.txt', 'w') as lf:
                        lf.write(json.dumps(latest))
                else:
                    raise Exception(f'Запрос к API вернул статус: {latest_["result"]}')
            except Exception as e:
                logger.error(f'Ошибка получения курсов валют по API: {e}')
        return latest
    except Exception as e:
        logger.error(f'Ошибка во время получения курсов валют: {e}')
        return {}, 500

@app.before_request
def before_request():
    g.user = None
    if 'steam_id' in session:
        g.user = db.find(USERS_COLLECTION, {'steam_id': session['steam_id']})
        if g.user['subscribed'] and datetime.strptime(g.user['subscription_expires'], SUBSCRIPTION_TIME_FORMAT) < datetime.now():
            g.user['subscribed'] = False
            db.update(USERS_COLLECTION, {'steam_id': session['steam_id']}, {'subscribed': False})

@app.route('/login')
@oid.loginhandler
def login_steam():
    if g.user is not None:
        return redirect(oid.get_next_url())
    else:
        return oid.try_login('https://steamcommunity.com/openid')

@oid.after_login
def new_steam_user(resp):
    steam_id = int(steam_id_re.search(resp.identity_url).group(1))
    g.user = get_or_create(db, steam_id)
    session['steam_id'] = steam_id
    return redirect(oid.get_next_url())

@app.route('/logout')
def logout():
    session.pop('steam_id', None)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f'404 - пользователь попытался перейти на несуществующую страницу: {request.path}')
    return render_template('error.html', error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.warning(f'500 - произошла ошибка сервера по адресу: {request.path}')
    return render_template('error.html', error=500), 500