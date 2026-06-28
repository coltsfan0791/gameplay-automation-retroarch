from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class _AnalogAction:
    kind: str
    target: str
    x: float = 0.0
    y: float = 0.0
    value: float = 1.0


class VGamepadBackend:
    """Windows virtual Xbox 360 gamepad backend backed by vgamepad.

    Supported action families:
    - Face buttons: a, b, x, y
    - D-pad: up, down, left, right
    - System buttons: start, back, select
    - Shoulders: lb, rb, l1, r1, left_shoulder, right_shoulder
    - Stick clicks: ls, rs, l3, r3, left_thumb, right_thumb
    - Triggers: lt, rt, l2, r2, left_trigger, right_trigger
    - Left stick directions: left_stick_up/down/left/right and ls_up/down/left/right
    - Right stick directions: right_stick_up/down/left/right and rs_up/down/left/right
    """

    def __init__(self) -> None:
        try:
            import vgamepad as vg
        except ImportError as exc:
            raise RuntimeError(
                "vgamepad is required. Install with: pip install vgamepad"
            ) from exc

        self._vg = vg
        self._pad = vg.VX360Gamepad()

        self._button_actions = {
            "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            "down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            "left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            "right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            "start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "menu": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "select": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "view": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "lb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "l1": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "left_shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "rb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "r1": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "right_shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "ls": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "l3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "left_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "left_stick_click": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "rs": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "r3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "right_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "right_stick_click": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        }

        self._analog_actions = self._build_analog_actions()

    def press(self, action: str) -> None:
        key = self._normalize(action)

        button = self._button_actions.get(key)
        if button is not None:
            self._pad.press_button(button=button)
            return

        analog = self._analog_actions.get(key)
        if analog is not None:
            self._apply_analog_press(analog)
            return

        raise KeyError(self._unsupported_message(action))

    def release(self, action: str) -> None:
        key = self._normalize(action)

        button = self._button_actions.get(key)
        if button is not None:
            self._pad.release_button(button=button)
            return

        analog = self._analog_actions.get(key)
        if analog is not None:
            self._apply_analog_release(analog)
            return

        raise KeyError(self._unsupported_message(action))

    def flush(self) -> None:
        self._pad.update()

    def supported_actions(self) -> list[str]:
        return sorted(set(self._button_actions) | set(self._analog_actions))

    def _normalize(self, action: str) -> str:
        return action.lower().strip().replace("-", "_").replace(" ", "_")

    def _unsupported_message(self, action: str) -> str:
        supported = ", ".join(self.supported_actions())
        return f"Unsupported action: {action}. Supported actions: {supported}"

    def _apply_analog_press(self, analog: _AnalogAction) -> None:
        if analog.kind == "trigger":
            setter = self._trigger_setter(analog.target)
            setter(value_float=analog.value)
            return

        if analog.kind == "stick":
            setter = self._stick_setter(analog.target)
            setter(x_value_float=analog.x, y_value_float=analog.y)
            return

        raise ValueError(f"Unsupported analog kind: {analog.kind}")

    def _apply_analog_release(self, analog: _AnalogAction) -> None:
        if analog.kind == "trigger":
            setter = self._trigger_setter(analog.target)
            setter(value_float=0.0)
            return

        if analog.kind == "stick":
            setter = self._stick_setter(analog.target)
            setter(x_value_float=0.0, y_value_float=0.0)
            return

        raise ValueError(f"Unsupported analog kind: {analog.kind}")

    def _trigger_setter(self, target: str) -> Callable[..., None]:
        if target == "left":
            return self._pad.left_trigger_float
        if target == "right":
            return self._pad.right_trigger_float
        raise ValueError(f"Unsupported trigger target: {target}")

    def _stick_setter(self, target: str) -> Callable[..., None]:
        if target == "left":
            return self._pad.left_joystick_float
        if target == "right":
            return self._pad.right_joystick_float
        raise ValueError(f"Unsupported stick target: {target}")

    def _build_analog_actions(self) -> dict[str, _AnalogAction]:
        actions: dict[str, _AnalogAction] = {}

        for alias in ("lt", "l2", "left_trigger"):
            actions[alias] = _AnalogAction(kind="trigger", target="left", value=1.0)
        for alias in ("rt", "r2", "right_trigger"):
            actions[alias] = _AnalogAction(kind="trigger", target="right", value=1.0)

        stick_vectors = {
            "up": (0.0, 1.0),
            "down": (0.0, -1.0),
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
        }

        for direction, (x, y) in stick_vectors.items():
            actions[f"left_stick_{direction}"] = _AnalogAction(
                kind="stick", target="left", x=x, y=y
            )
            actions[f"ls_{direction}"] = _AnalogAction(
                kind="stick", target="left", x=x, y=y
            )
            actions[f"right_stick_{direction}"] = _AnalogAction(
                kind="stick", target="right", x=x, y=y
            )
            actions[f"rs_{direction}"] = _AnalogAction(
                kind="stick", target="right", x=x, y=y
            )

        return actions
