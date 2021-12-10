from app.getter import Updater
from constants import Platform
import time


updater = Updater([Platform.C5GAME, Platform.STEAM])
updater.start()

while True:
    time.sleep(5)