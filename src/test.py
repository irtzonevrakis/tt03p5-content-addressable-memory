# A simple associative array in verilog: Cocotb testbench
# Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

async def reset_cam(dut):
    """Perform the CAM reset sequence; All signals LOW and rst_n LOW. Wait
       10 clock cycles, then rst_n HIGH, then wait another 2 clock cycles."""
    dut.we.value = 0
    dut.content.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

@cocotb.test()
async def test_reset(dut):
    """Test reset sequence."""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    assert int(dut.found_addr.value) == int('ffff', 16)

@cocotb.test()
async def test_write(dut):
    """Test simple writes."""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    dut.we.value = 1
    dut.content.value = int('01', 16)
    await FallingEdge(dut.clk)
    dut.content.value = int('7a', 16)
    await FallingEdge(dut.clk)
    dut.content.value = int('0a', 16)
    await FallingEdge(dut.clk)
    dut.content.value = int('7a', 16)
    await FallingEdge(dut.clk)
    dut.we.value = 0
    dut.content.value = int('0b', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == 0
    dut.content.value = int('7a', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000001010', 2)
    dut.content.value = int('01', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000000001', 2)
    dut.content.value = int('0a', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000000100', 2)

# TODO: Constrained random verification
