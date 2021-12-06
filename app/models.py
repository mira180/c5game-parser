from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Document):
    steam_id = db.IntField()
    name = db.StringField()
    profile = db.StringField()
    avatar = db.StringField()
    subscribed = db.BooleanField(default=False)
    expires = db.StringField()
    registered = db.StringField()
    last_seen = db.StringField()

@login.user_loader
def load_user(id):
    return User.objects(id=id).first()

class Platform(db.EmbeddedDocument):
    url = db.StringField()
    name = db.StringField()
    updated_at = db.StringField()
    volume = db.IntField()
    lowest_sell_order = db.FloatField()
    highest_buy_order = db.FloatField()
    sell_count = db.IntField()

class Item(db.Document):
    steam = db.EmbeddedDocumentField(Platform)
    c5game = db.EmbeddedDocumentField(Platform)

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