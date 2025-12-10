# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_over_screen.py
"""Game over and level complete screen displays."""

import time

import displayio
import terminalio
from adafruit_display_text import label
from game_config import DISPLAY_CENTER, DISPLAY_HEIGHT, DISPLAY_WIDTH, FRAME_DELAY
from helpers_esp32c3 import clear_displayio_bitmap


def create_text_label(text, x, y, color=0xFFFFFF):
    """
    Create a centered text label.

    Parameters
    ----------
    text : str
        Text to display.
    x : int
        X position (will be adjusted to center).
    y : int
        Y position.
    color : int
        Color in hex (default white).

    Returns
    -------
    label.Label
        Text label object.
    """
    text_label = label.Label(terminalio.FONT, text=text, color=color)

    # Center the text horizontally
    bbox = text_label.bounding_box
    text_width = bbox[2]
    text_label.x = x - (text_width // 2)
    text_label.y = y

    return text_label


def show_game_over_screen(display, bitmap, button):
    """
    Display game over screen with "GAME OVER" and "Press Start".

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    button : RotaryEncoderButton
        Button to wait for restart.

    Returns
    -------
    bool
        True if user wants to restart.
    """
    print("\n=== GAME OVER ===")

    # Create a new group for text
    text_group = displayio.Group()

    # Create text labels
    title_label = create_text_label("GAME OVER", DISPLAY_WIDTH // 2, 20)
    prompt_label = create_text_label("Press Start", DISPLAY_WIDTH // 2, 45)

    text_group.append(title_label)
    text_group.append(prompt_label)

    # Clear bitmap and add text group
    display.auto_refresh = False
    clear_displayio_bitmap(bitmap)

    # Get the main root group and append text
    root_group = display.root_group
    root_group.append(text_group)

    display.refresh()

    # Wait for button press
    button.wait_for_press()

    # Clean up text group
    root_group.remove(text_group)

    return True


def show_level_complete_screen(display, bitmap, button, level, score):
    """
    Display level complete screen with stats.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    button : RotaryEncoderButton
        Button to continue.
    level : int
        Level just completed.
    score : int
        Current score.

    Returns
    -------
    bool
        True when ready to continue.
    """
    print(f"\n=== LEVEL {level} COMPLETE ===")
    print(f"Score: {score}")

    # Create text group
    text_group = displayio.Group()

    # Create labels
    title_label = create_text_label(f"Level {level}", DISPLAY_WIDTH // 2, 15)
    complete_label = create_text_label("Complete!", DISPLAY_WIDTH // 2, 28)
    score_label = create_text_label(f"Score: {score}", DISPLAY_WIDTH // 2, 41)
    prompt_label = create_text_label("Press Start", DISPLAY_WIDTH // 2, 54)

    text_group.append(title_label)
    text_group.append(complete_label)
    text_group.append(score_label)
    text_group.append(prompt_label)

    # Display
    display.auto_refresh = False
    clear_displayio_bitmap(bitmap)

    root_group = display.root_group
    root_group.append(text_group)

    display.refresh()

    # Wait for button press
    button.wait_for_press()

    # Clean up
    root_group.remove(text_group)

    return True


def show_victory_screen(display, bitmap, button, score):
    """
    Display victory screen after beating all 10 levels.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    button : RotaryEncoderButton
        Button to continue.
    score : int
        Final score.

    Returns
    -------
    bool
        True when ready to continue.
    """
    print("\n=== VICTORY! ALL LEVELS COMPLETE ===")
    print(f"Final Score: {score}")

    # Create text group
    text_group = displayio.Group()

    # Create labels
    title_label = create_text_label("VICTORY!", DISPLAY_WIDTH // 2, 15)
    all_levels_label = create_text_label("All Levels", DISPLAY_WIDTH // 2, 28)
    complete_label = create_text_label("Complete!", DISPLAY_WIDTH // 2, 38)
    score_label = create_text_label(f"Score: {score}", DISPLAY_WIDTH // 2, 50)

    text_group.append(title_label)
    text_group.append(all_levels_label)
    text_group.append(complete_label)
    text_group.append(score_label)

    # Display
    display.auto_refresh = False
    clear_displayio_bitmap(bitmap)

    root_group = display.root_group
    root_group.append(text_group)

    display.refresh()

    # Flash the text for celebration effect
    for _ in range(3):
        time.sleep(0.3)
        for text_label in text_group:
            text_label.color = 0x000000  # Black (invisible)
        display.refresh()

        time.sleep(0.3)
        for text_label in text_group:
            text_label.color = 0xFFFFFF  # White (visible)
        display.refresh()

    # Add "Press Start" after celebration
    prompt_label = create_text_label("Press Start", DISPLAY_WIDTH // 2, 60)
    text_group.append(prompt_label)
    display.refresh()

    # Wait for button press
    button.wait_for_press()

    # Clean up
    root_group.remove(text_group)

    return True


def show_countdown(display, bitmap, count_from=3):
    """
    Show a countdown animation before starting level.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    count_from : int
        Number to count down from (default 3).
    """
    root_group = display.root_group
    display.auto_refresh = False

    for i in range(count_from, 0, -1):
        clear_displayio_bitmap(bitmap)

        # Create countdown number
        text_group = displayio.Group()
        countdown_label = create_text_label(
            str(i), DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2
        )
        text_group.append(countdown_label)

        root_group.append(text_group)
        display.refresh()
        time.sleep(0.5)

        root_group.remove(text_group)

    # Show "GO!"
    clear_displayio_bitmap(bitmap)
    text_group = displayio.Group()
    go_label = create_text_label("GO!", DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)
    text_group.append(go_label)

    root_group.append(text_group)
    display.refresh()
    time.sleep(0.5)

    root_group.remove(text_group)
