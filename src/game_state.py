# This file was made with the use of various A.I. LLMs, specifically, Claude sonnet 4.5
# game_state.py
"""Game state management for Dancie."""

from game_config import (
    GESTURE_INTERVAL,
    INITIAL_HEALTH,
    get_level_requirements,
    get_shape_speed,
)


class GameState:
    """
    Manages the current state of the game.

    Tracks score, health, level, current shape index, and determines
    when to show gesture prompts vs. sliding shapes.
    """

    def __init__(self, starting_level=1):
        """
        Initialize game state.

        Parameters
        ----------
        starting_level : int
            Level to start at (default 1).
        """
        self.level = starting_level
        self.score = 0
        self.health = INITIAL_HEALTH
        self.is_game_over = False
        self.level_complete = False

        # Track progress through current level
        self.shapes_completed = 0
        self.gestures_completed = 0

        # Get requirements for this level
        self.shapes_required, self.gestures_required = get_level_requirements(
            self.level
        )

        # Shape counter for gesture timing (gesture every 7th shape)
        self.shape_counter = 0

        # Current shape speed based on level
        self.current_speed = get_shape_speed(self.level)

    def add_score(self, points):
        """
        Add points to score (can be negative).

        Parameters
        ----------
        points : int
            Points to add (negative values subtract).
        """
        self.score += points
        if self.score < 0:
            self.score = 0  # Don't go negative

    def lose_health(self, amount=1):
        """
        Reduce health by specified amount.

        Parameters
        ----------
        amount : int
            Amount of health to lose (default 1).
        """
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_game_over = True

    def complete_shape(self):
        """
        Mark a shape as completed and increment counter.
        Checks if level is complete.
        """
        self.shapes_completed += 1
        self.shape_counter += 1

        # Check if level is complete
        if (
            self.shapes_completed >= self.shapes_required
            and self.gestures_completed >= self.gestures_required
        ):
            self.level_complete = True

    def complete_gesture(self):
        """
        Mark a gesture as completed.
        Checks if level is complete.
        """
        self.gestures_completed += 1

        # Check if level is complete
        if (
            self.shapes_completed >= self.shapes_required
            and self.gestures_completed >= self.gestures_required
        ):
            self.level_complete = True

    def should_show_gesture(self):
        """
        Determine if next event should be a gesture prompt.

        Returns
        -------
        bool
            True if gesture should appear, False if regular shape.
        """
        # Show gesture after every GESTURE_INTERVAL shapes
        # But only if we still need more gestures
        if self.gestures_completed >= self.gestures_required:
            return False

        if self.shape_counter >= GESTURE_INTERVAL:
            self.shape_counter = 0  # Reset counter
            return True

        return False

    def advance_level(self):
        """
        Advance to next level and reset level-specific counters.
        Preserves score and health.
        """
        self.level += 1
        self.level_complete = False
        self.shapes_completed = 0
        self.gestures_completed = 0
        self.shape_counter = 0

        # Update requirements for new level
        self.shapes_required, self.gestures_required = get_level_requirements(
            self.level
        )

        # Update speed for new level
        self.current_speed = get_shape_speed(self.level)

    def reset_game(self):
        """Reset game state to level 1 (for restart after game over)."""
        self.__init__(starting_level=1)

    def get_status_string(self):
        """
        Get current game status as formatted string.

        Returns
        -------
        str
            Status string like "L:1 S:0 H:5"
        """
        return f"L:{self.level} S:{self.score} H:{self.health}"

    def get_progress_string(self):
        """
        Get level progress as formatted string.

        Returns
        -------
        str
            Progress string like "Shapes: 14/14 Gestures: 1/2"
        """
        return (
            f"Shapes: {self.shapes_completed}/{self.shapes_required} "
            f"Gestures: {self.gestures_completed}/{self.gestures_required}"
        )
