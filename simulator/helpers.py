# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5, ChatGPT 4.1, and Gemini 3.0
import math
import sys

# Detect environment early
IS_CIRCUITPYTHON = sys.implementation.name == "circuitpython"

if IS_CIRCUITPYTHON:
    import ulab.numpy as np
else:
    import numpy as np
    from emulator.ssd1306 import SSD1306Emulator


def get_np_bitmap_center(bitmap: np.ndarray) -> tuple:
    if not hasattr(bitmap, "shape") or len(bitmap.shape) != 2:
        raise ValueError("bitmap must be a 2D NumPy array")
    rows, cols = bitmap.shape
    center_col = cols // 2
    center_row = rows // 2
    return (center_col, center_row)


def draw_rotation_center(
    display: SSD1306Emulator,
    bitmap: np.ndarray,
    origin: tuple[int, int],
    color: int = 1,
) -> None:
    rows, cols = bitmap.shape
    center_col = cols // 2
    center_row = rows // 2
    display.pixel(origin[0] + center_col, origin[1] + center_row, color)


def draw_bitmap(
    display: SSD1306Emulator,
    bitmap: np.ndarray,
    origin: tuple[int, int] = (0, 0),
    color: int = 1,
    draw_blank_pixels: bool = False,
) -> None:
    """
    Draw a bitmap on the display, aligning the bitmap's center point with the
    specified origin (screen position).

    Parameters
    ----------
    display : SSD1306Emulator
        The display object to draw the bitmap on.
    bitmap : np.ndarray
        The 2D array representing the monochrome bitmap to draw. Active pixels
        should have a value > 0.
    origin : tuple[int, int], optional
        The (x, y) screen coordinates where the bitmap's center point should be
        aligned (default is (0, 0)).
    color : int, optional
        The color value to use when drawing pixels (default is 1 for "on").
    draw_blank_pixels : bool, optional
        If True, draws blank pixels (value 0) as well, turning them off on the
        display. If False, skips blank pixels, allowing multiple bitmaps to
        overlay without erasing each other (default is False).

    Returns
    -------
    None

    Notes
    -----
    - The bitmap's center point is calculated as ((cols-1)/2, (rows-1)/2) to
      handle both even and odd dimensions correctly.
    - Each active pixel in the bitmap is translated so that the bitmap's center
      aligns with the specified origin on the screen.
    - Pixels are rounded to integer coordinates for display on the pixel grid.

    Examples
    --------
    To draw a bitmap centered on the screen:
    >>> center = (display.width // 2, display.height // 2)
    >>> draw_bitmap(display, my_bitmap, origin=center)

    To draw multiple overlapping bitmaps without erasing:
    >>> draw_bitmap(display, bitmap1, origin=(32, 32))
    >>> draw_bitmap(display, bitmap2, origin=(32, 32))  # Won't erase bitmap1
    """
    origin_x, origin_y = origin
    rows, cols = bitmap.shape

    # Calculate the bitmap's center using INTEGER division
    # This ensures no floating point rounding issues
    cx = cols // 2
    cy = rows // 2

    # Adjust the starting position so the bitmap's center aligns with origin
    start_x = origin_x - cx
    start_y = origin_y - cy

    # Draw each pixel - all integer math, no rounding needed
    for row in range(rows):
        for col in range(cols):
            if draw_blank_pixels or bitmap[row, col] > 0:
                pixel_color = color if bitmap[row, col] > 0 else 0
                display.pixel(start_x + col, start_y + row, pixel_color)


