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

# Pin definitions
PIN_ROTARY_BUTTON = "D7"  # Rotary encoder button
PIN_NEOPIXEL = "D3"  # NeoPixel data pin
PIN_MUX_S0 = "D8"  # Multiplexer select 0
PIN_MUX_S1 = "D9"  # Multiplexer select 1
PIN_MUX_S2 = "D10"  # Multiplexer select 2
PIN_MUX_SIG = "A2"  # Multiplexer analog signal

# NeoPixel settings
NUM_NEOPIXELS = 6
NEOPIXEL_BRIGHTNESS = 0.3
COLOR_POWER_ON = (0, 255, 0)  # Green for power indicator (first LED)
COLOR_HEALTH_FULL = (128, 0, 128)  # Purple for health LEDs
COLOR_HEALTH_OFF = (0, 0, 0)  # Off

# Gameplay settings
INITIAL_HEALTH = 5  # 5 health LEDs
SLIDING_SHAPE_SPEED = 2  # Pixels per frame
HIT_TOLERANCE = 5  # Pixels of tolerance for hit detection
SHAPE_SPAWN_DELAY = 0.5  # Seconds between shapes spawning

# Scoring settings
SCORE_PERFECT = 5  # 0 pixels off
SCORE_GREAT = 4  # 1-2 pixels off
SCORE_GOOD = 3  # 3-4 pixels off
SCORE_OK = 2  # 5-19 pixels off
SCORE_POOR = -2  # 20+ pixels off
SCORE_WRONG_BUTTON = -1  # Pressed wrong button
SCORE_GESTURE = 5  # Correct accelerometer gesture
GESTURE_PENALTY_HEALTH = 1  # Health lost for wrong/missed gesture

# Level settings
NUM_LEVELS = 10
SHAPES_PER_LEVEL_MULTIPLIER = 14  # (14 shapes + 2 gestures) * level
GESTURES_PER_LEVEL_MULTIPLIER = 2
GESTURE_INTERVAL = 7  # Show gesture after every 7th shape

# Timing per level (level 1 -> level 10)
# Speed increases and gesture time decreases linearly
BASE_SHAPE_SPEED = 1.5  # pixels/frame at level 1
MAX_SHAPE_SPEED = 4.0  # pixels/frame at level 10
BASE_GESTURE_TIME = 2.0  # seconds at level 1
MIN_GESTURE_TIME = 0.8  # seconds at level 10


def get_shape_speed(level):
    """Calculate shape speed for given level (linear progression)."""
    if level < 1:
        level = 1
    if level > NUM_LEVELS:
        level = NUM_LEVELS

    speed_range = MAX_SHAPE_SPEED - BASE_SHAPE_SPEED
    speed_per_level = speed_range / (NUM_LEVELS - 1)
    return BASE_SHAPE_SPEED + (speed_per_level * (level - 1))


def get_gesture_time(level):
    """Calculate gesture reaction time for given level (linear progression)."""
    if level < 1:
        level = 1
    if level > NUM_LEVELS:
        level = NUM_LEVELS

    time_range = BASE_GESTURE_TIME - MIN_GESTURE_TIME
    time_per_level = time_range / (NUM_LEVELS - 1)
    return BASE_GESTURE_TIME - (time_per_level * (level - 1))


def get_level_requirements(level):
    """
    Get number of shapes and gestures for a given level.

    Returns
    -------
    tuple
        (num_shapes, num_gestures)
    """
    num_shapes = SHAPES_PER_LEVEL_MULTIPLIER * level
    num_gestures = GESTURES_PER_LEVEL_MULTIPLIER * level
    return (num_shapes, num_gestures)


# Multiplexer settings
MUX_VOLTAGE_THRESHOLD = 30000  # ADC threshold (1.5V)
MUX_DEBOUNCE_SAMPLES = 5  # Number of samples for debouncing
MUX_SETTLE_TIME = 0.001  # Seconds for mux to settle

# Accelerometer settings
ACCEL_TILT_THRESHOLD = 5.0  # m/s² threshold for detecting tilt
# At rest, Z-axis should read ~9.8 m/s² (gravity)
# X-axis tilt left: X < -threshold
# X-axis tilt right: X > threshold
# Y-axis tilt forward: Y > threshold
# Y-axis tilt back: Y < -threshold

# Frame rate
TARGET_FPS = 20
FRAME_DELAY = 1.0 / TARGET_FPS  # 0.05 seconds

# Debug mode
DEBUG_SHOW_HITBOXES = False  # Set to True to see collision boxes
DEBUG_HITBOX_SIZE = 4
DEBUG_PRINT_INPUTS = False  # Set to True to print input events
