from flask import abort, render_template, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from app.admin import bp
from functools import wraps
from app.models import Order, User
from app.tables import TableBuilder, ORDERS_TABLE_COLUMNS, USERS_TABLE_COLUMNS
from app.getter import Updater
from datetime import datetime, timedelta
from constants import Platform
from config import UPDATE_INTERVAL, UPDATE_THREADS

orders_table_builder = TableBuilder(ORDERS_TABLE_COLUMNS)
users_table_builder = TableBuilder(USERS_TABLE_COLUMNS)
updater = Updater([Platform.STEAM, Platform.C5GAME], threads=UPDATE_THREADS, interval=UPDATE_INTERVAL)
updater.start()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/get_orders')
@login_required
@admin_required
def get_orders():
    data = []
    for order in Order.objects:
        order_ = {
            'order_id': order.order_id,
            'created': order.created,
            'amount': str(order.amount) + '$',
        }
        user = User.objects(steam_id=order.steam_id).first()
        order_['user'] = f'''<div class="user" {'style="color: rgba(255, 0, 0);"' if user.is_admin else ''}><a href="{user.profile}" class="ui image"><img src="{user.avatar}"></a><a href="{url_for('admin.user', steam_id=user.steam_id)}" style="color: inherit;"><div>{user.name}<br><span class="steam_id">{user.steam_id}</span></div></a></div>''',
        if order.status == 'PROCESS':
            order_['status'] = 'В процессе'
        elif order.status == 'SUCCESS':
            order_['status'] = 'Успешно'
        else:
            order_['status'] = 'Ошибка'
        data.append(order_)
    data = orders_table_builder.collect_data_serverside(request, data)
    return jsonify(data)

@bp.route('/get_users')
@login_required
@admin_required
def get_users():
    data = []
    for user in User.objects:
        user_ = {
            'user': f'''<div class="user" {'style="color: rgba(255, 0, 0);"' if user.is_admin else ''}><a href="{user.profile}" class="ui image"><img src="{user.avatar}"></a><a href="{url_for('admin.user', steam_id=user.steam_id)}" style="color: inherit;"><div>{user.name}<br><span class="steam_id">{user.steam_id}</span></div></a></div>''',
            'subscribed': 'Да' if user.subscribed else 'Нет',
            'expires': user.expires if user.subscribed else '-',
            'registered': user.registered,
            'last_seen': user.last_seen,
        }
        data.append(user_)
    data = users_table_builder.collect_data_serverside(request, data)
    return jsonify(data)

@bp.route('/orders')
@login_required
@admin_required
def orders():
    return render_template('admin/orders.html')

@bp.route('/users')
@login_required
@admin_required
def users():
    return render_template('admin/users.html')

@bp.route('/users/<int:steam_id>')
@login_required
@admin_required
def user(steam_id):
    user = User.objects(steam_id=steam_id).first()
    if not user:
        abort(404)
    return render_template('admin/user.html', user=user, orders=Order.objects(steam_id=steam_id).order_by('-order_id'))

@bp.route('/update')
@login_required
@admin_required
def update():
    return render_template('admin/update.html', statistics=updater.statistics, last_statistics=updater.last_statistics)

@bp.route('/control')
@login_required
@admin_required
def control():
    op = request.args.get('op')
    if op == 'give_sub':
        steam_id = request.args.get('steam_id')
        if not steam_id:
            abort(400)
        user = User.objects(steam_id=steam_id).first()
        if not user:
            abort(404)
        if user.subscribed and user.expires:
            expires = (datetime.strptime(user.expires, current_app.config['DATE_FORMAT']) + timedelta(days=30)).strftime(current_app.config['DATE_FORMAT'])
        else:
            expires = (datetime.utcnow() + timedelta(days=30)).strftime(current_app.config['DATE_FORMAT'])
        user.update(subscribed=True, expires=expires)
    elif op == 'take_sub':
        steam_id = request.args.get('steam_id')
        if not steam_id:
            abort(400)
        user = User.objects(steam_id=steam_id).first()
        if not user:
            abort(404)
        user.update(subscribed=False)
    else:
        abort(400)
    return 'YES'