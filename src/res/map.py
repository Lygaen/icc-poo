from __future__ import annotations

import itertools
import arcade
from pathlib import Path
from enum import Enum
from typing import Iterator, Self, cast
import typing

if typing.TYPE_CHECKING:
    from src.entities.gameobject import GameObject

arcade.resources.add_resource_handle("maps", Path("./assets/maps/").resolve())

class Map:
    __path: Path
    __physics_objects: arcade.SpriteList[GameObject]
    __passthrough_objects: arcade.SpriteList[GameObject]
    physics_engine: arcade.PhysicsEnginePlatformer
    player: GameObject

    class ObjectType(Enum):
        WALL = 1
        COIN = 2
        MONSTER = 3
        NOGO = 4
        START = 5

        @classmethod
        def from_representation(cls, value: str) -> Self:
            match value:
                case "=" | "-" | "x":
                    return cast(Self, cls.WALL)
                case "*":
                    return cast(Self, cls.COIN)
                case "o":
                    return cast(Self, cls.MONSTER)
                case "£":
                    return cast(Self, cls.NOGO)
                case "S":
                    return cast(Self, cls.START)
                case _:
                    raise ValueError(f"Invalid '{value}' for ObjectType enum")

    __GRID_SIZE = 64
    __GRID_SCALE = 0.5

    def __init__(self, path: str):
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.reload()
    
    def draw(self) -> None:
        self.__physics_objects.draw()
        self.__passthrough_objects.draw()

    def update(self, delta_time: float) -> None:
        self.physics_engine.update()
        self.__physics_objects.update(delta_time, map=self)
        self.__passthrough_objects.update(delta_time, map=self)

    @property
    def game_objects(self) -> Iterator[GameObject]:
        return itertools.chain(self.__passthrough_objects, self.__physics_objects)
    
    def reload(self) -> None:
        if not self.__path.exists():
            raise ValueError(f"Map '{self.__path}' was not found on disk")
        
        self.__physics_objects = arcade.SpriteList(use_spatial_hash=True)
        self.__passthrough_objects = arcade.SpriteList(use_spatial_hash=True)
        
        content: list[str]
        with self.__path.open("r", encoding="utf-8") as file:
            content = ["".join(file.readlines())]
            content = content[0].split("---", 1) # Split between header (0), map (1)
        
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            arcade.Sprite(),
            walls=self.__physics_objects,
            gravity_constant=1,
        )
        
        size = self.__parse_header(content[0])
        self.__parse_map(content[1], size)

        self.physics_engine.player_sprite = self.player
        self.physics_engine.walls.clear()
        self.physics_engine.walls.append(self.__physics_objects)
    
    @property
    def physics_colliders_list(self) -> arcade.SpriteList[GameObject]:
        return self.__physics_objects
    
    def __parse_map(self, map: str, size: arcade.Vec2, start: arcade.Vec2 = arcade.Vec2(0,0)) -> None:
        from src.entities.player import Player
        from src.entities.coin import Coin
        from src.entities.lava import Lava
        from src.entities.wall import Wall
        from src.entities.monster import Monster
        
        lines = map.splitlines()

        if len(lines) - 2 > size.y:
            raise ValueError("Invalid map height")
        
        lines = lines[1:-1]
        lines.reverse() # So that we loop bottom-up

        for y, line in enumerate(lines):
            if len(line) > size.x:
                raise ValueError(f"Invalid map width at line {y}")
            for x, char in enumerate(line):
                if char == " ":
                    continue

                pos = start + arcade.Vec2(x * self.__GRID_SIZE, y * self.__GRID_SIZE)
                objType = Map.ObjectType.from_representation(char)

                match objType:
                    case Map.ObjectType.START:
                        player = Player(
                                self,
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y)
                        self.__passthrough_objects.append(player)
                        self.player = player
                    case Map.ObjectType.MONSTER:
                        self.__passthrough_objects.append(Monster(self, 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.COIN:
                        self.__passthrough_objects.append(Coin(self, 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.NOGO:
                        self.__passthrough_objects.append(Lava(self,
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.WALL:
                        self.__physics_objects.append(Wall(self, char, 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))

    def __parse_header(self, header: str) -> arcade.Vec2:
        width: int
        height: int
        for line in header.splitlines():
            if line.lstrip() == "":
                continue
            vname = line.split(":", 1)[0]
            vvalue = line.split(":", 1)[1]

            match vname:
                case "width":
                    width = int(vvalue)
                case "height":
                    height = int(vvalue)
                case _:
                    raise ValueError(f"Unkown variable field name '{vname}' in map")
        
        return arcade.Vec2(width, height)

    def destroy(self, object: GameObject) -> None:
        for obj in self.__passthrough_objects:
            if obj == object:
                self.__passthrough_objects.remove(object)
                return
        
        for obj in self.__physics_objects:
            if obj == object:
                self.__passthrough_objects.remove(object)
                return
