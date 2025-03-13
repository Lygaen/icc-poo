from typing import Any
import arcade
from enum import Enum

from src.entities.gameobject import GameObject, DamageSource
from src.res.map import Map

class Dir(Enum):                #this is an enumeration type of cardinal directions, which will be used to check for hitboxes in the immediate neighborhood of the slime along the chosen direction
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
    direction : int
    gameover_sound: arcade.Sound
    HP: float
    __base_damage: float
    """Sound for when player touches the slime
    """

    def __init__(self, texture: str, base_HP: float, base_damage: float, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, texture, **kwargs)
        self.HP = base_HP
        self.__base_damage = base_damage

    def check_collision(self, dir : Dir)-> bool:
        """To check if there is a collider in the immediate neighborhood of the slime along a certain direction (in argument)
        """
        circle = arcade.SpriteCircle(1, arcade.color.WHITE)         #create a little circle, which we will place in the zone where we want to check for collisions. this allows us to check collisions on more precise parts of the sprite, and not always the sprite in a whole
        match dir:                                                  #place the little circle at the extremity of the sprite in the direction wanted. for the diagonals, put it a little further than the edges of the hitboxes so the result is not corrupted by the potentials colliders under and on the sides (but not diagonally) of the slime
            case Dir.down:
                circle.position = (self.position[0], self.position[1] - self.size[1]//2)
            case Dir.face:
                circle.position = (self.position[0] + self.scale_x*self.direction*self.size[0]//2, self.position[1])
            case Dir.facedown:
                circle.position = (self.position[0] + self.scale_x*self.direction*(self.size[0]//2 + 2), self.position[1] - self.size[1]//2 - 1)
            case _:
                #pas encore implémenté (pas de besoin pour le moment)
                return False
        return (len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) != 0)        #return true if there is at least one collider in collision with the little circle, false otherwise

    def on_damage(self, source: DamageSource, damage: float) -> None:
        if source == DamageSource.PLAYER:
            self.HP -= damage

        if self.HP <= 0:
            self.destroy()

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        for object in self.map.check_for_collisions_all(self):       #if slimey touches player, player dies
            object.on_damage(DamageSource.MONSTER, self.__base_damage * delta_time)

        super().update(delta_time, *args, **kwargs)

class Slime(Monster):
    direction: int
    gameover_sound: arcade.Sound
    """Sound for when player touches the slime
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(":resources:/images/enemies/slimeBlue.png", 100, 10, map, **kwargs)
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
        self.change_x = -1
        self.direction = -1

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        if not self.check_collision(Dir.down):      #if there is no ground under slimey, slimey cannot change direction and keep its inertia (little to no friction in this world)
            super().update(delta_time, **kwargs)
            return
        if self.check_collision(Dir.face) or not self.check_collision(Dir.facedown):        #if there is a collider or no ground in front of slimey, it cannot go further and must turn over
            self.change_x *= -1
            self.direction *= -1
            if self.change_x != 0:      #if slimey is not moving cause it's stuck, we don't want it to change direction every frames (i.e. making it unnoticeable for the player)
                self.scale_x *= -1
            if self.check_collision(Dir.face) or not self.check_collision(Dir.facedown):    #if there is also a collider or no ground to the other side of slimey, it cannot move anymore, thus starting a depression
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        elif self.change_x == 0:                                                            #if slimey was in depression (i.e. not moving) and the space in front of it or at its back is freed, it goes out of its depression and starts moving again
            self.change_x = self.direction                                                  #N.B. when we arrive at this part of the code (if we reach it), we already make sure that slimey can move in the direction he his looking (stocked with self.direction)
            if self.scale_x*self.direction < 0:     #when slimey was stuck, self.direction kept its directions changes, but the sprite was frozen to prevent it to change orientation every frames. now we accord the sprite orientation to self.direction so it's not gona start moonwalking
                self.scale_x *= -1
            super().update(delta_time, **kwargs)
            return
        super().update(delta_time, **kwargs)
