# TODO Make Tidy Class

global BlockPosition
BlockPosition = [
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2,
    2, 0, 1, 3,
    3, 0, 1, 2,
    2, 0, 3, 1,
    3, 0, 2, 1,
    1, 2, 0, 3,
    1, 3, 0, 2,
    2, 1, 0, 3,
    3, 1, 0, 2,
    2, 3, 0, 1,
    3, 2, 0, 1,
    1, 2, 3, 0,
    1, 3, 2, 0,
    2, 1, 3, 0,
    3, 1, 2, 0,
    2, 3, 1, 0,
    3, 2, 1, 0,

    # duplicates of 0-7 to eliminate modulus
    0, 1, 2, 3,
    0, 1, 3, 2,
    0, 2, 1, 3,
    0, 3, 1, 2,
    0, 2, 3, 1,
    0, 3, 2, 1,
    1, 0, 2, 3,
    1, 0, 3, 2
]

blockPositionInvert = [
    0, 1, 2, 4, 3, 5, 6, 7, 12, 18, 13, 19, 8, 10, 14, 20, 16, 22, 9, 11, 15, 21, 17, 23,
    0, 1, 2, 4, 3, 5, 6, 7
]


def Crypt(data, ec, i):
    ec = (0x41C64E6D * int(hex(ec), 16)) + 0x00006073 & 0xFFFFFFFF
    data[i] ^= ec >> 16 & 0xFF
    data[i + 1] ^= ec >> 24 & 0xFF

    return ec


def CryptArray(data, ec, start, end):
    for i in range(start, end, 2):
        ec = Crypt(data, ec, i)


def CryptPKM(data, ec, start, blockSize):
    end = (4 * blockSize) + start
    CryptArray(data, ec, start, end)
    if len(data) > end:
        CryptArray(data, ec, end, len(data))


def ShuffleArray(data, sv, blockSize):
    sdata = data.copy()
    i = (sv * 4) & 0xFF
    start = 8
    for b in range(4):
        ofs = BlockPosition[i + b]
        toCopy = data[start + (blockSize * ofs):start + (blockSize * ofs) + blockSize]
        sdata = sdata[:start + (blockSize * b)] + toCopy + sdata[start + (blockSize * b) + blockSize:]

    return sdata


def EncryptPb8(data):
    ec = int.from_bytes(data[0:4], byteorder='little') & 0xFFFFFFFF
    sv = ec >> 13 & 31

    ekm = ShuffleArray(data, blockPositionInvert[sv], 80)
    CryptPKM(ekm, ec, 8, 80)
    return ekm


def DecryptEb8(data):
    ec = int.from_bytes(data[0:4], byteorder='little') & 0xFFFFFFFF

    sv = ec >> 13 & 31

    CryptPKM(data, ec, 8, 80)
    return ShuffleArray(data, sv, 80)
