import math as m
import random
from enum import Enum
from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map


class Dir(
    Enum
):  # this is an enumeration type of cardinal directions, which will be used to check for hitboxes in the immediate neighborhood of the slime along the chosen direction
    """the direction which will be considered"""

    down = 0
    up = 1
    face = 2
    facedown = 3
    faceup = 4
    back = 5
    backdown = 6
    backup = 7


class Monster(GameObject):
    direction: int
    gameover_sound: arcade.Sound
    HP: float
    __base_damage: float
    """Sound for when player touches the slime
    """

    def __init__(
        self,
        texture: str,
        base_HP: float,
        base_damage: float,
        map: list[Map],
        **kwargs: Any,
    ) -> None:
        super().__init__(map, texture, **kwargs)
        self.HP = base_HP
        self.__base_damage = base_damage

    def check_collision(self, dir: Dir) -> bool:
        """To check if there is a collider in the immediate neighborhood of the slime along a certain direction (in argument)"""
        circle = arcade.SpriteCircle(
            1, arcade.color.WHITE
        )  # create a little circle, which we will place in the zone where we want to check for collisions. this allows us to check collisions on more precise parts of the sprite, and not always the sprite in a whole
        match dir:  # place the little circle at the extremity of the sprite in the direction wanted. for the diagonals, put it a little further than the edges of the hitboxes so the result is not corrupted by the potentials colliders under and on the sides (but not diagonally) of the slime
            case Dir.down:
                circle.position = (
                    self.position[0],
                    self.position[1] - self.size[1] // 2,
                )
            case Dir.face:
                circle.position = (
                    self.position[0]
                    + self.scale_x * self.direction * self.size[0] // 2,
                    self.position[1],
                )
            case Dir.facedown:
                circle.position = (
                    self.position[0]
                    + self.scale_x * self.direction * (self.size[0] // 2 + 2),
                    self.position[1] - self.size[1] // 2 - 1,
                )
            case _:
                # pas encore implémenté (pas de besoin pour le moment)
                return False
        return (
            len(
                arcade.check_for_collision_with_list(
                    circle, self.map.physics_colliders_list
                )
            )
            != 0
        )  # return true if there is at least one collider in collision with the little circle, false otherwise

    # if monstey hit something hurtful that belong to the player, monstey suffers (i.e. loses hp)
    def on_damage(self, source: DamageSource, damage: float) -> bool:
        if source == DamageSource.PLAYER:
            # if monstey has no HP left, monstey dies in atrocious circumstances
            self.HP -= damage
            if self.HP <= 0:
                self.destroy()
            return True
        return False

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        for object in self.map.check_for_collisions_all(
            self
        ):  # if monstey touches player, player suffer (i.e. loses HP)
            object.on_damage(DamageSource.MONSTER, self.__base_damage * delta_time)

        super().update(delta_time, *args, **kwargs)


class Bat(Monster):
    direction: int
    gameover_sound: arcade.Sound
    """Sound for when player touches the slime
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__("assets/bat.png", 50, 25, map, **kwargs)
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
        self.v_ro: float = 1
        self.v_phi: float = m.pi
        self.radius_movement: int = 150
        self.start: tuple[float, float] = (self.center_x, self.center_y)

    @property
    def dir(self) -> tuple[float, float]:
        """To convert the polar coordinate of the speed to plain coordinates to interact with the game"""
        return (self.v_ro * m.cos(self.v_phi), self.v_ro * m.sin(self.v_phi))

    @property
    def canmove(self, delta_time: float = 1 / 60) -> bool:
        """Test if the bat actual movement direction will bring it out of its radius movement"""
        #calculate the norm of the future position of the bat relative to the center of its movement circle, and return if the distance is less than the maximum distance it can goes away from the center (i.e. self.radius_movement)
        relative_pos: tuple[float, float] = (
            self.center_x + self.dir[0] * delta_time - self.start[0],
            self.center_y + self.dir[1] * delta_time - self.start[1],
        )
        start_dis = m.sqrt(relative_pos[0] ** 2 + relative_pos[1] ** 2)
        return start_dis <= self.radius_movement

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        variation_angle: float = random.randint(-10, 10) * m.pi/2 * delta_time
        #the bat changes angle  by a random angle between -pi/12 and pi/12, by steps of pi/120
        self.v_phi += variation_angle
        if not self.canmove:
            # if it is at the edge of the circle, go back inside
            self.v_phi += m.pi
        self.change_x, self.change_y = self.dir
        if self.change_x*self.scale_x > 0 and abs(self.change_x) > 15*delta_time:
            #to keep the sprite loking in the direction the bat faces, but it has to move fast enough to turn so its not turning constantly when the speed is around 0
            self.scale_x*= -1

        super().update(delta_time, **kwargs)


class Slime(Monster):
    direction: int
    gameover_sound: arcade.Sound
    """Sound for when player touches the slime
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(
            ":resources:/images/enemies/slimeBlue.png", 100, 10, map, **kwargs
        )
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
        self.change_x = -1
        self.direction = -1

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        if not self.check_collision(
            Dir.down
        ):  # if there is no ground under slimey, slimey cannot change direction and keep its inertia (little to no friction in this world)
            super().update(delta_time, **kwargs)
            return
        if (
            self.check_collision(Dir.face) or not self.check_collision(Dir.facedown)
        ):  # if there is a collider or no ground in front of slimey, it cannot go further and must turn over
            self.change_x *= -1
            self.direction *= -1
            if (
                self.change_x != 0
            ):  # if slimey is not moving cause it's stuck, we don't want it to change direction every frames (i.e. making it unnoticeable for the player)
                self.scale_x *= -1
            if (
                self.check_collision(Dir.face) or not self.check_collision(Dir.facedown)
            ):  # if there is also a collider or no ground to the other side of slimey, it cannot move anymore, thus starting a depression
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        elif (
            self.change_x == 0
        ):  # if slimey was in depression (i.e. not moving) and the space in front of it or at its back is freed, it goes out of its depression and starts moving again
            self.change_x = self.direction  # N.B. when we arrive at this part of the code (if we reach it), we already make sure that slimey can move in the direction he his looking (stocked with self.direction)
            if (
                self.scale_x * self.direction < 0
            ):  # when slimey was stuck, self.direction kept its directions changes, but the sprite was frozen to prevent it to change orientation every frames. now we accord the sprite orientation to self.direction so it's not gonna start moonwalking
                self.scale_x *= -1
            super().update(delta_time, **kwargs)
            return
        super().update(delta_time, **kwargs)
