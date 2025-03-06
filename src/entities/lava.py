from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

class Lava(GameObject):
    """The lava object, currently only resets the map
    """
    gameover_sound: arcade.Sound
    """Sound for when player touches lava
    """

    def __init__(self, map: Map, **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/tiles/lava.png", **kwargs)
        self.gameover_sound = arcade.Sound(":resources:sounds/gameover1.wav")
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)

        if arcade.check_for_collision(self.map.player, self):
            arcade.play_sound(self.gameover_sound)
            self.map.reload()