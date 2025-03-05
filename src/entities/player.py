from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

PLAYER_MOVEMENT_SPEED : int = 5
"""Lateral speed of the player, in pixels per frame."""

PLAYER_GRAVITY = 1
"""Gravity applied to the player, in pixels per frame²."""

PLAYER_JUMP_SPEED = 18
"""Instant vertical speed for jumping, in pixels per frame."""

class Player(GameObject):
    def __init__(self, map: Map, **kwargs: Any) -> None:
        super(Player, self).__init__(map, ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", **kwargs)
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                # start moving to the right
                self.change_x += PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                if self.map.physics_engine.can_jump():
                    self.change_y = PLAYER_JUMP_SPEED
                    self.destroy()
    
    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match key:
            case arcade.key.RIGHT:
                # stop lateral movement
                self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # stop lateral movement
                self.change_x += PLAYER_MOVEMENT_SPEED