import arcade
from src.res.map import Map

class GameView(arcade.View):
    """Main in-game view."""
    map: Map

    def __init__(self) -> None:
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.setup()

    def setup(self) -> None:
        """Set up the game here."""
        self.map = Map("map1.txt")

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()  
        self.map.draw()