from __future__ import annotations

import itertools
import arcade
from pathlib import Path
from enum import Enum
from typing import Iterator, Self, cast
import typing

# MyPy shenanigans for cycle deps, sorry future me ;(
# EDIT : Yeah, be sorry >:(
if typing.TYPE_CHECKING:
    from src.entities.gameobject import GameObject
    from src.gameview import GameView

arcade.resources.add_resource_handle("maps", Path("./assets/maps/").resolve())

class Map:
    """The main class handling :
    - Map Loading
    - GameObject registry
    - Full-map drawing and updating

    See the relevant functions for details
    """

    __path: Path
    """The Path to the map on disk
    """

    __physics_objects: arcade.SpriteList[GameObject]
    """The list of objects that should be checked for collisions,
    meaning that they can be walked on. This is used mainly because
    physics engine needs a sprite list in its constructor
    """

    __passthrough_objects: arcade.SpriteList[GameObject]
    """The list of objects that are not used for collisions on the
    physics engine. All other objects.
    """

    physics_engine: arcade.PhysicsEnginePlatformer
    """The physics engine that handles gravity and collisions
    for the player.
    """
    player: GameObject
    """The player gameobject. *SHOULD* only be modified internally.
    """

    __game_view_ref: list[GameView]
    """Using list to have a reference to the game view. *Should* only
    be accessed from the game_view property
    """

    @property
    def game_view(self) -> GameView:
        """Gives the game view in which the map was created.

        Returns:
            GameView: The parent game view
        """
        return self.__game_view_ref[0]


    class ObjectType(Enum):
        """The type of object to be added on the sprite list.
        Currently depends on the map format.

        Types are pretty self-explanatory, with the details of :
        - NOGO is currently only lava
        - START is the starting point of the player
        """

        WALL = 1
        COIN = 2
        MONSTER = 3
        NOGO = 4
        START = 5

        @classmethod
        def from_representation(cls, value: str) -> Self:
            """Returns the ObjectType from the string representation

            Args:
                value (str): The string representation of the object type,
                See implementation details for which type are returned for
                which string.

            Raises:
                ValueError: If and only if the given representation is not
                defined for any type

            Returns:
                Self: The ObjectType in question
            """
            match value:
                case "=" | "-" | "x":
                    return cast(Self, cls.WALL) # Ugly cast, mypy is eating my sanity
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
    """The size of the grid in pixels.
    """
    __GRID_SCALE = 0.5
    """Grid sprite scalar aka. by how much the sprites are scaled
    to fit inside a grid block.
    """
    __GRAVITY_CONSTANT = 1
    """The gravity constant (in pixels) for the physics engine,
    to be applied each and every update frame.
    """

    def __init__(self, view: list[GameView], path: str) -> None:
        """Initializes the map with a given path

        Args:
            view (list[GameView]): just pass in self. Make a reference to the parent game view.
            path (str): The path of the map, starting from the "assets/maps"
            folder
        """
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.__game_view_ref = view
        self.reload()
    
    def draw(self) -> None:
        """Draw the map and all sub-objects
        """
        self.__physics_objects.draw()
        self.__passthrough_objects.draw()

    def update(self, delta_time: float) -> None:
        """Updates the map and all sub-objects given the delta
        time between this frame and the last

        Args:
            delta_time (float): the delta in time between this frame
            and the last
        """
        self.physics_engine.update()
        self.__physics_objects.update(delta_time)
        self.__passthrough_objects.update(delta_time)

    @property
    def game_objects(self) -> Iterator[GameObject]:
        """All game objects, indefferent of type or the list
        they are in.

        Yields:
            Iterator[GameObject]: Iterator to loop through the gameobjects
        """
        return itertools.chain(self.__passthrough_objects, self.__physics_objects)
    
    def check_for_collisions_all(self, object: GameObject) -> list[GameObject]:
        """Checking for collisions, optimizing with spatial-hashing.
        This is the better way to check collision against anything.

        Args:
            object (GameObject): The target gameobject to check collisions against

        Returns:
            list[GameObject]: A list of all colliding gameobjects
        """
        return arcade.check_for_collision_with_lists(object, [self.__passthrough_objects, self.__physics_objects])

    def reload(self) -> None:
        """Reloads the map, player and engine

        Raises:
            ValueError: The map was not found on disk
        """

        if not self.__path.exists():
            raise ValueError(f"Map '{self.__path}' was not found on disk")
        
        self.__physics_objects = arcade.SpriteList(use_spatial_hash=True)
        self.__passthrough_objects = arcade.SpriteList(use_spatial_hash=True)
        
        content: list[str]
        with self.__path.open("r", encoding="utf-8") as file:
            content = ["".join(file.readlines())]
            content = content[0].split("---", 1) # Split between header (0), map (1)
        
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            arcade.Sprite(), # Empty because we have yet to initialize the map
            walls=self.__physics_objects,
            gravity_constant=self.__GRAVITY_CONSTANT,
        )
        
        size = self.__parse_header(content[0])
        self.__parse_map(content[1], size)

        self.physics_engine.player_sprite = self.player
        self.physics_engine.walls.clear()
        self.physics_engine.walls.append(self.__physics_objects)
    
    @property
    def physics_colliders_list(self) -> arcade.SpriteList[GameObject]:
        """The physics colliders lists, aka. the gameobjects that
        the sprites should be checking against for collisions,
        blocks, ...

        Returns:
            arcade.SpriteList[GameObject]: The sprite list (may be changed
            to an iterator later)
        """
        return self.__physics_objects
    
    def __parse_map(self, map: str, size: arcade.Vec2, start: arcade.Vec2 = arcade.Vec2(0,0)) -> None:
        """Parses the map, initializing internals with the parsed data.

        Args:
            map (str): The map as the string representation
            size (arcade.Vec2): The size of the map
            start (arcade.Vec2, optional): The start of the player. Defaults to arcade.Vec2(0,0).

        Raises:
            ValueError: Invalid map height if the given size and map do not match
            ValueError: Invalid width if a line do not match the given size (line_width > size.x)
        """

        # Once again, loooooove mypy for it forcing me
        # to use runtime imports !
        from src.entities.player import Player
        from src.entities.coin import Coin
        from src.entities.lava import Lava
        from src.entities.wall import Wall
        from src.entities.monster import Slime
        
        lines = map.splitlines() # Lines includes "---"

        if len(lines) - 2 > size.y:
            raise ValueError("Invalid map height")
        
        lines = lines[1:-1] # Remove "---"
        lines.reverse() # So that we loop bottom-up

        for y, line in enumerate(lines):
            if len(line) > size.x:
                raise ValueError(f"Invalid map width at line {y}")
            for x, char in enumerate(line):
                if char == " ": # ~void~
                    continue

                pos = start + arcade.Vec2(x * self.__GRID_SIZE, y * self.__GRID_SIZE)
                objType = Map.ObjectType.from_representation(char)

                # The following is *pretty* ugly. Because arcade
                # doesn't have a proper way to store dynamic values
                # at runtime, I wanted to create a Gameobject system.
                # So the following needs to be that way until I find
                # a better way to handle things.
                # I may come back later to refactor it. maybe. might.
                match objType:
                    case Map.ObjectType.START:
                        player = Player(
                                [self],
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y)
                        self.__passthrough_objects.append(player)
                        self.player = player
                    case Map.ObjectType.MONSTER:
                        self.__passthrough_objects.append(Slime([self], 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.COIN:
                        self.__passthrough_objects.append(Coin([self], 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.NOGO:
                        self.__passthrough_objects.append(Lava([self],
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))
                    case Map.ObjectType.WALL:
                        self.__physics_objects.append(Wall([self], char, 
                                scale=self.__GRID_SCALE,
                                center_x=pos.x,
                                center_y=pos.y))

    def __parse_header(self, header: str) -> arcade.Vec2:
        """Parses the header from the string, returning
        the metadata of the parsed header.

        Args:
            header (str): The header to parse from

        Raises:
            ValueError: An unkown variable was found

        Returns:
            arcade.Vec2: The size of the header
        """
        width: int = 0
        height: int = 0
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
        """Destroys a given gameobject from the map

        Args:
            object (GameObject): The object to destroy
        """
        for obj in self.__passthrough_objects:
            if obj == object:
                self.__passthrough_objects.remove(object)
                return
        
        for obj in self.__physics_objects:
            if obj == object:
                self.__physics_objects.remove(object)
                return
