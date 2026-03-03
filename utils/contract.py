# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from typing import Any, Dict, Optional


def ok(data: Any = None) -> Dict[str, Any]:
    if data is None:
        data = {}
    return {"ok": True, "data": data}


def err(code: str, message: str, detail: Optional[Any] = None) -> Dict[str, Any]:
    e: Dict[str, Any] = {"code": code, "message": message}
    if detail is not None:
        e["detail"] = detail
    return {"ok": False, "error": e}


def ensure_jsonable(value: Any) -> bool:
    try:
        json.dumps(value, ensure_ascii=False)
        return True
    except Exception:
        return False

