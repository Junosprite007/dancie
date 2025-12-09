# This file was made with the use of  Claude Sonnet 4.5 LLM
# show_button_number.py
"""Test multiplexer switch input by displaying switch number on screen."""

import time

import board
import displayio
import terminalio
from adafruit_display_text import label
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction


def display_active_switches(display, main_group):
    """
    Test multiplexer switch input - displays all 8 switches in a grid.

    Display shows 2 columns x 4 rows:
    0 1
    0 0
    0 0
    0 0

    Where "1" means switch is pressed (closed), "0" means switch is not pressed (open).

    Hardware setup:
    - CD74HC4067 16-channel multiplexer
    - S0 -> D8
    - S1 -> D9
    - S2 -> D10
    - SIG -> A2 (analog input with external 10kΩ pull-up to 3.3V)
    - S3 -> Not connected
    - EN -> GND (enable chip)
    - VCC -> 3V3
    - GND -> GND

    Switches:
    - Connect each normally-OPEN (NO) switch between mux channels C0-C7 and GND
    - When NOT pressed: reads ~2.9V (stable HIGH via pull-up)
    - When pressed: signal may flicker between ~0.03V and 2.9V (instability)
    - We detect INSTABILITY as the pressed state
    - Channel 0 = Switch 1, Channel 1 = Switch 2, etc.
    """

    # Initialize multiplexer control pins
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT

    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT

    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    # Use ANALOG input on A2 - this reads voltage as 0-65535
    analog_sig = AnalogIn(board.A2)

    # Voltage threshold: below this = LOW reading, above = HIGH reading
    # Set threshold at 1.5V = (1.5 / 3.3) * 65535 ≈ 30000
    VOLTAGE_THRESHOLD = 30000

    # Create 8 text labels in a 2x4 grid
    labels = []
    spacing_x = 30  # Horizontal spacing between columns
    spacing_y = 12  # Vertical spacing between rows
    start_x = display.width // 2 - spacing_x // 2  # Center horizontally
    start_y = 10  # Start near top

    for i in range(8):
        row = i // 2  # 0-3
        col = i % 2  # 0-1
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y

        text_label = label.Label(terminalio.FONT, text="0", color=0xFFFFFF, x=x, y=y)
        labels.append(text_label)
        main_group.append(text_label)

    print(
        "Multiplexer switch grid display initialized (NO switches - instability detection)"
    )
    print("Grid layout (2 columns x 4 rows):")
    print("Switch 1  Switch 2")
    print("Switch 3  Switch 4")
    print("Switch 5  Switch 6")
    print("Switch 7  Switch 8")
    print(
        f"Voltage threshold: {VOLTAGE_THRESHOLD} (~{VOLTAGE_THRESHOLD / 65535 * 3.3:.2f}V)"
    )
    print("Press Ctrl+C to exit")

    # Track switch states
    prev_states = [False] * 8  # Display state (what we show on screen)
    last_change = [0] * 8  # For logging state changes
    debounce_time = 0.1  # Only log changes after 100ms

    def select_channel(channel):
        """Select a channel (0-7) on the multiplexer."""
        s0.value = (channel & 0b001) != 0
        s1.value = (channel & 0b010) != 0
        s2.value = (channel & 0b100) != 0
        time.sleep(0.001)  # Small delay for mux to switch

    def read_switch_raw(channel):
        """Read raw switch state from specified channel using analog voltage."""
        select_channel(channel)
        # Read analog value and convert to boolean
        # NO switch: closed = LOW (connected to GND), open = HIGH (pull-up)
        analog_value = analog_sig.value
        return analog_value < VOLTAGE_THRESHOLD  # True = LOW/closed/pressed

    def detect_instability(channel):
        """
        Detect if signal is unstable (flickering).
        Returns True if pressed (unstable), False if not pressed (stable).
        """
        # Take MORE samples over a longer period to catch flickering
        samples = []
        for _ in range(10):  # 10 samples
            samples.append(read_switch_raw(channel))
            time.sleep(0.001)  # 1ms between samples (10ms total)

        # Count changes in the samples
        changes = 0
        for i in range(len(samples) - 1):
            if samples[i] != samples[i + 1]:
                changes += 1

        # If we see ANY changes (1+), signal is unstable = pressed
        # If we see 0 changes, signal is completely stable = not pressed
        is_pressed = changes >= 1

        return is_pressed

    # Main loop
    try:
        while True:
            current_time = time.monotonic()

            # Scan all 8 channels
            for channel in range(8):
                # Detect if this switch is pressed via instability
                switch_pressed = detect_instability(channel)

                # Update display state and log changes
                if switch_pressed != prev_states[channel]:
                    if current_time - last_change[channel] > debounce_time:
                        prev_states[channel] = switch_pressed
                        last_change[channel] = current_time

                        # Log state changes
                        state_name = "pressed" if switch_pressed else "released"
                        print(f"Switch {channel + 1} {state_name}")

                # Update the label for this switch
                labels[channel].text = "1" if prev_states[channel] else "0"

            # Refresh display once per scan cycle
            display.refresh()
            time.sleep(0.01)  # Small delay between full scans

    except KeyboardInterrupt:
        print("\nSwitch test stopped")
        # Clean up
        analog_sig.deinit()
        for text_label in labels:
            main_group.remove(text_label)
