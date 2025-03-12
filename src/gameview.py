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

    score: int
    """The current score of the player, saved
    between maps.
    """

    def __init__(self) -> None:
        """Initializes the game view and other arcade stuff.
        """
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0

        self.setup()

    def setup(self) -> None:
        """Set up the game, loading the map, ..."""
        self.map = Map([self], "map1.txt")
        self.camera = BetterCamera()

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()

        print(f"Score : {self.score}")

        with self.camera.activate():
            self.map.draw()
    
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