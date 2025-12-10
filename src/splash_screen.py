# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# splash_screen.py
"""Splash screen animation for Dancie."""

import time

import displayio
import terminalio
from adafruit_display_text import label
from game_config import DISPLAY_CENTER, DISPLAY_WIDTH, FRAME_DELAY
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    convert_bitmap_str_to_np,
    draw_numpy_to_displayio_bitmap,
)
from splash_frames import SPLASH_FRAMES


def run_splash_screen(display, bitmap, button):
    """
    Run the splash screen animation until button is pressed.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    button : digitalio.DigitalInOut
        The button input (configured with Pull.UP).

    Returns
    -------
    bool
        True if button was pressed to continue.
    """
    print("\n=== SPLASH SCREEN ===")
    print("Animating kaleidoscope...")
    print("Press button to start game!")

    # Create "Press Start" text label
    text_label = label.Label(terminalio.FONT, text="Press Start", color=0xFFFFFF)

    # Center the text horizontally
    bbox = text_label.bounding_box
    text_width = bbox[2]
    text_label.x = (DISPLAY_WIDTH // 2) - (text_width // 2)
    text_label.y = 55  # Position near bottom of screen

    # Create text group
    text_group = displayio.Group()
    text_group.append(text_label)

    # Add text group to display (on top of bitmap)
    root_group = display.root_group
    root_group.append(text_group)

    # Convert frames on-the-fly to save memory
    frame_idx = 0
    num_frames = len(SPLASH_FRAMES)

    # Animation loop - continues until button pressed
    try:
        while True:
            # Check button (active LOW with pull-up)
            if not button.value:
                print("\n✓ Button pressed! Starting game...")
                # Clean up text group before returning
                root_group.remove(text_group)
                return True

            # Animate splash screen
            display.auto_refresh = False
            clear_displayio_bitmap(bitmap)

            # Draw current kaleidoscope frame
            frame_np = convert_bitmap_str_to_np(SPLASH_FRAMES[frame_idx])
            draw_numpy_to_displayio_bitmap(frame_np, bitmap, origin=DISPLAY_CENTER)

            display.refresh()

            # Move to next frame (loop animation)
            frame_idx = (frame_idx + 1) % num_frames

            # Control frame rate
            time.sleep(FRAME_DELAY)

    except Exception as e:
        # Make sure to clean up on any error
        if text_group in root_group:
            root_group.remove(text_group)
        raise e
