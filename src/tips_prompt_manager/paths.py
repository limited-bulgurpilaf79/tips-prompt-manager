"""Runtime paths for source, frozen, and test execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def app_dir() -> Path:
    override = os.environ.get("TIPS_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(sys.argv[0]).resolve().parent


def config_path() -> Path:
    return app_dir() / "config.json"


def session_path() -> Path:
    return app_dir() / ".auth_session.json"


def settings_path() -> Path:
    return app_dir() / "settings.json"


def database_path() -> Path:
    return app_dir() / "prompts.db"
