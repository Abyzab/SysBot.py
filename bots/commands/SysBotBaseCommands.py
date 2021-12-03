import time


class SysBotBaseCommands:
    def __init__(self, con):
        self.con = con

        self.keyboard_keys = {
            "1": "30", "2": "31", "3": "32",
            "4": "33", "5": "34", "6": "35",
            "7": "36", "8": "37", "9": "38",
            "0": "39"
        }

        self.touch_coords = {
            "0": "700 600", "1": "500 450", "2": "700 450",
            "3": "800 450", "4": "500 500", "5": "700 500",
            "6": "800 500", "7": "500 550", "8": "700 550",
            "9": "800 550"
        }

    def parseJumps(self, pointer: str) -> str:
        if pointer[-1] == "]":
            pointer += "+0"
        evaluation = pointer.replace("main", "").replace("[", "").replace("]", "").split("+")
        evaluation.remove('')
        jumps = "0x" + " 0x".join(evaluation)
        return jumps

    def resolvePointer(self, pointer: str) -> bytes:
        self.sendCommand(f'pointerRelative {self.parseJumps(pointer)}')
        time.sleep(0.5)
        return self.con.recv(689)

    def sendCommand(self, command: str) -> None:
        print(command)
        command += '\r\n'
        self.con.sendall(command.encode("ascii"))

    def click(self, button: str, sleep: int = 0) -> None:
        self.sendCommand(f'click {button}')
        time.sleep(sleep)

    def press(self, button: str, sleep: int = 0) -> None:
        self.sendCommand(f'press {button}')
        time.sleep(sleep)

    def release(self, button: str, sleep: int = 0) -> None:
        self.sendCommand(f'release {button}')
        time.sleep(sleep)

    def peek(self, pointer: str, size: int) -> bytes:
        self.sendCommand(f'pointerPeek {size} {self.parseJumps(pointer)}')
        time.sleep(0.4)
        return self.con.recv(689)

    def poke(self, pointer: str, data: str) -> None:
        self.sendCommand(f'pointerPoke {data} {self.parseJumps(pointer)}')

    def setStick(self, stick: str, x: str, y: str, sleep: int = 0) -> None:
        self.sendCommand(f'setStick {stick} {x} {y}')
        time.sleep(sleep)

    def getTitleId(self) -> bytes:
        self.sendCommand('getTitleID')
        time.sleep(0.4)
        return self.con.recv(689)

    def getHeapBase(self) -> bytes:
        self.sendCommand('getHeapBase')
        time.sleep(0.4)
        return self.con.recv(689)

    def getMainNsoBase(self) -> bytes:
        self.sendCommand('getMainNsoBase')
        time.sleep(0.4)
        return self.con.recv(689)

    def enterCode(self, code: str) -> None:
        command = ""
        for number in code:
            command += self.keyboard_keys[number] + " "

        self.sendCommand(f'key {command.rstrip()}')

    def touch(self, x: str, y: str) -> None:
        self.sendCommand(f'touch {x} {y}')

    def touchSeq(self, code: str) -> None:
        command = ""
        for char in code:
            command += self.touch_coords[char] + " "
        self.sendCommand(f'touch {command.strip()}')

    def updateFreezeRate(self) -> None:
        self.sendCommand(f'configure freezeRate 1')

    def freeze(self, pointer: str, data: str) -> None:
        ofs = self.resolvePointer(pointer)
        self.sendCommand(f'freeze 0x{ofs.decode().rstrip()} {data}')

    def clickA(self, sleep: int = 0) -> None:
        self.sendCommand("click A")
        time.sleep(sleep)

    def clickB(self, sleep: int = 0) -> None:
        self.sendCommand("click B")
        time.sleep(sleep)

    def clickY(self, sleep: int = 0) -> None:
        self.sendCommand("click Y")
        time.sleep(sleep)

    def clickX(self, sleep: int = 0) -> None:
        self.sendCommand("click X")
        time.sleep(sleep)

    def clickUp(self, sleep: int = 0) -> None:
        self.sendCommand("click DUP")
        time.sleep(sleep)

    def clickDown(self, sleep: int = 0) -> None:
        self.sendCommand("click DDOWN")
        time.sleep(sleep)

    def clickLeft(self, sleep: int = 0) -> None:
        self.sendCommand("click DLEFT")
        time.sleep(sleep)

    def clickRight(self, sleep: int = 0) -> None:
        self.sendCommand("click DRIGHT")
        time.sleep(sleep)

    def clickL(self, sleep: int = 0) -> None:
        self.sendCommand("click L")
        time.sleep(sleep)

    def clickR(self, sleep: int = 0) -> None:
        self.sendCommand("click R")
        time.sleep(sleep)

    def clickZL(self, sleep: int = 0) -> None:
        self.sendCommand("click ZL")
        time.sleep(sleep)

    def clickZR(self, sleep: int = 0) -> None:
        self.sendCommand("click ZR")
        time.sleep(sleep)

    def clickPlus(self, sleep: int = 0) -> None:
        self.sendCommand("click PLUS")
        time.sleep(sleep)

    def clickMinus(self, sleep: int = 0) -> None:
        self.sendCommand("click MINUS")
        time.sleep(sleep)

    def clickHome(self, sleep: int = 0) -> None:
        self.sendCommand("click HOME")
        time.sleep(sleep)

    def clickCapture(self, sleep: int = 0) -> None:
        self.sendCommand("click CAPTURE")
        time.sleep(sleep)

    def moveForward(self, sleep: int = 0) -> None:
        self.sendCommand("setStick LEFT 0 0x7FFE")
        time.sleep(sleep)
        self.sendCommand("setStick LEFT 0 0")
