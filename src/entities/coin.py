from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map


class Coin(GameObject):
    """Generic coin object. Currently only self destroys."""

    coin_sound: arcade.Sound
    """Sound for when collecting a coin.
    """

    def __init__(self, map: list[Map], **kwargs: Any) -> None:
        super().__init__(map, 1.0, ":resources:/images/items/coinGold.png", **kwargs)
        self.coin_sound = arcade.Sound(":resources:sounds/coin1.wav")

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)

        if arcade.check_for_collision(self.map.player, self):
            self.damage(None, DamageSource.PLAYER, 10)

    def _on_damage(self, other: GameObject | None, source: DamageSource) -> bool:
        return source in {DamageSource.PLAYER}

    def destroy(self, is_health_death: bool = False) -> None:
        if is_health_death:
            arcade.play_sound(self.coin_sound)
            self.game_view.score += 1
        super().destroy()
