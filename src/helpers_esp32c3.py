# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
# helpers_esp32c3.py
"""Helper functions optimized for ESP32-C3 with CircuitPython and displayio."""

import math

import ulab.numpy as np


def convert_bitmap_str_to_np(bm: str):
    """Convert string bitmap to ulab numpy array."""
    lines = [line.strip() for line in bm.strip().splitlines() if line.strip()]
    arr = [[int(char) for char in line] for line in lines]
    return np.array(arr, dtype=np.uint8)


def generate_bitmap_with_anchor_offset(bitmap, radius=0.0, draw_anchor=False):
    """Generate bitmap with anchor point offset (ulab compatible)."""
    rows, cols = bitmap.shape
    actual_center = (rows - 1) / 2.0
    distance_from_top_to_center = actual_center
    distance_from_top_to_new_anchor = distance_from_top_to_center + radius
    pixels_above_new_anchor = int(math.ceil(distance_from_top_to_new_anchor))
    pixels_below_new_anchor = pixels_above_new_anchor
    new_rows = pixels_above_new_anchor + 1 + pixels_below_new_anchor

    new_bitmap = np.zeros((new_rows, cols), dtype=bitmap.dtype)
    new_bitmap[0:rows, :] = bitmap

    if draw_anchor:
        anchor_row = pixels_above_new_anchor
        anchor_col = cols // 2
        if 0 <= anchor_row < new_rows and 0 <= anchor_col < cols:
            new_bitmap[anchor_row, anchor_col] = 1

    return new_bitmap


def rotate_bitmap_in_place(bitmap, degrees, trim_blank_pixels=False):
    """Rotate bitmap around its center (ulab compatible)."""
    rows, cols = bitmap.shape
    max_dim = max(rows, cols)
    square_bitmap = np.zeros((max_dim, max_dim), dtype=bitmap.dtype)

    row_offset = (max_dim - rows) // 2
    col_offset = (max_dim - cols) // 2
    square_bitmap[row_offset : row_offset + rows, col_offset : col_offset + cols] = (
        bitmap
    )

    angle_rad = math.radians(degrees)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    center = (max_dim - 1) / 2.0

    rotated_points = []
    for y in range(max_dim):
        for x in range(max_dim):
            if square_bitmap[y, x] == 0:
                continue
            rel_x = x - center
            rel_y = y - center
            rot_x = rel_x * cos_a - rel_y * sin_a
            rot_y = rel_x * sin_a + rel_y * cos_a
            rotated_points.append((rot_x, rot_y))

    if not rotated_points:
        return square_bitmap

    if not trim_blank_pixels:
        xs, ys = zip(*rotated_points)
        extent = max(
            abs(math.floor(min(xs))),
            abs(math.ceil(max(xs))),
            abs(math.floor(min(ys))),
            abs(math.ceil(max(ys))),
        )
        new_dim = max(2 * extent + 1, max_dim)
        rotated_bitmap = np.zeros((new_dim, new_dim), dtype=bitmap.dtype)
        new_center = (new_dim - 1) / 2.0

        for rot_x, rot_y in rotated_points:
            px = int(round(rot_x + new_center))
            py = int(round(rot_y + new_center))
            if 0 <= px < new_dim and 0 <= py < new_dim:
                rotated_bitmap[py, px] = 1

    return rotated_bitmap


def clear_displayio_bitmap(displayio_bitmap):
    """
    Efficiently clear a displayio.Bitmap by setting all pixels to 0.

    This is separated so it can be called once per frame in the main loop
    instead of inside draw_rotated_copies_esp32().
    """
    for x in range(displayio_bitmap.width):
        for y in range(displayio_bitmap.height):
            displayio_bitmap[x, y] = 0


def draw_numpy_to_displayio_bitmap(np_bitmap, displayio_bitmap, origin=(0, 0)):
    """
    Copy numpy array pixels into displayio.Bitmap.

    This is the KEY function that bridges numpy arrays to CircuitPython display.
    """
    origin_x, origin_y = origin
    rows, cols = np_bitmap.shape

    # Calculate center offset
    cx = cols // 2
    cy = rows // 2
    start_x = origin_x - cx
    start_y = origin_y - cy

    # Copy pixels (displayio.Bitmap uses [x, y] indexing!)
    for row in range(rows):
        for col in range(cols):
            if np_bitmap[row, col] > 0:
                x = start_x + col
                y = start_y + row
                # Bounds checking
                if 0 <= x < displayio_bitmap.width and 0 <= y < displayio_bitmap.height:
                    displayio_bitmap[x, y] = 1


