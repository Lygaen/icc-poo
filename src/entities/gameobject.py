import enum

import arcade
from arcade.types import PathOrTexture, Point2

from src.gameview import GameView
from src.res.camera import BetterCamera
from src.res.map import Map


class DamageSource(enum.Enum):
    """Damage source enum. From which type
    of entity does the damage come from ?

    Each field is pretty much self-explanatory.
    """

    PLAYER = 1
    MONSTER = 2
    LAVA = 3
    VOID = 4


class GameObject(arcade.Sprite):
    """The GameObject superclass. Ideally should not
    be instantiated but only implemented in a subclass
    """

    __map_ref: list[Map]
    """The map where the gameobject is registered, using list
    for having a reference to it
    """

    event_listener: bool
    """Whether this game object should be called for windows events
    """

    @property
    def map(self) -> Map:
        """Returns the map where the object is registered

        Returns:
            Map: The map in question
        """
        return self.__map_ref[0]

    @property
    def game_view(self) -> GameView:
        """Returns the game view where the map is currently drawn onto.

        Returns:
            GameView: The game view in question
        """

        return self.map.game_view

    @property
    def camera(self) -> BetterCamera:
        """Returns the game view where the map is currently drawn onto.

        Returns:
            GameView: The game view in question
        """

        return self.map.game_view.camera

    def __init__(
        self,
        map: list[Map],
        path_or_texture: PathOrTexture | None = None,
        scale: Point2 | float = 1,
        center_x: float = 0,
        center_y: float = 0,
    ) -> None:
        """Initializes a gameobject given the parameters

        Args:
            map (list[Map]): The map where the object is registered
            path_or_texture (PathOrTexture | None, optional): The path or texture of the object. Defaults to None.
            scale (Point2 | float, optional): The scale of the sprite. Defaults to 1.
            center_x (float, optional): The position of the sprite, in x. Defaults to 0.
            center_y (float, optional): The position of the sprite, in y. Defaults to 0.
        """
        super().__init__(path_or_texture, scale, center_x, center_y)
        self.__map_ref = map
        self.event_listener = False

    def on_damage(self, source: DamageSource, damage: float) -> bool:
        """On damage event - General Event

        Returns whether the damage was taken into account or not.
        Args:
            source (DamageSource): The source of the damage
            damage (float): The amount of damage
        """
        return False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """On Key Press event - Window Event

        event_listener flag needs to be set for this function to be
        called !
        Args:
            symbol (int): the key pressed
            modifiers (int): the related modifiers
        """
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """On Key Release event

        event_listener flag needs to be set for this function to be
        called !
        Args:
            symbol (int): the key released
            modifiers (int): the related modifiers
        """
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """On Mouse Press event

        event_listener flag needs to be set for this function to be
        called !
        Args:
            x (int): x position of click
            y (int): y position of click
            button (int): button clicked
            modifiers (int): additional modifiers
        """
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """On Mouse Release event

        event_listener flag needs to be set for this function to be
        called !
        Args:
            x (int): x position of click
            y (int): y position of click
            button (int): button clicked
            modifiers (int): additional modifiers
        """
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """On Mouse Motion event

        event_listener flag needs to be set for this function to be
        called !
        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            dx (int): delta position of mouse, x coordinate
            dx (int): delta position of mouse, y coordinate
        """
        pass

    def destroy(self) -> None:
        """Destroys the current object on the map.
        Next tick, neither #draw or #update will be called.

        Any events will not be called as well.
        """
        self.map.destroy(self)
