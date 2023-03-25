import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

lfsr_bits = 64
init_value = 0x1234567890abcdef
all_ones = (1 << lfsr_bits) - 1

async def bringup(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # init module
    dut.init_value.value = 0
    dut.shift.value = False
    dut.load.value = False
    dut.data.value = 0
    dut.taps.value = 0

    await RisingEdge(dut.clk)

    dut.rst.value = 1
    await RisingEdge(dut.clk)

    dut.rst.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("reset done")

@cocotb.test()
async def test_lfsr_load(dut):
    await bringup(dut)

    assert dut.value.value == 0

    dut.init_value.value = init_value
    dut.load.value = 1
    dut.shift.value = 0

    await ClockCycles(dut.clk, 2)

    dut.load.value = 0
    # Confirm load success
    assert dut.value.value == init_value

    # Ensure that it's holding
    await ClockCycles(dut.clk, 1)
    assert dut.value.value == init_value

    dut.load.value = 1
    dut.shift.value = 1

    # Ensure that it's holding even with invalid commands
    await ClockCycles(dut.clk, 1)
    assert dut.value.value == init_value

    dut.load.value = 0
    dut.shift.value = 0
    dut.init_value.value = all_ones

    # Ensure that it's held even if input wires change
    await ClockCycles(dut.clk, 1)
    assert dut.value.value == init_value

    dut.load.value = 1

    # Make sure new value is loaded
    await ClockCycles(dut.clk, 2)
    assert dut.value.value == all_ones

    dut.rst.value = 1
    await RisingEdge(dut.clk)

    dut.rst.value = 0
    await RisingEdge(dut.clk)

    # Make sure value is cleared
    assert dut.value.value == 0

@cocotb.test()
async def test_lfsr_shifting(dut):
    await bringup(dut)

    dut.load.value = True
    dut.init_value.value = all_ones

    await ClockCycles(dut.clk, 2)
    assert dut.value.value == all_ones

    # Do XOR with self + 1
    dut.taps.value = all_ones

    # half way between cycles
    dut.load.value = False
    dut.shift.value = True
    await ClockCycles(dut.clk, 2)

    # walk the single bit all the way to the end
    for i in range(0, lfsr_bits-1):
        assert dut.value.value == (1 << i)
        await ClockCycles(dut.clk, 1)

    # MSB is set, taps are active, so 0 ^ all_ones = all_ones
    await ClockCycles(dut.clk, 1)
    assert dut.value.value == all_ones
