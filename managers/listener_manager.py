# -*- coding: utf-8 -*-

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from core import DrissionPageMCP


@dataclass
class ListenerManager:
    """
    Minimal listener state holder.

    It provides stable listener identifiers without changing tool names.
    Underlying buffers live in DrissionPageMCP (bounded deques).
    """

    dp: DrissionPageMCP

    current_cdp_listener_id: Optional[str] = None
    current_cdp_event_name: Optional[str] = None

    current_response_listener_id: Optional[str] = None

    def start_cdp_listener(self, event_name: str) -> str:
        listener_id = f"cdp:{event_name}"
        self.current_cdp_listener_id = listener_id
        self.current_cdp_event_name = event_name
        result = self.dp.listen_cdp_event(event_name=event_name)
        if not isinstance(result, dict) or result.get("listening") is not True:
            raise RuntimeError(f"failed to listen cdp event: {event_name}")
        return listener_id

    def get_cdp_snapshot(self) -> Dict[str, Any]:
        return {
            "listener_id": self.current_cdp_listener_id,
            "event_name": self.current_cdp_event_name,
            "maxlen": getattr(self.dp.cdp_event_data, "maxlen", None),
            "dropped": getattr(self.dp, "cdp_event_dropped", 0),
            "events": self.dp.get_cdp_event_data(),
        }

    def start_response_listener(self, tab_url: str, mimeType: str, url_include: str) -> str:
        # We keep a single active response listener in vNext (stdio single-session).
        listener_id = f"resp:{int(time.time() * 1000)}"
        self.current_response_listener_id = listener_id
        result = self.dp.get_url_with_response_listener(tab_url=tab_url, mimeType=mimeType, url_include=url_include)
        if not isinstance(result, dict) or result.get("listening") is not True:
            raise RuntimeError(f"failed to start response listener for: {tab_url}")
        return listener_id

    def get_response_snapshot(self) -> Dict[str, Any]:
        return {
            "listener_id": self.current_response_listener_id,
            "maxlen": getattr(self.dp.response_listener_data, "maxlen", None),
            "dropped": getattr(self.dp, "response_listener_dropped", 0),
            "events": self.dp.get_response_listener_data(),
        }
