from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when required guardian configuration is missing or unsafe."""


@dataclass(frozen=True)
class Settings:
    bot_token: str
    allowed_chat_id: int
    poll_seconds: float
    rate_limit_per_minute: int
    confirmation_ttl_seconds: int
    audit_log: Path
    stop_file: Path

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        values = os.environ if env is None else env
        token = values.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token or ":" not in token:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN must be a BotFather token.")

        chat_id = _positive_int(values, "TELEGRAM_ALLOWED_CHAT_ID")
        poll_seconds = _positive_float(values, "GUARDIAN_POLL_SECONDS", 3.0)
        rate_limit = _positive_int(values, "GUARDIAN_RATE_LIMIT_PER_MINUTE", 10)
        ttl = _positive_int(values, "GUARDIAN_CONFIRMATION_TTL_SECONDS", 60)
        audit_log = _path(values, "GUARDIAN_AUDIT_LOG", r"%ProgramData%\TelegramPcGuardian\audit.jsonl")
        stop_file = _path(values, "GUARDIAN_STOP_FILE", r"%ProgramData%\TelegramPcGuardian\STOP")
        return cls(token, chat_id, poll_seconds, rate_limit, ttl, audit_log, stop_file)


def _positive_int(values: dict[str, str], name: str, default: int | None = None) -> int:
    raw = values.get(name, str(default) if default is not None else "")
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer.") from exc
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be greater than zero.")
    return parsed


def _positive_float(values: dict[str, str], name: str, default: float) -> float:
    try:
        parsed = float(values.get(name, str(default)))
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number.") from exc
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be greater than zero.")
    return parsed


def _path(values: dict[str, str], name: str, default: str) -> Path:
    raw = os.path.expandvars(values.get(name, default)).strip()
    if not raw:
        raise ConfigurationError(f"{name} must not be empty.")
    return Path(raw).expanduser()
