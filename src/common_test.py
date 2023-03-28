from enum import IntEnum
from struct import pack, unpack
from collections import namedtuple, OrderedDict

CC = namedtuple("CrcConfig", "bitwidth check poly init reflect_in reflect_out xorout")

CRC_TABLE = OrderedDict({
    # Name, bitwidth, check,    poly,   init,   reflect_in, reflect_out, xorout
    "CRC-8": CC(8,	0xF4,	0x07,	0x00,	False,	False,	0x00),
    "FAKE4": CC(4,	0x00,	0xa,	0xb,	True,	False,	0xc),
    "FAKE8": CC(8,	0x00,	0xab,	0xcd,	True,	True,	0xef),
    "FAKE16": CC(16,	0x00,	0xabcd,	0xdead,	False,	True,	0xcafe),
    "FAKE32": CC(32,	0x00,	0xabcdef1,	0xcafeca1e,	False,	True,	0xdeadbeef),
    "FAKE60": CC(60,	0x00,	0x123456780abcdef,	0x123456780abcdef,	False,	True,	0x123456780abcdef),
})

def reflect(v, bitwidth):
    nv = 0
    for i in range(bitwidth):
        if v & (1 << i):
            nv |= 1 << (bitwidth - i - 1)

    return nv

def pack_nibbles(*nibbles):
    out = b""
    buf = 0

    for i, n in enumerate(nibbles):
        assert n >= 0 and n <= 15

        which = i % 2
        buf |= n << (which*4)

        # full byte or end of stream
        if (i+1) % 2 == 0 or (i+1) == len(nibbles):
            out += pack("<B", buf)
            buf = 0

    return out

def pack_to_nibbles(value, bitwidth):
    nibbles = []
    assert bitwidth % 4 == 0

    for n in range(0, bitwidth, 4):
        nibbles.append(value & 0xf)
        value >>= 4

    return nibbles

class CRC_CMD(IntEnum):
    CMD_RESET = 0
    CMD_SETUP = 1
    CMD_MESSAGE = 2
    CMD_FINAL = 3

class SETUP_FSM(IntEnum):
    SETUP_START = 0
    SETUP_CONFIG_LO = 1
    SETUP_CONFIG_HI = 2
    SETUP_POLY_N = 3
    SETUP_INIT_N = 4
    SETUP_XOR_N = 5
    SETUP_DONE = 6

