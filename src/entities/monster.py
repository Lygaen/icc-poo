from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

class Monster(GameObject):
    def __init__(self, map: Map, **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/enemies/slimeBlue.png", **kwargs)
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)