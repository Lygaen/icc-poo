from typing import Any

import arcade

from src.entities.gameobject import GameObject
from src.res.array2d import Array2D, Path
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
    """Generic wall object. Wall that does NOTHING. NADA. ZERO."""

    def __init__(self, map: list[Map], representation: str, **kwargs: Any) -> None:
        """Initializes the wall using the map and representation.

        Args:
            map (Map): The map of the GO
            representation (str): The string representation of the wall,
            if invalid, will default to a NO_TEXTURE
        """
        super().__init__(map, CHAR_INFO.get(representation), **kwargs)


class MovingPlatform(GameObject):
    path: Path
    old: tuple[int, int]
    target: tuple[int, int]
    time: float

    def __init__(
        self, map: list[Map], data: Array2D[str], pos: tuple[int, int], **kwargs: Any
    ) -> None:
        super().__init__(map, CHAR_INFO.get("x"), **kwargs)
        self.time = 0
        self.path = Path(data, pos)
        self.old = self.map.map_to_world(pos)
        self.target = self.map.map_to_world(self.path.next())

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        self.time += delta_time
        pos = arcade.Vec2(self.old[0], self.old[1]).lerp(
            arcade.Vec2(self.target[0], self.target[1]), self.time
        )
        self.position = (pos.x, pos.y)
        super().update(delta_time, *args, **kwargs)


class Exit(GameObject):
    """Exit sign, allowing the player to move to the next stage on touch."""

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
