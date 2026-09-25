from __future__ import annotations

import threading
from pathlib import Path

from .audit import AuditLog


def start(settings_stop_file: Path, audit: AuditLog) -> threading.Thread | None:
    """Start a visible tray icon when the optional Windows UI libraries are available."""
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        audit.write("tray_unavailable", reason="optional_dependencies_missing")
        return None

    image = Image.new("RGB", (64, 64), "white")
    ImageDraw.Draw(image).rectangle((8, 8, 56, 56), fill="#1f6feb")

    def stop(icon: object, item: object) -> None:
        settings_stop_file.parent.mkdir(parents=True, exist_ok=True)
        settings_stop_file.touch()
        audit.write("local_stop_requested", source="tray")
        icon.stop()  # type: ignore[attr-defined]

    def run() -> None:
        menu = pystray.Menu(pystray.MenuItem("Arresta guardian", stop, default=False))
        icon = pystray.Icon("telegram-pc-guardian", image, "Telegram PC Guardian", menu)
        icon.run()

    thread = threading.Thread(target=run, name="guardian-tray", daemon=True)
    thread.start()
    audit.write("tray_started")
    return thread
