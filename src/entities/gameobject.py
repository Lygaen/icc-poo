from typing import Any, cast
import arcade
from arcade.types import PathOrTexture, Point2

from src.res.map import Map

class GameObject(arcade.Sprite):
    map: Map

    def __init__(self, map: Map, path_or_texture: PathOrTexture | None = None, scale: Point2 | float = 1, center_x: float = 0, center_y: float = 0) -> None:
        super().__init__(path_or_texture, scale, center_x, center_y)
        self.map = map
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time)
        self.map = cast(Map, kwargs.get("map"))

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        pass
        
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        pass

    def destroy(self) -> None:
        self.map.destroy(self)