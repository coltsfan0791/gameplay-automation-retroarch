from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from input.vgamepad_backend import VGamepadBackend


def main() -> None:
    backend = VGamepadBackend()
    print("Supported actions:")
    for action in backend.supported_actions():
        print(f"- {action}")


if __name__ == "__main__":
    main()
