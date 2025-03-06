import arcade
from src.res.map import Map

class GameView(arcade.View):
    """Main in-game view."""
    map: Map
    camera: arcade.Camera2D

    def __init__(self) -> None:
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.setup()

    def setup(self) -> None:
        """Set up the game here."""
        self.map = Map("map1.txt")
        self.camera = arcade.Camera2D()

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()

        with self.camera.activate():
            self.map.draw()
    
    def on_update(self, delta_time: float) -> None:
        self.map.update(delta_time)
        self.camera.position = self.map.player.position
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        for listeners in self.map.game_objects:
            listeners.on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        for listeners in self.map.game_objects:
            listeners.on_key_release(symbol, modifiers)