import textwrap
from timeit import timeit
from typing import Callable

import arcade

from src.gameview import GameView
from src.res.map import Map

import pytest

def generate_map(width: int, height: int, char: str) -> str:
    s = [(char + " ") * (width // 2) for i in range(height)]
    final = ""

    for i, line in enumerate(s):
        final += (" " if i % 2 == 0 else "") + line
        if i % 2 == 0:
            final = final[:-1]
        final += "\n"
    final = "S" + final[1:-1]

    return textwrap.dedent(f"""
width: {width}
height: {height}
next_map: map1.txt
---
{final}
---
    """)


def time_map(map: list[Map], w: int, h: int, char: str) -> float:
    return (
        timeit(lambda: map[0].force_load_map(generate_map(w, h, char)), number=10) / 10
    )  # Only ten runs or else it takes way too long


def time_update(view: list[GameView], w: int, h: int, char: str) -> float:
    view[0].map.force_load_map(generate_map(w, h, char))

    return timeit(lambda: view[0].on_update(1 / 60), number=100) / 100


@pytest.mark.slow
def test_map_size(
    window: arcade.Window, record_testsuite_property: Callable[[str, object], None]
) -> None:
    view = GameView()

    print("--- MAP ---")

    for width in [1, 3, 5, 10, 50, 100, 500, 1000]:
        for height in [1, 3, 5, 10, 50, 100, 500, 1000]:
            t = time_map([view.map], width, height, "x")
            print(f"{width}x{height} : {t}")
            record_testsuite_property(f"map_{width}_{height}", t)

    print("-----------")

@pytest.mark.slow
def test_on_update(
    window: arcade.Window, record_testsuite_property: Callable[[str, object], None]
) -> None:
    view = GameView()

    print("--- UPD ---")

    for width in [1, 3, 5, 10, 50, 100, 500, 1000]:
        for height in [1, 3, 5, 10, 50, 100, 500, 1000]:
            t = time_update([view], width, height, "x")
            print(f"{width}x{height} : {t}")
            record_testsuite_property(f"update_{width}_{height}", t)

    print("-----------")