def generate_bitmap_with_anchor_offset(
    bitmap: np.ndarray,
    radius: float = 0.0,
    draw_anchor: bool = False,
) -> np.array:
    """
    Generate a new bitmap that adds anchor point information. This function assumes
    the bitmap image is oriented right-side up. Increasing the radius will move
    the virtual anchor point directly downwards, mirroring the image's
    dimensions (not the actual image) on the underside of the virtual anchor
    point. See deeper explanation after the function info.

    Parameters
    ----------
    bitmap : np.ndarray
        The 2D array representing the monochrome bitmap to add an anchor point
        to.
    radius : float
        The amount of pixels below the center of 'bitmap' to place the new anchor
        point. As you increase the radius, the new generated bitmap image will grow
        exponentially.
    draw_anchor: bool
        Whether or not to draw the anchor point on the new bitmap image.

    Explanation
    ----------
    The 'virtual' anchor point is simply the other end of the radius. The radius
    always extends from the center of the provide bitmap image. This means, with
    a radius of zero (0), the returned anchor point will be in the center of the
    new bitmap image (it's actually be the approximate center, since we're
    dealing with physical pixels on a screen); with a radius of 10, for example,
    the new anchor point will be place 10 pixels directly below the center of
    the original bitmap image. The idea is to alway keep the anchor point in the
    center of the bitmap, which means, when the new bitmap is generated, which
    will count the amount of pixels above the new anchor point, all the way to
    the top of the original bitmap's uppermost boundary, and create empty pixels
    below matching the amount that were counted above (see visualization below)

    Visualization
    ----------
    Let's say we have a 3x3 bitmap, where x is its anchor point:

    o  o  o
    o  x  o
    o  o  o

    Now let's move the anchor point down by 3 pixels, meaning we set the radius to 3:

    o  o  o
    o  o  o - ⌄
    o  o  o   1
       |      2
       x      3

    This function will then generate the new bitmap base on this information:

    o  o  o
    o  o  o
    o  o  o
    o  o  o
    o  x  o
    o  o  o
    o  o  o
    o  o  o
    o  o  o

    Notice how the new bitmap image has grown exponentially, but only in the y
    direction. It's now a 3x9 bitmap

    """

    rows, cols = bitmap.shape

    # Calculate the ACTUAL center position (using float for precision)
    # For odd dimensions: center is exactly on a pixel
    # For even dimensions: center is between two pixels
    actual_center = (rows - 1) / 2.0

    # Distance from top edge (row 0) to the actual center
    distance_from_top_to_center = actual_center

    # New anchor is 'radius' pixels below the actual center
    distance_from_top_to_new_anchor = distance_from_top_to_center + radius

    # Mirror this distance below the new anchor (round up to ensure symmetry)
    pixels_above_new_anchor = int(math.ceil(distance_from_top_to_new_anchor))
    pixels_below_new_anchor = pixels_above_new_anchor

    # Total rows = pixels above + anchor row + pixels below
    new_rows = pixels_above_new_anchor + 1 + pixels_below_new_anchor

    # Create new bitmap (width stays the same)
    new_bitmap = np.zeros((new_rows, cols), dtype=bitmap.dtype)

    # Copy original bitmap into the top portion
    new_bitmap[0:rows, :] = bitmap

    # Draw anchor point if requested
    if draw_anchor:
        anchor_row = pixels_above_new_anchor
        anchor_col = cols // 2
        if 0 <= anchor_row < new_rows and 0 <= anchor_col < cols:
            new_bitmap[anchor_row, anchor_col] = 1

    return new_bitmap


def rotate_point(point: tuple[float, float], angle_rad: float) -> tuple[float, float]:
    """Apply a standard 2D rotation matrix to a single point."""
    x, y = point
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (
        x * cos_a - y * sin_a,
        x * sin_a + y * cos_a,
    )


