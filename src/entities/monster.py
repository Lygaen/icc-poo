from typing import Any
import arcade
from enum import Enum

from src.entities.gameobject import GameObject
from src.res.map import Map
class Dir(Enum):
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

    def __init__(self, map: Map, **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/enemies/slimeBlue.png", **kwargs)
        self.change_x = -1
        self.direction = -1
    
    def check_collision(self, dir : Dir)-> bool:
        circle = arcade.SpriteCircle(1, arcade.color.WHITE)
        match dir:
            case Dir.down:
                circle.position = (self.position[0], self.position[1] - self.size[1]//2)
            case Dir.face:
                circle.position = (self.position[0] + self.direction*self.size[0]//2, self.position[1])
            case Dir.facedown:
                circle.position = (self.position[0] + self.direction*(self.size[0]//2 + 2), self.position[1] - self.size[1]//2 - 1)
            case _:
                #pas encore implémenté (pas de besoin pour le moment)
                return False
        return (len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) != 0)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        if not self.check_collision(Dir.down):
            super().update(delta_time, **kwargs)
            return
        if self.check_collision(Dir.face):
            self.change_x *= -1
            if self.check_collision(Dir.face):
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        if not self.check_collision(Dir.facedown):
            self.change_x *= -1
            if not self.check_collision(Dir.facedown):
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        elif self.change_x == 0:
            self.change_x = self.direction
            super().update(delta_time, **kwargs)
            return
        super().update(delta_time, **kwargs)












