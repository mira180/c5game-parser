from updater import Updater
from db import Database
from constants import Game, Platform
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    db = Database()
    updater = Updater(db, use_proxy=True)
    #updater.c5game_builder.build_database([Game.Z1, Game.TF2, Game.RUST, Game.STEAM, Game.PAYDAY2])
    updater.update_all([Game.Z1, Game.TF2, Game.RUST], [Platform.STEAM])
    #updater.c5game_builder.add_item('https://www.c5game.com/csgo/25910/S.html', Game.CSGO)
    """
    updater.c5game_builder.build_database([Game.CSGO])

    t = updater.get_comparison_table({'platform': Platform.C5GAME}, {'platform': Platform.STEAM, 'min_price': 1, 'max_price': 2, 'autobuy': True}, Game.CSGO)
    for i in range(10):
        print(t[i])
    
    updater.update_all([Game.CSGO], [Platform.STEAM, Platform.C5GAME])
    """
    #updater.update_item('619d40bca45cb40c0c0fb4fe', [Platform.STEAM, Platform.C5GAME])