import arcade
from pathlib import Path
from enum import Enum

arcade.resources.add_resource_handle("maps", Path("./assets/maps/").resolve())

MAP_GRID_SIZE = 64
MAP_SCALE_FACTOR = 0.5

class Map:
    __path: Path
    __player_pos: arcade.Vec2
    __walls: arcade.SpriteList[arcade.Sprite]
    __interactables: arcade.SpriteList[arcade.Sprite]

    class ObjectType(Enum):
        WALL = 1
        COIN = 2
        MONSTER = 3
        NOGO = 4
        START = 5

    MAP_CHAR_INFO: dict[str, tuple[str, ObjectType]] = {
        "=": (":resources:/images/tiles/grassMid.png", ObjectType.WALL),
        "-": (":resources:/images/tiles/grassHalf_mid.png", ObjectType.WALL),
        "x": (":resources:/images/tiles/boxCrate_double.png", ObjectType.WALL),
        "*": (":resources:/images/items/coinGold.png", ObjectType.COIN),
        "o": (":resources:/images/enemies/slimeBlue.png", ObjectType.MONSTER),
        "£": (":resources:/images/tiles/lava.png", ObjectType.NOGO),
        "S": (":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", ObjectType.START),
    }

    def __init__(self, path: str):
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.reload()
    
    def draw(self) -> None:
        self.__walls.draw()
        self.__interactables.draw()
    
    def reload(self) -> None:
        if not self.__path.exists():
            raise ValueError(f"Map '{self.__path}' was not found on disk")
        
        content: list[str]
        with self.__path.open("r", encoding="utf-8") as file:
            content = ["\n".join(file.readlines())]
            content = content[0].split("---", 1) # Split between header (0), map (1)
        
        size = self.__parse_header(content[0])
        self.__parse_map(content[1], size)
    
    @property
    def physics_colliders_list(self) -> arcade.SpriteList[arcade.Sprite]:
        return self.__walls

    @property
    def player_pos(self) -> arcade.Vec2:
        return self.__player_pos
    
    def __parse_map(self, map: str, size: arcade.Vec2, start: arcade.Vec2 = arcade.Vec2(0,0)) -> None:
        lines = map.splitlines()

        if len(lines) - 1 > size.y:
            raise ValueError("Invalid map height")
        
        lines = lines[:int(size.y)-1]
        lines.reverse() # So that we loop bottom-up

        for y, line in enumerate(lines):
            if len(line) > size.x:
                raise ValueError(f"Invalid map width at line {y}")
            for x, char in enumerate(line):
                if char == " ":
                    continue

                pos = start + arcade.Vec2(x * MAP_GRID_SIZE, y * MAP_GRID_SIZE)
                info = self.MAP_CHAR_INFO[char]

                sprite = arcade.Sprite(info[0], 
                                scale=MAP_SCALE_FACTOR,
                                center_x=pos.x,
                                center_y=pos.y)

                match info[1]:
                    case Map.ObjectType.START:
                        # TODO Player Start
                        pass
                    case Map.ObjectType.MONSTER:
                        # TODO Monster Start
                        pass
                    case Map.ObjectType.COIN | Map.ObjectType.NOGO:
                        self.__interactables.append(sprite)
                    case Map.ObjectType.WALL:
                        self.__walls.append(sprite)

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
