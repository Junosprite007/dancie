# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
import time

import numpy as np
from emulator.ssd1306 import SSD1306Emulator
from helpers import *


def main():
    disp = SSD1306Emulator()

    # Define your piece
    piece = """
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
"""

    # Convert to numpy and add anchor offset
    piece_np = convert_bitmap_str_to_np(piece)
    piece_with_anchor = generate_bitmap_with_anchor_offset(piece_np.copy(), 24, True)

    # Pre-compute animation frames (do this ONCE at startup)
    print("Pre-computing animation frames...")
    animation_cache = precompute_spinning_animation(
        piece_with_anchor,
        num_copies=8,
        base_angle=22.5,
        animation_steps=45,  # Adjust this: more = smoother but more memory
        degrees_per_cycle=45.0,
    )
    print(f"Pre-computed {len(animation_cache)} frames")
    print(f"Each frame has {len(animation_cache[0])} copies")

    # Animation loop
    frame_index = 0
    try:
        while True:
            # Draw the current frame from cache (NO rotation computation!)
            draw_precomputed_frame(disp, animation_cache[frame_index])

            # Move to next frame (loop back to start)
            frame_index = (frame_index + 1) % len(animation_cache)

            # Control animation speed
            time.sleep(0.033)  # ~30 FPS

    except KeyboardInterrupt:
        disp.close()
        print("\nAnimation stopped")


if __name__ == "__main__":
    main()
