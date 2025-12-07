# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_config.py
"""Game configuration and constants."""

# Display settings
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_CENTER = (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)

# Kaleidoscope settings
KALEIDOSCOPE_BASE_ANGLE = 22.5
KALEIDOSCOPE_NUM_COPIES = 8
KALEIDOSCOPE_RADIUS = 24

# Gameplay settings
SLIDING_SHAPE_SPEED = 2  # Pixels per frame
HIT_TOLERANCE = 5  # Pixels of tolerance for hit detection
SHAPE_SPAWN_DELAY = 2.0  # Seconds between shapes

# Frame rate
TARGET_FPS = 20
FRAME_DELAY = 1.0 / TARGET_FPS  # 0.05 seconds

# Debug mode
DEBUG_SHOW_HITBOXES = True
DEBUG_HITBOX_SIZE = 4
