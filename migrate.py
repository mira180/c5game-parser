from db import Database
from config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_AUTH_SOURCE

db = Database(db_name=DB_NAME)
db_ = Database(uri=f'mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?authSource={DB_AUTH_SOURCE}', db_name=DB_NAME)

print('start')
for item in db.find('item', {}, multiple=True):
    db_.insert('item', item)
print('end')