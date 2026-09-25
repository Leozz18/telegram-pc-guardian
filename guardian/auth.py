from __future__ import annotations

import secrets
import time
from dataclasses import dataclass


DESTRUCTIVE_ACTIONS = frozenset({"shutdown", "restart", "lock", "screenshot", "stop"})


@dataclass(frozen=True)
class Authorization:
    allowed: bool
    action: str | None = None
    needs_confirmation: bool = False
    confirmation_code: str | None = None
    reason: str = ""


@dataclass
class _Pending:
    action: str
    code: str
    expires_at: float


class CommandAuthorizer:
    """Allow one chat and require a fresh explicit confirmation for sensitive actions."""

    def __init__(self, allowed_chat_id: int, ttl_seconds: int = 60, clock=time.monotonic):
        self.allowed_chat_id = allowed_chat_id
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self._pending: dict[int, _Pending] = {}

    def inspect(self, chat_id: int, text: str) -> Authorization:
        if chat_id != self.allowed_chat_id:
            return Authorization(False, reason="chat_id_not_allowlisted")
        command = text.strip().split()
        if not command:
            return Authorization(False, reason="empty_command")
        name = command[0].lower().split("@", 1)[0]
        actions = {"shutdown", "restart", "lock", "screenshot", "stop"}
        if name == "/status":
            return Authorization(True, action="status")
        if name == "/help":
            return Authorization(True, action="help")
        if name.startswith("/") and name[1:] in actions and len(command) == 1:
            action = name[1:]
            code = secrets.token_urlsafe(8)
            self._pending[chat_id] = _Pending(action, code, self._clock() + self.ttl_seconds)
            return Authorization(True, action=action, needs_confirmation=True, confirmation_code=code)
        if name == "/confirm" and len(command) == 2:
            pending = self._pending.get(chat_id)
            if pending and pending.expires_at >= self._clock() and secrets.compare_digest(command[1], pending.code):
                del self._pending[chat_id]
                return Authorization(True, action=pending.action)
            if pending and pending.expires_at < self._clock():
                self._pending.pop(chat_id, None)
            return Authorization(False, reason="invalid_or_expired_confirmation")
        return Authorization(False, reason="unknown_or_malformed_command")
