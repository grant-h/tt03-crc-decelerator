import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from binascii import hexlify

from common_test import *

MAX_BITS = 32

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
    assert dut.crc.setup_fsm == 0

def build_config(dut, name):
    config = CRC_TABLE[name]

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

async def stream_in(dut, nibbles):
    for i, n in enumerate(nibbles):
        dut.data_in.value = n
        await ClockCycles(dut.clk, 1)

        # confirm that DUT is in SETUP
        if i == 0:
            assert dut.io_out[0].value == 1
            assert dut.crc.current_cmd == CRC_CMD.CMD_SETUP

    # wait 1 cycle for pipeline to sync
    await ClockCycles(dut.clk, 1)

@cocotb.test()
async def test_e2e_crc8(dut):
    await bringup(dut)
    crc_name = "CRC-8"
    config = CRC_TABLE["CRC-8"]
    config_bitstream = build_config(dut, crc_name)
    dut.cmd.value = CRC_CMD.CMD_SETUP

    await ClockCycles(dut.clk, 1)
    await stream_in(dut, config_bitstream)

    dut._log.info("Config streamed")
    await ClockCycles(dut.clk, 2)
    # add extra cycles to ensure that SETUP is holding, even though all data is streamed in
    await ClockCycles(dut.clk, 10)
    assert dut.crc.in_setup == 1
    assert int(dut.crc.bitwidth) == (config.bitwidth - 1)

    dut.cmd.value = CRC_CMD.CMD_RESET
    await ClockCycles(dut.clk, 2)
    assert dut.crc.current_cmd.value == CRC_CMD.CMD_RESET

    dut.cmd.value = CRC_CMD.CMD_MESSAGE
    await ClockCycles(dut.clk, 1)

    for c in CRC_CHECK_STRING.encode():
        # stream in byte a nibble at a time
        for v in [c & 0xf, (c >> 4) & 0xf]:
            dut.data_in.value = v
            await ClockCycles(dut.clk, 1)

        # wait for byte to be processed
        await ClockCycles(dut.clk, 8)

    dut.data_in.value = 0
    dut.cmd.value = CRC_CMD.CMD_FINAL
    await ClockCycles(dut.clk, 2)
    assert config.check == dut.io_out.value

@cocotb.test()
async def test_CMD_SETUP(dut):
    await bringup(dut)

    for crc_name in ["FAKE4", "FAKE8", "FAKE16", "FAKE32", "FAKE4"]:
        config = CRC_TABLE[crc_name]
        config_bitstream = build_config(dut, crc_name)

        dut.cmd.value = CRC_CMD.CMD_SETUP

        await ClockCycles(dut.clk, 1)
        await stream_in(dut, config_bitstream)

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
