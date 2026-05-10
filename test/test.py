import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def out_value(dut):
    return int(dut.uo_out.value)


def pwm_bit(dut):
    return out_value(dut) & 0x1


def mod_debug(dut):
    return (out_value(dut) >> 4) & 0xF


async def count_pwm_highs(dut, cycles):
    highs = 0

    for _ in range(cycles):
        await ClockCycles(dut.clk, 1)
        if pwm_bit(dut):
            highs += 1

    return highs


async def collect_mod_debug_values(dut, cycles):
    values = []

    for _ in range(cycles):
        await ClockCycles(dut.clk, 1)
        values.append(mod_debug(dut))

    return values


async def reset_dut(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start PWM tremolo waveform-select test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    # Test 1: disabled output should stay low
    dut.ui_in.value = 0b00000000
    disabled_highs = await count_pwm_highs(dut, 128)

    dut._log.info(f"disabled_highs = {disabled_highs}")
    assert disabled_highs == 0

    # Input bit map:
    # ui_in[0]   = enable
    # ui_in[2:1] = rate
    # ui_in[4:3] = depth
    # ui_in[6:5] = waveform

    # Test 2: saw-up waveform should create PWM activity
    # waveform = 00, depth = 11, rate = 00, enable = 1
    dut.ui_in.value = 0b00011001
    saw_up_highs = await count_pwm_highs(dut, 512)

    dut._log.info(f"saw_up_highs = {saw_up_highs}")
    assert saw_up_highs > 0

    # Test 3: saw-down waveform should create PWM activity
    # waveform = 01, depth = 11, rate = 00, enable = 1
    dut.ui_in.value = 0b00111001
    saw_down_highs = await count_pwm_highs(dut, 512)

    dut._log.info(f"saw_down_highs = {saw_down_highs}")
    assert saw_down_highs > 0

    # Test 4: square waveform behavior should differ from saw-up
    dut.ui_in.value = 0b01011001
    square_highs = await count_pwm_highs(dut, 2048)

    dut._log.info(f"square_highs = {square_highs}")

    assert square_highs != saw_up_highs

    # Test 5: triangle waveform should create PWM activity
    # waveform = 11, depth = 11, rate = 00, enable = 1
    dut.ui_in.value = 0b01111001
    triangle_highs = await count_pwm_highs(dut, 512)

    dut._log.info(f"triangle_highs = {triangle_highs}")
    assert triangle_highs > 0

    # Test 6: waveform modes should not all produce identical debug behavior
    await reset_dut(dut)

    dut.ui_in.value = 0b00011001
    saw_values = await collect_mod_debug_values(dut, 1024)

    await reset_dut(dut)

    dut.ui_in.value = 0b00111001
    saw_down_values = await collect_mod_debug_values(dut, 1024)

    dut._log.info(f"saw first={saw_values[0]}, last={saw_values[-1]}")
    dut._log.info(f"saw_down first={saw_down_values[0]}, last={saw_down_values[-1]}")

    assert saw_values != saw_down_values

    # Test 7: debug enable bit should follow enable input
    dut.ui_in.value = 0b01111001
    await ClockCycles(dut.clk, 5)

    assert (out_value(dut) & 0x8) != 0
