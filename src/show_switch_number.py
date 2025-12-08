# show_button_number.py
"""Test multiplexer switch input by displaying switch number on screen."""

import time

import board
import displayio
import terminalio
from adafruit_display_text import label
from digitalio import DigitalInOut, Direction, Pull


def display_active_switches(display, main_group):
    """
    Test multiplexer switch input - displays switch number (1-8) on screen.

    Hardware setup:
    - CD74HC4067 16-channel multiplexer
    - S0 -> D8
    - S1 -> D9
    - S2 -> D10
    - SIG -> D7
    - S3 -> Not connected
    - EN -> GND (enable chip)
    - VCC -> 3V3
    - GND -> GND

    Switches:
    - Connect each normally-open switch between mux channels C0-C7 and GND
    - Channel 0 = Switch 1, Channel 1 = Switch 2, etc.
    """

    # Initialize multiplexer control pins
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT

    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT

    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    # Initialize signal input pin (with pull-up so open = HIGH)
    sig = DigitalInOut(board.D7)
    sig.direction = Direction.INPUT
    sig.pull = Pull.UP

    # Create text label for displaying switch number
    text_label = label.Label(
        terminalio.FONT, text="Close a switch", color=0xFFFFFF, x=20, y=32
    )
    main_group.append(text_label)

    print("Multiplexer switch test initialized")
    print("Close switches 1-8 to see numbers on screen")
    print("Press Ctrl+C to exit")

    # Track previous switch states for debouncing
    prev_states = [False] * 8
    debounce_time = 0.05  # 50ms debounce
    last_change = [0] * 8

    # Track the most recently closed switch
    most_recent_switch = None
    last_switch_time = 0  # Add this line
    timeout_duration = 0.2  # 200ms timeout before clearing display

    def select_channel(channel):
        """Select a channel (0-7) on the multiplexer."""
        s0.value = (channel & 0b001) != 0
        s1.value = (channel & 0b010) != 0
        s2.value = (channel & 0b100) != 0
        time.sleep(0.001)  # Small delay for mux to switch

    def read_switch(channel):
        """Read switch state from specified channel. Returns True if closed."""
        select_channel(channel)
        # Switch closed = LOW (connected to GND), open = HIGH (pull-up)
        return not sig.value

    # Main test loop
    try:
        while True:
            current_time = time.monotonic()
            any_switch_closed = False

            # Scan all 8 channels
            for channel in range(8):
                switch_state = read_switch(channel)

                # Debouncing: only register change after debounce time
                if switch_state != prev_states[channel]:
                    if current_time - last_change[channel] > debounce_time:
                        prev_states[channel] = switch_state
                        last_change[channel] = current_time

                        if switch_state:  # Switch just closed
                            most_recent_switch = (
                                channel + 1
                            )  # Display 1-8 instead of 0-7
                            print(
                                f"Switch {most_recent_switch} closed (Channel {channel})"
                            )

                # Check if this switch is currently closed
                if switch_state:
                    any_switch_closed = True

            # Update display based on most recent switch
            current_time = time.monotonic()

            if any_switch_closed:
                last_switch_time = (
                    current_time  # Update the last time we saw a closed switch
                )

            if (
                most_recent_switch is not None
                and (current_time - last_switch_time) < timeout_duration
            ):
                # Show the most recently closed switch if we've seen one recently
                text_label.text = f"Switch {most_recent_switch}"
                text_label.x = 44  # Center single digit
            else:
                # No switch closed for timeout duration, reset display
                text_label.text = "Close a switch"
                text_label.x = 20
                most_recent_switch = None
            display.refresh()
            time.sleep(0.01)  # 100Hz scan rate

    except KeyboardInterrupt:
        print("\nSwitch test stopped")
        main_group.remove(text_label)
