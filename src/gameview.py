import arcade
from src.res.map import Map

class GameView(arcade.View):
    """Main in-game view."""

    map: Map
    """The current map of the game
    """
    camera: arcade.Camera2D
    """The camera pointing to the player.
    Will be changed to a proper camera handling
    """

    def __init__(self) -> None:
        """Initializes the game view and other arcade stuff.
        """
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.setup()

    def setup(self) -> None:
        """Set up the game, loading the map, ..."""
        self.map = Map("map2.txt")
        self.camera = arcade.Camera2D()

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()

        with self.camera.activate():
            self.map.draw()
    
    def on_update(self, delta_time: float) -> None:
        """Updates all related internals

        Args:
            delta_time (float): The delta time between the last frame and the current
        """
        self.map.update(delta_time)
        self.camera.position = arcade.Vec2(self.map.player.position[0], self.map.player.position[1])
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """On Key Press event

        Args:
            symbol (int): the key pressed
            modifiers (int): the related modifiers
        """
        for listeners in self.map.game_objects:
            listeners.on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """On Key Release event

        Args:
            symbol (int): the key released
            modifiers (int): the related modifiers
        """
        for listeners in self.map.game_objects:
            listeners.on_key_release(symbol, modifiers)