def rotate_bitmap_in_place(
    bitmap: np.array,
    degrees: float,
    trim_blank_pixels: bool = False,
) -> np.array:
    """
    Converts non-square bitmap to a square shape and rotates the active pixels
    around the bitmap's center point. Optionally, the blank pixels around
    the edge can be trimmed to form the smallest possible shape that still encompasses
    the full bitmap image. "Blank" pixels are simply pixels that are turned off.

    Parameters
    ----------
    bitmap : np.ndarray
        The 2D array representing the monochrome bitmap to rotate.
    degrees : float
        The amount of degrees to rotate the bitmap image.
    trim_blank_pixels : bool, optional
        If True, trims blank pixels around the edge after rotation to form the
        smallest possible shape (default is False).

    Returns
    ----------
    np.ndarray
        A new 2D NumPy array containing the rotated bitmap image.

    Examples
    ----------
    If the bitmap is as follows:

    0  1  0
    1  1  1
    0  1  0
    0  1  0

    and you rotate it 90 degrees, the shape of the NumPy array is first
    converted to a square:

    0  1  0  0
    1  1  1  0
    0  1  0  0
    0  1  0  0

    Then the image is rotated:

    0  0  1  0
    1  1  1  1
    0  0  1  0
    0  0  0  0

    If trim_blank_pixels is True, the surrounding empty pixels are trimmed:

    0  0  1  0
    1  1  1  1
    0  0  1  0

    Note how the 3x4 bitmap morphs into a 4x3 bitmap, but needs to
    expand before doing so. When trim_blank_pixels is False, the bitmap
    maintains square dimensions, expanding as needed to fit the rotated image
    while keeping the rotation center in the middle.
    """

    rows, cols = bitmap.shape

    # Step 1: Expand to square by padding with zeros, CENTERED
    max_dim = max(rows, cols)
    square_bitmap = np.zeros((max_dim, max_dim), dtype=bitmap.dtype)

    # Center the original bitmap in the square canvas
    row_offset = (max_dim - rows) // 2
    col_offset = (max_dim - cols) // 2
    square_bitmap[row_offset : row_offset + rows, col_offset : col_offset + cols] = (
        bitmap
    )

    # Step 2: Rotate around the center of the square bitmap
    angle_rad = math.radians(degrees)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    center = (max_dim - 1) / 2.0  # Use true center for precision

    # Collect rotated coordinates (relative to the original center)
    rotated_points: list[tuple[float, float]] = []
    for y in range(max_dim):
        for x in range(max_dim):
            if square_bitmap[y, x] == 0:
                continue
            # Rotate around center - store as relative coordinates
            rel_x = x - center
            rel_y = y - center
            rot_x = rel_x * cos_a - rel_y * sin_a
            rot_y = rel_x * sin_a + rel_y * cos_a
            rotated_points.append((rot_x, rot_y))

    if not rotated_points:
        # Return empty square bitmap if no active pixels
        return square_bitmap

    if trim_blank_pixels:
        # Determine bounding box of rotated points (still relative to center)
        xs, ys = zip(*rotated_points)
        min_x, max_x = math.floor(min(xs)), math.ceil(max(xs))
        min_y, max_y = math.floor(min(ys)), math.ceil(max(ys))
        new_cols = max_x - min_x + 1
        new_rows = max_y - min_y + 1

        # Create rotated bitmap with dimensions to fit all rotated pixels
        rotated_bitmap = np.zeros((new_rows, new_cols), dtype=bitmap.dtype)

        for rot_x, rot_y in rotated_points:
            px = int(round(rot_x - min_x))
            py = int(round(rot_y - min_y))
            if 0 <= px < new_cols and 0 <= py < new_rows:
                rotated_bitmap[py, px] = 1
    else:
        # Calculate dimensions needed to fit all rotated pixels
        xs, ys = zip(*rotated_points)
        extent = max(
            abs(math.floor(min(xs))),
            abs(math.ceil(max(xs))),
            abs(math.floor(min(ys))),
            abs(math.ceil(max(ys))),
        )
        # Create square canvas that fits the full extent in all directions
        new_dim = 2 * extent + 1

        # Make sure we don't shrink below the original square size
        new_dim = max(new_dim, max_dim)

        # Create the canvas with the center at the middle
        rotated_bitmap = np.zeros((new_dim, new_dim), dtype=bitmap.dtype)
        new_center = (new_dim - 1) / 2.0

        # Place rotated points relative to the new center
        for rot_x, rot_y in rotated_points:
            px = int(round(rot_x + new_center))
            py = int(round(rot_y + new_center))
            if 0 <= px < new_dim and 0 <= py < new_dim:
                rotated_bitmap[py, px] = 1

    return rotated_bitmap


