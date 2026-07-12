"""Double-click launcher for TIPS Prompt Manager."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tips_prompt_manager.app import main


if __name__ == "__main__":
    main()
