class Pb8:
    def __init__(self, data: bytearray) -> None:
        self._data = data
    
    def __str__(self) -> str:
        return "-".join([hex(x)[2:].upper().zfill(2) for x in self.data])
    
    def __eq__(self, other) -> bool:
        return self.data == other.data
    
    @property
    def data(self) -> bytearray:
        return self._data
    
    @property
    def ec(self) -> int:
        return int.from_bytes(self._data[:4], byteorder="little")
    
    @property
    def pid(self) -> int:
        return int.from_bytes(self._data[28:32], byteorder="little")
    
    @property
    def sid(self) -> int:
        return int.from_bytes(self._data[14:16], byteorder="little")

    @property
    def tid(self) -> int:
        return int.from_bytes(self._data[12:14], byteorder="little")
    
    @property
    def psv(self) -> int:
        return (self.pid >> 16 ^ (self.pid & 0xFFFF)) >> 4
    
    @property
    def tsv(self) -> int: 
        return (self.tid ^ self.sid) >> 4
    
    @property
    def xor(self) -> int:
        return (self.tid ^ self.sid) ^ (self.pid >> 16 ^ (self.pid & 0xFFFF))
    
    @property
    def species(self) -> int:
        return int.from_bytes(self._data[8:10], byteorder="little")
    
    @property
    def nature(self) -> int:
        return self._data[32]
    
    @property
    def ability_no(self) -> int:
        return self._data[22]
    
    @property
    def iv_hp(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 0) & 0x1F
    
    @property
    def iv_atk(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 5) & 0x1F

    @property
    def iv_def(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 10) & 0x1F

    @property
    def iv_spe(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 15) & 0x1F

    @property
    def iv_spa(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 20) & 0x1F

    @property
    def iv_spd(self) -> int:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 25) & 0x1F
    
    @property
    def nickname(self) -> str:
        return "".join(chr(x) for x in self._data[88:112] if x != 0)
    
    @property
    def friendship(self) -> bool:
        return int.from_bytes(self._data[274:275], byteorder="little")


    @property
    def isEgg(self) -> bool:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 30) & 0x1 == 1
    
    @property
    def isNicknamed(self) -> bool:
        return (int.from_bytes(self._data[140:144], byteorder="little") >> 31) & 0x1 == 1

    @property
    def isShiny(self) -> bool:
        return self.psv == self.tsv
    