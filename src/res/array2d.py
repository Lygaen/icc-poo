from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Self

# Position : TypeAlias = tuple[int, int]
Position = tuple[int, int]


@dataclass
class Array2D[T]:
    data: list[list[T]]

    def items(self: Self) -> Iterator[tuple[T, int, int]]:
        for y, row in enumerate(self.data):
            for x, item in enumerate(row):
                yield (item, x, y)

    def in_bounds(self: Self, position: tuple[int, int]) -> bool:
        return (
            position[0] > 0
            and position[1] > 0
            and len(self.data) > position[1]
            and len(self.data[position[1]]) > position[0]
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


CARDINAUX: dict[Array2D.Direction, str] = {
    Array2D.Direction.N: "↑",
    Array2D.Direction.S: "↓",
    Array2D.Direction.E: "→",
    Array2D.Direction.W: "←",
}


class Path:
    __current: int
    __positions: list[Position]
    __direction: int

    def __init__(self, map: Array2D[str], pos: Position) -> None:
        self.__positions, self.__current = Path.truc(map, pos)

        if len(self.__positions) == 1:
            self.__direction = 0
        else:
            self.__direction = 1

    @property
    def current(self) -> int:
        return self.__current

    @property
    def positions(self) -> list[Position]:
        return self.__positions

    @property
    def direction(self) -> int:
        return self.__direction

    def next_idx(self) -> int:
        """calcule l'index suivant auquel se trouvera le block"""
        if not (len(self.positions) > self.current + self.direction >= 0):
            self.__direction *= -1
        return self.current + self.direction

    def next(self) -> Position:
        """retourne la prochaine position"""
        return self.positions[self.next_idx()]

    def go_next(self) -> Position:
        """avance le current au prochain index et retourne la nouvelle position"""
        self.__current = self.next_idx()
        return self.positions[self.current]

    @staticmethod
    def is_directions_dict_valid(directions: dict[Array2D.Direction, bool]) -> bool:
        """vérifie qu'un bloc n'ait pas de mouvement à la fois horizontal et vertical assigné, à partir d'un dictionnaire où pour chaque direction un bool nous dit si il y a ou non un mouvement dans cette direction-là"""
        # les bools se comportent comme des ints et du coup si le membre de gauche est non nul, alors il y a au moins
        # une direction verticale assignée, si le membre de droite est non nul, alors il y a au moins une direction
        # horizontale assignée, et donc si la multiplication des deux est non nulle on a assigné au moins une direction
        # horizontale et une verticale en même temps -> le chemin est invalide
        # (si ce n'est pas le cas, alors le chemin est valide)
        return (
            directions.get(Array2D.Direction.N, False)
            + directions.get(Array2D.Direction.S, False)
        ) * (
            directions.get(Array2D.Direction.E, False)
            + directions.get(Array2D.Direction.W, False)
        ) != 0

    @staticmethod
    def dir_path(
        map: Array2D[str], pos: Position, dir: Array2D.Direction
    ) -> list[Position]:
        """calcule et retourne le chemin total du block dans une direction, à partir des flèches qui lui sont directement connectées"""
        next: Position = (pos[0] + dir.value[0], pos[1] + dir.value[1])
        if map.at_position_with_direction(next, dir) == CARDINAUX[dir]:
            return [next] + Path.dir_path(map, next, dir)
        else:
            return []

    @staticmethod
    def group(
        map: Array2D[str], pos: Position, visited: set[Position] = set()
    ) -> set[Position]:
        """renvoie tous les blocs dans le même groupe que celui à la position pos"""
        visited.add(pos)
        neighbour: set[Position] = {pos}
        for dir in CARDINAUX:
            newpos: Position = (pos[0] + dir.value[0], pos[1] + dir.value[1])
            if (
                map.at_position_with_direction(pos, dir) in {"=", "-", "X", "E"}
                and newpos not in visited
            ):
                visited.add(newpos)
                neighbour = neighbour | {newpos} | Path.group(map, newpos, visited)
        return neighbour

    @staticmethod  # pour obtenir la liste des positions et l'index de départ
    def truc(
        map: Array2D[str],
        pos: Position,
    ) -> tuple[list[Position], int]:
        """renvoie la listes des positions que le bloc à la position pos prendra au cours du temps, ainsi que l'index de sa position initiale sur cette liste"""
        group: set[Position] = Path.group(map, pos)
        # pour garder en mémoire à la fois la liste de déplacement que subit le groupe dans une direction, mais aussi où,
        # pour pouvoir calculer les déplacements relatifs des autres blocs
        directions: dict[Array2D.Direction, tuple[list[Position], Position]] = {
            Array2D.Direction.N: ([], pos),
            Array2D.Direction.S: ([], pos),
            Array2D.Direction.E: ([], pos),
            Array2D.Direction.W: ([], pos),
        }
        for block in group:
            for dir in CARDINAUX:
                dir_path: list[Position] = Path.dir_path(map, block, dir)
                if dir_path != []:
                    if len(directions[dir][0]) != 0:
                        # si on arrive ici, alors on a deux poussées différentes dans la même direction sur le groupe de blocs => son mouvement n'est pas valide
                        raise ValueError(
                            "The group of blocks has an invalid movement setup"
                        )
                    directions[dir] = (dir_path, block)
        # vérifie si le groupe subit à la fois une poussée verticale et horizontale : si oui, c'est un problème
        if not Path.is_directions_dict_valid(
            {dir: len(directions[dir][0]) != 0 for dir in CARDINAUX}
        ):
            raise ValueError("The group of blocks has an invalid movement setup")
        # pour chaque direction, on calcule la liste des positions trouvées dans le groupe en rajoutant la position relative de pos à celle du bloc où les flèches ont étées trouvées
        paths: dict[Array2D.Direction, list[Position]] = {
            dir: [
                (
                    directions[dir][0][i][0] + directions[dir][1][0] - pos[0],
                    directions[dir][0][i][1] + directions[dir][1][1] - pos[1],
                )
                for i in range(len(directions[Array2D.Direction.N][0]))
            ]
            for dir in CARDINAUX
        }
        # comme le chemin est valide, au moins une des deux listes est vide. on obtient donc la liste des flèches de la direction dominante
        strong_path: list[Position] = (
            paths[Array2D.Direction.N] + paths[Array2D.Direction.E]
        )
        # comme le chemin est valide, au moins une des deux listes est vide. on obtient donc la liste des flèches de la direction secondaire
        weak_path: list[Position] = (
            paths[Array2D.Direction.S] + paths[Array2D.Direction.W]
        )
        # down part de la position, alors que nous on veut un mouvement uniforme, donc une liste qui va de la position la plus "faible" à la position la plus "forte"
        weak_path.reverse()
        return weak_path + [pos] + strong_path, len(weak_path)
