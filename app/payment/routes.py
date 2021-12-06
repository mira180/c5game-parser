from flask import redirect, request, current_app, abort
from flask_login import current_user, login_required
from app.payment import bp
from app.models import Order, User
from hashlib import md5
from urllib.parse import urlencode
import logging
from datetime import datetime, timedelta
from app.payment.client import get_client_ip

logger = logging.getLogger(__name__)

@bp.route('/make')
@login_required
def make():
    months = request.args.get('months', type=int, default=1)
    if months < 1 or months > 999:
        months = 1
    m = current_app.config['MERCHANT_ID']
    format_float = lambda f: f if f % 1 else int(f)
    oa = format_float(months * current_app.config['PRICE_PER_MONTH'])
    currency = current_app.config['PRICE_CURRENCY']
    order = Order(steam_id=current_user.steam_id, status='PROCESS', amount=oa, currency=currency, created=datetime.utcnow().strftime(current_app.config['DATE_FORMAT']))
    o = order.order_id
    order.save()
    s = md5(f"{m}:{oa}:{current_app.config['MERCHANT_SECRET_1']}:{currency}:{o}".encode('utf-8')).hexdigest()
    return redirect('https://pay.freekassa.ru/?' + urlencode({'m': m, 'oa': oa, 'currency': currency, 'o': o, 's': s}))

@bp.route('/result')
def result():
    client_ip = get_client_ip(request)
    logger.info(client_ip)
    if client_ip not in current_app.config['MERCHANT_ALLOWED_IP_ADDRESSES']:
        logger.info('не разрешенный ip')
        abort(403)
    merchant_id = request.args.get('MERCHANT_ID', type=int)
    format_float = lambda f: f if f % 1 else int(f)
    amount = format_float(request.args.get('AMOUNT', type=float))
    intid = request.args.get('intid', type=int)
    merchant_order_id = request.args.get('MERCHANT_ORDER_ID', type=int)
    p_email = request.args.get('P_EMAIL')
    p_phone = request.args.get('P_PHONE')
    cur_id = request.args.get('CUR_ID', type=int)
    sign = request.args.get('SIGN')
    payer_account = request.args.get('PAYER_ACCOUNT')
    if sign != md5(f"{current_app.config['MERCHANT_ID']}:{amount}:{current_app.config['MERCHANT_SECRET_2']}:{merchant_order_id}".encode('utf-8')).hexdigest():
        logger.warning(f'ошибка подписи {sign}')
        abort(400)
    order = Order.objects(order_id=merchant_order_id).first()
    if not order or order.amount != amount or order.status != 'PROCESS':
        logger.warning(f'ошибка заказа {merchant_order_id}')
        abort(400)
    user = User.objects(steam_id=order.steam_id).first()
    months = order.amount / current_app.config['PRICE_PER_MONTH']
    if user.subscribed and user.expires:
        expires = (datetime.strptime(user.expires, current_app.config['DATE_FORMAT']) + timedelta(days=30 * months)).strftime(current_app.config['DATE_FORMAT'])
    else:
        expires = (datetime.utcnow() + timedelta(days=30 * months)).strftime(current_app.config['DATE_FORMAT'])
    user.update(subscribed=True, expires=expires)
    order.update(status='SUCCESS', merchant_id=merchant_id, operation_id=intid, email=p_email, phone=p_phone, currency_id=cur_id, payer_account=payer_account)
    return 'YES'

@bp.route('/success')
def success():
    return 'SUCCESS'

@bp.route('/failed')
def failed():
    return 'FAILED'
