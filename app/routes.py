from flask import render_template, redirect, request, url_for, g, session, jsonify
from flask_openid import OpenID
from app import app

import json
import requests
import logging
import time
from datetime import datetime

from .user import get_or_create
from .table import TableBuilder
from db import Database
from config import ITEMS_COLLECTION, USERS_COLLECTION, SUBSCRIPTION_TIME_FORMAT, EXCHANGER_API_KEY
from constants import Platform, Game, fee, steam_id_re


logger = logging.getLogger(__name__)
db = Database()
oid = OpenID(app, '/tmp', safe_roots=[])
table_builder = TableBuilder()


@app.route('/')
@app.route('/index')
def index():
    return redirect('/dota')

@app.route('/get_table')
def get_table():
    data = []
    games = [game.name for game in Game]
    platforms = [platform.name for platform in Platform]
    first_platform = request.args.get('first_platform', '')
    second_platform = request.args.get('second_platform', '')
    first_min_price = request.args.get('first_min_price', '')
    first_max_price = request.args.get('first_max_price', '')
    first_min_diff = request.args.get('first_min_diff', '')
    first_max_diff = request.args.get('first_max_diff', '')
    first_min_volume = request.args.get('first_min_volume', '')
    first_max_volume = request.args.get('first_max_volume', '')
    first_autobuy = request.args.get('first_autobuy', 'false')
    second_min_price = request.args.get('second_min_price', '')
    second_max_price = request.args.get('second_max_price', '')
    second_min_diff = request.args.get('second_min_diff', '')
    second_max_diff = request.args.get('second_max_diff', '')
    second_min_volume = request.args.get('second_min_volume', '')
    second_max_volume = request.args.get('second_max_volume', '')
    second_autobuy = request.args.get('second_autobuy', 'false')
    subscribed = g.user is not None and g.user['subscribed']
    game = request.args.get('game', '')
    if game in games and first_platform in platforms and second_platform in platforms:
        for record in db.find(ITEMS_COLLECTION, {'game': game, first_platform: {'$exists': True}, second_platform: {'$exists': True}}, multiple=True):
            try:
                item = {}
                item['name'] = record[Platform.STEAM.name]['name']
                platforms_ = []
                for platform in platforms:
                    if platform in record:
                        try:
                            platform_ = {
                                'name': platform,
                                'logo': f'/static/images/{platform}_logo.png',
                                'url': record[platform]['url']
                            }
                            if 'volume' in record[platform]:
                                platform_['volume'] = record[platform]['volume']
                            platforms_.append(platform_)
                        except:
                            pass
                # намного быстрее, чем render_template
                item['platforms'] = '''<div class="platforms">'''
                for platform in platforms_:
                    item['platforms'] += f'''<a href="{platform['url']}" class="ui image" data-platform="{platform['name']}"'''
                    if 'volume' in platform:
                        item['platforms'] += f''' data-tooltip="{platform['volume']} продаж" data-inverted><div class="floating ui black label mini">{platform['volume']}</div'''
                    item['platforms'] += f'''><img src="{platform['logo']}" style="width: 24px;"></a>'''
                item['platforms'] += '''</div>'''
                for idx, platform in enumerate([first_platform, second_platform]):
                    price = ['first_price', 'second_price'][idx]
                    volume = ['first_volume', 'second_volume'][idx]
                    updated = ['first_updated', 'second_updated'][idx]
                    autobuy = True if [first_autobuy, second_autobuy][idx] == 'true' else False
                    if platform == Platform.C5GAME.name:
                        if not autobuy:
                            item[price] = record[platform]['lowest_sell_order']['usd']
                        else:
                            raise Exception("Автопокупка не доступна для платформы")
                    elif platform == Platform.STEAM.name:
                        if not autobuy:
                            item[price] = record[platform]['lowest_sell_order']
                        else:
                            item[price] = record[platform]['highest_buy_order']
                        if 'volume' in record[platform]:
                            item[volume] = record[platform]['volume']
                    item[updated] = record[platform]['updated_at']
                item['first_diff'] = round((item['second_price'] / fee[second_platform][game] / item['first_price'] - 1) * 100, 2)
                item['second_diff'] = round((item['first_price'] / fee[first_platform][game] / item['second_price'] - 1) * 100, 2)
                if not subscribed:
                    if item['first_price'] > 1.0 or item['second_price'] > 1.0:
                        continue
                if first_min_price:
                    try:
                        first_min_price = float(first_min_price)
                        if item['first_price'] < first_min_price:
                            continue
                    except ValueError:
                        pass
                if first_max_price:
                    try:
                        first_max_price = float(first_max_price)
                        if item['first_price'] > first_max_price:
                            continue
                    except ValueError:
                        pass
                if first_min_diff:
                    try:
                        first_min_diff = float(first_min_diff)
                        if item['first_diff'] < first_min_diff:
                            continue
                    except ValueError:
                        pass
                if first_max_diff:
                    try:
                        first_max_diff = float(first_max_diff)
                        if item['first_diff'] > first_max_diff:
                            continue
                    except ValueError:
                        pass
                if first_min_volume:
                    try:
                        first_min_volume = int(first_min_volume)
                        if 'first_volume' in item:
                            volume = item['first_volume']
                        else:
                            volume = 0
                        if volume < first_min_volume:
                            continue
                    except ValueError:
                        pass
                if first_max_volume:
                    try:
                        first_max_volume = int(first_max_volume)
                        if 'first_volume' in item:
                            volume = item['first_volume']
                        else:
                            volume = 0
                        if volume > first_max_volume:
                            continue
                    except ValueError:
                        pass
                if second_min_price:
                    try:
                        second_min_price = float(second_min_price)
                        if item['second_price'] < second_min_price:
                            continue
                    except ValueError:
                        pass
                if second_max_price:
                    try:
                        second_max_price = float(second_max_price)
                        if item['second_price'] > second_max_price:
                            continue
                    except ValueError:
                        pass
                if second_min_diff:
                    try:
                        second_min_diff = float(second_min_diff)
                        if item['second_diff'] < second_min_diff:
                            continue
                    except ValueError:
                        pass
                if second_max_diff:
                    try:
                        second_max_diff = float(second_max_diff)
                        if item['second_diff'] > second_max_diff:
                            continue
                    except ValueError:
                        pass
                if second_min_volume:
                    try:
                        second_min_volume = int(second_min_volume)
                        if 'second_volume' in item:
                            volume = item['second_volume']
                        else:
                            volume = 0
                        if volume < second_min_volume:
                            continue
                    except ValueError:
                        pass
                if second_max_volume:
                    try:
                        second_max_volume = int(second_max_volume)
                        if 'second_volume' in item:
                            volume = item['second_volume']
                        else:
                            volume = 0
                        if volume > second_max_volume:
                            continue
                    except ValueError:
                        pass
                for (price, updated) in zip(['first_price', 'second_price'], ['first_updated', 'second_updated']):
                    item[price] = f'''<div data-tooltip="{item[updated]}" data-inverted>{item[price]}$</div>'''
                for diff in ['first_diff', 'second_diff']:
                    item[diff] = str(item[diff]) + '%'
                data.append(item)
            except Exception as e:
                pass

    data = table_builder.collect_data_serverside(request, data)
    return jsonify(data)

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
    
    platforms = {}
    for platform in Platform:
        platforms[platform.name] = {
            'name': platform.name
        }
    return render_template('table.html', game=game, platforms=platforms)

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

@app.route('/payment/result')
def payment_result():
    merchant_id = request.args.get('MERCHANT_ID')
    amount = request.args.get('AMOUNT')
    intid = request.args.get('intid')
    merchant_order_id = request.args.get('MERCHANT_ORDER_ID')
    p_email = request.args.get('P_EMAIL')
    p_phone = request.args.get('P_PHONE')
    cur_id = request.args.get('CUR_ID')
    sign = request.args.get('SIGN')
    us_key = request.args.get('us_key')
    print(f'{merchant_id}, {amount}, {intid}, {merchant_order_id}, {p_email}, {p_phone}, {cur_id}, {sign}, {us_key}')
    return 'OK'

@app.route('/payment/success')
def payment_success():
    redirect('/')

@app.route('/payment/failed')
def payment_failed():
    redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f'404 - пользователь попытался перейти на несуществующую страницу: {request.path}')
    return render_template('error.html', error=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.warning(f'500 - произошла ошибка сервера по адресу: {request.path}')
    return render_template('error.html', error=500), 500