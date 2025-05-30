import math
from abc import abstractmethod
from typing import Any, Final

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map

PLAYER_MOVEMENT_SPEED: int = 3
"""Lateral speed of the player, in pixels per frame."""

PLAYER_JUMP_SPEED = 12
"""Instant vertical speed for jumping, in pixels per frame."""

WEAPON_SCALE = 0.5 * 0.7
"""Weapon scale in world.
"""

PLAYER_JUMP_BUFFER = 0.1
"""Base timer buffer for jumping, in seconds.
"""

PLAYER_COYOTE_TIME = 0.07
"""Base timer buffer for coyote time, in seconds.
"""

SWORD_DOT_DAMAGE = 75
"""Sword damage-over-time.
"""

ARROW_SPEED = 10
"""The speed of the arrow, in units per second
"""

ARROW_WAIT_TIME = 0.25
"""The time to not shoot arrows between arrows being shot
"""

ARROW_DAMAGE = 25
"""Damage inflicted by one arrow, on hit
"""


class Weapon(GameObject):
    """Class to have a general framework for adding weapons"""

    __scale_factor: float
    """The scale factor of the sprite (aka. how far it is)
    """
    __positive_angle: float
    """The correction angle when dir.y > 0
    """
    __negative_angle: float
    """The correction angle when dir.y < 0
    """
    dir: arcade.Vec2
    """The current direction of the bow
    """

    def __init__(
        self,
        map: list[Map],
        texture: str,
        scale_factor: float,
        positive_angle: float,
        negative_angle: float,
        **kwargs: Any,
    ) -> None:
        """Creates a new weapon, giving its texture, the scale_factor as well
        as the angles of the sprite on the texture.
        """

        super().__init__(map, float("inf"), texture, **kwargs)
        self.scale = (WEAPON_SCALE, WEAPON_SCALE)
        self.event_listener = True
        self.visible = False

        self.__scale_factor = scale_factor
        self.__positive_angle = positive_angle
        self.__negative_angle = negative_angle
        self.dir = arcade.Vec2(0, 0)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if not self.visible:
            return

        mouse = self.camera.unproject(self.__mouse_position)
        self.dir = arcade.Vec2(
            mouse.x - self.map.player.position[0], mouse.y - self.map.player.position[1]
        )
        self.dir = self.dir.normalize()

        if self.dir.x < 0:
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
            start_pos[0] + self.dir[0] * self.size[0] * self.__scale_factor,
            start_pos[1] + self.dir[1] * self.size[1] * self.__scale_factor,
        )

        angle = math.asin(self.dir.x) + self.__positive_angle

        if self.dir.y < 0:
            angle = -angle + self.__negative_angle
        self.radians = angle

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.visible = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.__mouse_position = (x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.visible = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.__mouse_position = (x, y)

    @abstractmethod
    def get_weapon_texture(self) -> arcade.Texture: ...

    @staticmethod
    def change_weapon(current_weapon: "Weapon") -> "Weapon":
        """Change weapon, returning a new weapon
        depending on the current weapon type.
        """
        match current_weapon.__class__.__name__:
            case "Sword":
                return Bow([current_weapon.map])
            case "Bow":
                return Sword([current_weapon.map])
            case _:
                raise ValueError("Invalid weapon !")


class Bow(Weapon):
    """The bow weapon class"""

    class Arrow(GameObject):
        """The internal arrow gameobject that is shot from the bow"""

        time_to_live: float
        """The time left to live of the arrow
        """

        def __init__(
            self,
            map: list[Map],
            bow_position: arcade.types.Point2,
            bow_angle: float,
            dir: arcade.Vec2,
            **kwargs: Any,
        ) -> None:
            """Creates a new arrow, given the bow position, the bow angle
            and the direction as a vec2"""

            super().__init__(map, float("inf"), "assets/arrow.png", **kwargs)
            self.scale = (WEAPON_SCALE, WEAPON_SCALE)
            self.position = bow_position
            self.radians = bow_angle + (math.pi / 2)

            self.velocity = dir.normalize() * 10
            self.time_to_live = 5

        def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
            super().update(delta_time, *args, **kwargs)
            self.time_to_live -= delta_time

            if self.time_to_live <= 0:  # Destroys the arrow
                self.destroy()

            objects = self.map.check_for_collisions_all(self)

            filtered = [
                ob
                for ob in objects
                if ob.__class__.__name__ not in ["Bow", "Player", "Arrow"]
                and ob.visible
            ]  # Ignore collisions with the bow, player or other arrows

            if len(filtered) == 0:  # Free arroooooww
                self.change_y -= ARROW_SPEED * delta_time

                dir = arcade.Vec2(self.velocity[0], self.velocity[1])
                dir = dir.normalize()

                angle = math.asin(dir.x) - (3 * math.pi / 4) + (math.pi / 2)

                if dir.y < 0:
                    angle = -angle - (math.pi / 2) + math.pi
                self.radians = angle
            elif self.velocity != (
                0,
                0,
            ):  # We collided with something, and the arrow is moving
                self.velocity = (0, 0)
                for hits in filtered:
                    if hits.damage(self, DamageSource.PLAYER, ARROW_DAMAGE):
                        self.destroy()

    spawn_next_tick: bool
    """Whether or not to spawn the arrow next tick
    """

    last_shot: float
    """Time in seconds since the last shot
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(
            map, "assets/bow.png", 0.2, -(3 * math.pi / 4), -(math.pi / 2), **kwargs
        )
        self.spawn_next_tick = False
        self.last_shot = 0

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)
        self.last_shot -= delta_time

        if self.spawn_next_tick:
            arrow = self.Arrow([self.map], self.position, self.radians, self.dir)

            self.map.add_objects([arrow])

            self.spawn_next_tick = False

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)

        # Ignore the input if the last shot was not too far in time
        if button == arcade.MOUSE_BUTTON_LEFT and self.last_shot <= 0:
            self.spawn_next_tick = True
            self.last_shot = ARROW_WAIT_TIME

    BOW_UI_TEXTURE = arcade.load_texture("assets/bow.png")

    def get_weapon_texture(self) -> arcade.Texture:
        return self.BOW_UI_TEXTURE

    def destroy(self, is_health_death: bool = False) -> None:
        super().destroy()


class Sword(Weapon):
    """The sword weapon"""

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(
            map,
            "assets/sword_silver.png",
            0.4,
            -(math.pi / 4),
            (math.pi / 2),
            **kwargs,
        )

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if not self.visible:
            return

        for hits in self.map.check_for_collisions_all(self):
            hits.damage(self, DamageSource.PLAYER, SWORD_DOT_DAMAGE)

    SWORD_UI_TEXTURE = arcade.load_texture("assets/sword_silver.png")

    def get_weapon_texture(self) -> arcade.Texture:
        return self.SWORD_UI_TEXTURE


class Player(GameObject):
    """The main player game object."""

    is_move_initiated: tuple[bool, bool]
    """Whether the move was initiated (the key was pressed)
    on a frame where the player was present. First element is
    for left, second for right.
    """
    gameover_sound: arcade.Sound
    """Sound for when player touches lava
    """

    hurt_sound: arcade.Sound

    jump_sound: arcade.Sound
    """SFX for when the player is jumping.
    """

    weapon: Weapon
    """GameObject of the weapon the player is using.
    """

    __buffered_jump_timer: float = 0
    """The timer whether a jump was buffered
    """
    __coyote_timer: float = 0
    """A timer for coyote time jumps.
    """

    __knockback: Final[list[float]]
    """The knockback the player takes when hit, a list to modify it without being able to change its length
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        """Initializes the player tl;dr see GameObject#__init__"""

        super().__init__(
            map,
            100,
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            **kwargs,
        )

        # Ugly bug where arcade didn't register on my laptop
        # when a key was pressed on specific frames but registered
        # the release when the map was just reloaded.
        # Very specific. Very annoying.
        # It needs to be a tuple depending on the direction
        # because of course arcade doesn't have a way of checking
        # the currently pressed keys! Yay.
        self.is_move_initiated = (False, False)

        self.jump_sound = arcade.Sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
        self.event_listener = True
        self.weapon = Sword(map)
        self.hurt_sound = arcade.Sound(":resources:/sounds/hurt3.wav")

        self.__buffered_jump_timer = 0
        self.__coyote_timer = 0
        self.__knockback = [0, 0]

        self.map.add_objects([self.weapon])

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.weapon.destroy()
            self.weapon = Weapon.change_weapon(self.weapon)
            self.map.add_objects([self.weapon])

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.change_x += PLAYER_MOVEMENT_SPEED
                self.is_move_initiated = (self.is_move_initiated[0], True)
            case arcade.key.LEFT:
                self.change_x -= PLAYER_MOVEMENT_SPEED
                self.is_move_initiated = (True, self.is_move_initiated[1])
            case arcade.key.UP:
                self.__buffered_jump_timer = PLAYER_JUMP_BUFFER

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                if self.is_move_initiated[
                    1
                ]:  # See in __init__ for explanation (yes, there is one)
                    self.change_x -= PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                if self.is_move_initiated[0]:
                    self.change_x += PLAYER_MOVEMENT_SPEED

    def _on_damage(self, other: GameObject | None, source: DamageSource) -> bool:
        damaged = source in {DamageSource.LAVA, DamageSource.VOID, DamageSource.MONSTER}
        if damaged:
            arcade.play_sound(self.hurt_sound)
        if source == DamageSource.MONSTER and other is not None:
            knockback: arcade.Vec2 = arcade.Vec2(
                self.center_x - other.center_x, self.center_y - other.center_y
            )
            knockback = knockback.normalize()
            self.__knockback[0] = 1000 * knockback.normalize()[0]
            self.__knockback[1] = 1000 * (knockback.normalize()[1] + 0.5)
        return damaged

    def knock(self, delta_time: float = 1 / 60) -> None:
        """applies the knockback to the player"""
        self.center_x += self.__knockback[0] * delta_time
        self.center_y += self.__knockback[1] * delta_time
        for i in range(len(self.__knockback)):
            self.__knockback[i] *= 0.7
            if abs(self.__knockback[i]) < 0.01:
                self.__knockback[i] = 0

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        self.knock(delta_time)

        if self.center_y < -500:
            self.damage(None, DamageSource.VOID, float("inf"))

        on_ground = self.map.physics_engine.can_jump()

        if on_ground:  # Reset coyote-timer
            self.__coyote_timer = PLAYER_COYOTE_TIME
        elif self.__coyote_timer > 0:  # Simulate being on ground
            self.__coyote_timer -= delta_time
            on_ground = True

        if (
            on_ground and self.__buffered_jump_timer > 0
        ):  # A jump was buffered and we're considered on ground
            self.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)
            self.__buffered_jump_timer = 0
        elif self.__buffered_jump_timer > 0:
            self.__buffered_jump_timer -= delta_time

    def destroy(self, is_health_death: bool = False) -> None:
        if is_health_death:
            arcade.play_sound(self.gameover_sound)
            self.game_view.score = 0
            self.map.respawn_player()
        else:
            self.weapon.destroy()
            super().destroy()
