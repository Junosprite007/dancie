# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
# code.py
import gc
import math
import time

import adafruit_displayio_ssd1306
import board
import busio
import displayio
import i2cdisplaybus
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    convert_bitmap_str_to_np,
    draw_collision_points,
    draw_numpy_to_displayio_bitmap,
)
from splash_frames import SPLASH_FRAMES

# Setup display
displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Create displayio bitmap and palette
bitmap = displayio.Bitmap(128, 64, 2)
palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xFFFFFF

# Setup display group
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group = displayio.Group()
main_group.append(tile_grid)
display.root_group = main_group

print(f"Free memory: {gc.mem_free()} bytes")
print(f"Splash frames available: {len(SPLASH_FRAMES)}")

# SPLASH SCREEN ANIMATION - Convert frames on-the-fly
print("\nStarting splash screen animation...")
display_center = (64, 32)

# Play animation (3 complete cycles)
for cycle in range(3):
    print(f"  Cycle {cycle + 1}/3")
    for frame_idx, frame_str in enumerate(SPLASH_FRAMES):
        # Convert frame on-the-fly (only one in memory at a time)
        frame_np = convert_bitmap_str_to_np(frame_str)

        display.auto_refresh = False
        clear_displayio_bitmap(bitmap)
        draw_numpy_to_displayio_bitmap(frame_np, bitmap, origin=display_center)
        display.refresh()

        # Free the frame immediately
        del frame_np
        gc.collect()

        time.sleep(0.05)  # 20 FPS

print("✓ Splash complete!")
gc.collect()

# Calculate collision centers for gameplay
base_angle = 22.5
num_copies = 8
collision_centers = []

for i in range(num_copies):
    angle = base_angle + (360.0 / num_copies * i)
    angle_rad = math.radians(angle)
    radius = 24

    piece_center_x = 64 + int(radius * math.sin(angle_rad))
    piece_center_y = 32 - int(radius * math.cos(angle_rad))

    collision_centers.append((piece_center_x, piece_center_y))

print(f"Collision points: {collision_centers}")

# Draw static gameplay kaleidoscope (first frame)
display_center = (64, 32)
static_frame = convert_bitmap_str_to_np(SPLASH_FRAMES[0])
display.auto_refresh = False
clear_displayio_bitmap(bitmap)
draw_numpy_to_displayio_bitmap(static_frame, bitmap, origin=display_center)

# DEBUG: Draw collision points (comment out for production)
draw_collision_points(bitmap, collision_centers, size=4, color=1)

display.refresh()

print("\n✓ Game ready!")
print("✓ Static kaleidoscope displayed")
print("✓ Collision points visualized (DEBUG MODE)")
print(f"✓ Free memory: {gc.mem_free()} bytes")

# Game loop (placeholder)
while True:
    pass
