import textwrap
from typing import Any, Iterator

import arcade

from src.gameview import GameView


def iter_count(iter: Iterator[Any]) -> int:
    return sum(1 for _ in iter)


def test_map_loads(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        ---
        S  o
        ====
        ---
        """)
    )
    window.show_view(view)

    assert iter_count(view.map.game_objects) == 2 + 1 + 4
    assert len(view.map.physics_colliders_list) == 4
    assert (
        iter_count(view.map.event_listeners) == 2
    )  # One for the sword, 1 for the player
