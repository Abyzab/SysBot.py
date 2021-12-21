import binascii
import socket
import time
import datetime

from bots.commands.SysBotBaseCommands import SysBotBaseCommands
from bots.utils.JsonHandler import JsonHandler
from bots.utils.Pb8 import Pb8
from bots.utils.PokeCrypto import DecryptEb8


class EggBotConnection:
    def __init__(self, address: str, port: int) -> None:
        self.con = None
        self.connectSocket(address, port)
        self.commands = SysBotBaseCommands(self.con)
        self.pointers = JsonHandler('pointers')
        self.settings = JsonHandler('settings')
        self.freezeInstantText()
        self.current_egg = None

    def freezeInstantText(self) -> None:
        self.commands.updateFreezeRate()
        self.commands.freeze(self.pointers["instantText"], "0xFFFF7F7F")
        self.commands.freeze(self.pointers["fps"], "0x01")

    def connectSocket(self, address: str, port: int) -> None:
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting...")

        self.con.connect((address, port))  # TODO Add error handling for the socket not attaching

        print("Connected")

    def awaitEggScreen(self) -> None:
        while self.commands.peek(self.pointers['day_care_dialogue'], 1) != b"00":
            self.commands.clickA(0.5)

    def teleport(self, location):
        if location == "bike_down":
            self.commands.poke(self.pointers['player_x'],
                                "0x"
                                "00000CC400000040AC3F1E"
                                "4400000000000000800000"
                                "0080000000800000803F00"
                                "00803F0000803F0000803F")

        elif location == "collect_egg":
            self.commands.poke(self.pointers['player_x'],
                                "0x"
                                "FCFF0AC400000040D6FE21"
                                "440000000000000080F404"
                                "353F00000080F404353F00"
                                "00803F0000803F0000803F")

    def bikeUntilEgg(self) -> None:
        time_passed = datetime.datetime.now()

        self.teleport("bike_down")

        self.commands.setStick("LEFT", "0x0", "-0x8000")
                
        while self.commands.peek(self.pointers['is_egg'], 1) != b'01':
            if (datetime.datetime.now() - time_passed).seconds >= 3:
                self.teleport("bike_down")
                time_passed = datetime.datetime.now()

        self.commands.setStick("LEFT", "0x0", "0x0")
        time.sleep(1)

    def collectEgg(self) -> None:
        self.teleport("collect_egg")
        time.sleep(0.4)
        self.commands.clickA(0.5)

        self.awaitEggScreen()
        time.sleep(0.5)

        self.commands.clickB(2)
        self.commands.clickA(3)
        self.commands.clickA(0.5)
        self.commands.clickA(2)

    def checkEgg(self) -> bool:
        egg = self.commands.peek(self.pointers['b1s1'], 344)
        egg = Pb8(DecryptEb8(bytearray(binascii.unhexlify(egg))))

        if egg.species == 0:
            return False

        print(egg.ec)
        return egg.isShiny

    def mainRoutine(self) -> None:
        encounters = 1
        while True:
            print(f"Starting Egg {encounters}")
            self.bikeUntilEgg()
            self.collectEgg()
            if self.checkEgg():
                break
            else:
                self.commands.poke(self.pointers['b1s1'], BlankPKM)
            encounters += 1
        print(f"Shiny found after {encounters} encounters!")


BlankPKM = "0x0000000000008B0400007EE97152B031428ECCE2C5AFDB6733FC2CEF5EFCC5CAD6EB3D99BC7AA7CBD65D7891A6278D619216B8CF5D3780307C40FB481332E7FEA3DF693D9E63291D8DEA9662689297A3491C036EAA3189AAC5D3EAC3D982C6E05C943B4E5F5A2824B3FBE1BF8E7B7F00C44048C8D1BFB6383B9023FB237D34BE00DA6A70C5DF84BA14E4A1602B2B388FA0B66041361609F04BB50E26A8B6437BCBF9EF68D4AF5F74FFC303E0EC988B84DB11002480CCC4A7A2B755A85C1C42A23A8604AFD31119B0CF57E94E60BA1B452E17A934932D66092D11E0A17442C4730B2B23F2432854A660CB42C062D669715B8DCD3D9387B1A01911D97E66B499F63A7D03BEEC40F079B185B5DCB0D1C9F9DC0BA7A3E77BA6EBD4ABA987E544D207FA346109D3240E4800FCCB709F806F2C8FCB51F2334F866A094BF770E85DC06AE7EB2D723C68103800007EE97152B031428ECCE2C5AFDB67"
