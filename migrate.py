from db import Database

db = Database()
db_ = Database(db_name='c5game_parser')

for item in db_.find('items', {}, multiple=True):
    item_copy = item
    if 'lowest_sell_order' in item['C5GAME']:
        item['C5GAME']['lowest_sell_order'] = item['C5GAME']['lowest_sell_order']['usd']
    if 'updated_at' in item['C5GAME']:
        item['C5GAME']['updated'] = item['C5GAME']['updated_at']
        del item['C5GAME']['updated_at']
    if 'updated_at' in item['STEAM']:
        item['STEAM']['updated'] = item['STEAM']['updated_at']
        del item['STEAM']['updated_at']
    item['STEAM'] = item['steam']
    del item['STEAM']
    item['C5GAME'] = item['c5game']
    del item['C5GAME']
    db_.insert('item', item)