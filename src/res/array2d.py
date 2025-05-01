from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Self


@dataclass
class Array2D[T]:
    data: list[list[T]]

    def items(self: Self) -> Iterator[tuple[T, int, int]]:
        for y, row in enumerate(self.data):
            for x, item in enumerate(row):
                yield (item, x, y)

    def in_bounds(self: Self, position: tuple[int, int]) -> bool:
        return (
            len(self.data) > position[1] and len(self.data[position[1]]) > position[0]
        )

    def at(self: Self, position: tuple[int, int]) -> T | None:
        return self.data[position[1]][position[0]] if self.in_bounds(position) else None

    class Direction(Enum):
        N = (0, 1)
        NE = (1, 1)
        E = (1, 0)
        SE = (1, -1)
        S = (0, -1)
        SW = (-1, -1)
        W = (-1, 0)
        NW = (-1, 0)

    def at_position_with_direction(
        self: Self, position: tuple[int, int], dir: Direction
    ) -> T | None:
        return self.at((position[0] + dir.value[0], position[1] + dir.value[1]))

    @staticmethod
    def from_size[V](width: int, height: int, val: V) -> Array2D[V]:
        return Array2D([[val for i in range(width)] for y in range(height)])

CARDINAUX : dict[Array2D.Direction, str] = {Array2D.Direction.N : "↑", Array2D.Direction.S : "↓", Array2D.Direction.E : "→", Array2D.Direction.W : "←"}
class Path:

    __current : int
    __positions : list[tuple[int, int]]
    __direction : int


    def __init__(self, map : Array2D[str], pos : tuple[int, int]) -> None:
        if not self.is_valid(map, pos):
            raise ValueError("Block has non-valid movement (incorrect nearby arrows on map)")
        up : list[tuple[int, int]] = self.dir_path(map, pos, Array2D.Direction.N) + self.dir_path(map, pos, Array2D.Direction.E) 
        down : list[tuple[int, int]] = self.dir_path(map, pos, Array2D.Direction.S) + self.dir_path(map, pos, Array2D.Direction.W)
        down.reverse()
        self.__positions = down + [pos] + up
        self.__current = len(down)
        if len(self.__positions) == 1:
            self.__direction = 0
        else:
            self.__direction = 1
        
    @property
    def current(self) -> int:
        return self.__current 
    @property
    def positions(self) -> list[tuple[int, int]]:
        return self.__positions
    @property
    def direction(self) -> int:
        return self.__direction 

    def is_valid(self, map : Array2D[str], pos : tuple[int, int]) -> bool:
        directions : dict[Array2D.Direction, bool] = {dir : (map.at_position_with_direction(pos, dir) == CARDINAUX[dir]) for dir in CARDINAUX}
        if (directions[Array2D.Direction.N]+directions[Array2D.Direction.S])*(directions[Array2D.Direction.E]+directions[Array2D.Direction.W]) != 0:
            return False
        return True

    def dir_path(self, map : Array2D[str], pos : tuple[int, int], dir : Array2D.Direction) -> list[tuple[int, int]]:
        next : tuple[int, int] = (pos[0] + dir.value[0], pos[1] + dir.value[1])
        if map.at_position_with_direction(next, dir) is CARDINAUX[dir]:
            return [next] + self.dir_path(map, next, dir)
        else:
            return []

    def next_idx(self) -> int:
        if not (len(self.positions) > self.current + self.direction >= 0):
            self.__direction *= -1
        return self.current + self.direction
    
    def next(self) -> tuple[int, int]:
        current = self.next_idx()
        return self.positions[current]


