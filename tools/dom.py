# -*- coding: utf-8 -*-

import json

from state import get_browser_manager, get_dp
from utils.contract import err, ok


async def getInputElementsInfo():
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})

    # Return JSON-serializable data (strings) instead of DOM Element objects.
    js_code = (
        "const inputElements = Array.from(document.querySelectorAll('input, select, textarea, button'));"
        "return inputElements.filter(el => !el.disabled).map(el => el.outerHTML);"
    )
    try:
        tab = get_dp().browser.latest_tab
        elements = tab.run_js(js_code)
        return ok({"elements": elements})
    except Exception as e:
        return err("INTERNAL_ERROR", "getInputElementsInfo failed", {"exception": str(e)})


async def getSimplifiedDomTree():
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})

    try:
        raw = get_dp().getSimplifiedDomTree()
        # Current implementation returns JSON string; normalize to dict.
        if isinstance(raw, str):
            return ok({"dom": json.loads(raw)})
        return ok({"dom": raw})
    except json.JSONDecodeError as e:
        return err("INTERNAL_ERROR", "DOM JSON decode failed", {"exception": str(e)})
    except Exception as e:
        return err("INTERNAL_ERROR", "getSimplifiedDomTree failed", {"exception": str(e)})


async def get_body_text():
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        return ok(get_dp().get_body_text())
    except Exception as e:
        return err("INTERNAL_ERROR", "get_body_text failed", {"exception": str(e)})
