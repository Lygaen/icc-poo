from typing import Any

import arcade

from src.entities.gameobject import DamageSource, GameObject
from src.res.map import Map

LEVER_OFF = ":resources:/images/tiles/leverLeft.png"
LEVER_ON = ":resources:/images/tiles/leverRight.png"

SwitchData = Map.Metadata.SwitchPosition
GateData = Map.Metadata.GatePosition


class Gate(GameObject):
    isOpen: bool
    data: GateData | None

    def __init__(
        self, map: list[Map], meta: Map.Metadata, pos: tuple[int, int], **kwargs: Any
    ) -> None:
        super().__init__(
            map, ":resources:/images/tiles/stoneCenter_rounded.png", **kwargs
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
            self.data = GateData(pos[0], pos[1], GateData.State.closed)

    def update_gate(self, open: bool) -> None:
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


class Switch(GameObject):
    data: SwitchData
    isOn: bool
    isDisabled: bool

    last_hit: float

    HIT_INVULNERABILITY: float = 1.0

    def __init__(
        self, map: list[Map], meta: Map.Metadata, pos: tuple[int, int], **kwargs: Any
    ) -> None:
        super().__init__(map, LEVER_OFF, **kwargs)
        self.last_hit = 0
        self.isOn = False
        self.isDisabled = False
        self.append_texture(arcade.load_texture(LEVER_ON))

        for switch in meta.switches or []:
            if switch.x == pos[0] and switch.y == pos[1]:
                self.data = switch
                break

        if self.data is None:
            raise ValueError(
                f"Switch at position x:'{pos[0]}' y'{pos[1]}' is not defined in the header !"
            )

        if not hasattr(self.data, "state"):
            self.data.state = SwitchData.State.off

        if self.data.state == SwitchData.State.on:
            self.isOn = True
            self.set_texture(1)

    def update(self, delta_time: float = 1 / 60, *args: Any, **kwargs: Any) -> None:
        self.last_hit = max(0, self.last_hit - delta_time)
        super().update(delta_time, **kwargs)

    def on_damage(self, source: DamageSource, damage: float) -> bool:
        if source == DamageSource.PLAYER and self.last_hit <= 0:
            self.last_hit = self.HIT_INVULNERABILITY
            self.on_switch_change()
            return True

        return False

    def do_switch_action(self, action: SwitchData.Action) -> None:
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
        for obj in self.map.game_objects:
            if isinstance(obj, Gate) and obj.data is not None:
                if obj.data.x == action.x and obj.data.y == action.y:
                    return obj
        return None

    def on_switch_change(self) -> None:
        if self.isDisabled:
            return

        self.set_texture(0 if self.isOn else 1)
        self.isOn = not self.isOn

        actions = self.data.switch_on if self.isOn else self.data.switch_off

        for action in actions or []:
            self.do_switch_action(action)
