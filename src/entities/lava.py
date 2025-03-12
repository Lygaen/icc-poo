from typing import Any
import arcade

from src.entities.gameobject import GameObject, DamageSource
from src.res.map import Map

class Lava(GameObject):
    """The lava object, currently only resets the map
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/tiles/lava.png", **kwargs)
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)

        for item in self.map.check_for_collisions_all(self):
            item.on_damage(DamageSource.LAVA, 1.0)