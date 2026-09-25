from __future__ import annotations

import ctypes
import platform
from pathlib import Path


class WindowsActionError(RuntimeError):
    pass


def notify_user(title: str, message: str) -> None:
    if platform.system() != "Windows":
        return
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)


def perform(action: str, screenshot_path: Path | None = None) -> Path | None:
    if platform.system() != "Windows":
        raise WindowsActionError("Windows APIs are only available on Windows.")
    user32 = ctypes.windll.user32
    if action == "lock":
        if not user32.LockWorkStation():
            raise WindowsActionError("LockWorkStation failed.")
    elif action in {"shutdown", "restart"}:
        flags = 0x00000001 if action == "shutdown" else 0x00000002
        if not user32.ExitWindowsEx(flags, 0):
            raise WindowsActionError("ExitWindowsEx failed; administrator privileges may be required.")
    elif action == "screenshot":
        if screenshot_path is None:
            raise WindowsActionError("A screenshot destination is required.")
        try:
            from PIL import ImageGrab
            image = ImageGrab.grab(all_screens=True)
            image.save(screenshot_path, format="PNG")
        except Exception as exc:
            raise WindowsActionError(f"Screenshot unavailable: {exc}") from exc
        return screenshot_path
    else:
        raise WindowsActionError(f"Unsupported action: {action}")
    return None
