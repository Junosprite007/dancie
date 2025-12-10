# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# code.py
"""Main entry point for Dancie rhythm game."""

import gc

import adafruit_displayio_ssd1306
import board
import busio
import displayio
import i2cdisplaybus
from game_loop import run_game
from input_handler import AccelerometerInput, MultiplexerInput, RotaryEncoderButton
from neopixel_manager import NeoPixelManager
from splash_screen import run_splash_screen

print("\n" + "=" * 50)
print("   DANCIE - Dance Rhythm Game")
print("=" * 50)
print(f"Free memory at startup: {gc.mem_free()} bytes\n")

# ============================================================================
# HARDWARE INITIALIZATION
# ============================================================================

print("Initializing hardware...")

# --- Display Setup ---
print("  • Setting up OLED display...")
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

print("    ✓ Display ready (128x64 OLED)")

# --- NeoPixel Setup ---
print("  • Setting up NeoPixels...")
neopixels = NeoPixelManager(pin=board.D3)
print("    ✓ NeoPixels ready (6 LEDs - 1 power + 5 health)")

# --- Input Setup ---
print("  • Setting up input devices...")

# Multiplexer (8 limit switches)
mux = MultiplexerInput()
print("    ✓ Multiplexer ready (8 limit switches)")

# Accelerometer
accel = AccelerometerInput(i2c)
print("    ✓ Accelerometer ready (ADXL345)")

# Rotary encoder button
button = RotaryEncoderButton(pin=board.D7)
print("    ✓ Rotary encoder button ready (D7)")

# Package inputs into dictionary
inputs = {
    "mux": mux,
    "accel": accel,
    "button": button,
}

print("\n✓ All hardware initialized successfully!")
print(f"Free memory after init: {gc.mem_free()} bytes\n")

# ============================================================================
# SPLASH SCREEN
# ============================================================================

print("Starting splash screen...")
print("Press rotary encoder button to start game!\n")

# Run splash screen (loops until button pressed)
run_splash_screen(display, bitmap, button)

# Clear screen after splash
display.auto_refresh = False
from helpers_esp32c3 import clear_displayio_bitmap

clear_displayio_bitmap(bitmap)
display.refresh()

gc.collect()
print(f"Free memory after splash: {gc.mem_free()} bytes\n")

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

print("=" * 50)
print("   Starting Game!")
print("=" * 50)

try:
    # Run the game (infinite loop with level progression and restarts)
    run_game(display, bitmap, inputs, neopixels)

except KeyboardInterrupt:
    # Clean shutdown on Ctrl+C
    print("\n\nGame interrupted by user")

except Exception as e:
    # Catch any unexpected errors and display them
    print("\n\n!!! GAME ERROR !!!")
    print(f"Error: {e}")
    import traceback

    traceback.print_exception(type(e), e, e.__traceback__)

finally:
    # Cleanup
    print("\nCleaning up...")
    neopixels.turn_off_all()
    mux.deinit()
    button.deinit()
    print("Goodbye!")
