# voltage_test.py
"""Quick test to read raw voltage from one multiplexer channel."""

import time

import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction

# Setup multiplexer control pins
s0 = DigitalInOut(board.D8)
s0.direction = Direction.OUTPUT
s1 = DigitalInOut(board.D9)
s1.direction = Direction.OUTPUT
s2 = DigitalInOut(board.D10)
s2.direction = Direction.OUTPUT

# Analog input on A2
analog_sig = AnalogIn(board.A2)

# Select channel 3 (C3)
s0.value = True  # bit 0 = 1
s1.value = True  # bit 1 = 1
s2.value = False  # bit 2 = 0
# 011 in binary = 3 in decimal

print("Reading voltage from Channel 3 (C3)")
print("Press and release the switch a few times...")
print("Format: ADC_value, Voltage")
print("-" * 40)

while True:
    adc = analog_sig.value
    voltage = adc / 65535 * 3.3
    print(f"{adc:5d}, {voltage:.3f}V")
    time.sleep(0.1)  # Read 10 times per second
