# A simple associative array in verilog: Cocotb testbench
# Copyright (C) 2023 Ioannis-Rafail Tzonevrakis.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
import random

# Begin helper coroutines
async def reset_cam(dut):
    """Perform the CAM reset sequence; All signals LOW and rst_n LOW. Wait
       10 clock cycles, then rst_n HIGH, then wait another 2 clock cycles."""
    dut.we.value = 0
    dut.content.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

async def write_cam(dut, value):
    """Write to the CAM: Raise we HIGH and content to the value we want to
       write. Wait a clock cycle, then rise we low"""
    dut.we.value = 1
    dut.content.value = value
    await FallingEdge(dut.clk)
    dut.we.value = 0
# End helper coroutines

# Begin cocotb tests
@cocotb.test()
async def test_reset(dut):
    """Test reset sequence."""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    assert int(dut.found_addr.value) == int('ffff', 16)
    assert int(dut.uio_oe.value) == int('ff', 16)

@cocotb.test()
async def test_reset_then_miss(dut):
    """Test reset sequence, followed by causing a miss"""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    for i in range(16):
        dut.content.value = 1
        await FallingEdge(dut.clk)
        assert int(dut.found_addr.value) == 0

@cocotb.test()
async def test_write(dut):
    """Test simple writes."""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    await write_cam(dut, int('01', 16))
    await write_cam(dut, int('7a', 16))
    await write_cam(dut, int('0a', 16))
    await write_cam(dut, int('7a', 16))
    dut.content.value = int('0b', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == 0
    # Test match collision: Two lines should be active
    dut.content.value = int('7a', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000001010', 2)
    # Simple matches
    dut.content.value = int('01', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000000001', 2)
    dut.content.value = int('0a', 16)
    await FallingEdge(dut.clk)
    assert int(dut.found_addr.value) == int('0000000000000100', 2)

@cocotb.test()
async def test_fill(dut):
    """Test filling up the CAM (writes + address current overflow)"""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Write values from 1..16 to the CAM, and check that the match
    # lines behave as expected
    for i in range(1, 17):
        await write_cam(dut, i)
        dut.content.value = i
        await FallingEdge(dut.clk)
        assert int(dut.found_addr.value) == 1 << (i-1) 
    # CAM is full now, so it should cycle back to position zero.
    # Write successive zeroes to check whether the address
    # has successfully cycled
    for i in range(16):
        await write_cam(dut, 0)
        dut.content.value = 0
        await FallingEdge(dut.clk)
        for j, bitval in enumerate(dut.found_addr.value):
            # cocotb seems to be big endian. Adjust for that:
            if 15-j <= i:
                assert bitval == 1
            else:
                assert bitval == 0

@cocotb.test()
async def test_fill_then_miss(dut):
    """Test filling up the CAM, then causing misses"""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Write values from 1..16 to the CAM, and check that the match
    # lines behave as expected
    for i in range(1, 17):
        await write_cam(dut, i)
        dut.content.value = i
        await FallingEdge(dut.clk)
        assert int(dut.found_addr.value) == 1 << (i-1) 
    # CAM is full now, so it should cycle back to position zero.
    # Read successive zeroes to check whether misses behave as expected
    for i in range(16):
        dut.content.value = 0
        await FallingEdge(dut.clk)
        assert int(dut.found_addr.value) == 0

@cocotb.test()
async def test_random(dut):
    """16*5000 = 80000 random reads/writes"""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Keep track of the CAM's contents to know which match lines 
    # should be HIGH
    memory_contents = [0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0]
    # Keep track of how many content collisions we've caused
    collisions = 0

    for i in range(5000):
        # Perform 5000 successive CAM fills
        for i in range(16):
            # Select a random value between 0 and 2**7-1 = 127 and write it
            # to the CAM
            val = random.randint(0, 127)
            await write_cam(dut, val)
            # Log the expected memory content, and check match lines
            # accordingly
            memory_contents[i] = val
            dut.content.value = val
            await FallingEdge(dut.clk)
            # Find which lines we expect to be HIGH
            expected_HIGH = [15-i for i, v in enumerate(memory_contents)
                             if v == val]
            if len(expected_HIGH) > 1:
                # More than 1 lines are expected to be HIGH.
                # Increase the collision counter
                collisions += 1
            for j, bitval in enumerate(dut.found_addr.value):
                if j in expected_HIGH:
                    assert bitval == 1
                else:
                    assert bitval == 0

    dut._log.info(f'Observed {collisions} collisions.')

@cocotb.test()
async def test_random_rw_cycles(dut):
    """16*5000 = 80000 random read/write cycles """
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Keep track of the CAM's contents to know which match lines 
    # should be HIGH
    memory_contents = [0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0]
    # Keep track of how many content collisions we've caused
    collisions = 0

    for i in range(5000):
        # Perform 5000 successive CAM fills
        for i in range(16):
            # Select a random value between 0 and 2**7-1 = 127 and write it
            # to the CAM
            val = random.randint(0, 127)
            await write_cam(dut, val)
            # Log the expected memory content, and check match lines
            # accordingly
            memory_contents[i] = val
            await FallingEdge(dut.clk)
        for val in memory_contents:
            assert dut.we.value == 0
            dut.content.value = val
            await FallingEdge(dut.clk)
            # Find which lines we expect to be HIGH
            expected_HIGH = [15-i for i, v in enumerate(memory_contents)
                             if v == val]
            if len(expected_HIGH) > 1:
                # More than 1 lines are expected to be HIGH.
                # Increase the collision counter
                collisions += 1
            for j, bitval in enumerate(dut.found_addr.value):
                if j in expected_HIGH:
                    assert bitval == 1
                else:
                    assert bitval == 0

    dut._log.info(f'Observed {collisions} collisions.')

@cocotb.test()
async def test_random_misses(dut):
    """16*5000 = 80000 random write/miss cycles """
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Keep track of the CAM's contents to know which match lines 
    # should be HIGH
    memory_contents = [0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(5000):
        # Perform 5000 successive CAM fills
        for i in range(16):
            # Select a random value between 0 and 2**7-1 = 127 and write it
            # to the CAM
            val = random.randint(0, 127)
            await write_cam(dut, val)
            # Log the expected memory content, and check match lines
            # accordingly
            memory_contents[i] = val
            await FallingEdge(dut.clk)
        
        # Find test values that aren't in memory
        test_values = []
        while True:
            val = random.randint(0, 127)
            if val not in memory_contents:
                test_values.append(val)
            if len(test_values) == len(memory_contents):
                break

        for val in test_values:
            # We should only be getting misses
            assert dut.we.value == 0
            dut.content.value = val
            await FallingEdge(dut.clk)
            assert int(dut.found_addr.value) == 0

@cocotb.test()
async def test_random_rw_cycles_with_misses(dut):
    """16*5000 = 80000 random read/write cycles with misses"""
    clock = Clock(dut.clk, 1, units="ms")
    cocotb.start_soon(clock.start())
    await reset_cam(dut)
    await FallingEdge(dut.clk)
    # Keep track of the CAM's contents to know which match lines 
    # should be HIGH
    memory_contents = [0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0]
    # Keep track of how many content collisions we've caused
    collisions = 0

    for i in range(5000):
        # Perform 5000 successive CAM fills
        for i in range(16):
            # Select a random value between 0 and 2**7-1 = 127 and write it
            # to the CAM
            val = random.randint(0, 127)
            await write_cam(dut, val)
            # Log the expected memory content, and check match lines
            # accordingly
            memory_contents[i] = val
            await FallingEdge(dut.clk)
        for val in memory_contents:
            # Decide whether we will cause a miss:
            miss = random.random() < 0.5
            if miss:
                # Query for a value not in memory
                while True:
                    v = random.randint(0, 127)
                    if v not in memory_contents:
                        val = v
                        break

            assert dut.we.value == 0
            dut.content.value = val
            await FallingEdge(dut.clk)
            # Find which lines we expect to be HIGH
            if miss:
                assert int(dut.found_addr.value) == 0
                continue
            expected_HIGH = [15-i for i, v in enumerate(memory_contents)
                             if v == val]
            if len(expected_HIGH) > 1:
                # More than 1 lines are expected to be HIGH.
                # Increase the collision counter
                collisions += 1
            for j, bitval in enumerate(dut.found_addr.value):
                if j in expected_HIGH:
                    assert bitval == 1
                else:
                    assert bitval == 0

    dut._log.info(f'Observed {collisions} collisions.')


# End cocotb tests
