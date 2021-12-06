from flask import redirect, request, current_app
from flask_login import current_user, login_required
from app.payment import bp

import hashlib
import urllib.parse
import logging

logger = logging.getLogger(__name__)

@bp.route('/make')
@login_required
def make():
    months = request.args.get('months', type=int, default=1)
    if months < 1 or months > 999:
        months = 1
    m = current_app.config['MERCHANT_ID']
    oa = round(months * current_app.config['PRICE_PER_MONTH'], 2)
    o = current_user.steam_id
    secret = current_app.config['MERCHANT_SECRET_1']
    currency = current_app.config['PRICE_CURRENCY']
    s = hashlib.md5(f'{m}:{oa}:{secret}:{currency}:{o}'.encode('utf-8')).hexdigest()
    return redirect('https://pay.freekassa.ru/?' + urllib.parse.urlencode({'m': m, 'oa': oa, 'currency': currency, 'o': o, 's': s}))

@bp.route('/result')
def result():
    merchant_id = request.args.get('MERCHANT_ID')
    amount = request.args.get('AMOUNT')
    intid = request.args.get('intid')
    merchant_order_id = request.args.get('MERCHANT_ORDER_ID')
    p_email = request.args.get('P_EMAIL')
    p_phone = request.args.get('P_PHONE')
    cur_id = request.args.get('CUR_ID')
    sign = request.args.get('SIGN')
    logger.info(f'{merchant_id}, {amount}, {intid}, {merchant_order_id}, {p_email}, {p_phone}, {cur_id}, {sign}')
    return 'YES'

@bp.route('/success')
def success():
    return 'SUCCESS'

@bp.route('/failed')
def failed():
    return 'FAILED'
