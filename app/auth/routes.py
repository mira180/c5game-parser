from flask import redirect, url_for
from flask_login import current_user, logout_user, login_user
from app import oid
from app.auth import bp
from app.models import User
from app.auth.user import create_user, update_user
from constants import steam_id_re


"""
@bp.before_request
def before_request():
    g.user = None
    if 'steam_id' in session:
        g.user = db.find(USERS_COLLECTION, {'steam_id': session['steam_id']})
        if g.user['subscribed'] and datetime.strptime(g.user['subscription_expires'], SUBSCRIPTION_TIME_FORMAT) < datetime.now():
            g.user['subscribed'] = False
            db.update(USERS_COLLECTION, {'steam_id': session['steam_id']}, {'subscribed': False})
"""


@bp.route('/login')
@oid.loginhandler
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return oid.try_login('https://steamcommunity.com/openid')

@oid.after_login
def after_login(resp):
    steam_id = int(steam_id_re.search(resp.identity_url).group(1))
    user = User.objects(steam_id=steam_id).first()
    if user is None:
        user = create_user(steam_id)
    else:
        user = update_user(steam_id)
    login_user(user, remember=True)
    return redirect(oid.get_next_url())

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))