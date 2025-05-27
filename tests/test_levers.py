import textwrap
from typing import Iterator, Type, TypeVar, cast

import arcade

from src.entities.gameobject import GameObject
from src.entities.gates_lever import Gate, Switch
from src.gameview import GameView

T = TypeVar("T")


def get_first_of_type(tp: Type[T], objects: Iterator[GameObject]) -> T:
    for obj in objects:
        if isinstance(obj, tp):
            return cast(T, obj)
    assert False


def test_gate_def_open(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        switches:
          - x: 1
            y: 1
        gates:
          - x: 2
            y: 1
            state: open
        ---
        S^|
        ====
        ---
        """)
    )
    window.show_view(view)

    # Manually do the first tick of the gate
    get_first_of_type(Gate, view.map.game_objects).update(1 / 60)

    assert get_first_of_type(Gate, view.map.game_objects).isOpen


def test_gate_def_close(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        switches:
          - x: 1
            y: 1
        gates:
          - x: 2
            y: 1
            state: closed
        ---
        S^|
        ====
        ---
        """)
    )
    window.show_view(view)

    assert not get_first_of_type(Gate, view.map.game_objects).isOpen


def test_switch_on_off_disable(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        switches:
          - x: 1
            y: 1
            state: on
            switch_off:
              - action: disable
        gates:
          - x: 2
            y: 1
            state: closed
        ---
        S^|
        ====
        ---
        """)
    )
    window.show_view(view)

    assert get_first_of_type(Switch, view.map.game_objects).isOn

    view.on_mouse_press(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)
    view.on_mouse_release(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )

    assert not get_first_of_type(Switch, view.map.game_objects).isOn
    assert get_first_of_type(Switch, view.map.game_objects).isDisabled

    window.test(60)

    view.on_mouse_press(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)
    view.on_mouse_release(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )

    assert not get_first_of_type(Switch, view.map.game_objects).isOn


def test_switch_actually_works_as_a_switch(window: arcade.Window) -> None:
    view = GameView()

    view.map.force_load_map(
        textwrap.dedent("""
        width: 4
        height: 2
        switches:
          - x: 1
            y: 1
            switch_on:
              - action: open-gate
                x: 2
                y: 1
            switch_off:
              - action: close-gate
                x: 2
                y: 1
        gates:
          - x: 2
            y: 1
            state: closed
        ---
        S^|
        ====
        ---
        """)
    )
    window.show_view(view)

    assert not get_first_of_type(Switch, view.map.game_objects).isOn
    assert not get_first_of_type(Gate, view.map.game_objects).isOpen

    view.on_mouse_press(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)
    view.on_mouse_release(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)

    assert get_first_of_type(Switch, view.map.game_objects).isOn
    assert get_first_of_type(Gate, view.map.game_objects).isOpen

    window.test(60)

    view.on_mouse_press(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)
    view.on_mouse_release(
        int(window.center_x + 100), int(window.center_y), arcade.MOUSE_BUTTON_LEFT, 0
    )
    window.test(10)

    assert not get_first_of_type(Switch, view.map.game_objects).isOn
    assert not get_first_of_type(Gate, view.map.game_objects).isOpen
