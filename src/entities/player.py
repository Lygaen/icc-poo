import math
from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map

PLAYER_MOVEMENT_SPEED: int = 3
"""Lateral speed of the player, in pixels per frame."""

PLAYER_JUMP_SPEED = 12
"""Instant vertical speed for jumping, in pixels per frame."""

SWORD_SCALE = 0.5 * 0.7
"""Sword scale in world.
"""

PLAYER_JUMP_BUFFER = 0.1
"""Base timer buffer for jumping, in seconds.
"""

PLAYER_COYOTE_TIME = 0.07
"""Base timer buffer for coyote time, in seconds.
"""

SWORD_DOT_DAMAGE = 50
"""Sword damage-over-time.
"""


class Bow(GameObject):
    __mouse_position: arcade.types.Point2
    """Mouse position, used for calculating the bow position/rotation.
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, "assets/bow.png", **kwargs)
        self.scale = (SWORD_SCALE, SWORD_SCALE)
        self.event_listener = True
        self.visible = False

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if not self.visible:
            return

        mouse = self.camera.unproject(self.__mouse_position)
        dir = arcade.Vec2(mouse.x - self.position[0], mouse.y - self.position[1])
        dir = dir.normalize()

        SCALE_FACTOR = 0.2

        if dir.x < 0:
            start_pos = (
                self.map.player.left,
                self.map.player.center_y - self.map.player.size[1] // 3,
            )
        else:
            start_pos = (
                self.map.player.right,
                self.map.player.center_y - self.map.player.size[1] // 3,
            )

        self.position = (
            start_pos[0] + dir[0] * self.size[0] * SCALE_FACTOR,
            start_pos[1] + dir[1] * self.size[1] * SCALE_FACTOR,
        )

        angle = math.asin(dir.x) - (3 * math.pi / 4)

        if dir.y < 0:
            angle = -angle - (math.pi / 2)
        self.radians = angle

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        self.visible = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        self.visible = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.__mouse_position = (x, y)


class Sword(GameObject):
    __mouse_position: arcade.types.Point2
    """Mouse position, used for calculating the sword position/rotation.
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, "assets/sword_silver.png", **kwargs)
        self.scale = (SWORD_SCALE, SWORD_SCALE)
        self.event_listener = True
        self.visible = False

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if not self.visible:
            return

        for hits in self.map.check_for_collisions_all(self):
            hits.on_damage(DamageSource.PLAYER, SWORD_DOT_DAMAGE * delta_time)

        mouse = self.camera.unproject(self.__mouse_position)
        dir = arcade.Vec2(mouse.x - self.position[0], mouse.y - self.position[1])
        dir = dir.normalize()

        SCALE_FACTOR = 0.4
        if dir.x < 0:
            start_pos = (
                self.map.player.left,
                self.map.player.center_y - self.map.player.size[1] // 3,
            )
        else:
            start_pos = (
                self.map.player.right,
                self.map.player.center_y - self.map.player.size[1] // 3,
            )

        self.position = (
            start_pos[0] + dir[0] * self.size[0] * SCALE_FACTOR,
            start_pos[1] + dir[1] * self.size[1] * SCALE_FACTOR,
        )

        angle = math.asin(dir.x) - (math.pi / 4)

        if dir.y < 0:
            angle = -angle + (math.pi / 2)
        self.radians = angle

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        self.visible = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        self.visible = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.__mouse_position = (x, y)


class Player(GameObject):
    """The main player game object."""

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
    """GameObject of the sword the player is using.
    """

    HP: float
    """Health-Point of the gameobject.
    """

    base_HP: float = 20
    """Base healtpoint of the player.
    """

    __buffered_jump_timer: float = 0
    __coyote_timer: float = 0

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        """Initializes the player tl;dr see GameObject#__init__"""

        super().__init__(
            map,
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            **kwargs,
        )

        # Ugly bug where arcade didn't register on my laptop
        # when a key was pressed on specific frames but registered
        # the release when the map was just reloaded.
        # Very specific. Very annoying.
        self.is_move_initiated = False
        self.jump_sound = arcade.Sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
        self.event_listener = True
        self.sword = Sword(map)

        self.__buffered_jump_timer = 0
        self.__coyote_timer = 0
        self.HP = self.base_HP

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
                self.__buffered_jump_timer = PLAYER_JUMP_BUFFER

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                if (
                    self.is_move_initiated
                ):  # See in __init__ for explanation (yes, there is one)
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

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        on_ground = self.map.physics_engine.can_jump()

        if on_ground:
            self.__coyote_timer = PLAYER_COYOTE_TIME

        if not on_ground and self.__coyote_timer > 0:
            self.__coyote_timer -= delta_time
            on_ground = True

        if on_ground and self.__buffered_jump_timer > 0:
            self.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)
            self.__buffered_jump_timer = 0
        elif self.__buffered_jump_timer > 0:
            self.__buffered_jump_timer -= delta_time

    def destroy(self) -> None:
        self.sword.destroy()  # Destroy the sword as well
        super().destroy()
