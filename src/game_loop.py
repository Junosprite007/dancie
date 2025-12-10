# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_loop.py
"""Main game loop and logic."""

import gc
import random
import time

from arrow_sprites import ARROWS
from game_config import (
    DEBUG_HITBOX_SIZE,
    DEBUG_SHOW_HITBOXES,
    DISPLAY_CENTER,
    FRAME_DELAY,
    GESTURE_PENALTY_HEALTH,
    HIT_TOLERANCE,
    KALEIDOSCOPE_BASE_ANGLE,
    KALEIDOSCOPE_NUM_COPIES,
    KALEIDOSCOPE_RADIUS,
    NUM_LEVELS,
    SCORE_GESTURE,
    SCORE_WRONG_BUTTON,
    SHAPE_SPAWN_DELAY,
    get_gesture_time,
)
from game_objects import SlidingShape, calculate_collision_centers, determine_spawn_side
from game_over_screen import (
    show_countdown,
    show_game_over_screen,
    show_level_complete_screen,
    show_victory_screen,
)
from game_state import GameState
from helpers_esp32c3 import (
    clear_displayio_bitmap,
    convert_bitmap_str_to_np,
    draw_collision_points,
    draw_numpy_to_displayio_bitmap,
)
from splash_frames import SPLASH_FRAMES


