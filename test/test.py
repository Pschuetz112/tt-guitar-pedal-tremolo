import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


async def count_toggles(dut, cycles):
    last = int(dut.uo_out[0].value)
    toggles = 0

    for _ in range(cycles):
        await ClockCycles(dut.clk, 1)
        now = int(dut.uo_out[0].value)

        if now != last:
            toggles += 1
            last = now

    return toggles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start stronger tremolo controller test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Test 1: enable off should force tremolo output low
    dut.ui_in.value = 0b00000000
    await ClockCycles(dut.clk, 40)
    assert int(dut.uo_out[0].value) == 0

    # Test 2: enable on, fastest rate should toggle
    # ui_in[0] = enable
    # ui_in[2:1] = rate = 00
    dut.ui_in.value = 0b00000001
    fast_toggles = await count_toggles(dut, 128)

    dut._log.info(f"fast_toggles = {fast_toggles}")
    assert fast_toggles > 0

    # Test 3: slower rate should toggle fewer times
    # rate = 11, enable = 1
    dut.ui_in.value = 0b00000111
    slow_toggles = await count_toggles(dut, 128)

    dut._log.info(f"slow_toggles = {slow_toggles}")
    assert slow_toggles > 0
    assert slow_toggles < fast_toggles
