from typing import Any, cast
import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map

import math

PLAYER_MOVEMENT_SPEED : int = 3
"""Lateral speed of the player, in pixels per frame."""

PLAYER_JUMP_SPEED = 12
"""Instant vertical speed for jumping, in pixels per frame."""

class Sword(GameObject):
    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, "assets/sword_silver.png", **kwargs)
        self.scale = (0.5 * 0.7, 0.5 * 0.7)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if not self.visible:
            return

        for hits in self.map.check_for_collisions_all(self):
            hits.on_damage(DamageSource.PLAYER, 50 * delta_time)

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

    sword: Sword

    HP: float

    __mouse_position: arcade.types.Point2

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
        self.event_listener = True
        self.sword = Sword(map)
        self.sword.visible = False
        self.__mouse_position = arcade.Vec2(0, 0)
        self.HP = 20

        self.map.add_objects([self.sword])

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

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                if self.is_move_initiated: # See in __init__ for explanation (yes, there is one)
                    self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                if self.is_move_initiated:
                    self.change_x += PLAYER_MOVEMENT_SPEED

    def on_damage(self, source: DamageSource, damage: float) -> None:
        match source:
            case DamageSource.LAVA:
                self.HP = 0
            case DamageSource.MONSTER:
                self.HP -= damage
            case _:
                return

        if self.HP <= 0:
            arcade.play_sound(self.gameover_sound)
            self.game_view.score = 0
            self.map.reload()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.sword.visible = True

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.__mouse_position = (x, y)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        mouse = self.camera.unproject(self.__mouse_position)
        dir = arcade.Vec2(mouse.x - self.map.player.position[0], mouse.y - self.map.player.position[1])
        dir = dir.normalize()
        SCALE_FACTOR = 0.4
        start_pos = self.position

        if dir.x < 0:
            start_pos = (self.left, self.center_y - self.size[1] // 3)
        else:
            start_pos = (self.right, self.center_y - self.size[1] // 3)

        self.sword.position = (start_pos[0] + dir[0] * self.sword.size[0] * SCALE_FACTOR,
            start_pos[1] + dir[1] * self.sword.size[1] * SCALE_FACTOR)

        angle = math.asin(dir.x) - (math.pi / 4)

        if dir.y < 0:
            angle = -angle + (math.pi / 2)
        self.sword.radians = angle

        super().update(delta_time, *args, **kwargs)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.sword.visible = False

    def destroy(self) -> None:
        self.sword.destroy()
        super().destroy()
