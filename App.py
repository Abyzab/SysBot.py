import json
import os
import threading
import traceback

from bots.EggBot import EggBotConnection
from bots.Sysbot import PycordManager, SysBotConnection
from bots.utils.JsonHandler import JsonHandler
from bots.commands.Pycord import UserQueue


def makeBlankConfig():
    defaultConfig = {"token": "", "tradeTimeout": 60, "maxQueue": 20, "botOwner": [], "discordPrefix" : "+", "address": "",
                     "port": 6000, "botType": "Sysbot", "eggConfig" : {"shiny" : True, 
                     "ivs" : [None, None, None, None, None, None], "nature" : "", "ability" : None}}
    with open("config.json", "w+") as newConfig:
        json.dump(defaultConfig, newConfig, indent=4)
    print("Blank Config created, please fill out your settings")


if __name__ == "__main__":

    if os.path.exists(f"{os.path.abspath(os.curdir)}/config.json"):
        Configs = JsonHandler(f"{os.path.abspath(os.curdir)}/config.json", True)
        try:
            if Configs["botType"].lower() == "eggbot":
                EggBot = EggBotConnection(Configs["address"], Configs["port"], Configs["eggConfig"])
                EggBot.mainRoutine()

            elif Configs["botType"].lower() == "sysbot":
                settings = JsonHandler('settings')
                q = UserQueue(settings)
                startTradeRoutine = threading.Semaphore(q.size())
                PyBot = PycordManager(startTradeRoutine, q, Configs, settings)
                SysBot = SysBotConnection(Configs["address"], int(Configs["port"]), startTradeRoutine, q, Configs, settings,
                                        PyBot)

                threading.Thread(target=SysBot.start).start()
                PyBot.run(Configs["token"])
        except Exception:
            print(traceback.format_exc())

    else:
        makeBlankConfig()
