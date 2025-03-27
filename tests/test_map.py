import textwrap
from typing import Any, Iterable, Iterator

import arcade

from src.gameview import GameView


def iter_count(iter: Iterator[Any] | Iterable[Any]) -> int:
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


def test_entities_spawn(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 8
        height: 8
        next-map: lol.txt
        ---
        S
        **
        www
        ====
        -----
        ££££££
        ooooooo
        xxxxxxxx
        ---
        """)
    )
    window.show_view(view)

    def count_of_class_type(iter: Iterator[Any] | Iterable[Any], name: str) -> int:
        count = 0
        for obj in iter:
            if obj.__class__.__name__ == name:
                count += 1
        return count

    assert count_of_class_type(view.map.game_objects, "Player") == 1
    assert count_of_class_type(view.map.game_objects, "Coin") == 2
    assert count_of_class_type(view.map.game_objects, "Bat") == 3
    assert count_of_class_type(view.map.game_objects, "Wall") == 4 + 5 + 8
    assert count_of_class_type(view.map.game_objects, "Lava") == 6
    assert count_of_class_type(view.map.game_objects, "Slime") == 7
