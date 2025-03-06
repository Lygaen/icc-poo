from typing import Any
import arcade

from src.entities.gameobject import GameObject
from src.res.map import Map

class Coin(GameObject):
    """Generic coin object. Currently only self destroys.
    """
    coin_sound: arcade.Sound
    """Sound for when collecting a coin.
    """

    def __init__(self, map: Map, **kwargs: Any) -> None:
        super().__init__(map, ":resources:/images/items/coinGold.png", **kwargs)
        self.coin_sound = arcade.Sound(":resources:sounds/coin1.wav")
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)

        if arcade.check_for_collision(self.map.player, self):
            arcade.play_sound(self.coin_sound)
            self.destroy()