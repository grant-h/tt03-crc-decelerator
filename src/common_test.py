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

# Automatically generated from ./create_crc_tables.py
CRC_TABLE = OrderedDict({
    # Name, bitwidth, check,    poly,   init,   reflect_in, reflect_out, xorout
    #"CRC-82/DARC":                CC(82,	0x09ea83f625023801fd612,	0x0308c0111011401440411,	0x000000000000000000000,	True,	True,	0x000000000000000000000),
    #"CRC-64/XZ":                  CC(64,	0x995dc9bbdf1939fa,	0x42f0e1eba9ea3693,	0xffffffffffffffff,	True,	True,	0xffffffffffffffff),
    #"CRC-64/WE":                  CC(64,	0x62ec59e3f1a4f00a,	0x42f0e1eba9ea3693,	0xffffffffffffffff,	False,	False,	0xffffffffffffffff),
    #"CRC-64/REDIS":               CC(64,	0xe9c6d914c4b8d9ca,	0xad93d23594c935a9,	0x0000000000000000,	True,	True,	0x0000000000000000),
    #"CRC-64/MS":                  CC(64,	0x75d4b74f024eceea,	0x259c84cba6426349,	0xffffffffffffffff,	True,	True,	0x0000000000000000),
    #"CRC-64/GO-ISO":              CC(64,	0xb90956c775a41001,	0x000000000000001b,	0xffffffffffffffff,	True,	True,	0xffffffffffffffff),
    #"CRC-64/ECMA-182":            CC(64,	0x6c40df5f0b497347,	0x42f0e1eba9ea3693,	0x0000000000000000,	False,	False,	0x0000000000000000),
    #"CRC-40/GSM":                 CC(40,	0xd4164fc646,	0x0004820009,	0x0000000000,	False,	False,	0xffffffffff),
    "CRC-32/XFER":                CC(32,	0xbd0be338,	0x000000af,	0x00000000,	False,	False,	0x00000000),
    "CRC-32/MPEG-2":              CC(32,	0x0376e6e7,	0x04c11db7,	0xffffffff,	False,	False,	0x00000000),
    "CRC-32/MEF":                 CC(32,	0xd2c22f51,	0x741b8cd7,	0xffffffff,	True,	True,	0x00000000),
    "CRC-32/JAMCRC":              CC(32,	0x340bc6d9,	0x04c11db7,	0xffffffff,	True,	True,	0x00000000),
    "CRC-32/ISO-HDLC":            CC(32,	0xcbf43926,	0x04c11db7,	0xffffffff,	True,	True,	0xffffffff),
    "CRC-32/ISCSI":               CC(32,	0xe3069283,	0x1edc6f41,	0xffffffff,	True,	True,	0xffffffff),
    "CRC-32/CKSUM":               CC(32,	0x765e7680,	0x04c11db7,	0x00000000,	False,	False,	0xffffffff),
    "CRC-32/CD-ROM-EDC":          CC(32,	0x6ec2edc4,	0x8001801b,	0x00000000,	True,	True,	0x00000000),
    "CRC-32/BZIP2":               CC(32,	0xfc891918,	0x04c11db7,	0xffffffff,	False,	False,	0xffffffff),
    "CRC-32/BASE91-D":            CC(32,	0x87315576,	0xa833982b,	0xffffffff,	True,	True,	0xffffffff),
    "CRC-32/AUTOSAR":             CC(32,	0x1697d06a,	0xf4acfb13,	0xffffffff,	True,	True,	0xffffffff),
    "CRC-32/AIXM":                CC(32,	0x3010bf7f,	0x814141ab,	0x00000000,	False,	False,	0x00000000),
    "CRC-31/PHILIPS":             CC(31,	0x0ce9e46c,	0x04c11db7,	0x7fffffff,	False,	False,	0x7fffffff),
    "CRC-30/CDMA":                CC(30,	0x04c34abf,	0x2030b9c7,	0x3fffffff,	False,	False,	0x3fffffff),
    "CRC-24/OS-9":                CC(24,	0x200fa5,	0x800063,	0xffffff,	False,	False,	0xffffff),
    "CRC-24/OPENPGP":             CC(24,	0x21cf02,	0x864cfb,	0xb704ce,	False,	False,	0x000000),
    "CRC-24/LTE-B":               CC(24,	0x23ef52,	0x800063,	0x000000,	False,	False,	0x000000),
    "CRC-24/LTE-A":               CC(24,	0xcde703,	0x864cfb,	0x000000,	False,	False,	0x000000),
    "CRC-24/INTERLAKEN":          CC(24,	0xb4f3e6,	0x328b63,	0xffffff,	False,	False,	0xffffff),
    "CRC-24/FLEXRAY-B":           CC(24,	0x1f23b8,	0x5d6dcb,	0xabcdef,	False,	False,	0x000000),
    "CRC-24/FLEXRAY-A":           CC(24,	0x7979bd,	0x5d6dcb,	0xfedcba,	False,	False,	0x000000),
    "CRC-24/BLE":                 CC(24,	0xc25a56,	0x00065b,	0x555555,	True,	True,	0x000000),
    "CRC-21/CAN-FD":              CC(21,	0x0ed841,	0x102899,	0x000000,	False,	False,	0x000000),
    "CRC-17/CAN-FD":              CC(17,	0x04f03,	0x1685b,	0x00000,	False,	False,	0x00000),
    "CRC-16/XMODEM":              CC(16,	0x31c3,	0x1021,	0x0000,	False,	False,	0x0000),
    "CRC-16/USB":                 CC(16,	0xb4c8,	0x8005,	0xffff,	True,	True,	0xffff),
    "CRC-16/UMTS":                CC(16,	0xfee8,	0x8005,	0x0000,	False,	False,	0x0000),
    "CRC-16/TMS37157":            CC(16,	0x26b1,	0x1021,	0x89ec,	True,	True,	0x0000),
    "CRC-16/TELEDISK":            CC(16,	0x0fb3,	0xa097,	0x0000,	False,	False,	0x0000),
    "CRC-16/T10-DIF":             CC(16,	0xd0db,	0x8bb7,	0x0000,	False,	False,	0x0000),
    "CRC-16/SPI-FUJITSU":         CC(16,	0xe5cc,	0x1021,	0x1d0f,	False,	False,	0x0000),
    "CRC-16/RIELLO":              CC(16,	0x63d0,	0x1021,	0xb2aa,	True,	True,	0x0000),
    "CRC-16/PROFIBUS":            CC(16,	0xa819,	0x1dcf,	0xffff,	False,	False,	0xffff),
    "CRC-16/OPENSAFETY-B":        CC(16,	0x20fe,	0x755b,	0x0000,	False,	False,	0x0000),
    "CRC-16/OPENSAFETY-A":        CC(16,	0x5d38,	0x5935,	0x0000,	False,	False,	0x0000),
    "CRC-16/NRSC-5":              CC(16,	0xa066,	0x080b,	0xffff,	True,	True,	0x0000),
    "CRC-16/MODBUS":              CC(16,	0x4b37,	0x8005,	0xffff,	True,	True,	0x0000),
    "CRC-16/MCRF4XX":             CC(16,	0x6f91,	0x1021,	0xffff,	True,	True,	0x0000),
    "CRC-16/MAXIM-DOW":           CC(16,	0x44c2,	0x8005,	0x0000,	True,	True,	0xffff),
    "CRC-16/M17":                 CC(16,	0x772b,	0x5935,	0xffff,	False,	False,	0x0000),
    "CRC-16/LJ1200":              CC(16,	0xbdf4,	0x6f63,	0x0000,	False,	False,	0x0000),
    "CRC-16/KERMIT":              CC(16,	0x2189,	0x1021,	0x0000,	True,	True,	0x0000),
    "CRC-16/ISO-IEC-14443-3-A":   CC(16,	0xbf05,	0x1021,	0xc6c6,	True,	True,	0x0000),
    "CRC-16/IBM-SDLC":            CC(16,	0x906e,	0x1021,	0xffff,	True,	True,	0xffff),
    "CRC-16/IBM-3740":            CC(16,	0x29b1,	0x1021,	0xffff,	False,	False,	0x0000),
    "CRC-16/GSM":                 CC(16,	0xce3c,	0x1021,	0x0000,	False,	False,	0xffff),
    "CRC-16/GENIBUS":             CC(16,	0xd64e,	0x1021,	0xffff,	False,	False,	0xffff),
    "CRC-16/EN-13757":            CC(16,	0xc2b7,	0x3d65,	0x0000,	False,	False,	0xffff),
    "CRC-16/DNP":                 CC(16,	0xea82,	0x3d65,	0x0000,	True,	True,	0xffff),
    "CRC-16/DECT-X":              CC(16,	0x007f,	0x0589,	0x0000,	False,	False,	0x0000),
    "CRC-16/DECT-R":              CC(16,	0x007e,	0x0589,	0x0000,	False,	False,	0x0001),
    "CRC-16/DDS-110":             CC(16,	0x9ecf,	0x8005,	0x800d,	False,	False,	0x0000),
    "CRC-16/CMS":                 CC(16,	0xaee7,	0x8005,	0xffff,	False,	False,	0x0000),
    "CRC-16/CDMA2000":            CC(16,	0x4c06,	0xc867,	0xffff,	False,	False,	0x0000),
    "CRC-16/ARC":                 CC(16,	0xbb3d,	0x8005,	0x0000,	True,	True,	0x0000),
    "CRC-15/MPT1327":             CC(15,	0x2566,	0x6815,	0x0000,	False,	False,	0x0001),
    "CRC-15/CAN":                 CC(15,	0x059e,	0x4599,	0x0000,	False,	False,	0x0000),
    "CRC-14/GSM":                 CC(14,	0x30ae,	0x202d,	0x0000,	False,	False,	0x3fff),
    "CRC-14/DARC":                CC(14,	0x082d,	0x0805,	0x0000,	True,	True,	0x0000),
    "CRC-13/BBC":                 CC(13,	0x04fa,	0x1cf5,	0x0000,	False,	False,	0x0000),
    "CRC-12/UMTS":                CC(12,	0xdaf,	0x80f,	0x000,	False,	True,	0x000),
    "CRC-12/GSM":                 CC(12,	0xb34,	0xd31,	0x000,	False,	False,	0xfff),
    "CRC-12/DECT":                CC(12,	0xf5b,	0x80f,	0x000,	False,	False,	0x000),
    "CRC-12/CDMA2000":            CC(12,	0xd4d,	0xf13,	0xfff,	False,	False,	0x000),
    "CRC-11/UMTS":                CC(11,	0x061,	0x307,	0x000,	False,	False,	0x000),
    "CRC-11/FLEXRAY":             CC(11,	0x5a3,	0x385,	0x01a,	False,	False,	0x000),
    "CRC-10/GSM":                 CC(10,	0x12a,	0x175,	0x000,	False,	False,	0x3ff),
    "CRC-10/CDMA2000":            CC(10,	0x233,	0x3d9,	0x3ff,	False,	False,	0x000),
    "CRC-10/ATM":                 CC(10,	0x199,	0x233,	0x000,	False,	False,	0x000),
    "CRC-8/WCDMA":                CC(8,	0x25,	0x9b,	0x00,	True,	True,	0x00),
    "CRC-8/TECH-3250":            CC(8,	0x97,	0x1d,	0xff,	True,	True,	0x00),
    "CRC-8/SMBUS":                CC(8,	0xf4,	0x07,	0x00,	False,	False,	0x00),
    "CRC-8/SAE-J1850":            CC(8,	0x4b,	0x1d,	0xff,	False,	False,	0xff),
    "CRC-8/ROHC":                 CC(8,	0xd0,	0x07,	0xff,	True,	True,	0x00),
    "CRC-8/OPENSAFETY":           CC(8,	0x3e,	0x2f,	0x00,	False,	False,	0x00),
    "CRC-8/NRSC-5":               CC(8,	0xf7,	0x31,	0xff,	False,	False,	0x00),
    "CRC-8/MIFARE-MAD":           CC(8,	0x99,	0x1d,	0xc7,	False,	False,	0x00),
    "CRC-8/MAXIM-DOW":            CC(8,	0xa1,	0x31,	0x00,	True,	True,	0x00),
    "CRC-8/LTE":                  CC(8,	0xea,	0x9b,	0x00,	False,	False,	0x00),
    "CRC-8/I-CODE":               CC(8,	0x7e,	0x1d,	0xfd,	False,	False,	0x00),
    "CRC-8/I-432-1":              CC(8,	0xa1,	0x07,	0x00,	False,	False,	0x55),
    "CRC-8/HITAG":                CC(8,	0xb4,	0x1d,	0xff,	False,	False,	0x00),
    "CRC-8/GSM-B":                CC(8,	0x94,	0x49,	0x00,	False,	False,	0xff),
    "CRC-8/GSM-A":                CC(8,	0x37,	0x1d,	0x00,	False,	False,	0x00),
    "CRC-8/DVB-S2":               CC(8,	0xbc,	0xd5,	0x00,	False,	False,	0x00),
    "CRC-8/DARC":                 CC(8,	0x15,	0x39,	0x00,	True,	True,	0x00),
    "CRC-8/CDMA2000":             CC(8,	0xda,	0x9b,	0xff,	False,	False,	0x00),
    "CRC-8/BLUETOOTH":            CC(8,	0x26,	0xa7,	0x00,	True,	True,	0x00),
    "CRC-8/AUTOSAR":              CC(8,	0xdf,	0x2f,	0xff,	False,	False,	0xff),
    "CRC-7/UMTS":                 CC(7,	0x61,	0x45,	0x00,	False,	False,	0x00),
    "CRC-7/ROHC":                 CC(7,	0x53,	0x4f,	0x7f,	True,	True,	0x00),
    "CRC-7/MMC":                  CC(7,	0x75,	0x09,	0x00,	False,	False,	0x00),
    "CRC-6/GSM":                  CC(6,	0x13,	0x2f,	0x00,	False,	False,	0x3f),
    "CRC-6/G-704":                CC(6,	0x06,	0x03,	0x00,	True,	True,	0x00),
    "CRC-6/DARC":                 CC(6,	0x26,	0x19,	0x00,	True,	True,	0x00),
    "CRC-6/CDMA2000-B":           CC(6,	0x3b,	0x07,	0x3f,	False,	False,	0x00),
    "CRC-6/CDMA2000-A":           CC(6,	0x0d,	0x27,	0x3f,	False,	False,	0x00),
    "CRC-5/USB":                  CC(5,	0x19,	0x05,	0x1f,	True,	True,	0x1f),
    "CRC-5/G-704":                CC(5,	0x07,	0x15,	0x00,	True,	True,	0x00),
    "CRC-5/EPC-C1G2":             CC(5,	0x00,	0x09,	0x09,	False,	False,	0x00),
    "CRC-4/INTERLAKEN":           CC(4,	0xb,	0x3,	0xf,	False,	False,	0xf),
    "CRC-4/G-704":                CC(4,	0x7,	0x3,	0x0,	True,	True,	0x0),
    "CRC-3/ROHC":                 CC(3,	0x6,	0x3,	0x7,	True,	True,	0x0),
    "CRC-3/GSM":                  CC(3,	0x4,	0x3,	0x0,	False,	False,	0x7),
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
