from flask_login import UserMixin
from app import db, login
from constants import Game

class User(UserMixin, db.Document):
    steam_id = db.IntField()
    name = db.StringField()
    profile = db.StringField()
    avatar = db.StringField()
    subscribed = db.BooleanField(default=False)
    expires = db.StringField()
    registered = db.StringField()
    last_seen = db.StringField()
    is_admin = db.BooleanField(default=False)

    def get_id(self):
        return str(self.steam_id)

@login.user_loader
def load_user(steam_id):
    return User.objects(steam_id=steam_id).first()

class Platform(db.EmbeddedDocument):
    url = db.StringField()
    name = db.StringField()
    updated = db.StringField()
    volume = db.IntField()
    lowest_sell_order = db.FloatField()
    highest_buy_order = db.FloatField()
    sell_count = db.IntField()
    image = db.StringField()
    median_price = db.FloatField()

class Item(db.Document):
    game = db.EnumField(Game)
    STEAM = db.EmbeddedDocumentField(Platform)
    C5GAME = db.EmbeddedDocumentField(Platform)

class Order(db.Document):
    order_id = db.SequenceField()
    steam_id = db.IntField()
    status = db.StringField()
    amount = db.FloatField()
    currency = db.StringField()
    created = db.StringField()
    merchant_id = db.IntField()
    operation_id = db.IntField()
    email = db.StringField()
    phone = db.StringField()
    currency_id = db.IntField()
    payer_account = db.StringField()