from typing import Any
import arcade

from src.entities.evlistener import EventListener

class Player(arcade.Sprite, EventListener):
    def __init__(self, **kwargs: Any) -> None:
        super(Player, self).__init__(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", **kwargs)
    
    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        print(f"{symbol} pressed !")