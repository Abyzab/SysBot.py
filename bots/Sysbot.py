import binascii
import socket
import time
import discord
import threading
import os
import random
import datetime

from bots.commands.SysBotBaseCommands import SysBotBaseCommands
from bots.commands.Pycord import UserQueue
from discord.ext import commands
from bots.utils.JsonHandler import JsonHandler
from bots.utils.Pb8 import Pb8
from bots.utils.PokeCrypto import DecryptEb8, EncryptPb8


class SysBotConnection:
    # Please, send help
    def __init__(self, address: str, port: int, startTradeRoutine: threading.Semaphore, q: UserQueue,
                 config: JsonHandler, settings: JsonHandler, PyBot) -> None:
        self.con = None
        self.PyBot = PyBot
        self.triggerEvent = startTradeRoutine

        self.ConnectSocket(address, port)
        self.commands = SysBotBaseCommands(self.con)
        self.pointers = JsonHandler('pointers')

        self.queue = q
        self.config = config
        self.settings = settings

        self.pokemon = {}
        self.curr_user = None
        self.curr_linkcode = None
        self.start_time = None

        self.loadPokemonFromDir()
        self.startupCommands()

    def startupCommands(self) -> None:
        self.commands.updateFreezeRate()
        self.commands.freeze(self.pointers["instantText"], "0xFFFF7F7F")
        self.commands.freeze(self.pointers["fps"], "0x01")
        self.commands.sendCommand("configure keySleepTime 35")

    def start(self) -> None:
        self.await_thread()

    def ConnectSocket(self, address: str, port: int) -> None:
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting...")

        self.con.connect((address, port))

        print("Connected")

    def checkTimeout(self) -> bool:
        print(f'{(datetime.datetime.now() - self.start_time).seconds} seconds have passed')
        return (datetime.datetime.now() - self.start_time).seconds <= int(self.config['tradeTimeout'])

    def loadPokemonFromDir(self) -> None:
        dir_path = f"{os.path.dirname(os.path.realpath(__file__))}/distribute"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        for filename in os.listdir(dir_path):
            names = filename.rsplit(".", 2)
            if names[1].lower() == 'pb8':
                with open(f'{dir_path}/{filename}', "rb") as f:
                    unencryptedBytes = bytearray(f.read())
                    if len(unencryptedBytes) == 0x158:
                        self.pokemon[names[0].lower()] = EncryptPb8(unencryptedBytes)
        
        if len(self.pokemon) == 0:
            raise Exception("Distribute directory has no valid pb8 files. Nothing to distribute!")

    def generateLinkCode(self) -> str:
        linkcode = ""
        for x in range(8):
            linkcode += str(random.randint(0, 9))
        return linkcode

    def awaitTradeDialogue(self) -> bool:
        res = self.commands.peek(self.pointers["dialogue_open"], 1)
        unexpired = self.checkTimeout()
        while res != b'07' and unexpired:
            res = self.commands.peek(self.pointers["dialogue_open"], 1)
            unexpired = self.checkTimeout()
        return unexpired

    def awaitTradeWindow(self) -> bool:
        res = self.commands.peek(self.pointers["is_trading"], 1)
        unexpired = self.checkTimeout()
        while (res != b'01') and unexpired:
            self.commands.clickA(0.3)
            unexpired = self.checkTimeout()
            res = self.commands.peek(self.pointers["is_trading"], 1)
        return unexpired

    def awaitTradeOffer(self) -> None:
        while self.commands.peek(self.pointers["is_receive"], 1) == b'00':
            pass

    def awaitTradeComplete(self) -> None:
        time.sleep(5)  # Ensure Trade has started
        while self.commands.peek(self.pointers["tradeFlowState"], 1) != b'01':
            pass
    
    def readTradePokemon(self) -> Pb8:
        mon = self.commands.peek(self.pointers["trade"], 344)
        return Pb8(DecryptEb8(bytearray(binascii.unhexlify(mon))))

    def waitForConnection(self) -> None:
        self.commands.clickA(0.5)
        while self.commands.peek(self.pointers["connectionDetect"], 1) not in [b'2D', b'25']:
            pass
        if self.commands.peek(self.pointers["connectionDetect"], 1) == b'25':
            self.commands.clickA(0.5)
            time.sleep(3)

    def joinUnionRoom(self) -> None:
        self.commands.clickY(0.5)
        self.commands.clickRight(0.5)
        self.commands.clickA(1)
        self.commands.clickA(1)
        self.commands.clickA(0.8)
        self.commands.clickDown(0.5)
        self.commands.clickDown(1)
        self.commands.clickA(1)
        self.commands.clickA(0.5)

        self.waitForConnection()

        self.commands.clickA(0.5)
        self.commands.clickA(8)

        print(self.curr_linkcode)

        self.commands.enterCode(self.curr_linkcode)
        time.sleep(0.5)

        self.commands.clickPlus(1.5)

        self.commands.clickA(8)

        self.commands.moveForward(0.5)
        time.sleep(2.5)

        if self.commands.peek(self.pointers["in_union"], 1) ==  b'00':
            print(self.commands.peek(self.pointers["in_union"], 1))
            self.restartGame()
            self.PyBot.loop.create_task(self.PyBot.sendMessage(self.curr_user,
                                                                f"Error has occured restarting game and attempting to join the room again. {self.curr_linkcode[:4]}-{self.curr_linkcode[5:]}"))
            return self.joinUnionRoom()
        self.commands.poke(self.pointers["player_x"], "0xAB4968C1")
        self.commands.poke(self.pointers["player_y"], "0x45C92741")
        self.commands.poke(self.pointers["rot_x"], "0x80000000")

        time.sleep(8)

    def startTradeLoop(self) -> bool:
        if self.checkTimeout():
            self.commands.clickY(1)
            self.commands.clickA(1)
            self.commands.clickDown(1)
            self.commands.clickA()



            time.sleep(0.6)

            if not self.awaitTradeDialogue():
                return False

            if not self.awaitTradeWindow():
                self.commands.clickA(0.4)
                return self.startTradeLoop()

            self.awaitTradeOffer()
            
            offered = self.readTradePokemon()

            if offered.isEgg and offered.friendship == 0:
                self.restartGame()
                self.PyBot.loop.create_task(self.PyBot.sendMessage(self.curr_user,
                                                                    f"Please do not try to softlock the bot. Removed from Queue."))
                return None

            if offered.species in [61, 64, 67, 75, 79, 93, 95, 112, 117, 123, 125, 126, 137, 233, 356, 366]:
                self.restartGame()
                self.PyBot.loop.create_task(self.PyBot.sendMessage(self.curr_user,
                                                                    f"Please do not offer trade evolutions. Removed from Queue."))
                return None
            
            if offered.nickname.lower() in self.pokemon.keys():
                self.commands.poke(self.pointers["b1s1"], "0x" + self.pokemon[offered.nickname.lower()].hex())
            else:
                self.commands.poke(self.pointers["b1s1"], "0x" + self.pokemon[random.choice(list(self.pokemon.keys()))].hex())

            self.commands.clickA(0.3)
            self.commands.clickA(0.5)

            # Offered, find error handling pointers later
            self.commands.clickA(0.3)
            self.commands.clickA(3)
            self.commands.clickA(3)
            self.commands.clickA(4)

            # TODO Add Handling For Trades Being Cancelled

            self.awaitTradeComplete()

            time.sleep(4)
            self.commands.clickB(0.3)
            self.commands.clickUp(0.3)
            self.commands.clickA(2)
            self.commands.clickA(3)

            return True
        return False


    def restartGame(self):
        self.commands.clickHome(1.3)
        self.commands.clickX(0.5)
        self.commands.clickA(3.5)
        self.commands.clickA(1)
        self.commands.clickA(1)
        self.commands.clickA(25)
        self.commands.clickA(3)
        self.commands.clickA(14)

    def leaveUnionRoom(self) -> None:
        self.commands.clickB(0.3)
        self.commands.clickY(0.5)
        self.commands.clickDown(0.5)
        self.commands.clickA(5)

    def await_thread(self) -> None:
        while True:
            self.triggerEvent.acquire()
            self.curr_user = self.queue[0]
            self.curr_linkcode = self.generateLinkCode()
            self.PyBot.loop.create_task(self.PyBot.sendMessage(self.curr_user,
                                                               f"I am waiting for you in Global Room "
                                                               f"{self.curr_linkcode[0:4]}-{self.curr_linkcode[4:]}."))
            if self.queue.size() > 1:
                self.PyBot.loop.create_task(self.PyBot.sendMessage(self.queue[1],
                                                    f"Your turn is coming up next. Please be ready."))
            self.joinUnionRoom()
            self.start_time = datetime.datetime.now()
            result = self.startTradeLoop()
            if not result:
                if result is not None:
                    self.PyBot.loop.create_task(self.PyBot.sendMessage(self.curr_user,
                                                                   f"Time limit exceeded. Trainer skipped. "
                                                                   f"please queue again."))
                # self.recoverStart()
            else:
                self.settings["tradeCount"] += 1
            
            if result is not None:
                self.leaveUnionRoom()
            del self.queue[0]


class PycordManager(commands.Bot):
    def __init__(self, startTradeRoutine: threading.Semaphore, q: UserQueue,
                 config: JsonHandler, settings: JsonHandler) -> None:
        self.__triggerEvent = startTradeRoutine
        self.queue = q
        intents = discord.Intents().all()
        super().__init__(command_prefix='+', intents=intents, case_insensitive=True)
        self.config = config
        self.settings = settings

        self.load_extension('bots.commands.Pycord')

    async def sendMessage(self, msgID: int, msg: str) -> None:
        await self.wait_until_ready()
        user = self.get_user(msgID)
        await user.send(content=msg)

    def trigger_add_event(self) -> None:
        self.__triggerEvent.release()

    def trigger_remove_event(self) -> None:
        self.__triggerEvent.acquire()

    async def on_ready(self) -> None:
        print('Logged in as')
        print(super().user.name)
        print(super().user.id)
        print('------')
