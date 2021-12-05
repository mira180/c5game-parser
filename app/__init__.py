from flask import Flask
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_openid import OpenID
from config import FlaskConfig

db = MongoEngine()
login = LoginManager()
login.login_view = 'auth.login'
oid = OpenID()

app = Flask(__name__)
app.config.from_object(FlaskConfig)

db.init_app(app)
login.init_app(app)
oid.init_app(app)

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.payment import bp as payment_bp
app.register_blueprint(payment_bp, url_prefix='/payment')

from app import models