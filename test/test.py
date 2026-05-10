import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start tremolo controller test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # enable = ui_in[0] = 1
    # rate = ui_in[2:1] = 00
    dut.ui_in.value = 0b00000001

    await ClockCycles(dut.clk, 50)

    assert int(dut.uo_out.value) != 0
