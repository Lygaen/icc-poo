import arcade
from pathlib import Path
from enum import Enum

arcade.resources.add_resource_handle("maps", Path("./assets/maps/").resolve())


class Map:
    __path: Path
    __walls: arcade.SpriteList[arcade.Sprite]
    __interactables: arcade.SpriteList[arcade.Sprite]

    class ObjectType(Enum):
        WALL = 1
        COIN = 2
        MONSTER = 3
        NOGO = 4
        START = 5

    __CHAR_INFO: dict[str, tuple[str, ObjectType]] = {
        "=": (":resources:/images/tiles/grassMid.png", ObjectType.WALL),
        "-": (":resources:/images/tiles/grassHalf_mid.png", ObjectType.WALL),
        "x": (":resources:/images/tiles/boxCrate_double.png", ObjectType.WALL),
        "*": (":resources:/images/items/coinGold.png", ObjectType.COIN),
        "o": (":resources:/images/enemies/slimeBlue.png", ObjectType.MONSTER),
        "£": (":resources:/images/tiles/lava.png", ObjectType.NOGO),
        "S": (":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", ObjectType.START),
    }
    __GRID_SIZE = 64
    __GRID_SCALE = 0.5

    def __init__(self, path: str):
        self.__path = arcade.resources.resolve(":maps:" + path)
        self.reload()
    
    def draw(self) -> None:
        self.__walls.draw()
        self.__interactables.draw()
    
    def reload(self) -> None:
        if not self.__path.exists():
            raise ValueError(f"Map '{self.__path}' was not found on disk")
        
        self.__walls = arcade.SpriteList(use_spatial_hash=True)
        self.__interactables = arcade.SpriteList(use_spatial_hash=True)
        
        content: list[str]
        with self.__path.open("r", encoding="utf-8") as file:
            content = ["".join(file.readlines())]
            content = content[0].split("---", 1) # Split between header (0), map (1)
        
        size = self.__parse_header(content[0])
        self.__parse_map(content[1], size)
    
    @property
    def physics_colliders_list(self) -> arcade.SpriteList[arcade.Sprite]:
        return self.__walls
    
    def __parse_map(self, map: str, size: arcade.Vec2, start: arcade.Vec2 = arcade.Vec2(0,0)) -> None:
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
                info = self.__CHAR_INFO[char]

                sprite = arcade.Sprite(info[0], 
                                scale=self.__GRID_SCALE,
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
