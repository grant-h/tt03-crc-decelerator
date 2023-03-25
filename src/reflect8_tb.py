import cocotb
from cocotb.triggers import Timer

from common_test import reflect

@cocotb.test()
async def test_reflect8(dut):
    dut._log.info("start")

    for test_value in range(0x100):
        dut.inp.value = test_value
        await Timer(10, units="ns")
        value = int(dut.outp.value)
        req_value = reflect(test_value, 8)
        assert value == req_value
        #dut._log.info("%s REFLECT8 -> %s", bin(test_value), bin(req_value))
