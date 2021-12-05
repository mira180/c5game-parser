from flask import redirect, request, abort, session
from app.payment import bp

import hashlib
import urllib.parse
import logging

logger = logging.getLogger(__name__)

@bp.route('/make')
def make():
    months = request.args.get('months', type=int, default=1)
    if months < 1 or months > 999:
        abort(400)
    if 'steam_id' not in session:
        abort(401)
    steam_id = session['steam_id']
    logger.info(f'Оплата: Пользователь {steam_id} - {months} месяцев')
    return 'MAKE'

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
    us_key = request.args.get('us_key')
    logger.info(f'{merchant_id}, {amount}, {intid}, {merchant_order_id}, {p_email}, {p_phone}, {cur_id}, {sign}, {us_key}')
    return 'YES'

@bp.route('/success')
def success():
    return 'SUCCESS'

@bp.route('/failed')
def failed():
    return 'FAILED'
