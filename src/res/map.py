from __future__ import annotations

import itertools
import json
import typing
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterator, cast

import arcade
import yaml

from src.res.array2d import Array2D

# MyPy shenanigans for cycle deps, sorry future me ;(
# EDIT : Yeah, be sorry >:(
if typing.TYPE_CHECKING:
    from src.entities.gameobject import GameObject
    from src.entities.player import Player
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
    player: Player
    """The player gameobject. *SHOULD* only be modified internally.
    """
    player_spawn_point: arcade.types.Point2
    """The player spawn point as described in the map.
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

    def __init__(
        self, view: list[GameView], path: str, first_load: bool = True
    ) -> None:
        """Initializes the map with a given path

        Args:
            view (list[GameView]): just pass in self. Make a reference to the parent game view.
            path (str): The path of the map, starting from the "assets/maps"
            folder
        """
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.__game_view_ref = view

        if first_load:
            self.reload()

    def draw(self) -> None:
        """Draw the map and all sub-objects"""
        self.__physics_objects.draw()
        self.__passthrough_objects.draw()

    def update(self, delta_time: float) -> None:
        """Updates the map and all sub-objects given the delta
        time between this frame and the last

        Args:
            delta_time (float): the delta in time between this frame
            and the last
        """
        self.__physics_objects.update(delta_time)
        self.physics_engine.update()
        self.__passthrough_objects.update(delta_time)

    @property
    def game_objects(self) -> Iterator[GameObject]:
        """All game objects, indefferent of type or the list
        they are in.

        Yields:
            Iterator[GameObject]: Iterator to loop through the gameobjects
        """
        return itertools.chain(self.__passthrough_objects, self.__physics_objects)

    @property
    def event_listeners(self) -> Iterator[GameObject]:
        """Event listener filtered game objects.
        Iterator to loop over all game objects that explicitly
        ask to listen for windows events.

        Yields:
            Iterator[GameObject]: Iterator to loop through event listeners
        """

        return filter(lambda obj: obj.event_listener, self.game_objects)

    def check_for_collisions_all(self, object: GameObject) -> list[GameObject]:
        """Checking for collisions, optimizing with spatial-hashing.
        This is the better way to check collision against anything.

        Args:
            object (GameObject): The target gameobject to check collisions against

        Returns:
            list[GameObject]: A list of all colliding gameobjects
        """
        return arcade.check_for_collision_with_lists(
            object, [self.__passthrough_objects, self.__physics_objects]
        )

    def change_maps(self, path: str) -> None:
        """Change maps based on a path to the new map"""
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.reload()

    def reload(self) -> None:
        """Reloads the map, player and engine

        Raises:
            ValueError: The map was not found on disk
        """

        if not self.__path.exists():
            raise ValueError(f"Map '{self.__path}' was not found on disk")

        content: str
        with self.__path.open("r", encoding="utf-8") as file:
            content = "".join(file.readlines())
            self.force_load_map(content)

    def respawn_player(self) -> None:
        """Respawns the player instead of full reloading the map."""
        if hasattr(self, "player"):
            self.player.destroy()

        from src.entities.player import Player

        self.player = Player(
            [self],
            scale=self.__GRID_SCALE,
            center_x=self.player_spawn_point[0],
            center_y=self.player_spawn_point[1],
        )
        self.__passthrough_objects.append(self.player)
        self.physics_engine.player_sprite = self.player

    def force_load_map(self, full_map_str: str) -> None:
        """Forces loading a map from a string instead of
        from a map path.
        """
        self.__physics_objects = arcade.SpriteList(use_spatial_hash=True)
        self.__passthrough_objects = arcade.SpriteList(use_spatial_hash=True)

        content = full_map_str.split("---", 1)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            arcade.Sprite(),
            walls=self.__physics_objects,
            gravity_constant=self.__GRAVITY_CONSTANT,
        )

        info = self.__parse_header(content[0])
        self.__parse_map(content[1], info)

        self.physics_engine.walls.clear()
        self.physics_engine.platforms.clear()
        self.physics_engine.platforms.append(self.__physics_objects)

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

    def map_to_world(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Converts from a coordinate in map-space to world space"""
        return (pos[0] * self.__GRID_SIZE, pos[1] * self.__GRID_SIZE)

    def __parse_map(
        self, map: str, info: Metadata, start: arcade.Vec2 = arcade.Vec2(0, 0)
    ) -> None:
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
        from src.entities.coin import Coin
        from src.entities.gates_lever import Gate, Switch
        from src.entities.monster import Bat, DarkBat, Slime
        from src.entities.wall import Exit, Lava, MovingPlatform

        lines = map.splitlines()  # Lines includes "---"

        if len(lines) - 2 > info.height:
            raise ValueError("Invalid map height")

        lines = lines[1:-1]  # Remove "---"
        lines.reverse()  # So that we loop bottom-up
        array = Array2D.from_size(info.width, info.height, " ")

        for y, line in enumerate(lines):
            if len(line) > info.width:
                raise ValueError(
                    f"Invalid map width at line {y}, for width {len(line)} (expected {info.width})"
                )

            for x, char in enumerate(line):
                array.data[y][x] = char

        for char, x, y in array.items():
            pos = start + self.map_to_world((x, y))

            # The following is *pretty* ugly. Because arcade
            # doesn't have a proper way to store dynamic values
            # at runtime, I wanted to create a Gameobject system.
            # So the following needs to be that way until I find
            # a better way to handle things.
            # I may come back later to refactor it. maybe. might.

            match char:
                case "S":
                    self.player_spawn_point = (pos.x, pos.y)
                    self.respawn_player()
                case "^":
                    self.__passthrough_objects.append(
                        Switch(
                            [self],
                            info,
                            array,
                            (x, y),
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "|":
                    gate = Gate(
                        [self],
                        info,
                        (x, y),
                        scale=self.__GRID_SCALE,
                        center_x=pos.x,
                        center_y=pos.y,
                    )
                    if gate.isOpen:
                        self.__passthrough_objects.append(gate)
                    else:
                        self.__physics_objects.append(gate)
                case "o":
                    self.__passthrough_objects.append(
                        Slime(
                            [self],
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "w":
                    self.__passthrough_objects.append(
                        Bat(
                            [self],
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "W":
                    self.__passthrough_objects.append(
                        DarkBat(
                            [self],
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "*":
                    self.__passthrough_objects.append(
                        Coin(
                            [self],
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "£":
                    self.__passthrough_objects.append(
                        Lava(
                            [self],
                            array,
                            (x, y),
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )
                case "x" | "=" | "-":
                    self.__physics_objects.append(
                        MovingPlatform(
                            [self],
                            char,
                            array,
                            (x, y),
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )

                case "#":
                    pass
                case "E":
                    if info.next_map is None:
                        raise ValueError("Found exit but no next_map !")
                    self.__passthrough_objects.append(
                        Exit(
                            [self],
                            info.next_map,
                            array,
                            (x, y),
                            scale=self.__GRID_SCALE,
                            center_x=pos.x,
                            center_y=pos.y,
                        )
                    )

    class Metadata:
        """Metadata of the map, parsed from the header.
        Only used internally to pass information functions to functions.
        """

        width: int
        """Width of the map in character
        """
        height: int
        """Height of the map in character
        """
        next_map: str | None
        """Relative path to the next map, None if none (lol)
        """

        def __init__(self, dict_: dict[str, Any]):
            self.__dict__.update(dict_)

        class GatePosition:
            """The gate metadata"""

            x: int
            """The gate x position in world coordinate
            """
            y: int
            """The gate y position in world coordinate
            """

            class State(StrEnum):
                """Whether a gate is opened or closed"""

                open = "open"
                closed = "closed"

            state: State
            """The default state of a gate
            """

        gates: list[GatePosition] | None = None
        """The list of gates represented in the header
        """

        class SwitchPosition:
            """The switch metadata"""

            x: int
            """The x position of the switch
            """
            y: int
            """The y position of the switch
            """

            class State(StrEnum):
                """State of the lever (on/off)"""

                on = "on"
                off = "off"

            state: State = State.off
            """Default state of the lever, defaults to off if not
            specified
            """

            class Action:
                """Action of a lever"""

                class Kind(StrEnum):
                    """The action kind of a lever"""

                    open_gate = "open-gate"
                    close_gate = "close-gate"
                    disable = "disable"

                action: Kind
                """What the lever does in kind
                """
                x: int
                """The gate affected if specified, in map x coordinate
                """
                y: int
                """The gate affected if specified, in map y coordinate
                """

            switch_on: list[Action] | None = None
            """The action to act on when the lever is turned on
            """
            switch_off: list[Action] | None = None
            """The action to act on when the lever is turned off
            """

        switches: list[SwitchPosition] | None = None
        """The list of switches in the map
        """

    def __parse_header(self, header: str) -> Metadata:
        """Parses the header from the string, returning
        the metadata of the parsed header.

        Args:
            header (str): The header to parse from

        Raises:
            ValueError: An unkown variable was found

        Returns:
            Metadata: The header
        """
        d = yaml.safe_load(header)
        return cast(Map.Metadata, json.loads(json.dumps(d), object_hook=Map.Metadata))

    def destroy(self, object: GameObject) -> None:
        """Destroys a given gameobject from the map

        Args:
            object (GameObject): The object to destroy
        """
        if object in self.__passthrough_objects:
            self.__passthrough_objects.remove(object)
        if object in self.__physics_objects:
            self.__physics_objects.remove(object)

    def add_objects(self, objects: list[GameObject], is_physics: bool = False) -> None:
        """Adds an object to the map

        Args:
            objects (list[GameObject]): the objects to add
            is_physics (bool, optional): whether the object should have collisions. Defaults to False.
        """
        if is_physics:
            for obj in objects:
                self.__physics_objects.append(obj)
        else:
            for obj in objects:
                self.__passthrough_objects.append(obj)
