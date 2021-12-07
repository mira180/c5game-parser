from flask import abort, render_template, request, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from functools import wraps
from app.models import Order, User
from app.tables import TableBuilder, ORDERS_TABLE_COLUMNS, USERS_TABLE_COLUMNS

orders_table_builder = TableBuilder(ORDERS_TABLE_COLUMNS)
users_table_builder = TableBuilder(USERS_TABLE_COLUMNS)

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
        order_['user'] = f'''<div class="user"><a href="{user.profile}" class="ui image"><img src="{user.avatar}"></a><div>{user.name}<br><span class="steam_id">{user.steam_id}</span></div>'''
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
            'user': f'''<div class="user"><a href="{user.profile}" class="ui image"><img src="{user.avatar}"></a><div>{user.name}<br><span class="steam_id">{user.steam_id}</span></div>''',
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

@bp.route('/update')
@login_required
@admin_required
def update():
    return 'UPDATE'