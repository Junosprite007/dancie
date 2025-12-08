# This file was made with the use of  Claude Sonnet 4.5 LLM
# show_button_number.py
"""Test multiplexer switch input by displaying switch number on screen."""

import time

import board
import displayio
import terminalio
from adafruit_display_text import label
from digitalio import DigitalInOut, Direction, Pull


def activate_switches(display, main_group):
    """
    Test multiplexer switch input - displays switch number (1-8) on screen.

    Display two columns and four rows, where each cell is the state of the connected
    switch. There are 8 switches. Here's what an example grid would look like all
    switch opened, except for switch 2:

    0 1
    0 0
    0 0
    0 0

    These 8 cells display on the center of the screen.

    Hardware setup:

    I'm using an ESP32-C3 with a CD74HC4067 16-channel multiplexer and the following
    circuit mapping.
    - S0 -> D8
    - S1 -> D9
    - S2 -> D10
    - SIG -> D7
    - S3 -> Not connected to anything
    - EN -> GND
    - VCC -> 3V3
    - GND -> GND

    Switches:
    - Each normally-open (NO) switch is connected between a mux channel (C0-C7) and GND
    - Channel 0 = Switch 1, Channel 1 = Switch 2, etc.
    """
    # Setup multiplexer control pins
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT

    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT

    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    # Setup signal pin with pull-up resistor
    sig = DigitalInOut(board.D7)
    sig.direction = Direction.INPUT
    sig.pull = Pull.UP

    # Create labels for the 8 switches in 2 columns x 4 rows
    labels = []
    spacing_x = 40  # Horizontal spacing between columns
    spacing_y = 30  # Vertical spacing between rows
    start_x = display.width // 2 - spacing_x // 2  # Center horizontally
    start_y = display.height // 2 - (spacing_y * 3) // 2  # Center vertically

    for i in range(8):
        row = i // 2
        col = i % 2
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y

        text_label = label.Label(terminalio.FONT, text="0", color=0xFFFFFF, x=x, y=y)
        labels.append(text_label)
        main_group.append(text_label)

    def select_channel(channel):
        """Select multiplexer channel (0-7) by setting S0, S1, S2."""
        s0.value = channel & 0b001
        s1.value = channel & 0b010
        s2.value = channel & 0b100
        time.sleep(0.001)  # Small delay for mux to settle

    # Main loop - continuously read switches and update display
    while True:
        for channel in range(8):
            select_channel(channel)
            # Read switch state (LOW = pressed/closed, HIGH = not pressed/open)
            switch_state = not sig.value  # Invert: True = pressed, False = not pressed
            labels[channel].text = "1" if switch_state else "0"

        time.sleep(0.05)  # Small delay to avoid excessive updates


# Main execution
if __name__ == "__main__":
    # Release any existing displays
    displayio.release_displays()

    # Get the built-in display
    display = board.DISPLAY

    # Create main display group
    main_group = displayio.Group()

    # Show the group on the display
    display.root_group = main_group

    # Start the switch monitoring
    activate_switches(display, main_group)


# This file was made with the use of  Claude Sonnet 4.5 LLM
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

    Display two columns and four rows, where each cell is the state of the connected
    switch. There are 8 switches. Here's what an example grid would look like all
    switch opened, except for switch 2:

    0 1
    0 0
    0 0
    0 0

    These 8 cells display on the center of the screen.

    Hardware setup:

    I'm using an ESP32-C3 with a CD74HC4067 16-channel multiplexer and the following
    circuit mapping.
    - S0 -> D8
    - S1 -> D9
    - S2 -> D10
    - SIG -> D7
    - S3 -> Not connected to anything
    - EN -> GND
    - VCC -> 3V3
    - GND -> GND

    Switches:
    - Each normally-open (NO) switch is connected between a mux channel (C0-C7) and GND
    - Channel 0 = Switch 1, Channel 1 = Switch 2, etc.
    """

    # Setup multiplexer control pins
    s0 = DigitalInOut(board.D8)
    s0.direction = Direction.OUTPUT
    s1 = DigitalInOut(board.D9)
    s1.direction = Direction.OUTPUT
    s2 = DigitalInOut(board.D10)
    s2.direction = Direction.OUTPUT

    # Setup signal pin (reads the mux output)
    sig = DigitalInOut(board.D7)
    sig.direction = Direction.INPUT
    sig.pull = Pull.UP  # Pull-up because switches connect to GND

    # Create text label for displaying switch state
    text_label = label.Label(
        terminalio.FONT,
        text="0",
        color=0xFFFFFF,
        y=display.height // 2,
    )
    main_group.append(text_label)

    def select_channel(channel):
        """Select a multiplexer channel (0-7) by setting S0, S1, S2 with bitwise AND (&)."""
        s0.value = (channel >> 0) & 1  # Shift right 0, mask bit 0
        s1.value = (channel >> 1) & 1  # Shift right 1, mask bit 0
        s2.value = (channel >> 2) & 1  # Shift right 2, mask bit 0

    switch_states = [0] * 8

    # Notice how I must first select a change (channel = switch, in this case).
    # When the switch is opened, sig.value is equal to True; when the switch is
    # closed, sig.value is equal to False.
    select_channel(0)
    text_label.text = str(sig.value)
    display.refresh()
    time.sleep(2)

    # Temporarily test without mux
    test_pin = DigitalInOut(board.D7)
    test_pin.direction = Direction.INPUT
    test_pin.pull = Pull.UP

    while True:
        print(f"Direct read: {test_pin.value}")
        time.sleep(0.1)
    # # Main loop
    # while True:
    #     select_channel(0)
    #     print(f"sig.value: {sig.value}, S0={s0.value}, S1={s1.value}, S2={s2.value}")
    #     text_label.text = str(sig.value)
    #     display.refresh()
    #     time.sleep(1.00)

    # if

    # Read the switch state
    # sig.value is False (0) when switch is closed (pressed)
    # sig.value is True (1) when switch is open (not pressed)
    # switch_pressed = not sig.value

    # Update display: show "1" if pressed, "0" if not
    # text_label.text = str(switch_states)
    # text_label.text = str(sig.value)
    # text_label.text = str(sig)

    # Refresh display since auto_refresh is False
    # display.refresh()
    # break
    # time.sleep(0.1)  # Short delay before next read
