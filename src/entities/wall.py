from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

CHAR_INFO: dict[str, str] = {
    "=": ":resources:/images/tiles/grassMid.png",
    "-": ":resources:/images/tiles/grassHalf_mid.png",
    "x": ":resources:/images/tiles/boxCrate_double.png",
}
"""The char to resource dictionary for the different
representations.
"""

class Wall(GameObject):
    """Generic wall object. Wall that does NOTHING. NADA. ZERO.
    """

    def __init__(self, map: Map, representation: str, **kwargs: Any) -> None:
        """Initializes the wall using the map and representation.

        Args:
            map (Map): The map of the GO
            representation (str): The string representation of the wall,
            if invalid, will default to a NO_TEXTURE
        """
        super().__init__(map, CHAR_INFO.get(representation), **kwargs)