from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

CHAR_INFO: dict[str, str] = {
        "=": ":resources:/images/tiles/grassMid.png",
        "-": ":resources:/images/tiles/grassHalf_mid.png",
        "x": ":resources:/images/tiles/boxCrate_double.png",
    }

class Wall(GameObject):
    def __init__(self, map: Map, representation: str, **kwargs: Any) -> None:
        super().__init__(map, CHAR_INFO.get(representation), **kwargs)