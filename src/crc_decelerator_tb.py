import cocotb
import math
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from cocotb.regression import TestFactory
from binascii import hexlify

from common_test import *

async def bringup(dut):
    dut._log.info("BRINGUP")

    # init inputs
    dut.cmd.value = 0
    dut.data_in.value = 0

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    await RisingEdge(dut.clk)

    dut.rst.value = 1
    await RisingEdge(dut.clk)

    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("reset done")

@cocotb.test()
async def test_power_up(dut):
    await bringup(dut)

    await ClockCycles(dut.clk, 1)

    assert dut.io_out == 0
    if NGL_TEST: assert dut.crc.setup_fsm == 0

async def stream_in_setup(dut, nibbles):
    for i, n in enumerate(nibbles):
        dut.data_in.value = n
        await ClockCycles(dut.clk, 1)

        # confirm that DUT is in SETUP
        if i == 0:
            assert dut.io_out[0].value == 1
            if NGL_TEST: assert dut.crc.current_cmd == CRC_CMD.CMD_SETUP

    # wait 1 cycle for pipeline to sync
    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_CMD_SETUP(dut):
    if GL_TEST:
        return

    await bringup(dut)

    for crc_name in ["FAKE4", "FAKE8", "FAKE16", "FAKE32", "FAKE4"]:
        config = CRC_TABLE_FAKE[crc_name]
        config_bitstream = build_config(dut, crc_name)

        dut.cmd.value = CRC_CMD.CMD_SETUP

        await ClockCycles(dut.clk, 1)
        await stream_in_setup(dut, config_bitstream)

        dut._log.info("Config streamed")

        assert dut.crc.bitwidth.value == (config.bitwidth - 1)

        dut.cmd.value = CRC_CMD.CMD_RESET

        assert int(dut.crc.crc_state.value) == CRC_STATE.CRC_INIT
        assert int(dut.crc.setup_fsm.value) == SETUP_FSM.SETUP_XOR_N
        await ClockCycles(dut.clk, 1)

        assert dut.crc.current_cmd == CRC_CMD.CMD_SETUP
        assert int(dut.crc.setup_fsm.value) == SETUP_FSM.SETUP_DONE

        await ClockCycles(dut.clk, 1)

        assert dut.crc.current_cmd == CRC_CMD.CMD_RESET
        assert int(dut.crc.setup_fsm.value) == SETUP_FSM.SETUP_START

        assert config.poly == dut.crc.crc_poly
        assert config.init == dut.crc.crc_init
        assert config.xorout == dut.crc.crc_xor
        assert config.reflect_in == dut.crc.crc_reflect_in
        assert config.reflect_out == dut.crc.crc_reflect_out

@cocotb.test()
async def test_CMD_SETUP_hold(dut):
    if GL_TEST:
        return

    await bringup(dut)

    crc_name = "CRC-8/SMBUS"
    config = CRC_TABLE[crc_name]
    config_bitstream = build_config(dut, crc_name)
    dut.cmd.value = CRC_CMD.CMD_SETUP

    await ClockCycles(dut.clk, 1)
    await stream_in_setup(dut, config_bitstream)

    dut._log.info("Config streamed")
    await ClockCycles(dut.clk, 2)
    # add extra cycles to ensure that SETUP is holding, even though all data is streamed in
    await ClockCycles(dut.clk, 10)
    assert dut.crc.in_setup == 1
    assert int(dut.crc.bitwidth) == (config.bitwidth - 1)

def golden_crc(crc_name, inp):
    config = CRC_TABLE[crc_name]

    bitmask = (1 << config.bitwidth) - 1
    crc = config.init

    for c in inp:
        b, direction = (0, 1) if config.reflect_in else (7, -1)

        for i in range(8):
            ib = int(bool(c & (1 << b)))
            msb = bool((crc >> (config.bitwidth - 1)) ^ ib)
            crc_shifted = ((crc << 1) & bitmask)
            crc = crc_shifted ^ config.poly if msb else crc_shifted
            b += direction

    crc = reflect(crc, config.bitwidth) if config.reflect_out else crc

    return (crc ^ config.xorout) & bitmask

async def test_crc_e2e(dut, crc_name=None, reset=True, test_string=CRC_CHECK_STRING):
    if reset:
        await bringup(dut)

    config = CRC_TABLE[crc_name]
    config_bitstream = build_config(dut, crc_name)
    dut.cmd.value = CRC_CMD.CMD_SETUP

    await ClockCycles(dut.clk, 1)
    await stream_in_setup(dut, config_bitstream)

    dut._log.info("Config streamed")
    await ClockCycles(dut.clk, 2)
    if NGL_TEST: assert int(dut.crc.bitwidth) == (config.bitwidth - 1)

    dut.cmd.value = CRC_CMD.CMD_RESET
    await ClockCycles(dut.clk, 2)
    if NGL_TEST: assert dut.crc.current_cmd.value == CRC_CMD.CMD_RESET

    dut.cmd.value = CRC_CMD.CMD_MESSAGE
    await ClockCycles(dut.clk, 1)

    if isinstance(test_string, str):
        test_string = test_string.encode()

    for c in test_string:
        # stream in byte a nibble at a time
        for v in [c & 0xf, (c >> 4) & 0xf]:
            dut.data_in.value = v
            await ClockCycles(dut.clk, 1)

        # wait for byte to be processed
        await ClockCycles(dut.clk, 8)

    dut.cmd.value = CRC_CMD.CMD_FINAL

    golden_crc_result = golden_crc(crc_name, test_string)
    dut._log.info("Golden CRC 0x%x", golden_crc_result)

    for b in range(int(math.ceil(config.bitwidth/8))):
        dut.data_in.value = b
        await ClockCycles(dut.clk, 2)

        crc_b = int(dut.io_out.value) & 0xff
        expected_b = (golden_crc_result >> (b*8)) & 0xff
        dut._log.info("CRC_RES%d [expected %02x == %02x]", b, expected_b, crc_b)

        assert expected_b == crc_b

class PostfixStr(str):
    def __init__(self, choices):
        self.cur = 0
        self.choices = choices

    def __str__(self):
        c = self.choices[self.cur]
        self.cur = (self.cur + 1) % (len(self.choices))
        return c

tf = TestFactory(test_crc_e2e)
crcs_to_test = CRC_TABLE.keys()
tf.add_option('crc_name', crcs_to_test)
tf.generate_tests(postfix=PostfixStr(["_" + x.replace("/", "_").replace("-", "_").lower() for x in crcs_to_test]))

@cocotb.test()
async def test_multi_random(dut):
    random.seed(128937378398)
    await bringup(dut)

    trials = 10
    test_amount = 20
    crc_keys = list(CRC_TABLE.keys())

    for trial in range(trials):
        #await bringup(dut)
        random.shuffle(crc_keys)

        for crc_name in crc_keys[:test_amount]:
            test_string = bytes(random.choice(range(0, 0x100)) for i in range(trial+1))
            await test_crc_e2e(dut, crc_name, reset=False, test_string=test_string)

