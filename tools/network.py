# -*- coding: utf-8 -*-

from typing import Any

from state import get_browser_manager, get_dp, get_listener_manager
from utils.contract import ensure_jsonable, err, ok


async def run_js(js_code: str, as_expr: bool = False):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        r = get_dp().run_js(js_code=js_code, as_expr=as_expr)
        # Best-effort: fail fast if result is not JSON-serializable.
        if not ensure_jsonable(r):
            return err("INVALID_ARGUMENT", "JS result is not JSON-serializable", {"result_type": type(r).__name__})
        data = {"result": r}
        if r is None and (not as_expr) and ("return" not in js_code):
            data["hint"] = "run_js uses function-body semantics by default; add return or set as_expr=true for expression evaluation."
        return ok(data)
    except Exception as e:
        return err("INTERNAL_ERROR", "run_js failed", {"exception": str(e)})


async def run_cdp(cmd: str, cmd_args: dict[str, Any] | None = None):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})

    if cmd_args is None:
        cmd_args = {}
    elif not isinstance(cmd_args, dict):
        return err("INVALID_ARGUMENT", "cmd_args must be an object", {"got_type": type(cmd_args).__name__})

    try:
        r = get_dp().run_cdp(cmd, **cmd_args)
        if not ensure_jsonable(r):
            return err("CDP_ERROR", "CDP result is not JSON-serializable", {"result_type": type(r).__name__})
        return ok({"result": r})
    except Exception as e:
        return err("CDP_ERROR", "run_cdp failed", {"exception": str(e), "cmd": cmd})


async def listen_cdp_event(event_name: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        listener_id = get_listener_manager().start_cdp_listener(event_name=event_name)
        snap = get_listener_manager().get_cdp_snapshot()
        return ok(
            {
                "listening": True,
                "listener_id": listener_id,
                "event_name": event_name,
                "buffer": {"maxlen": snap.get("maxlen"), "dropped": snap.get("dropped")},
            }
        )
    except Exception as e:
        return err("CDP_ERROR", "listen_cdp_event failed", {"exception": str(e), "event_name": event_name})


def get_cdp_event_data():
    try:
        return ok(get_listener_manager().get_cdp_snapshot())
    except Exception as e:
        return err("INTERNAL_ERROR", "get_cdp_event_data failed", {"exception": str(e)})


async def get_url_with_response_listener(tab_url: str, mimeType: str, url_include: str = "."):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        listener_id = get_listener_manager().start_response_listener(tab_url=tab_url, mimeType=mimeType, url_include=url_include)
        snap = get_listener_manager().get_response_snapshot()
        return ok(
            {
                "listening": True,
                "listener_id": listener_id,
                "tab_url": tab_url,
                "mimeType": mimeType,
                "url_include": url_include,
                "buffer": {"maxlen": snap.get("maxlen"), "dropped": snap.get("dropped")},
            }
        )
    except Exception as e:
        return err("INTERNAL_ERROR", "get_url_with_response_listener failed", {"exception": str(e)})


async def response_listener_stop(clear_data: bool = False):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        raw = get_dp().response_listener_stop(clear_data=clear_data)
        if isinstance(raw, dict):
            return ok(raw)
        return ok({"stopped": True, "cleared": clear_data, "result": raw})
    except Exception as e:
        return err("INTERNAL_ERROR", "response_listener_stop failed", {"exception": str(e)})


def get_response_listener_data():
    try:
        return ok(get_listener_manager().get_response_snapshot())
    except Exception as e:
        return err("INTERNAL_ERROR", "get_response_listener_data failed", {"exception": str(e)})
