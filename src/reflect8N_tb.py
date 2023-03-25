import cocotb
from cocotb.triggers import Timer

from common_test import reflect

@cocotb.test()
async def test_reflect8N(dut):
    dut._log.info("start")

    trials = 10000

    for bytewidth in range(8):
        bytewidth += 1
        dut._log.info("reflect8N_%d", bytewidth)

        dut.bytewidth.value = bytewidth - 1
        max_value = 2**(8*bytewidth)
        stride = max_value // trials

        if stride == 0:
            stride = 1
        else:
            # make stride have an unusual pattern
            stride += 7

        for test_value in range(0, max_value, stride):
            dut.value.value = test_value
            # combinational delay
            await Timer(10, units="ns")

            #dut._log.info("%s", dut.reflected_value.value)
            value = int(dut.reflected_value.value)
            req_value = reflect(test_value, 8*bytewidth)
            #dut._log.info("%s REFLECT8N -> %s", bin(test_value), bin(req_value))
            assert value == req_value
