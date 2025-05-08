from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.array2d import Array2D, Path
from src.res.map import Map

CHAR_INFO: dict[str, str] = {
    "=": ":resources:/images/tiles/grassMid.png",
    "-": ":resources:/images/tiles/grassHalf_mid.png",
    "x": ":resources:/images/tiles/boxCrate_double.png",
    "E": ":resources:/images/tiles/signExit.png",
    "£": ":resources:/images/tiles/lava.png",
    "^": ":resources:/images/tiles/leverLeft.png",
}
"""The char to resource dictionary for the different
representations.
"""

class MovingPlatform(GameObject):
    """All moving platforms encapsulating type
    """
    path: Path
    """The internal path of a block
    """
    old: tuple[int, int]
    """The old coordinate that it lerps from
    """
    target: tuple[int, int]
    """The target coordinate that it lerps to
    """
    time: float
    """The current lerping time 0 < time < 1
    """

    def __init__(
        self, map: list[Map], representation: str, data: Array2D[str], pos: tuple[int, int], **kwargs: Any
    ) -> None:
        super().__init__(map, CHAR_INFO.get(representation), **kwargs)
        self.time = 0
        self.path = Path(data, pos)
        self.old = self.map.map_to_world(pos)
        self.target = self.map.map_to_world(self.path.go_next())

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        self.time += delta_time
        pos = arcade.Vec2(self.old[0], self.old[1]).lerp(
            arcade.Vec2(self.target[0], self.target[1]), self.time
        )
        self.change_x = pos.x - self.position[0]
        self.change_y = pos.y - self.position[1]

        if self.time >= 1:
            self.time = 0
            self.old = self.target
            self.target = self.map.map_to_world(self.path.go_next())


class Exit(MovingPlatform):
    """Exit sign, allowing the player to move to the next stage on touch."""

    __next_map: str
    """Path to the next map, passed to the map object.
    """

    def __init__(self, map: list[Map], next_map: str,data: Array2D[str], pos: tuple[int, int], **kwargs: Any) -> None:
        """Initializes the wall using the map and representation.

        Args:
            map (Map): The map of the GO
            next_map (str): The path to the next map
        """
        super().__init__(map, "E", data, pos, **kwargs)
        self.__next_map = next_map

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, *args, **kwargs)
        super(GameObject, self).update(delta_time, **kwargs)

        if arcade.check_for_collision(self, self.map.player):
            self.map.change_maps(self.__next_map)

class Lava(MovingPlatform):
    """The lava object, currently only resets the map"""

    def __init__(self, map: list[Map], data: Array2D[str], pos: tuple[int, int], **kwargs: Any) -> None:
        super().__init__(map, "£", data, pos, **kwargs)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)
        super(GameObject, self).update(delta_time, **kwargs)

        for item in self.map.check_for_collisions_all(self):
            item.on_damage(DamageSource.LAVA, 1.0)
