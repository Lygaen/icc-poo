import textwrap

import arcade

from src.gameview import GameView


def test_map_loads(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 20
        height: 2
        ---
         S          *o   x*
        ======£££££=========
        ---
        """)
    )
    window.show_view(view)

    window.test(60 * 5)