def rotate_around_anchor_point(
    bitmap: np.ndarray,
    degrees: float = 180.0,
    pixel_anchor: tuple = None,
    round_for_pixels: bool = True,
) -> np.ndarray:
    """
    Rotate a 2D NumPy array (bitmap) around a specified anchor point.

    Parameters
    ----------
    bitmap : np.ndarray
        The 2D array representing the monochrome bitmap to rotate.
    degrees : float, optional
        The angle in degrees to rotate the bitmap (default is 180.0).
    pixel_anchor : tuple
        The (x, y) coordinates (column, row) of the anchor point around which to
        rotate the bitmap. NOTE: this will actually default to the center of the
        bitmap image since pixel_anchor cannot ultimately be set to None.
    round_for_pixels : bool, optional
        If True, rounds the resulting coordinates to the nearest integer to fit
        pixel grid (default is True). If False, the rotation will use the
        provided float type.

    Returns
    -------
    np.ndarray
        A new 2D NumPy array of the same shape as `bitmap`, containing the
        rotated bitmap.

    Notes
    -----
    - The anchor point is specified in sequential order of column (x), then row
      (y), matching NumPy's (x, y) convention.
    - Pixels that rotate outside the screen's bounds will be discarded, but the
      bitmap may change dimension (if it's not symmetrical) when being rotated
      to maintain its aspect ratio.
    - This function does not perform interpolation; it is intended for binary
      (monochrome) images.
    """
    if pixel_anchor is None:
        pixel_anchor = get_np_bitmap_center(bitmap)

    angle_rad = math.radians(degrees)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    # Collect rotated coordinates first
    rotated_points: list[tuple[float, float]] = []
    for y in range(bitmap.shape[0]):
        for x in range(bitmap.shape[1]):
            if bitmap[y, x] == 0:
                continue
            rel_x = x - pixel_anchor[0]
            rel_y = y - pixel_anchor[1]
            rot_x = rel_x * cos_a - rel_y * sin_a + pixel_anchor[0]
            rot_y = rel_x * sin_a + rel_y * cos_a + pixel_anchor[1]
            rotated_points.append((rot_x, rot_y))

    if not rotated_points:
        return np.zeros_like(bitmap)

    # Determine new bounding box
    xs, ys = zip(*rotated_points)
    min_x, max_x = math.floor(min(xs)), math.ceil(max(xs))
    min_y, max_y = math.floor(min(ys)), math.ceil(max(ys))
    new_cols = max_x - min_x + 1
    new_rows = max_y - min_y + 1
    output = np.zeros((new_rows, new_cols), dtype=bitmap.dtype)

    # Reposition points into the new canvas
    for rot_x, rot_y in rotated_points:
        if round_for_pixels:
            px = int(round(rot_x - min_x))
            py = int(round(rot_y - min_y))
        else:
            px = rot_x - min_x
            py = rot_y - min_y
        if 0 <= px < new_cols and 0 <= py < new_rows:
            output[py, px] = 1

    return output


def convert_bitmap_str_to_np(bm: str) -> np.array:
    """
    Convert a string bitmap into a NumPy array bitmap.

    Example:
    ```
    piece = \"\"\"010
               111
               010\"\"\"
    ```
    -->
    ```
    piece = np.array(
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    )
    ```
    """
    lines = [line.strip() for line in bm.strip().splitlines() if line.strip()]
    arr = [[int(char) for char in line] for line in lines]
    return np.array(arr, dtype=np.uint8)


