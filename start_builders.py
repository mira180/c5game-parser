import builders.markettm
from constants import Game, Platform

if __name__ == '__main__':
    games = [Game.DOTA]
    platforms = [Platform.MARKETTM]
    
    if Platform.MARKETTM in platforms:
        builders.markettm.build(games)