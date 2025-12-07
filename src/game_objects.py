# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_objects.py
"""Game objects and collision detection."""

import math


class SlidingShape:
    """A shape that slides across the screen toward a target."""

    def __init__(self, shape_bitmap, target_center, start_side="left", speed=2):
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
        speed : int
            Pixels to move per frame.
        """
        self.bitmap = shape_bitmap
        self.target_x, self.target_y = target_center
        self.speed = speed
        self.active = True

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
        """Check if shape is within tolerance of target."""
        distance = abs(self.x - self.target_x)
        return distance <= tolerance

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
