from typing import Any, cast
import arcade
from arcade.types import PathOrTexture, Point2

from src.res.map import Map

class GameObject(arcade.Sprite):
    """The GameObject superclass. Ideally should not
    be instantiated but only implemented in a subclass
    """

    map: Map
    """The map where the gameobject is registered
    """

    def __init__(self, map: Map, path_or_texture: PathOrTexture | None = None, scale: Point2 | float = 1, center_x: float = 0, center_y: float = 0) -> None:
        """Initializes a gameobject given the parameters

        Args:
            map (Map): The map where the object is registered
            path_or_texture (PathOrTexture | None, optional): The path or texture of the object. Defaults to None.
            scale (Point2 | float, optional): The scale of the sprite. Defaults to 1.
            center_x (float, optional): The position of the sprite, in x. Defaults to 0.
            center_y (float, optional): The position of the sprite, in y. Defaults to 0.
        """
        super().__init__(path_or_texture, scale, center_x, center_y)
        self.map = map
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        """Updates the gameobject for the current delta-time.
        The function should add the map where it is called from as a positional
        argument. As such, it shall not be called outside of the internal map update.

        Args:
            delta_time (float, optional): The current delta-time. Defaults to 1/60.
        """
        super().update(delta_time)
        self.map = cast(Map, kwargs.get("map"))

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """On Key Press event

        Args:
            symbol (int): the key pressed
            modifiers (int): the related modifiers
        """
        pass
        
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """On Key Release event

        Args:
            symbol (int): the key released
            modifiers (int): the related modifiers
        """
        pass

    def destroy(self) -> None:
        """Destroys the current object on the map.
        Next tick, neither #draw or #update will be called.

        Any events will not be called as well.
        """
        self.map.destroy(self)