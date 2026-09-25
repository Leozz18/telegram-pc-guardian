from __future__ import annotations

import logging
import tempfile
import threading
import time
from pathlib import Path

from .audit import AuditLog
from .auth import CommandAuthorizer
from .config import Settings
from .rate_limit import RateLimiter
from .telegram import TelegramClient
from .tray import start as start_tray
from .windows import WindowsActionError, notify_user, perform

HELP = "/status, /shutdown, /restart, /lock, /screenshot, /stop. Le azioni sensibili richiedono /confirm CODICE."


def run(settings: Settings) -> None:
    audit = AuditLog(settings.audit_log)
    client = TelegramClient(settings.bot_token)
    authorizer = CommandAuthorizer(settings.allowed_chat_id, settings.confirmation_ttl_seconds)
    limiter = RateLimiter(settings.rate_limit_per_minute)
    audit.write("startup", allowed_chat_id=settings.allowed_chat_id)
    start_tray(settings.stop_file, audit)
    notify_user("Telegram PC Guardian", "Guardian avviato. Controllo trasparente attivo; usa il file STOP per disabilitare localmente.")
    offset = None
    try:
        while not settings.stop_file.exists():
            for update in client.get_updates(offset):
                offset = update.update_id + 1
                if not limiter.allow():
                    audit.write("rate_limited", chat_id=update.chat_id)
                    continue
                decision = authorizer.inspect(update.chat_id, update.text)
                audit.write("command", chat_id=update.chat_id, command=update.text.split()[0] if update.text else "", allowed=decision.allowed, reason=decision.reason)
                if not decision.allowed:
                    continue
                if decision.action == "status":
                    client.send_message(update.chat_id, "Guardian attivo. Nessuna operazione eseguita.")
                elif decision.action == "help":
                    client.send_message(update.chat_id, HELP)
                elif decision.needs_confirmation:
                    client.send_message(update.chat_id, f"Conferma esplicita richiesta per {decision.action}: /confirm {decision.confirmation_code} (valida {settings.confirmation_ttl_seconds}s)")
                elif decision.action == "stop":
                    settings.stop_file.parent.mkdir(parents=True, exist_ok=True)
                    settings.stop_file.touch()
                    client.send_message(update.chat_id, "Arresto confermato. Il guardian si disabiliterà.")
                else:
                    _execute_confirmed(client, audit, update.chat_id, decision.action, settings)
            time.sleep(settings.poll_seconds)
    finally:
        audit.write("shutdown")
        notify_user("Telegram PC Guardian", "Guardian arrestato.")


def _execute_confirmed(client: TelegramClient, audit: AuditLog, chat_id: int, action: str | None, settings: Settings) -> None:
    if action not in {"shutdown", "restart", "lock", "screenshot"}:
        return
    notify_user("Telegram PC Guardian", f"Azione autorizzata: {action}.")
    try:
        path = Path(tempfile.gettempdir()) / "telegram-pc-guardian-screenshot.png" if action == "screenshot" else None
        result = perform(action, path)
        audit.write("action_completed", action=action, chat_id=chat_id)
        if result:
            client.send_photo(chat_id, str(result))
            result.unlink(missing_ok=True)
        else:
            client.send_message(chat_id, f"Azione completata: {action}.")
    except (WindowsActionError, OSError, RuntimeError) as exc:
        audit.write("action_failed", action=action, chat_id=chat_id, error=type(exc).__name__)
        client.send_message(chat_id, f"Azione non completata: {exc}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    run(Settings.from_env())


if __name__ == "__main__":
    main()
