from typing import Any
import arcade

from src.entities.gameobject import DamageSource, GameObject
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
    gameover_sound: arcade.Sound
    """Sound for when player touches lava
    """

    jump_sound: arcade.Sound
    """SFX for when the player is jumping.
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        """Initializes the player tl;dr see GameObject#__init__
        """

        super().__init__(map, ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", **kwargs)

        # Ugly bug where arcade didn't register on my laptop
        # when a key was pressed on specific frames but registered
        # the release when the map was just reloaded.
        # Very specific. Very annoying.
        self.is_move_initiated = False
        self.jump_sound = arcade.Sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
    
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
                    arcade.play_sound(self.jump_sound)
    
    def on_key_release(self, key: int, modifiers: int) -> None:
        match key:
            case arcade.key.RIGHT:
                if self.is_move_initiated: # See in __init__ for explanation (yes, there is one)
                    self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                if self.is_move_initiated:
                    self.change_x += PLAYER_MOVEMENT_SPEED
    
    def on_damage(self, source: DamageSource, damage: float) -> None:
        match source:
            case DamageSource.MONSTER | DamageSource.LAVA:
                arcade.play_sound(self.gameover_sound)
                self.game_view.score = 0
                self.map.reload()
                return
            case _:
                return