def run_game(display, bitmap, inputs, neopixels):
    """
    Main game loop.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        The display object.
    bitmap : displayio.Bitmap
        The bitmap to draw on.
    inputs : dict
        Dictionary with keys: 'mux', 'accel', 'button' for input handlers.
    neopixels : NeoPixelManager
        NeoPixel manager for health display.
    """
    print("\n=== Starting Dancie ===")

    # Load static kaleidoscope background
    static_kaleidoscope = convert_bitmap_str_to_np(SPLASH_FRAMES[0])

    # Calculate collision centers for all 8 pieces
    collision_centers = calculate_collision_centers(
        KALEIDOSCOPE_BASE_ANGLE,
        KALEIDOSCOPE_NUM_COPIES,
        KALEIDOSCOPE_RADIUS,
        DISPLAY_CENTER,
    )

    # Load piece bitmap for sliding shapes
    piece_bitmap = convert_bitmap_str_to_np("""
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

    # Initialize game state
    game_state = GameState(starting_level=1)

    # Extract input handlers
    mux = inputs["mux"]
    accel = inputs["accel"]
    button = inputs["button"]

    # Main game loop - runs until player quits
    while True:
        # Start level
        print(f"\n=== Level {game_state.level} ===")
        print(f"Shapes required: {game_state.shapes_required}")
        print(f"Gestures required: {game_state.gestures_required}")
        print(f"Shape speed: {game_state.current_speed:.2f} px/frame")

        # Show countdown before level starts
        show_countdown(display, bitmap, count_from=3)

        # Reset health LEDs for new level
        neopixels.set_health(game_state.health)

        # Level loop - run shapes and gestures
        run_level(
            display,
            bitmap,
            game_state,
            inputs,
            neopixels,
            static_kaleidoscope,
            piece_bitmap,
            collision_centers,
        )

        # Check if game over
        if game_state.is_game_over:
            # Show game over screen
            show_game_over_screen(display, bitmap, button)

            # Reset game state
            game_state.reset_game()
            neopixels.set_health(game_state.health)
            continue

        # Check if level complete
        if game_state.level_complete:
            # Play victory animation on LEDs
            neopixels.victory_animation(duration=2.0)

            # Check if all levels complete
            if game_state.level >= NUM_LEVELS:
                # Show final victory screen
                show_victory_screen(display, bitmap, button, game_state.score)

                # Reset to level 1
                game_state.reset_game()
                neopixels.set_health(game_state.health)
            else:
                # Show level complete screen
                show_level_complete_screen(
                    display, bitmap, button, game_state.level, game_state.score
                )

                # Advance to next level
                game_state.advance_level()


def run_level(
    display,
    bitmap,
    game_state,
    inputs,
    neopixels,
    static_kaleidoscope,
    piece_bitmap,
    collision_centers,
):
    """
    Run a single level with shapes and gestures.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        Display object.
    bitmap : displayio.Bitmap
        Bitmap to draw on.
    game_state : GameState
        Current game state.
    inputs : dict
        Input handlers.
    neopixels : NeoPixelManager
        NeoPixel manager.
    static_kaleidoscope : np.ndarray
        Background kaleidoscope bitmap.
    piece_bitmap : np.ndarray
        Shape bitmap for sliding pieces.
    collision_centers : list
        List of target centers for each map piece.
    """
    mux = inputs["mux"]
    accel = inputs["accel"]
    button = inputs["button"]

    # Active sliding shape
    current_shape = None
    shape_spawn_timer = 0

    # Game loop timing
    last_frame_time = time.monotonic()

    # Level runs until complete or game over
    while not game_state.level_complete and not game_state.is_game_over:
        current_time = time.monotonic()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        # Check if it's time to show gesture or spawn shape
        if current_shape is None:
            shape_spawn_timer += delta_time

            if shape_spawn_timer >= SHAPE_SPAWN_DELAY:
                shape_spawn_timer = 0

                # Decide: gesture or shape?
                if game_state.should_show_gesture():
                    # Show gesture prompt
                    run_gesture_prompt(
                        display,
                        bitmap,
                        game_state,
                        accel,
                        neopixels,
                        static_kaleidoscope,
                    )
                else:
                    # Spawn new shape (if we still need shapes)
                    if game_state.shapes_completed < game_state.shapes_required:
                        current_shape = spawn_random_shape(
                            piece_bitmap, collision_centers, game_state.current_speed
                        )

        # Update and render current shape
        if current_shape is not None:
            display.auto_refresh = False
            clear_displayio_bitmap(bitmap)

            # Draw background kaleidoscope
            draw_numpy_to_displayio_bitmap(
                static_kaleidoscope, bitmap, origin=DISPLAY_CENTER
            )

            # Update shape position
            current_shape.update()

            # Draw shape
            draw_numpy_to_displayio_bitmap(
                current_shape.bitmap, bitmap, origin=current_shape.get_position()
            )

            # Debug: draw hitboxes
            if DEBUG_SHOW_HITBOXES:
                draw_collision_points(
                    bitmap, collision_centers, size=DEBUG_HITBOX_SIZE, color=1
                )
                draw_collision_points(
                    bitmap,
                    [current_shape.get_position()],
                    size=DEBUG_HITBOX_SIZE,
                    color=1,
                )

            # Check for button press
            pressed_buttons = mux.get_pressed_buttons()
            if pressed_buttons:
                button_pressed = pressed_buttons[0]  # Take first button
                handle_button_press(
                    button_pressed, current_shape, game_state, neopixels
                )

            # Check if shape passed target without being hit
            if current_shape.has_passed_target() and not current_shape.was_hit:
                current_shape.mark_as_missed()
                game_state.lose_health(1)
                neopixels.set_health(game_state.health)
                print(f"Missed shape! Health: {game_state.health}")

            # Remove shape if inactive
            if not current_shape.active:
                game_state.complete_shape()
                print(
                    f"Shape {game_state.shapes_completed}/{game_state.shapes_required} complete"
                )
                current_shape = None

            display.refresh()

        # Frame rate control
        time.sleep(FRAME_DELAY)

        # Garbage collection
        if game_state.shapes_completed % 10 == 0:
            gc.collect()


def spawn_random_shape(piece_bitmap, collision_centers, speed):
    """
    Spawn a random sliding shape targeting one of the 8 map pieces.

    Parameters
    ----------
    piece_bitmap : np.ndarray
        Shape bitmap.
    collision_centers : list
        List of target centers.
    speed : float
        Movement speed.

    Returns
    -------
    SlidingShape
        New sliding shape.
    """
    # Pick random target (0-7)
    target_index = random.randint(0, 7)
    target_center = collision_centers[target_index]

    # Determine spawn side based on target position
    spawn_side = determine_spawn_side(target_center, DISPLAY_CENTER)

    # Create shape
    shape = SlidingShape(
        piece_bitmap,
        target_center,
        start_side=spawn_side,
        speed=speed,
        target_index=target_index,
    )

    print(f"Spawned shape targeting piece {target_index + 1} from {spawn_side}")
    return shape


def handle_button_press(button_number, current_shape, game_state, neopixels):
    """
    Handle button press during shape movement.

    Parameters
    ----------
    button_number : int
        Button pressed (1-8).
    current_shape : SlidingShape
        Current active shape.
    game_state : GameState
        Game state.
    neopixels : NeoPixelManager
        NeoPixel manager.
    """
    # Check if correct button
    if button_number == current_shape.button_number:
        # Correct button! Calculate score based on alignment
        score = current_shape.calculate_score()
        distance = current_shape.get_distance_from_target()

        game_state.add_score(score)
        current_shape.mark_as_hit(score)

        print(f"HIT! Button {button_number}, Distance: {distance}px, Score: {score:+d}")
        print(f"Total score: {game_state.score}")
    else:
        # Wrong button pressed
        game_state.add_score(SCORE_WRONG_BUTTON)
        print(
            f"Wrong button! Pressed {button_number}, needed {current_shape.button_number}"
        )
        print(f"Score: {SCORE_WRONG_BUTTON:+d}, Total: {game_state.score}")


def run_gesture_prompt(
    display, bitmap, game_state, accel, neopixels, static_kaleidoscope
):
    """
    Show gesture prompt and wait for user to tilt accelerometer.

    Parameters
    ----------
    display : adafruit_displayio_ssd1306.SSD1306
        Display object.
    bitmap : displayio.Bitmap
        Bitmap to draw on.
    game_state : GameState
        Game state.
    accel : AccelerometerInput
        Accelerometer input handler.
    neopixels : NeoPixelManager
        NeoPixel manager.
    static_kaleidoscope : np.ndarray
        Background kaleidoscope.
    """
    # Choose random direction
    directions = ["up", "down", "left", "right"]
    required_direction = random.choice(directions)

    # Get arrow bitmap
    arrow_bitmap = convert_bitmap_str_to_np(ARROWS[required_direction])

    # Calculate gesture timeout for this level
    gesture_timeout = get_gesture_time(game_state.level)

    print(
        f"Gesture prompt: Tilt {required_direction.upper()} within {gesture_timeout:.1f}s"
    )

    # Show arrow on screen
    display.auto_refresh = False
    clear_displayio_bitmap(bitmap)

    # Draw background
    draw_numpy_to_displayio_bitmap(static_kaleidoscope, bitmap, origin=DISPLAY_CENTER)

    # Draw arrow in center
    draw_numpy_to_displayio_bitmap(arrow_bitmap, bitmap, origin=DISPLAY_CENTER)

    display.refresh()

    # Wait for tilt
    detected_direction = accel.wait_for_tilt(timeout=gesture_timeout)

    # Check result
    if detected_direction == required_direction:
        # Correct!
        game_state.add_score(SCORE_GESTURE)
        game_state.complete_gesture()
        print(f"Gesture SUCCESS! +{SCORE_GESTURE} points")
        print(
            f"Gestures: {game_state.gestures_completed}/{game_state.gestures_required}"
        )
    else:
        # Wrong or timeout
        game_state.lose_health(GESTURE_PENALTY_HEALTH)
        game_state.complete_gesture()  # Still counts as completed (just with penalty)
        neopixels.set_health(game_state.health)

        if detected_direction is None:
            print(f"Gesture TIMEOUT! Lost {GESTURE_PENALTY_HEALTH} health")
        else:
            print(
                f"Gesture WRONG! Tilted {detected_direction}, needed {required_direction}"
            )
            print(f"Lost {GESTURE_PENALTY_HEALTH} health")

        print(f"Health: {game_state.health}")
        print(
            f"Gestures: {game_state.gestures_completed}/{game_state.gestures_required}"
        )

    # Brief pause before continuing
    time.sleep(0.5)
