import cocotb
import os
from enum import IntEnum
from struct import pack, unpack
from collections import namedtuple, OrderedDict

GL_TEST = "GATES" in os.environ and os.environ["GATES"] == "yes"
NGL_TEST = not GL_TEST

CC = namedtuple("CrcConfig", "bitwidth check poly init reflect_in reflect_out xorout")

CRC_CHECK_STRING = "123456789"
MAX_BITS = 32

CRC_TABLE = OrderedDict({
    # Name, bitwidth, check,    poly,   init,   reflect_in, reflect_out, xorout
    "CRC-32": CC(32,	0xCBF43926,	0x04C11DB7,	0xFFFFFFFF,	True,	True,	0xFFFFFFFF),
    "CRC-32/BZIP2": CC(32,	0xFC891918,	0x04C11DB7,	0xFFFFFFFF,	False,	False,	0xFFFFFFFF),
    "CRC-32/JAMCRC": CC(32,	0x340BC6D9,	0x04C11DB7,	0xFFFFFFFF,	True,	True,	0x00000000),
    "CRC-32/MPEG-2": CC(32,	0x0376E6E7,	0x04C11DB7,	0xFFFFFFFF,	False,	False,	0x00000000),
    "CRC-32/POSIX": CC(32,	0x765E7680,	0x04C11DB7,	0x00000000,	False,	False,	0xFFFFFFFF),
    "CRC-32/SATA": CC(32,	0xCF72AFE8,	0x04C11DB7,	0x52325032,	False,	False,	0x00000000),
    "CRC-32/XFER": CC(32,	0xBD0BE338,	0x000000AF,	0x00000000,	False,	False,	0x00000000),
    "CRC-32C": CC(32,	0xE3069283,	0x1EDC6F41,	0xFFFFFFFF,	True,	True,	0xFFFFFFFF),
    "CRC-32D": CC(32,	0x87315576,	0xA833982B,	0xFFFFFFFF,	True,	True,	0xFFFFFFFF),
    "CRC-32Q": CC(32,	0x3010BF7F,	0x814141AB,	0x00000000,	False,	False,	0x00000000),
    "CRC-16/ARC": CC(16,	0xBB3D,	0x8005,	0x0000,	True,	True,	0x0000),
    "CRC-16/AUG-CCITT": CC(16,	0xE5CC,	0x1021,	0x1D0F,	False,	False,	0x0000),
    "CRC-16/BUYPASS": CC(16,	0xFEE8,	0x8005,	0x0000,	False,	False,	0x0000),
    "CRC-16/CCITT-False": CC(16,	0x29B1,	0x1021,	0xFFFF,	False,	False,	0x0000),
    "CRC-16/CDMA2000": CC(16,	0x4C06,	0xC867,	0xFFFF,	False,	False,	0x0000),
    "CRC-16/DDS-110": CC(16,	0x9ECF,	0x8005,	0x800D,	False,	False,	0x0000),
    "CRC-16/DECT-R": CC(16,	0x007E,	0x0589,	0x0000,	False,	False,	0x0001),
    "CRC-16/DECT-X": CC(16,	0x007F,	0x0589,	0x0000,	False,	False,	0x0000),
    "CRC-16/DNP": CC(16,	0xEA82,	0x3D65,	0x0000,	True,	True,	0xFFFF),
    "CRC-16/EN-13757": CC(16,	0xC2B7,	0x3D65,	0x0000,	False,	False,	0xFFFF),
    "CRC-16/GENIBUS": CC(16,	0xD64E,	0x1021,	0xFFFF,	False,	False,	0xFFFF),
    "CRC-16/KERMIT": CC(16,	0x2189,	0x1021,	0x0000,	True,	True,	0x0000),
    "CRC-16/MAXIM": CC(16,	0x44C2,	0x8005,	0x0000,	True,	True,	0xFFFF),
    "CRC-16/MCRF4XX": CC(16,	0x6F91,	0x1021,	0xFFFF,	True,	True,	0x0000),
    "CRC-16/MODBUS": CC(16,	0x4B37,	0x8005,	0xFFFF,	True,	True,	0x0000),
    "CRC-16/RIELLO": CC(16,	0x63D0,	0x1021,	0xB2AA,	True,	True,	0x0000),
    "CRC-16/T10-DIF": CC(16,	0xD0DB,	0x8BB7,	0x0000,	False,	False,	0x0000),
    "CRC-16/TELEDISK": CC(16,	0x0FB3,	0xA097,	0x0000,	False,	False,	0x0000),
    "CRC-16/TMS37157": CC(16,	0x26B1,	0x1021,	0x89EC,	True,	True,	0x0000),
    "CRC-16/USB": CC(16,	0xB4C8,	0x8005,	0xFFFF,	True,	True,	0xFFFF),
    "CRC-16/X-25": CC(16,	0x906E,	0x1021,	0xFFFF,	True,	True,	0xFFFF),
    "CRC-16/XMODEM": CC(16,	0x31C3,	0x1021,	0x0000,	False,	False,	0x0000),
    "CRC-A": CC(16,	0xBF05,	0x1021,	0xC6C6,	True,	True,	0x0000),
    "CRC-8": CC(8,	0xF4,	0x07,	0x00,	False,	False,	0x00),
    "CRC-8/CDMA2000": CC(8,	0xDA,	0x9B,	0xFF,	False,	False,	0x00),
    "CRC-8/DARC": CC(8,	0x15,	0x39,	0x00,	True,	True,	0x00),
    "CRC-8/DVB-S2": CC(8,	0xBC,	0xD5,	0x00,	False,	False,	0x00),
    "CRC-8/EBU": CC(8,	0x97,	0x1D,	0xFF,	True,	True,	0x00),
    "CRC-8/I-CODE": CC(8,	0x7E,	0x1D,	0xFD,	False,	False,	0x00),
    "CRC-8/ITU": CC(8,	0xA1,	0x07,	0x00,	False,	False,	0x55),
    "CRC-8/MAXIM": CC(8,	0xA1,	0x31,	0x00,	True,	True,	0x00),
    "CRC-8/ROHC": CC(8,	0xD0,	0x07,	0xFF,	True,	True,	0x00),
    "CRC-8/WCDMA": CC(8,	0x25,	0x9B,	0x00,	True,	True,	0x00),
    #"CRC-5/USB": CC(5,	0x19,	0x05,	0x1f,	True,	True,	0x1f),
})

