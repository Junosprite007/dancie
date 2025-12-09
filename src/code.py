# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# code.py
"""Main entry point for Dancie rhythm game."""

import gc

import adafruit_displayio_ssd1306
import board
import busio
import displayio
import i2cdisplaybus
from digitalio import DigitalInOut, Direction, Pull
from game_loop import run_game

# Clear screen before starting game
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    diagnose_multiplexer,
    test_multiplexer_switches,
    test_single_channel,
)
from show_switch_number import display_active_switches

# Run splash screen (loops until button pressed)
from splash_screen import run_splash_screen

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

# Setup button (using same pin as your example: D7)
button = DigitalInOut(board.D7)
button.direction = Direction.INPUT
button.pull = Pull.UP

print("=== DANCIE ===")
print(f"Free memory: {gc.mem_free()} bytes")
print("Button configured on D7")


# run_splash_screen(display, bitmap, button)


display.auto_refresh = False
clear_displayio_bitmap(bitmap)
display.refresh()

gc.collect()
print(f"Free memory after splash: {gc.mem_free()} bytes")

# Start game
# run_game(display, bitmap)

# Test multiplexer buttons
# display_active_switches(display, main_group)

# test_multiplexer_switches()

diagnose_multiplexer()

# test_single_channel(0)
