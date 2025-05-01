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
