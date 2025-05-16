from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.entities.wall import MovingPlatform
from src.res.array2d import Array2D
from src.res.map import Map

LEVER_ON = ":resources:/images/tiles/leverRight.png"

SwitchData = Map.Metadata.SwitchPosition
GateData = Map.Metadata.GatePosition


class Gate(GameObject):
    """The gate that can open and close"""

    isOpen: bool
    """Whether the gate is opened or not
    """
    data: GateData | None
    """Internal metadata of the gate
    """

    def __init__(
        self, map: list[Map], meta: Map.Metadata, pos: tuple[int, int], **kwargs: Any
    ) -> None:
        super().__init__(
            map,
            float("inf"),
            ":resources:/images/tiles/stoneCenter_rounded.png",
            **kwargs,
        )

        self.isOpen = False
        self.data = None
        for gate in meta.gates or []:
            if gate.x == pos[0] and gate.y == pos[1]:
                if gate.state == GateData.State.open:
                    self.update_gate(True)
                self.data = gate
                break

        if self.data is None:
            self.data = GateData()

            self.data.x = pos[0]
            self.data.y = pos[1]
            self.data.state = GateData.State.closed

    def update_gate(self, open: bool) -> None:
        """Updates the gate with open or closed

        Args:
            open (bool): whether to open or close the gate
        """
        if open == self.isOpen:
            return
        self.isOpen = open
        self.visible = not self.isOpen

        self.hit_box = arcade.hitbox.RotatableHitBox(
            self.texture.hit_box_points,
            position=self._position,
            angle=self.angle,
            scale=(0, 0) if self.isOpen else self._scale,
        )


class Switch(MovingPlatform):
    """The switch object"""

    data: SwitchData
    """The switch metadata
    """
    isOn: bool
    """Whether the switch is on or off
    """
    isDisabled: bool
    """Whether the switch is disabled
    """

    def __init__(
        self,
        map: list[Map],
        meta: Map.Metadata,
        data: Array2D[str],
        pos: tuple[int, int],
        **kwargs: Any,
    ) -> None:
        super().__init__(map, "^", data, pos, **kwargs)
        self.isOn = False
        self.isDisabled = False
        self.append_texture(arcade.load_texture(LEVER_ON))

        for switch in meta.switches or []:
            if switch.x == pos[0] and switch.y == pos[1]:
                self.data = switch
                break

        if self.data is None:
            raise ValueError(
                f"Switch at position x:'{pos[0]}' y: '{pos[1]}' is not defined in the header !"
            )

        if not hasattr(self.data, "state"):
            self.data.state = SwitchData.State.off
            return

        if self.data.state == SwitchData.State.on or self.data.state:
            self.isOn = True
            self.set_texture(1)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        super().update(delta_time, **kwargs)
        GameObject.update(self, delta_time, **kwargs)

    def _on_damage(self, other: GameObject | None, source: DamageSource) -> bool:
        if source == DamageSource.PLAYER:
            self.on_switch_change()
            return True

        return False

    def do_switch_action(self, action: SwitchData.Action) -> None:
        """Effectuate a specific switch action"""
        ActionKind = SwitchData.Action.Kind
        match action.action:
            case ActionKind.open_gate:
                g = self.gate_from_action(action)
                if g is None:
                    raise ValueError(f"Gate not found at '{action.x}' '{action.y}'")
                g.update_gate(True)
            case ActionKind.close_gate:
                g = self.gate_from_action(action)
                if g is None:
                    raise ValueError(f"Gate not found at '{action.x}' '{action.y}'")
                g.update_gate(False)
            case ActionKind.disable:
                self.isDisabled = True

    def gate_from_action(self, action: SwitchData.Action) -> Gate | None:
        """Fetch the gate from a specified action"""
        for obj in self.map.game_objects:
            if isinstance(obj, Gate) and obj.data is not None:
                if obj.data.x == action.x and obj.data.y == action.y:
                    return obj
        return None

    def on_switch_change(self) -> None:
        """On switch change event handler"""
        if self.isDisabled:
            return

        self.set_texture(0 if self.isOn else 1)
        self.isOn = not self.isOn

        if self.isOn and hasattr(self.data, "switch_on"):
            for action in self.data.switch_on or []:
                self.do_switch_action(action)
        elif not self.isOn and hasattr(self.data, "switch_off"):
            for action in self.data.switch_off or []:
                self.do_switch_action(action)
