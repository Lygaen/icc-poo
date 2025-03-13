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

    def __init__(self, map: list[Map], representation: str, **kwargs: Any) -> None:
        """Initializes the wall using the map and representation.

        Args:
            map (Map): The map of the GO
            representation (str): The string representation of the wall,
            if invalid, will default to a NO_TEXTURE
        """
        super().__init__(map, CHAR_INFO.get(representation), **kwargs)

class Exit(GameObject):
    """Exit sign, allowing the player to move to the next stage on touch.
    """
    __next_map: str
    """Path to the next map, passed to the map object.
    """

    def __init__(self, map: list[Map], next_map: str, **kwargs: Any) -> None:
        """Initializes the wall using the map and representation.

        Args:
            map (Map): The map of the GO
            next_map (str): The path to the next map
        """
        super().__init__(map, ":resources:/images/tiles/signExit.png", **kwargs)
        self.__next_map = next_map

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)

        if arcade.check_for_collision(self, self.map.player):
            self.map.change_maps(self.__next_map)
