import binascii
import socket
import time
import datetime

from bots.commands.SysBotBaseCommands import SysBotBaseCommands
from bots.utils.JsonHandler import JsonHandler
from bots.utils.Pb8 import Pb8
from bots.utils.PokeCrypto import DecryptEb8


class EggBotConnection:
    def __init__(self, address: str, port: int, stop_conditions: dict) -> None:
        self.con = None
        self.iv_util = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
        self.nature_util = ["hardy", "lonely", "brave", "adamant", "naughty", "bold", "docile", "relaxed", "impish",
                            "lax", "timid", "hasty", "serious", "jolly", "naive", "modest", "mild", "quiet", "bashful",
                            "rash", "calm", "gentle", "sassy", "careful", "quirky", ""]
        self.validate_conditions(stop_conditions)
        self.connectSocket(address, port)
        self.commands = SysBotBaseCommands(self.con)
        self.pointers = JsonHandler('pointers')
        self.settings = JsonHandler('settings')
        self.freezeInstantText()
        self.current_egg = None
        self.egg_config = stop_conditions


    def validate_conditions(self, stop_conditions: dict) -> None:
        reason = []
        if type(stop_conditions["shiny"]) != bool:
            reason.append(". Shiny must be true or false.")
        
        iv_list = stop_conditions["ivs"]
        if type(iv_list) != list:
            reason.append(". ivs must be a list.")
        
        for i in range(len(iv_list)):
            if iv_list[i] not in range(32) and iv_list[i] is not None:
                reason.append(f". {self.iv_util[i]} iv must be between 0 and 31 or null for any.")
        
        if stop_conditions["nature"].lower() not in self.nature_util:
            reason.append(". Nature must be a valid Pokémon nature.")
        
        if stop_conditions["ability"] not in [1,2,4,None]:
            reason.append(". Ability must be 1, 2 or 4.")

        if reason:
            raise Exception(f"Invalid stop conditions detected within eggConfig in config.json. "
                            f"Reason{'s' if len(reason) > 1 else ''}:\n{chr(10).join([str(i+1) + reason[i] for i in range(len(reason))])}")

    def freezeInstantText(self) -> None:
        self.commands.updateFreezeRate()
        self.commands.freeze(self.pointers["instantText"], "0xFFFF7F7F")
        self.commands.freeze(self.pointers["fps"], "0x01")

    def connectSocket(self, address: str, port: int) -> None:
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting...")

        self.con.connect((address, port))  # TODO Add error handling for the socket not attaching

        print("Connected")

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

        self.commands.clickA(0.5)
        self.commands.clickA(0.5)
        self.commands.clickA(0.5)
        self.commands.clickA(0.5)
        self.commands.clickA(0.5)

        time.sleep(3)

        self.commands.clickA(0.5)
        self.commands.clickA(3)
        self.commands.clickA(4)
        self.commands.clickB(0.5)
        self.commands.clickB(0.5)

    def checkEgg(self) -> bool:
        egg = self.commands.peek(self.pointers['b1s1'], 344)
        egg = Pb8(DecryptEb8(bytearray(binascii.unhexlify(egg))))

        if egg.species == 0:
            return False
        
        egg_ivs = [egg.iv_hp, egg.iv_atk, egg.iv_def, egg.iv_spa, egg.iv_spd, egg.iv_spe]

        if egg.isShiny != self.egg_config["shiny"]:
            return False
        
        if egg.ability_no != self.egg_config["ability"] and self.egg_config["ability"]:
            return False
        
        for i in range(len(self.egg_config["ivs"])):
            iv = self.egg_config["ivs"][i]
            if iv and iv != egg_ivs[i]:
                return False
        
        if self.nature_util[egg.nature] != self.egg_config["nature"].lower() and self.egg_config["nature"]:
            return False

        return True

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
        print(f"Egg found after {encounters} eggs!")


BlankPKM = "0x0000000000008B0400007EE97152B031428ECCE2C5AFDB6733FC2CEF5EFCC5CAD6EB3D99BC7AA7CBD65D7891A6278D619216B8CF5D3780307C40FB481332E7FEA3DF693D9E63291D8DEA9662689297A3491C036EAA3189AAC5D3EAC3D982C6E05C943B4E5F5A2824B3FBE1BF8E7B7F00C44048C8D1BFB6383B9023FB237D34BE00DA6A70C5DF84BA14E4A1602B2B388FA0B66041361609F04BB50E26A8B6437BCBF9EF68D4AF5F74FFC303E0EC988B84DB11002480CCC4A7A2B755A85C1C42A23A8604AFD31119B0CF57E94E60BA1B452E17A934932D66092D11E0A17442C4730B2B23F2432854A660CB42C062D669715B8DCD3D9387B1A01911D97E66B499F63A7D03BEEC40F079B185B5DCB0D1C9F9DC0BA7A3E77BA6EBD4ABA987E544D207FA346109D3240E4800FCCB709F806F2C8FCB51F2334F866A094BF770E85DC06AE7EB2D723C68103800007EE97152B031428ECCE2C5AFDB67"
