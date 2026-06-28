from __future__ import annotations


class VGamepadBackend:
    """Windows virtual gamepad backend backed by vgamepad."""

    def __init__(self) -> None:
        try:
            import vgamepad as vg
        except ImportError as exc:
            raise RuntimeError(
                "vgamepad is required. Install with: pip install vgamepad"
            ) from exc

        self._vg = vg
        self._pad = vg.VX360Gamepad()
        self._actions = {
            "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            "down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            "left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            "right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        }

    def press(self, action: str) -> None:
        button = self._resolve(action)
        self._pad.press_button(button=button)

    def release(self, action: str) -> None:
        button = self._resolve(action)
        self._pad.release_button(button=button)

    def flush(self) -> None:
        self._pad.update()

    def _resolve(self, action: str):
        key = action.lower().strip()
        if key not in self._actions:
            raise KeyError(f"Unsupported action: {action}")
        return self._actions[key]
