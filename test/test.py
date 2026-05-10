import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


def bit0(signal):
    return int(signal.value) & 0x1


async def count_pwm_highs(dut, cycles):
    highs = 0

    for _ in range(cycles):
        await ClockCycles(dut.clk, 1)

        if bit0(dut.uo_out):
            highs += 1

    return highs


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start PWM tremolo controller test")

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

    # Test 1: disabled output should stay low
    dut.ui_in.value = 0b00000000
    disabled_highs = await count_pwm_highs(dut, 128)

    dut._log.info(f"disabled_highs = {disabled_highs}")
    assert disabled_highs == 0

    # Test 2: enabled PWM should produce some high pulses
    # ui_in[0] = enable
    # ui_in[2:1] = rate = 00
    # ui_in[4:3] = depth = 00
    dut.ui_in.value = 0b00000001
    light_depth_highs = await count_pwm_highs(dut, 256)

    dut._log.info(f"light_depth_highs = {light_depth_highs}")
    assert light_depth_highs > 0

    # Test 3: deepest depth should also produce PWM activity
    # depth = 11, rate = 00, enable = 1
    dut.ui_in.value = 0b00011001
    deep_depth_highs = await count_pwm_highs(dut, 256)

    dut._log.info(f"deep_depth_highs = {deep_depth_highs}")
    assert deep_depth_highs > 0

    # Test 4: debug enable bit should follow enable input
    assert (int(dut.uo_out.value) & 0x8) != 0
