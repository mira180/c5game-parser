from flask import Blueprint

bp = Blueprint('payment', __name__)

from app.payment import routes