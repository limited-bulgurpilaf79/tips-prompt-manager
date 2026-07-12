"""Local password setup and per-boot authentication state."""

from __future__ import annotations

import ctypes
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime

from .paths import config_path, session_path

PASSWORD_ITERATIONS = 260_000


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def password_hash(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return salt.hex(), digest.hex()


def load_config() -> dict[str, object]:
    path = config_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {}


def save_config(config: dict[str, object]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def verify_password(password: str, config: dict[str, object]) -> bool:
    salt = str(config.get("password_salt", ""))
    expected = str(config.get("password_hash", ""))
    if not salt or not expected:
        return False
    _, actual = password_hash(password, salt)
    return hmac.compare_digest(actual, expected)


def current_boot_token() -> str:
    try:
        uptime_ms = ctypes.windll.kernel32.GetTickCount64()
        boot_epoch = time.time() - (uptime_ms / 1000)
        return str(round(boot_epoch / 10) * 10)
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


def is_boot_session_authenticated(config: dict[str, object]) -> bool:
    if not config.get("password_hash") or not session_path().exists():
        return False
    try:
        data = json.loads(session_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        data.get("boot_token") == current_boot_token()
        and data.get("password_hash") == config.get("password_hash")
    )


def mark_boot_session_authenticated(config: dict[str, object]) -> None:
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    session = {
        "boot_token": current_boot_token(),
        "password_hash": config.get("password_hash"),
        "verified_at": now_text(),
    }
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def create_password_config(password: str) -> dict[str, object]:
    salt, digest = password_hash(password)
    return {
        "password_salt": salt,
        "password_hash": digest,
        "iterations": PASSWORD_ITERATIONS,
        "created_at": now_text(),
    }
