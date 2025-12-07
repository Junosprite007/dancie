# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
# simulate.py
import time

from emulator.ssd1306 import SSD1306Emulator
from helpers import (
    convert_bitmap_str_to_np,
    draw_rotated_copies,
    generate_bitmap_with_anchor_offset,
)


def main():
    # Create display (128x64)
    disp = SSD1306Emulator()

    # Screen center
    center = (disp.width // 2, disp.height // 2)

    # Define your piece (same as code.py)
    piece = convert_bitmap_str_to_np("""
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

    # Add anchor offset for spinning effect
    # Adjust radius to control how far from center the pieces spin
    piece_with_anchor = generate_bitmap_with_anchor_offset(
        piece.copy(),
        radius=30,  # Distance from center (adjust as needed)
        draw_anchor=False,  # Set to True to see rotation point
    )

    # Animation variables
    base_angle = 22.5  # Starting offset for nice alignment
    angle_offset = 0  # This will increment each frame
    angle_step = 1  # Degrees to rotate per frame (adjust for speed)
    num_copies = 8  # The 8 kaleidoscope copies

    print("Starting real-time 8-copy spinning animation...")
    print(f"Piece size: {piece.shape}")
    print(f"Piece with anchor: {piece_with_anchor.shape}")
    print("Press Ctrl+C to stop")

    try:
        frame_count = 0
        while True:
            # Draw all 8 rotated copies in real-time
            # The start_angle increments to create the spinning effect
            draw_rotated_copies(
                disp,
                piece_with_anchor,
                num_copies=num_copies,
                start_angle=base_angle + angle_offset,
                origin=center,
                clear_display=True,
                show_display=True,
            )

            # Increment angle for next frame
            angle_offset = (angle_offset + angle_step) % 45.0  # 45° for 8-fold symmetry

            # Optional: Print FPS every 60 frames
            frame_count += 1
            if frame_count % 60 == 0:
                print(f"Frame {frame_count}")

            # Control frame rate (~20 FPS for ESP32 compatibility)
            time.sleep(0.05)

    except KeyboardInterrupt:
        disp.close()
        print("\nAnimation stopped")


if __name__ == "__main__":
    main()
