from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

PLAYER_MOVEMENT_SPEED : int = 3
"""Lateral speed of the player, in pixels per frame."""

PLAYER_JUMP_SPEED = 12
"""Instant vertical speed for jumping, in pixels per frame."""

class Player(GameObject):
    """The main player game object.
    """
    is_move_initiated: bool
    """Whether the move was initiated (the key was pressed)
    on a frame where the player was present.
    """

    def __init__(self, map: Map, **kwargs: Any) -> None:
        """Initializes the player tl;dr see GameObject#__init__
        """

        super().__init__(map, ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", **kwargs)
        self.is_move_initiated = False
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.change_x += PLAYER_MOVEMENT_SPEED
                self.is_move_initiated = True
            case arcade.key.LEFT:
                self.change_x -= PLAYER_MOVEMENT_SPEED
                self.is_move_initiated = True
            case arcade.key.UP:
                if self.map.physics_engine.can_jump():
                    self.change_y = PLAYER_JUMP_SPEED
    
    def on_key_release(self, key: int, modifiers: int) -> None:
        match key:
            case arcade.key.RIGHT:
                if self.is_move_initiated:
                    self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                if self.is_move_initiated:
                    self.change_x += PLAYER_MOVEMENT_SPEED