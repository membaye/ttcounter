# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, Timer

LOAD, OE, EN = 1 << 0, 1 << 1, 1 << 2


async def tick(dut, n=1):
    for _ in range(n):
        await FallingEdge(dut.clk)


def count(dut):
    return int(dut.uo_out.value)


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 10, "us").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await tick(dut, 3)
    dut.rst_n.value = 1
    await tick(dut)


@cocotb.test()
async def test_reset(dut):
    await setup(dut)
    assert count(dut) == 0, "count should be 0 after reset"


@cocotb.test()
async def test_counting_and_hold(dut):
    await setup(dut)
    dut.ui_in.value = EN
    await tick(dut, 5)
    assert count(dut) == 5, f"need 5, got {count(dut)}"

    dut.ui_in.value = 0          # EN off: should hold
    await tick(dut, 4)
    assert count(dut) == 5, "count changed while EN was 0"


@cocotb.test()
async def test_sync_load(dut):
    await setup(dut)
    dut.uio_in.value = 0xA5
    dut.ui_in.value = LOAD
    await Timer(1, "us")         # no clock edge yet
    assert count(dut) == 0, "load must wait for the clock (synchronous)"
    await tick(dut)
    assert count(dut) == 0xA5, f"expected 0xA5, got {count(dut):#04x}"


@cocotb.test()
async def test_load_beats_enable(dut):
    await setup(dut)
    dut.uio_in.value = 0x40
    dut.ui_in.value = LOAD | EN
    await tick(dut)
    assert count(dut) == 0x40, "load should take priority over count enable"


@cocotb.test()
async def test_wraparound(dut):
    await setup(dut)
    dut.uio_in.value = 0xFE
    dut.ui_in.value = LOAD
    await tick(dut)
    dut.ui_in.value = EN
    await tick(dut, 3)           # FE -> FF -> 00 -> 01
    assert count(dut) == 0x01, f"expected wrap to 0x01, got {count(dut):#04x}"


@cocotb.test()
async def test_async_reset(dut):
    await setup(dut)
    dut.ui_in.value = EN
    await tick(dut, 7)
    assert count(dut) == 7
    dut.rst_n.value = 0
    await Timer(1, "us")         # mid-cycle, no clock edge
    assert count(dut) == 0, "reset must clear immediately (asynchronous)"
    dut.rst_n.value = 1


@cocotb.test()
async def test_tristate(dut):
    await setup(dut)
    dut.uio_in.value = 0x3C
    dut.ui_in.value = LOAD       # OE off while loading
    await tick(dut)
    assert int(dut.uio_oe.value) == 0x00, "bus should be high-Z when OE=0"

    dut.ui_in.value = OE
    await tick(dut)
    assert int(dut.uio_oe.value) == 0xFF, "bus should drive when OE=1"
    assert int(dut.uio_out.value) == 0x3C, "bus should carry the count"