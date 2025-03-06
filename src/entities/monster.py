from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

class Monster(GameObject):
    def __init__(self, map: Map, **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/enemies/slimeBlue.png", **kwargs)
    
    

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        down = (self.position[0], self.position[1] - self.size[1]//2)
        face = (self.position[0] + self.change_x*self.size[0]//2, self.position[1])
        facedown = (self.position[0] + self.change_x*(self.size[0]//2 + 2), self.position[1] - self.size[1]//2 - 1)
        circle = arcade.SpriteCircle(1, arcade.color.WHITE)
        circle.position = down
        if len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) == 0:
            super().update(delta_time, **kwargs)
            return
        circle.position = face
        if len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) != 0:
            self.change_x *= -1
            face = (self.position[0] + self.change_x*self.size[0]//2, self.position[1])
            circle.position = face
            if len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) != 0:
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        circle.position = facedown
        if len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) == 0:
            self.change_x *= -1
            facedown = (self.position[0] + self.change_x*(self.size[0]//2 + 2), self.position[1] - self.size[1]//2 - 1)
            circle.position = facedown
            if len(arcade.check_for_collision_with_list(circle, self.map.physics_colliders_list)) == 0:
                self.change_x *= 0
            super().update(delta_time, **kwargs)
            return
        elif self.change_x == 0:
            self.change_x = -1
            super().update(delta_time, **kwargs)
            return
        super().update(delta_time, **kwargs)












