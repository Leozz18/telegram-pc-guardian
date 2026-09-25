from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Update:
    update_id: int
    chat_id: int
    text: str


class TelegramClient:
    def __init__(self, token: str, timeout: float = 20):
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.timeout = timeout

    def _call(self, method: str, data: dict[str, str]) -> dict:
        encoded = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(f"{self.base_url}/{method}", data=encoded)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram API error for {method}.")
        return payload["result"]

    def get_updates(self, offset: int | None) -> list[Update]:
        data = {"timeout": "15"}
        if offset is not None:
            data["offset"] = str(offset)
        result = self._call("getUpdates", data)
        return [
            Update(item["update_id"], item["message"]["chat"]["id"], item["message"].get("text", ""))
            for item in result
            if item.get("message")
        ]

    def send_message(self, chat_id: int, text: str) -> None:
        self._call("sendMessage", {"chat_id": str(chat_id), "text": text})

    def send_photo(self, chat_id: int, path: str) -> None:
        # Kept explicit: urllib is sufficient for text, while photo upload is delegated to requests.
        import requests
        with open(path, "rb") as photo:
            response = requests.post(f"{self.base_url}/sendPhoto", data={"chat_id": str(chat_id)}, files={"photo": photo}, timeout=self.timeout)
        if not response.ok or not response.json().get("ok"):
            raise RuntimeError("Telegram photo upload failed.")
