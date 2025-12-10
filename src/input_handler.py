# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# input_handler.py
"""Input handling for multiplexer, accelerometer, and rotary encoder."""

import time

import adafruit_adxl34x
import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from game_config import (
    ACCEL_TILT_THRESHOLD,
    DEBUG_PRINT_INPUTS,
    MUX_DEBOUNCE_SAMPLES,
    MUX_SETTLE_TIME,
    MUX_VOLTAGE_THRESHOLD,
)


class MultiplexerInput:
    """
    Handles 8 limit switches via CD74HC4067 multiplexer.

    Uses instability detection method for normally-open switches.
    """

    def __init__(self):
        """Initialize multiplexer control pins and analog input."""
        # Control pins S0, S1, S2
        self.s0 = DigitalInOut(board.D8)
        self.s0.direction = Direction.OUTPUT

        self.s1 = DigitalInOut(board.D9)
        self.s1.direction = Direction.OUTPUT

        self.s2 = DigitalInOut(board.D10)
        self.s2.direction = Direction.OUTPUT

        # Analog signal input
        self.analog_sig = AnalogIn(board.A2)

        # Track previous states for edge detection
        self.prev_states = [False] * 8

    def select_channel(self, channel):
        """
        Select multiplexer channel (0-7).

        Parameters
        ----------
        channel : int
            Channel number (0-7).
        """
        self.s0.value = (channel & 0b001) != 0
        self.s1.value = (channel & 0b010) != 0
        self.s2.value = (channel & 0b100) != 0
        time.sleep(MUX_SETTLE_TIME)

    def read_switch(self, channel):
        """
        Read switch state using instability detection.

        Parameters
        ----------
        channel : int
            Channel number (0-7).

        Returns
        -------
        bool
            True if switch is pressed, False otherwise.
        """
        self.select_channel(channel)

        # Take multiple samples to detect instability
        samples = []
        for _ in range(MUX_DEBOUNCE_SAMPLES):
            raw_value = self.analog_sig.value
            samples.append(raw_value < MUX_VOLTAGE_THRESHOLD)
            time.sleep(0.001)

        # If we see variation in samples, switch is pressed (unstable)
        # If all samples are the same, switch is not pressed (stable)
        variations = len(set(samples))
        is_pressed = variations > 1 or samples[0]

        return is_pressed

    def scan_all(self):
        """
        Scan all 8 channels and return current states.

        Returns
        -------
        list
            List of 8 booleans, True if switch is pressed.
        """
        states = []
        for channel in range(8):
            states.append(self.read_switch(channel))
        return states

    def get_pressed_buttons(self):
        """
        Get list of currently pressed button numbers (1-8).

        Returns
        -------
        list
            List of pressed button numbers (1-8).
        """
        pressed = []
        for channel in range(8):
            if self.read_switch(channel):
                pressed.append(channel + 1)  # Return 1-indexed button numbers
        return pressed

    def wait_for_button_press(self):
        """
        Block until any button is pressed, then return button number.

        Returns
        -------
        int
            Button number (1-8) that was pressed.
        """
        while True:
            for channel in range(8):
                if self.read_switch(channel):
                    if DEBUG_PRINT_INPUTS:
                        print(f"Button {channel + 1} pressed")
                    return channel + 1
            time.sleep(0.01)

    def deinit(self):
        """Clean up resources."""
        self.analog_sig.deinit()
        self.s0.deinit()
        self.s1.deinit()
        self.s2.deinit()


class AccelerometerInput:
    """
    Handles ADXL345 accelerometer for gesture detection.

    Detects tilts in 4 directions: left, right, up (forward), down (back).
    """

    def __init__(self, i2c):
        """
        Initialize accelerometer.

        Parameters
        ----------
        i2c : busio.I2C
            I2C bus object.
        """
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)

    def get_acceleration(self):
        """
        Get current acceleration values.

        Returns
        -------
        tuple
            (x, y, z) acceleration in m/s².
        """
        return self.accelerometer.acceleration

    def detect_tilt_direction(self):
        """
        Detect current tilt direction.

        Returns
        -------
        str or None
            "left", "right", "up", "down", or None if no clear tilt.
        """
        x, y, z = self.accelerometer.acceleration

        # Check X-axis (left/right)
        if x < -ACCEL_TILT_THRESHOLD:
            return "left"
        elif x > ACCEL_TILT_THRESHOLD:
            return "right"

        # Check Y-axis (forward/back = up/down on screen)
        if y > ACCEL_TILT_THRESHOLD:
            return "up"
        elif y < -ACCEL_TILT_THRESHOLD:
            return "down"

        return None

    def wait_for_tilt(self, timeout=2.0):
        """
        Wait for a tilt gesture within timeout period.

        Parameters
        ----------
        timeout : float
            Maximum time to wait in seconds (default 2.0).

        Returns
        -------
        str or None
            Direction tilted ("left", "right", "up", "down") or None if timeout.
        """
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            direction = self.detect_tilt_direction()
            if direction is not None:
                if DEBUG_PRINT_INPUTS:
                    print(f"Tilt detected: {direction}")
                return direction
            time.sleep(0.05)  # Check 20 times per second

        if DEBUG_PRINT_INPUTS:
            print("Tilt timeout")
        return None


class RotaryEncoderButton:
    """
    Handles rotary encoder button input.

    Note: This simplified version only handles the button.
    Full rotary encoder support (CLK/DT pins) can be added later.
    """

    def __init__(self, pin=board.D7):
        """
        Initialize button on rotary encoder.

        Parameters
        ----------
        pin : board pin
            Pin connected to encoder button (default D7).
        """
        self.button = DigitalInOut(pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP

        # Track state for edge detection
        self.prev_state = True  # Not pressed (pull-up)

    def is_pressed(self):
        """
        Check if button is currently pressed.

        Returns
        -------
        bool
            True if pressed (active LOW with pull-up).
        """
        return not self.button.value

    def wait_for_press(self):
        """Block until button is pressed (with debouncing)."""
        # Wait for button to be released first
        while self.is_pressed():
            time.sleep(0.01)

        # Wait for button to be pressed
        while not self.is_pressed():
            time.sleep(0.01)

        # Debounce delay
        time.sleep(0.05)

        if DEBUG_PRINT_INPUTS:
            print("Encoder button pressed")

    def deinit(self):
        """Clean up resources."""
        self.button.deinit()
