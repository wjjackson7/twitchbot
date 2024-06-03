# main for running twitchbot

from twitchbot import Twitchbot
from riotbot import Riotbot

if __name__ == "__main__":
    t = Twitchbot()
    t.run()
    t.get_Summoner('Strangeness')

    r = Riotbot()
    r.getSummoner("Strangeness")