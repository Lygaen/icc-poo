import arcade

from src.res.camera import BetterCamera
from src.res.map import Map


class GameView(arcade.View):
    """Main in-game view."""

    map: Map
    """The current map of the game
    """
    camera: BetterCamera
    """The camera pointing to the player.
    Will be changed to a proper camera handling
    """

    ui_camera: arcade.Camera2D

    score: int
    """The current score of the player, saved
    between maps.
    """

    def __init__(self) -> None:
        """Initializes the game view and other arcade stuff."""
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0

        self.setup()

    def setup(self) -> None:
        """Set up the game, loading the map, ..."""
        self.map = Map([self], "map1.txt")
        self.camera = BetterCamera()
        self.ui_camera = arcade.Camera2D()

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()

        with self.camera.activate():
            self.map.draw()

            for object in self.map.game_objects:
                object.draw_ui()

        with self.ui_camera.activate():
            self.draw_ui()

    def draw_ui(self) -> None:
        top = self.window.size[1]
        arcade.Text(f"Score : {self.score}", 50, top - 50, (255, 255, 255), 18).draw()

    def on_update(self, delta_time: float) -> None:
        """Updates all related internals

        Args:
            delta_time (float): The delta time between the last frame and the current
        """
        self.map.update(delta_time)
        self.camera.update(delta_time, self.map.player.position)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """On Key Press event

        Args:
            symbol (int): the key pressed
            modifiers (int): the related modifiers
        """
        for listeners in self.map.event_listeners:
            listeners.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """On Key Release event

        Args:
            symbol (int): the key released
            modifiers (int): the related modifiers
        """
        for listeners in self.map.event_listeners:
            listeners.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """On Mouse Press event

        Args:
            x (int): x position of click
            y (int): y position of click
            button (int): button clicked
            modifiers (int): additional modifiers
        """
        for listeners in self.map.event_listeners:
            listeners.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """On Mouse Release event

        Args:
            x (int): x position of click
            y (int): y position of click
            button (int): button clicked
            modifiers (int): additional modifiers
        """
        for listeners in self.map.event_listeners:
            listeners.on_mouse_release(x, y, button, modifiers)

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
        for listeners in self.map.event_listeners:
            listeners.on_mouse_motion(x, y, dx, dy)
