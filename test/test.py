# SPDX-FileCopyrightText: 2024 Bojjireddy Rishika
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles

def ntt_butterfly(x, w=3, q=17):
    """Expected NTT output: (x * w) mod q"""
    return (x * w) % q

@cocotb.test()
async def test_project(dut):
    """NTT-Based PQC Core Verification"""
    dut._log.info("Starting NTT Core Verification...")

    # Start clock: 20ns period = 50MHz
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    # Apply reset
    dut.rst_n.value  = 0
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.ena.value    = 1

    await Timer(40, units="ns")   # Hold reset 2 cycles
    dut.rst_n.value = 1
    await Timer(20, units="ns")   # 1 cycle settle

    # Test vectors: (x * 3) mod 17
    test_vectors = [
        0x00,   # 0  → 0
        0x01,   # 1  → 3
        0x05,   # 5  → 15
        0x06,   # 6  → 1  (18 mod 17)
        0x10,   # 16 → 14 (48 mod 17)
        0x0A,   # 10 → 13 (30 mod 17)
        0x04,   # 4  → 12
        0x03,   # 3  → 9
    ]

    for ui_val in test_vectors:
        expected = ntt_butterfly(ui_val)

        dut.ui_in.value = ui_val
        await ClockCycles(dut.clk, 2)

        got = int(dut.uo_out.value)
        assert got == expected, \
            f"FAIL: ui_in=0x{ui_val:02X}({ui_val}) → got {got}, expected {expected}"

        # Check status flags: ready=1, done=1
        status = int(dut.uio_out.value) & 0x03
        assert status == 0x03, \
            f"FAIL: Status flags wrong, uio_out=0x{int(dut.uio_out.value):02X}"

        # Check output enables
        assert int(dut.uio_oe.value) == 0x03, \
            f"FAIL: uio_oe expected 0x03, got 0x{int(dut.uio_oe.value):02X}"

        dut._log.info(f"PASS: ui_in={ui_val} → ntt_out={got} ✓")

    dut._log.info("All NTT verification checks passed!")
