import textwrap
from typing import Any, Iterable, Iterator

import arcade

from src.gameview import GameView


def iter_count(iter: Iterator[Any] | Iterable[Any]) -> int:
    return sum(1 for _ in iter)


def test_collect_coins(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 3
        height: 2
        ---
        *S*
        ===
        ---
        """)
    )
    window.show_view(view)

    assert view.score == 0
    view.on_key_press(arcade.key.LEFT, 0)
    window.test(10)
    view.on_key_release(arcade.key.LEFT, 0)
    assert view.score == 1
    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(20)
    view.on_key_release(arcade.key.RIGHT, 0)
    assert view.score == 2


def test_player_death(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        ---
        S o
        =£==
        ---
        """)
    )
    window.show_view(view)
    maxHP = view.map.player.health_points

    view.on_key_press(arcade.key.UP, 0)
    view.on_key_press(arcade.key.RIGHT, 0)
    window.test(30)
    view.on_key_release(arcade.key.UP, 0)
    view.on_key_release(arcade.key.RIGHT, 0)

    window.test(20)
    assert view.map.player.health_points < maxHP
    view.on_key_press(arcade.key.LEFT, 0)
    window.test(20)
    view.on_key_release(arcade.key.LEFT, 0)

    assert view.map.player.center_x == view.map.player_spawn_point[0]
    assert view.map.player.center_y == view.map.player_spawn_point[1]


def test_next_map(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 1
        height: 2
        next_map: map1.txt
        ---
        S
        E
        ---
        """)
    )
    window.show_view(view)

    assert iter_count(view.map.game_objects) == 2 + 1
    window.test(20)
    assert iter_count(view.map.game_objects) != 2 + 1  # Next map was loaded