# Used for easier visual inspection. Bogus check word
CRC_TABLE_FAKE = OrderedDict({
    # Name, bitwidth, check,    poly,   init,   reflect_in, reflect_out, xorout
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
    #assert bitwidth % 4 == 0

    for n in range(0, bitwidth, 4):
        nibbles.append(value & 0xf)
        value >>= 4

    return nibbles

def build_config(dut, name):
    if name in CRC_TABLE:
        config = CRC_TABLE[name]
    else:
        config = CRC_TABLE_FAKE[name]

    assert config.bitwidth <= MAX_BITS
    nibbles = config.bitwidth // 4
    bitwidth_minus = config.bitwidth - 1

    config_lo = pack_to_nibbles(bitwidth_minus, 4)
    config_hi = pack_to_nibbles((((bitwidth_minus >> 4) & 0x3) << 2) | (config.reflect_out << 1) | config.reflect_in, 4)
    poly = pack_to_nibbles(config.poly, config.bitwidth)
    init = pack_to_nibbles(config.init, config.bitwidth)
    xor = pack_to_nibbles(config.xorout, config.bitwidth)

    config_bitstream = config_lo + config_hi + poly + init + xor
    config_bitstream_packed = pack_nibbles(*config_bitstream)

    dut._log.info("%s config: %s" % (name, config_bitstream))
    dut._log.info("%s config: %s" % (name, config_bitstream_packed))

    return config_bitstream


class CRC_CMD(IntEnum):
    CMD_RESET = 0
    CMD_SETUP = 1
    CMD_MESSAGE = 2
    CMD_FINAL = 3

class CRC_STATE(IntEnum):
    CRC_INIT = 0
    CRC_DATA_LO = 1
    CRC_DATA_HI = 2
    CRC_SHIFTING = 3

class SETUP_FSM(IntEnum):
    SETUP_START = 0
    SETUP_CONFIG_LO = 1
    SETUP_CONFIG_HI = 2
    SETUP_POLY_N = 3
    SETUP_INIT_N = 4
    SETUP_XOR_N = 5
    SETUP_DONE = 6

def list_dut_elements(dut, show_values=False):
    for de in dut:
        path = de._path
        name = de._name

        ignore = False
        for ignore_prefix in ["_", "FILLER", "TAP", "PHY", "clkbuf_"]:
            if name.startswith(ignore_prefix):
                ignore = True
                break

        if ignore:
            continue

        dut._log.info("%s", de._path)
        if isinstance(de, cocotb.handle.HierarchyObject):
            list_dut_elements(de, show_values=show_values)
