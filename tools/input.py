# -*- coding: utf-8 -*-

from state import get_browser_manager, get_dp
from utils.contract import err, ok


def _map_input_error(e: Exception, message: str, detail: dict):
    if isinstance(e, (LookupError, IndexError)):
        return err("ELEMENT_NOT_FOUND", message, {"exception": str(e), **detail})
    if isinstance(e, ValueError):
        return err("INVALID_ARGUMENT", message, {"exception": str(e), **detail})
    if isinstance(e, TimeoutError):
        return err("TIMEOUT", message, {"exception": str(e), **detail})
    return err("INTERNAL_ERROR", message, {"exception": str(e), **detail})


async def click_by_xpath(xpath: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().click_by_xpath(xpath=xpath))
    except Exception as e:
        return _map_input_error(e, "click_by_xpath failed", {"xpath": xpath})


async def click_by_containing_text(content: str, index: int = None):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().click_by_containing_text(content=content, index=index))
    except Exception as e:
        return _map_input_error(e, "click_by_containing_text failed", {"content": content, "index": index})


async def input_by_xapth(xpath: str, input_value: str, clear_first: bool = True):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().input_by_xapth(xpath=xpath, input_value=input_value, clear_first=clear_first))
    except Exception as e:
        return _map_input_error(e, "input_by_xapth failed", {"xpath": xpath})


async def send_enter():
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().send_enter())
    except Exception as e:
        return _map_input_error(e, "send_enter failed", {})


async def send_key(key: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().send_key(key=key))
    except Exception as e:
        return _map_input_error(e, "send_key failed", {"key": key})


async def move_to(xpath: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().move_to(xpath=xpath))
    except Exception as e:
        return _map_input_error(e, "move_to failed", {"xpath": xpath})


async def drag(xpath: str, offset_x: int, offset_y: int, duration: int = 1000):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().drag(xpath=xpath, offset_x=offset_x, offset_y=offset_y, duration=duration))
    except Exception as e:
        return _map_input_error(e, "drag failed", {"xpath": xpath})
