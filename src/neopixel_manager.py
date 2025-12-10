# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# neopixel_manager.py
"""NeoPixel health indicator management."""

import board
import neopixel
from game_config import (
    COLOR_HEALTH_FULL,
    COLOR_HEALTH_OFF,
    COLOR_POWER_ON,
    NEOPIXEL_BRIGHTNESS,
    NUM_NEOPIXELS,
)


class NeoPixelManager:
    """
    Manages the 6 NeoPixel LEDs.

    LED 0: Power indicator (green when on)
    LEDs 1-5: Health indicators (purple when alive, off when dead)
    """

    def __init__(self, pin=board.D3):
        """
        Initialize NeoPixel strip.

        Parameters
        ----------
        pin : board pin
            Pin connected to NeoPixel data line (default D3).
        """
        self.pixels = neopixel.NeoPixel(
            pin, NUM_NEOPIXELS, brightness=NEOPIXEL_BRIGHTNESS, auto_write=False
        )

        # Turn on power indicator
        self.pixels[0] = COLOR_POWER_ON

        # Initialize all health LEDs to full
        self.set_health(5)

        self.pixels.show()

    def set_health(self, health):
        """
        Set health LEDs based on current health value.

        Parameters
        ----------
        health : int
            Current health (0-5). Each point corresponds to one LED.
        """
        # Clamp health between 0 and 5
        if health < 0:
            health = 0
        if health > 5:
            health = 5

        # Update LEDs 1-5 (indices 1-5)
        for i in range(5):
            led_index = i + 1  # Offset by 1 (LED 0 is power indicator)

            if i < health:
                # This LED is still alive
                self.pixels[led_index] = COLOR_HEALTH_FULL
            else:
                # This LED is dead
                self.pixels[led_index] = COLOR_HEALTH_OFF

        self.pixels.show()

    def flash_health(self, times=3, delay=0.1):
        """
        Flash health LEDs (for visual feedback).

        Parameters
        ----------
        times : int
            Number of times to flash (default 3).
        delay : float
            Delay between flashes in seconds (default 0.1).
        """
        import time

        # Store current health colors
        original_colors = [self.pixels[i] for i in range(1, 6)]

        for _ in range(times):
            # Turn off health LEDs
            for i in range(1, 6):
                self.pixels[i] = COLOR_HEALTH_OFF
            self.pixels.show()
            time.sleep(delay)

            # Restore original colors
            for i in range(1, 6):
                self.pixels[i] = original_colors[i - 1]
            self.pixels.show()
            time.sleep(delay)

    def turn_off_all(self):
        """Turn off all LEDs (for cleanup/shutdown)."""
        for i in range(NUM_NEOPIXELS):
            self.pixels[i] = (0, 0, 0)
        self.pixels.show()

    def victory_animation(self, duration=2.0):
        """
        Play a victory animation (level complete).

        Parameters
        ----------
        duration : float
            Duration of animation in seconds (default 2.0).
        """
        import time

        # Rainbow cycle through health LEDs
        colors = [
            (255, 0, 0),  # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
        ]

        start_time = time.monotonic()
        frame = 0

        while time.monotonic() - start_time < duration:
            for i in range(5):
                color_index = (i + frame) % len(colors)
                self.pixels[i + 1] = colors[color_index]

            self.pixels.show()
            time.sleep(0.1)
            frame += 1

        # Restore power indicator
        self.pixels[0] = COLOR_POWER_ON
        self.pixels.show()
