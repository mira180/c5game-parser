from flask import render_template, request
from app.errors import bp

import logging

logger = logging.getLogger(__name__)

@bp.app_errorhandler(404)
def page_not_found(e):
    logger.warning(f'404 - пользователь попытался перейти на несуществующую страницу: {request.path}')
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    logger.warning(f'500 - произошла ошибка сервера по адресу: {request.path}')
    return render_template('errors/500.html'), 500