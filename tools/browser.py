# -*- coding: utf-8 -*-

import json

from state import get_browser_manager, get_dp
from utils.contract import err, ok


def _normalize_dom_payload(payload: dict):
    if not isinstance(payload, dict):
        return payload
    dom = payload.get("dom")
    if isinstance(dom, str):
        try:
            payload = dict(payload)
            payload["dom"] = json.loads(dom)
        except json.JSONDecodeError:
            # Keep original value; caller still gets a valid envelope.
            pass
    return payload


async def connect_or_open_browser(
    debug_port: int | None = None,
    browser_path: str | None = None,
    headless: bool | None = None,
    address: str | None = None,
    config: dict | None = None,
):
    try:
        merged_config = dict(config or {})
        if address is not None:
            merged_config["address"] = address
        if debug_port is not None:
            merged_config["debug_port"] = debug_port
        elif "address" not in merged_config and "debug_port" not in merged_config:
            # Keep backward compatibility: default to local 9222 when nothing provided.
            merged_config["debug_port"] = 9222
        if browser_path is not None:
            merged_config["browser_path"] = browser_path
        if headless is not None:
            merged_config["headless"] = bool(headless)

        data = await get_dp().connect_or_open_browser(config=merged_config)
        get_browser_manager().set_default_config(merged_config)
        return ok(data)
    except Exception as e:
        return err("INTERNAL_ERROR", "connect_or_open_browser failed", {"exception": str(e)})


async def new_tab(url: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(_normalize_dom_payload(await get_dp().new_tab(url=url)))
    except Exception as e:
        return err("INTERNAL_ERROR", "new_tab failed", {"exception": str(e), "url": url})


async def get(url: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(_normalize_dom_payload(await get_dp().get(url=url)))
    except Exception as e:
        return err("INTERNAL_ERROR", "get failed", {"exception": str(e), "url": url})


async def wait(a: int):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        get_dp().wait(a)
        return ok({"waited_seconds": a})
    except Exception as e:
        return err("INTERNAL_ERROR", "wait failed", {"exception": str(e), "seconds": a})


def get_current_tab_info():
    if not get_browser_manager().has_browser():
        return err("NOT_CONNECTED", "browser not connected")
    try:
        return ok(get_dp().get_current_tab_info())
    except Exception as e:
        return err("INTERNAL_ERROR", "get_current_tab_info failed", {"exception": str(e)})