def convert_bitmap_np_to_str(arr: np.ndarray) -> str:
    """
    Convert a NumPy array bitmap into a string bitmap.

    Example:
    ```
    piece = np.array(
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        dtype=np.uint8,
    )
    ```
    -->
    ```
    piece = \"\"\"010
               111
               010\"\"\"
    ```
    """
    return "\n".join("".join(str(cell) for cell in row) for row in arr)


# def draw_shape(
#     display: SSD1306Emulator,
#     shape: list[tuple[float, float]],
#     angle_rad: float,
#     origin: tuple[int, int],
#     color: int = 1,
# ) -> None:
#     """Rotate the supplied shape by angle_rad and render it at origin."""
#     ox, oy = origin
#     transformed = []
#     for point in shape:
#         rx, ry = rotate_point(point, angle_rad)
#         transformed.append((round(rx + ox), round(ry + oy)))

#     for (x0, y0), (x1, y1) in zip(transformed, transformed[1:]):
#         display.line(x0, y0, x1, y1, color)


# def draw_frame(display: SSD1306Emulator, tick: float) -> None:
#     display.fill(0)
#     cx = display.width // 2
#     cy = display.height // 2
#     draw_shape(display, LINE_SHAPE, tick, (cx, cy))
#     display.show()


def draw_frame(
    display: SSD1306Emulator,
    np_bitmap: np.array,
    tick: float,
    origin: tuple = None,
) -> None:
    """
    Draw a single bitmap frame on the display.

    Parameters
    ----------
    display : SSD1306Emulator
        The display object to draw on.
    np_bitmap : np.array
        The bitmap to draw.
    tick : float
        Time value (for potential animations, not currently used).
    origin : tuple, optional
        The (x, y) origin point. If None, uses the center of the display.
    """
    display.fill(0)
    if origin is None:
        center = (display.width // 2, display.height // 2)
    else:
        center = origin

    draw_bitmap(display, np_bitmap, center)
    display.show()


def draw_rotated_copies(
    display: SSD1306Emulator,
    np_bitmap: np.array,
    num_copies: int = 8,
    start_angle: float = 0.0,
    origin: tuple = None,
    clear_display: bool = True,
    show_display: bool = True,
) -> None:
    """
    Draw multiple rotated copies of a bitmap on the display.

    Parameters
    ----------
    display : SSD1306Emulator
        The display object to draw on.
    np_bitmap : np.array
        The bitmap to draw and rotate.
    num_copies : int, optional
        The number of rotated copies to draw (default is 8).
    start_angle : float, optional
        The starting angle in degrees for the first copy (default is 0.0).
    origin : tuple, optional
        The (x, y) origin point for all copies. If None, uses the center of
        the display.
    clear_display : bool, optional
        If True, clears the display before drawing (default is True).
    show_display : bool, optional
        If True, calls display.show() after drawing all copies (default is True).

    Examples
    --------
    Draw 8 copies evenly spaced around 360 degrees:
    >>> draw_rotated_copies(display, bitmap, num_copies=8)

    Draw 4 copies starting at 22.5 degrees:
    >>> draw_rotated_copies(display, bitmap, num_copies=4, start_angle=22.5)

    Draw 6 copies at a custom position without clearing:
    >>> draw_rotated_copies(
    ...     display, bitmap, num_copies=6, origin=(40, 30), clear_display=False
    ... )
    """
    if clear_display:
        display.fill(0)

    if origin is None:
        center = (display.width // 2, display.height // 2)
    else:
        center = origin

    # Calculate angle step between copies
    angle_step = 360.0 / num_copies

    # Draw each rotated copy
    for i in range(num_copies):
        angle = start_angle + (angle_step * i)
        rotated = rotate_bitmap_in_place(np_bitmap, angle)
        draw_bitmap(display, rotated, center, draw_blank_pixels=False)

    if show_display:
        display.show()


def precompute_spinning_animation(
    np_bitmap: np.ndarray,
    num_copies: int = 8,
    base_angle: float = 0.0,
    animation_steps: int = 45,
    degrees_per_cycle: float = 45.0,
) -> list[list[np.ndarray]]:
    """
    Pre-compute all rotated bitmap frames for a spinning animation.

    This function creates a cache of pre-rotated bitmaps to avoid expensive
    rotation operations during runtime on resource-constrained devices like ESP32-C3.

    Parameters
    ----------
    np_bitmap : np.ndarray
        The base bitmap to create spinning animation from.
    num_copies : int, optional
        Number of rotated copies to create per frame (default is 8).
    base_angle : float, optional
        Starting angle offset in degrees (default is 0.0).
    animation_steps : int, optional
        Number of animation frames to pre-compute. More steps = smoother
        animation but uses more memory (default is 45).
    degrees_per_cycle : float, optional
        How many degrees to rotate through in one complete animation cycle.
        For 8-fold symmetry, 45 degrees brings you back to the same visual
        (default is 45.0).

    Returns
    -------
    list[list[np.ndarray]]
        A list of frames, where each frame is a list of pre-rotated bitmaps
        (one for each copy).

    Examples
    --------
    Pre-compute 45 frames with 8-fold symmetry:
    >>> cache = precompute_spinning_animation(bitmap, num_copies=8)
    >>> # cache[0] = first frame with 8 rotated copies
    >>> # cache[44] = last frame with 8 rotated copies

    Pre-compute faster animation with fewer steps:
    >>> cache = precompute_spinning_animation(bitmap, animation_steps=20)

    Notes
    -----
    Memory usage: For a 50x50 bitmap with 8 copies and 45 steps:
    - Approximate: 50 * 50 * 8 * 45 = ~900KB (worst case)
    - Actual: Much less due to sparse bitmaps and variable sizes
    """
    rotation_cache = []
    angle_step = 360.0 / num_copies

    for step in range(animation_steps):
        # Calculate offset for this animation frame
        animation_offset = (step / animation_steps) * degrees_per_cycle

        # Create all rotated copies for this frame
        frame_copies = []
        for i in range(num_copies):
            angle = base_angle + (angle_step * i) + animation_offset
            rotated = rotate_bitmap_in_place(np_bitmap, angle)
            frame_copies.append(rotated)

        rotation_cache.append(frame_copies)

    return rotation_cache


def draw_precomputed_frame(
    display: SSD1306Emulator,
    precomputed_copies: list[np.ndarray],
    origin: tuple = None,
    clear_display: bool = True,
    show_display: bool = True,
) -> None:
    """
    Draw a single frame from pre-computed animation cache.

    Parameters
    ----------
    display : SSD1306Emulator
        The display object to draw on.
    precomputed_copies : list[np.ndarray]
        A list of pre-rotated bitmaps to draw (one frame from the cache).
    origin : tuple, optional
        The (x, y) origin point. If None, uses the center of the display.
    clear_display : bool, optional
        If True, clears the display before drawing (default is True).
    show_display : bool, optional
        If True, calls display.show() after drawing (default is True).

    Examples
    --------
    Draw frame 10 from pre-computed cache:
    >>> cache = precompute_spinning_animation(bitmap)
    >>> draw_precomputed_frame(display, cache[10])

    Cycle through animation:
    >>> for frame in cache:
    >>>     draw_precomputed_frame(display, frame)
    >>>     time.sleep(0.033)  # ~30 FPS
    """
    if clear_display:
        display.fill(0)

    if origin is None:
        center = (display.width // 2, display.height // 2)
    else:
        center = origin

    # Draw each pre-rotated copy
    for rotated_copy in precomputed_copies:
        draw_bitmap(display, rotated_copy, center, draw_blank_pixels=False)

    if show_display:
        display.show()