def draw_rotated_copies_esp32(
    displayio_bitmap,
    np_bitmap,
    num_copies=8,
    start_angle=0.0,
    origin=None,
    clear_first=False,
):
    """
    Draw multiple rotated copies onto a displayio.Bitmap.
    ESP32-specific version.

    Parameters
    ----------
    displayio_bitmap : displayio.Bitmap
        The bitmap to draw onto.
    np_bitmap : np.ndarray
        The numpy array bitmap to rotate and draw.
    num_copies : int
        Number of rotated copies (default 8 for octagonal symmetry).
    start_angle : float
        Starting angle in degrees for the first copy.
    origin : tuple or None
        (x, y) center point. If None, uses center of display.
    clear_first : bool
        If True, clears the bitmap before drawing. For smooth animation,
        set to False and clear manually in the main loop BEFORE calling this.
    """
    if origin is None:
        origin = (displayio_bitmap.width // 2, displayio_bitmap.height // 2)

    # Optional clear - but you should clear ONCE in main loop instead
    if clear_first:
        clear_displayio_bitmap(displayio_bitmap)

    angle_step = 360.0 / num_copies

    # Draw all copies
    for i in range(num_copies):
        angle = start_angle + (angle_step * i)
        rotated = rotate_bitmap_in_place(np_bitmap, angle)
        draw_numpy_to_displayio_bitmap(rotated, displayio_bitmap, origin)


def draw_collision_points(displayio_bitmap, centers, size=3, color=1, style="box"):
    """
    Draw collision points for debugging hit detection zones.

    Parameters
    ----------
    displayio_bitmap : displayio.Bitmap
        The bitmap to draw on.
    centers : list of tuples
        List of (x, y) center coordinates.
    size : int, optional
        Size of the markers (default is 3).
    color : int, optional
        Color value to draw (1 for white, 0 for black).
    style : str, optional
        Marker style: "box" (hollow square), "cross" (crosshair), or "dot" (single pixel).
        Default is "box" for development.
    """
    for cx, cy in centers:
        if style == "box":
            # Draw hollow square outline
            for offset in range(-size, size + 1):
                # Top and bottom edges
                if 0 <= cx + offset < displayio_bitmap.width:
                    if 0 <= cy - size < displayio_bitmap.height:
                        displayio_bitmap[cx + offset, cy - size] = color
                    if 0 <= cy + size < displayio_bitmap.height:
                        displayio_bitmap[cx + offset, cy + size] = color

                # Left and right edges
                if 0 <= cy + offset < displayio_bitmap.height:
                    if 0 <= cx - size < displayio_bitmap.width:
                        displayio_bitmap[cx - size, cy + offset] = color
                    if 0 <= cx + size < displayio_bitmap.width:
                        displayio_bitmap[cx + size, cy + offset] = color

        elif style == "cross":
            # Draw crosshair
            for x in range(cx - size, cx + size + 1):
                if (
                    0 <= x < displayio_bitmap.width
                    and 0 <= cy < displayio_bitmap.height
                ):
                    displayio_bitmap[x, cy] = color

            for y in range(cy - size, cy + size + 1):
                if (
                    0 <= cx < displayio_bitmap.width
                    and 0 <= y < displayio_bitmap.height
                ):
                    displayio_bitmap[cx, y] = color

        elif style == "dot":
            # Draw single pixel
            if 0 <= cx < displayio_bitmap.width and 0 <= cy < displayio_bitmap.height:
                displayio_bitmap[cx, cy] = color


def i2c_bus_scanner():
    import adafruit_displayio_ssd1306
    import board
    import busio
    import displayio
    import i2cdisplaybus

    # Setup display with I2C scanning
    displayio.release_displays()

    print("Scanning I2C bus...")
    i2c = busio.I2C(board.SCL, board.SDA)

    # Wait for I2C to initialize
    import time

    time.sleep(0.5)

    # Lock the I2C bus while scanning
    while not i2c.try_lock():
        pass

    try:
        print(
            "I2C addresses found:", [hex(device_address) for device_address in i2c.scan()]
        )
    except Exception as e:
        print(f"I2C scan error: {e}")
    finally:
        i2c.unlock()

    # Now try to connect to display
    try:
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
        print("Display connected successfully!")
    except ValueError as e:
        print(f"Display connection failed: {e}")
        print("Check your wiring!")
