# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# code.py
"""Main entry point for Dancie rhythm game."""

import gc

import adafruit_displayio_ssd1306
import board
import busio
import displayio
import i2cdisplaybus

# Setup display
displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Create displayio bitmap and palette
bitmap = displayio.Bitmap(128, 64, 2)
palette = displayio.Palette(2)
palette[0] = 0x000000  # Black
palette[1] = 0xFFFFFF  # White

# Setup display group
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group = displayio.Group()
main_group.append(tile_grid)
display.root_group = main_group

print("=== DANCIE ===")
print(f"Free memory: {gc.mem_free()} bytes")

# TODO: Add splash screen animation here
# from splash_animation import run_splash_screen
# run_splash_screen(display, bitmap)

# Start game
from game_loop import run_game

run_game(display, bitmap)
