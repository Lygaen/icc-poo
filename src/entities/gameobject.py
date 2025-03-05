from typing import Any
import arcade
from arcade.types import PathOrTexture, Point2


class GameObject(arcade.Sprite):
    list: arcade.SpriteList['GameObject']

    def __init__(self, list: arcade.SpriteList, path_or_texture: PathOrTexture | None = None, scale: Point2 | float = 1, center_x: float = 0, center_y: float = 0) -> None:
        super().__init__(path_or_texture, scale, center_x, center_y)

        self.list = list

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        pass
    
    def destroy(self) -> None:
        self.list.remove(self)