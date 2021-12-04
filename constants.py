from enum import Enum
import re

class Game(Enum):
    DOTA = 0
    CSGO = 1
    TF2 = 2
    Z1 = 3
    RUST = 4
    STEAM = 5
    PAYDAY2 = 6

class Platform(Enum):
    C5GAME = 0
    STEAM = 1

fee = {
    Platform.C5GAME.name: {
        Game.DOTA.name: 1,
        Game.CSGO.name: 1,
        Game.TF2.name: 1,
        Game.Z1.name: 1,
        Game.RUST.name: 1,
        Game.STEAM.name: 1,
        Game.PAYDAY2.name: 1
    },
    Platform.STEAM.name: {
        Game.DOTA.name: 1.15,
        Game.CSGO.name: 1.15,
        Game.TF2.name: 1.10,
        Game.Z1.name: 1,
        Game.RUST.name: 1,
        Game.STEAM.name: 1,
        Game.PAYDAY2.name: 1
    }
}

steam_id_re = re.compile(r'steamcommunity.com\/openid\/id\/(\d+)$')
price_re = re.compile(r'<div[^>]*>([\d\.\$]+)</div>')