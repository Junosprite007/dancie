# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
# generate_splash_frames.py
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

import numpy as np
from helpers import (
    convert_bitmap_str_to_np,
    generate_bitmap_with_anchor_offset,
    rotate_bitmap_in_place,
)

# Same piece definition
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

piece_with_anchor = generate_bitmap_with_anchor_offset(piece, radius=24)

# Create complete kaleidoscope
kaleidoscope_size = 64
base_kaleidoscope = np.zeros((kaleidoscope_size, kaleidoscope_size), dtype=np.uint8)

base_angle = 22.5
num_copies = 8
angle_step = 360.0 / num_copies  # 45° spacing between pieces (DON'T CHANGE)

# Draw all 8 pieces into one bitmap
for i in range(num_copies):
    angle = base_angle + (angle_step * i)
    rotated_piece = rotate_bitmap_in_place(piece_with_anchor, angle)
    rows, cols = rotated_piece.shape

    center_x = kaleidoscope_size // 2
    center_y = kaleidoscope_size // 2

    start_x = center_x - cols // 2
    start_y = center_y - rows // 2

    for y in range(rows):
        for x in range(cols):
            bm_x = start_x + x
            bm_y = start_y + y
            if 0 <= bm_x < kaleidoscope_size and 0 <= bm_y < kaleidoscope_size:
                if rotated_piece[y, x] > 0:
                    base_kaleidoscope[bm_y, bm_x] = 1

print("Base kaleidoscope created!")
print(f"Size: {base_kaleidoscope.shape}")

# ANIMATION SETTINGS - CHANGE THESE!
degrees_per_frame = 10.0  # How much to rotate each frame
total_rotation = 90  # Total degrees to rotate (180° or 360° recommended)

# Calculate number of frames needed
num_frames = int(total_rotation / degrees_per_frame)

print(f"\nAnimation settings:")
print(f"  Rotation per frame: {degrees_per_frame}°")
print(f"  Total rotation: {total_rotation}°")
print(f"  Number of frames: {num_frames}")
print(f"\nGenerating {num_frames} rotation frames...")

# Write to splash_frames.py
with open("src/splash_frames.py", "w") as f:
    f.write("# splash_frames.py\n")
    f.write("# Pre-rendered kaleidoscope rotation frames\n")
    f.write(f"# Generated with {num_frames} frames, {degrees_per_frame}° per frame\n\n")
    f.write("SPLASH_FRAMES = [\n")

    for frame_num in range(num_frames):
        rotation_angle = frame_num * degrees_per_frame

        print(
            f"Generating frame {frame_num + 1}/{num_frames} at {rotation_angle:.1f}°..."
        )

        # Rotate the kaleidoscope
        rotated = rotate_bitmap_in_place(base_kaleidoscope, rotation_angle)

        # Convert to string bitmap
        bitmap_str = '"""'
        for row in rotated:
            bitmap_str += "\n" + "".join(str(int(pixel)) for pixel in row)
        bitmap_str += '\n"""'

        f.write(f"    # Frame {frame_num + 1}/{num_frames} - {rotation_angle:.1f}°\n")
        f.write(f"    {bitmap_str},\n")

    f.write("]\n")

print(f"\n✓ Generated splash_frames.py with {num_frames} frames!")
print(f"✓ Estimated file size: ~{num_frames * 64 * 64 * 2} bytes")
print(f"✓ Animation duration: {num_frames * 0.05:.1f}s at 20 FPS")
