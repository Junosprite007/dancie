# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# splash_screen.py
"""Splash screen animation for Dancie."""

import time

from game_config import DISPLAY_CENTER, FRAME_DELAY
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    convert_bitmap_str_to_np,
    draw_numpy_to_displayio_bitmap,
)
from splash_frames import SPLASH_FRAMES


def draw_text_press_start(displayio_bitmap):
    """
    Draw 'PRESS START' text on the display.

    For now, we'll use a simple approach. You can enhance this later
    with a proper font or bitmap text.
    """
    # Simple text representation as a small bitmap
    # This is a placeholder - you might want to use a proper font library
    # or create a bitmap text in your generator script

    # For now, let's draw some simple pixels to indicate text area
    # Center position for text (bottom third of screen)
    text_y = 50

    # Draw a simple indicator line
    for x in range(40, 88):  # Centered horizontally
        if 0 <= x < displayio_bitmap.width and 0 <= text_y < displayio_bitmap.height:
            displayio_bitmap[x, text_y] = 1


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

    # Convert frames on-the-fly to save memory
    frame_idx = 0
    num_frames = len(SPLASH_FRAMES)

    # Animation loop - continues until button pressed
    while True:
        # Check button (active LOW with pull-up)
        if not button.value:
            print("\n✓ Button pressed! Starting game...")
            return True

        # Animate splash screen
        display.auto_refresh = False
        clear_displayio_bitmap(bitmap)

        # Draw current kaleidoscope frame
        frame_np = convert_bitmap_str_to_np(SPLASH_FRAMES[frame_idx])
        draw_numpy_to_displayio_bitmap(frame_np, bitmap, origin=DISPLAY_CENTER)

        # Draw "PRESS START" text (simple version)
        draw_text_press_start(bitmap)

        display.refresh()

        # Move to next frame (loop animation)
        frame_idx = (frame_idx + 1) % num_frames

        # Control frame rate
        time.sleep(FRAME_DELAY)
