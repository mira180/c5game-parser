from flask import render_template, redirect, request, jsonify
from flask_login import login_required, current_user
from app.main import bp
from app.main.table import TableBuilder
from app.main.conversion import ConversionRates

import logging
from datetime import datetime
from db import Database
from config import ITEMS_COLLECTION, EXCHANGER_API_KEY, DATE_FORMAT
from constants import Platform, Game, fee


logger = logging.getLogger(__name__)
table_builder = TableBuilder()
conversion_rates = ConversionRates(EXCHANGER_API_KEY)
db = Database()


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow().strftime(DATE_FORMAT)
        if current_user.subscribed and datetime.strptime(current_user.expires, DATE_FORMAT) < datetime.utcnow():
            current_user.subscribed = False
        current_user.save()

@bp.route('/')
@bp.route('/index')
def index():
    return redirect('/dota')

@bp.route('/get_table')
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
    subscribed = current_user.subscribed
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

@bp.route('/dota')
@bp.route('/csgo')
@bp.route('/tf2')
@bp.route('/z1')
@bp.route('/rust')
@bp.route('/steam')
@bp.route('/payday2')
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

@bp.route('/account')
@login_required
def account():
    return render_template('account.html')

@bp.route('/get_conversion_rates')
def get_conversion_rates():
    return conversion_rates.get()