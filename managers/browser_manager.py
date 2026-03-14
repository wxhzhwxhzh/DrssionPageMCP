# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from core import DrissionPageMCP


@dataclass
class BrowserManager:
    """
    Minimal browser lifecycle guard.

    This is intentionally small: later tasks will introduce richer state
    (active tab id, listener management, error normalization, etc.).
    """

    dp: DrissionPageMCP
    default_config: dict

    @staticmethod
    def _auto_reconnect_enabled() -> bool:
        value = os.getenv("DRISSIONPAGE_MCP_AUTO_RECONNECT", "false").strip().lower()
        return value in {"1", "true", "yes", "on"}

    async def ensure_browser(self) -> Tuple[bool, Optional[str]]:
        if self.dp.browser is not None:
            return True, None
        if not self._auto_reconnect_enabled():
            return False, "browser not connected; call connect_or_open_browser explicitly"
        try:
            await self.dp.connect_or_open_browser(config=self.default_config)
            return True, None
        except Exception as e:
            return False, str(e)

    def has_browser(self) -> bool:
        return self.dp.browser is not None

    def get_latest_tab(self) -> Any:
        # DrissionPage types are optional at runtime; keep it generic.
        return self.dp.browser.latest_tab

    def set_default_config(self, config: dict) -> None:
        # Keep the latest successful connection config for future auto-reconnect.
        self.default_config = dict(config or {})
