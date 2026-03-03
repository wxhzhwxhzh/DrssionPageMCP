# -*- coding: utf-8 -*-

"""
Global state holder for the MCP server.

We keep a single DrissionPageMCP instance because the stdio transport is
typically single-session. Later tasks will replace this with a proper
BrowserManager/ListenerManager.
"""

from core import DrissionPageMCP
from managers.browser_manager import BrowserManager
from managers.listener_manager import ListenerManager

_dp = DrissionPageMCP()
_browser_manager = BrowserManager(dp=_dp, default_config={"debug_port": 9222})
_listener_manager = ListenerManager(dp=_dp)


def get_dp() -> DrissionPageMCP:
    return _dp


def get_browser_manager() -> BrowserManager:
    return _browser_manager


def get_listener_manager() -> ListenerManager:
    return _listener_manager
