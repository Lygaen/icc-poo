import arcade
from pathlib import Path

arcade.resources.add_resource_handle("maps", "./maps/")

class Map:
    __path: Path
    __player_pos: arcade.Vec2
    __walls: arcade.SpriteList[arcade.Sprite]
    __interactables: arcade.SpriteList[arcade.Sprite]

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
    
    def __parse_map(self, map: str, size: arcade.Vec2) -> None:
        pass
        
    def __parse_header(self, header: str) -> arcade.Vec2:
        width: int
        height: int
        for line in header.splitlines():
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
