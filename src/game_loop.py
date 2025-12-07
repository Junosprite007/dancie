# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_loop.py
"""Main game loop and logic."""

import gc
import time

from game_config import (
    DEBUG_HITBOX_SIZE,
    DEBUG_SHOW_HITBOXES,
    DISPLAY_CENTER,
    FRAME_DELAY,
    HIT_TOLERANCE,
    KALEIDOSCOPE_BASE_ANGLE,
    KALEIDOSCOPE_NUM_COPIES,
    KALEIDOSCOPE_RADIUS,
    SLIDING_SHAPE_SPEED,
)
from game_objects import SlidingShape, calculate_collision_centers
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    convert_bitmap_str_to_np,
    draw_collision_points,
    draw_numpy_to_displayio_bitmap,
)
from splash_frames import SPLASH_FRAMES


def run_game(display, bitmap):
    """
    Main game loop.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    """
    print("\n=== Starting Game ===")

    # Load static kaleidoscope background
    static_kaleidoscope = convert_bitmap_str_to_np(SPLASH_FRAMES[0])

    # Calculate collision centers for all 8 pieces
    collision_centers = calculate_collision_centers(
        KALEIDOSCOPE_BASE_ANGLE,
        KALEIDOSCOPE_NUM_COPIES,
        KALEIDOSCOPE_RADIUS,
        DISPLAY_CENTER,
    )
    print(f"Collision centers: {collision_centers}")

    # Create test sliding shape (targeting first piece - top of kaleidoscope)
    # Using the same base piece shape
    test_piece = convert_bitmap_str_to_np("""
1111111111111
1111111111111
1100000000011
1100000000011
0110000000110
0110000000110
0011000001100
0011000001100
0001100011000
0001111111000
0000111110000
""")

    sliding_shape = SlidingShape(
        test_piece,
        target_center=collision_centers[0],  # Target top piece
        start_side="left",
        speed=SLIDING_SHAPE_SPEED,
    )

    print("✓ Game initialized!")
    print("✓ Shape sliding from left toward top piece")
    print(f"✓ Free memory: {gc.mem_free()} bytes")

    # Main game loop
    while True:
        display.auto_refresh = False
        clear_displayio_bitmap(bitmap)

        # Draw static kaleidoscope background
        draw_numpy_to_displayio_bitmap(
            static_kaleidoscope, bitmap, origin=DISPLAY_CENTER
        )

        # Draw sliding shape
        if sliding_shape.active:
            sliding_shape.update()
            shape_pos = sliding_shape.get_position()
            draw_numpy_to_displayio_bitmap(
                sliding_shape.bitmap, bitmap, origin=shape_pos
            )

            # Check if reached target
            if sliding_shape.is_at_target(tolerance=HIT_TOLERANCE):
                print("✓ Shape reached target! Disappearing...")
                sliding_shape.active = False

        # DEBUG: Draw hitboxes
        if DEBUG_SHOW_HITBOXES:
            # Draw kaleidoscope collision centers
            draw_collision_points(
                bitmap, collision_centers, size=DEBUG_HITBOX_SIZE, color=1
            )

            # Draw sliding shape hitbox
            if sliding_shape.active:
                draw_collision_points(
                    bitmap,
                    [sliding_shape.get_position()],
                    size=DEBUG_HITBOX_SIZE,
                    color=1,
                )

        display.refresh()

        # Control frame rate
        time.sleep(FRAME_DELAY)

        # For testing: exit after shape disappears
        if not sliding_shape.active:
            print("Test complete! Shape animation finished.")
            break

    # Keep display showing
    print("\nGame paused. Press Ctrl+C to reset.")
    while True:
        time.sleep(1)
