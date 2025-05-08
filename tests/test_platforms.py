import textwrap
from typing import Any, Iterable, Iterator

import pytest
import arcade

from src.gameview import GameView
from src.entities.gameobject import GameObject

# the block moves only vertically
def test_block_moving(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 1
        height: 3
        next_map: map1.txt
        ---
        ↑
        =
        ↓
        ---
        """)
    )
    window.show_view(view)
    block : GameObject = view.map.game_objects.__next__()
    position : tuple[float, float] = (block.center_x, block.center_y)
    window.test(20)
    for block in view.map.game_objects:
        assert(position[0] == block.center_x and position[1] != block.center_y)

# all the group moves, even if there is only two blocks with arrows, all blocks types that are supposed to move, only horizontal movement
def test_blocks_moving_together(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 3
        switches:
          - x: 3
            y: 2
        next_map: map1.txt
        ---
         ←←^
        E-£x
        =→
        ---
        """)
    )
    window.show_view(view)
    position : dict[GameObject, tuple[float, float]] = {}
    for block in view.map.game_objects:
        position[block] = (block.center_x, block.center_y)
    window.test(20)
    for block in view.map.game_objects:
        assert(position[block][0] != block.center_x and position[block][1] == block.center_y)





def test_throws_errors() -> None:
    view = GameView()

    # incompatible directions on a block
    with pytest.raises(ValueError):
        view.map.force_load_map(
            textwrap.dedent("""
            width: 2
            height: 2
            next_map: map1.txt
            ---
            ↑S
            =→
            ---
            """)
        )

    # two times the same direction on a group
    with pytest.raises(ValueError):
        view.map.force_load_map(
            textwrap.dedent("""
            width: 5
            height: 2
            next_map: map1.txt
            ---
            =====
             ↓ ↓            
            ---
            """)
        )

    # incompatible directions on a group
    with pytest.raises(ValueError):
        view.map.force_load_map(
            textwrap.dedent("""
                width: 4
                height: 3
                next_map: map1.txt
                ---
                 ←=→        
                ====
                ↓
                ---
                """)
        )