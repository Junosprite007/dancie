# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_objects.py
"""Game objects and collision detection."""

import math

from game_config import SCORE_GOOD, SCORE_GREAT, SCORE_OK, SCORE_PERFECT, SCORE_POOR


class SlidingShape:
    """A shape that slides across the screen toward a target."""

    def __init__(
        self, shape_bitmap, target_center, start_side="left", speed=2, target_index=0
    ):
        """
        Initialize a sliding shape.

        Parameters
        ----------
        shape_bitmap : np.ndarray
            The bitmap image of the shape.
        target_center : tuple
            The (x, y) coordinates the shape should reach.
        start_side : str
            Which side to start from: "left" or "right".
        speed : float
            Pixels to move per frame.
        target_index : int
            Which map piece this shape targets (0-7).
        """
        self.bitmap = shape_bitmap
        self.target_x, self.target_y = target_center
        self.speed = speed
        self.active = True
        self.target_index = target_index  # Which map piece (0-7)
        self.button_number = target_index + 1  # Corresponding button (1-8)

        # Track if shape was hit by user
        self.was_hit = False
        self.score_awarded = 0

        # Track if shape passed target without being hit (health penalty)
        self.missed = False

        # Starting position
        if start_side == "left":
            self.x = 0  # Start at left edge
        else:
            self.x = 128  # Start at right edge

        self.y = self.target_y  # Y position matches target

    def update(self):
        """Update position for next frame."""
        if not self.active:
            return

        # Move toward target
        if self.x < self.target_x:
            self.x += self.speed
            if self.x > self.target_x:
                self.x = self.target_x
        elif self.x > self.target_x:
            self.x -= self.speed
            if self.x < self.target_x:
                self.x = self.target_x

    def is_at_target(self, tolerance=5):
        """
        Check if shape is within tolerance of target.

        Parameters
        ----------
        tolerance : int
            Pixel tolerance (default 5).

        Returns
        -------
        bool
            True if within tolerance.
        """
        distance = abs(self.x - self.target_x)
        return distance <= tolerance

    def get_distance_from_target(self):
        """
        Get current distance from target in pixels.

        Returns
        -------
        int
            Absolute distance in pixels.
        """
        return abs(int(self.x - self.target_x))

    def calculate_score(self):
        """
        Calculate score based on distance from perfect alignment.

        Returns
        -------
        int
            Score points earned (5, 4, 3, 2, or -2).
        """
        distance = self.get_distance_from_target()

        if distance == 0:
            return SCORE_PERFECT  # 5 points
        elif distance <= 2:
            return SCORE_GREAT  # 4 points
        elif distance <= 4:
            return SCORE_GOOD  # 3 points
        elif distance <= 19:
            return SCORE_OK  # 2 points
        else:
            return SCORE_POOR  # -2 points

    def has_passed_target(self):
        """
        Check if shape has completely passed the target.
        Used to determine if player missed the shape.

        Returns
        -------
        bool
            True if shape passed target without being hit.
        """
        # Shape has passed if it's on opposite side of target from start
        if self.speed > 0:  # Moving right
            return self.x > self.target_x + 10
        else:  # Moving left
            return self.x < self.target_x - 10

    def mark_as_hit(self, score):
        """
        Mark shape as successfully hit by player.

        Parameters
        ----------
        score : int
            Score earned for this hit.
        """
        self.was_hit = True
        self.score_awarded = score
        self.active = False  # Remove from screen

    def mark_as_missed(self):
        """Mark shape as missed (passed target without being hit)."""
        if not self.was_hit:
            self.missed = True
            self.active = False

    def get_position(self):
        """Get current center position as (x, y) tuple."""
        return (int(self.x), int(self.y))


def calculate_collision_centers(base_angle, num_copies, radius, display_center):
    """
    Calculate the collision centers for all kaleidoscope pieces.

    Returns
    -------
    list of tuples
        List of (x, y) coordinates for each piece's collision center.
    """
    collision_centers = []

    for i in range(num_copies):
        angle = base_angle + (360.0 / num_copies * i)
        angle_rad = math.radians(angle)

        piece_center_x = display_center[0] + int(radius * math.sin(angle_rad))
        piece_center_y = display_center[1] - int(radius * math.cos(angle_rad))

        collision_centers.append((piece_center_x, piece_center_y))

    return collision_centers


def determine_spawn_side(target_center, display_center):
    """
    Determine which side a shape should spawn from based on target position.

    Shapes targeting left side of screen spawn from left.
    Shapes targeting right side of screen spawn from right.

    Parameters
    ----------
    target_center : tuple
        (x, y) coordinates of target.
    display_center : tuple
        (x, y) coordinates of screen center.

    Returns
    -------
    str
        "left" or "right".
    """
    target_x = target_center[0]
    center_x = display_center[0]

    if target_x < center_x:
        return "left"
    else:
        return "right"
