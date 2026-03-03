# -*- coding: utf-8 -*-

import mimetypes
import time
from pathlib import Path

from state import get_browser_manager, get_dp
from utils.contract import err, ok


def _resolve_download_dir(path: str) -> Path:
    """
    Resolve download directory with a predictable base.

    - If `path` is absolute: use it.
    - If `path` is '.' or empty: use cwd/dp_artifacts/downloads.
    - Else: use cwd/dp_artifacts/downloads/<path>.
    """
    base = Path.cwd() / "dp_artifacts" / "downloads"
    if not path or path == ".":
        return base
    p = Path(path)
    if p.is_absolute():
        return p
    return base / p


async def download_file(url: str, path: str, rename: str):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        out_dir = _resolve_download_dir(path)
        out_dir.mkdir(parents=True, exist_ok=True)
        raw = get_dp().download_file(url=url, path=str(out_dir), rename=rename)

        out_path = (out_dir / rename).resolve()
        mime = mimetypes.guess_type(str(out_path))[0] or "application/octet-stream"
        size = None
        try:
            size = out_path.stat().st_size
        except Exception:
            pass

        return ok({"path": str(out_path), "mime": mime, "size": size, "raw_result": raw})
    except Exception as e:
        return err("IO_ERROR", "download_file failed", {"exception": str(e), "url": url, "path": path})


async def upload_file(file_path: str, xpath: str = "//input[@type='file']"):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        raw = get_dp().upload_file(file_path=file_path, xpath=xpath)
        if isinstance(raw, dict):
            return ok(raw)
        return ok({"uploaded": True, "result": raw, "file_path": file_path, "xpath": xpath})
    except LookupError as e:
        return err("ELEMENT_NOT_FOUND", "upload_file failed", {"exception": str(e), "file_path": file_path, "xpath": xpath})
    except ValueError as e:
        return err("INVALID_ARGUMENT", "upload_file failed", {"exception": str(e), "file_path": file_path, "xpath": xpath})
    except Exception as e:
        return err("IO_ERROR", "upload_file failed", {"exception": str(e), "file_path": file_path, "xpath": xpath})


def get_current_tab_screenshot():
    # vNext contract: no bytes over stdio. Always save to disk and return {path,mime,size}.
    if not get_browser_manager().has_browser():
        return err("NOT_CONNECTED", "browser not connected")

    try:
        out_dir = Path.cwd() / "dp_artifacts" / "screenshots"
        out_dir.mkdir(parents=True, exist_ok=True)
        name = f"screenshot_{int(time.time() * 1000)}.jpg"
        path = get_dp().get_current_tab_screenshot_as_file(path=str(out_dir), name=name)
        mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
        size = None
        try:
            size = Path(path).stat().st_size
        except Exception:
            pass
        return ok({"path": str(Path(path).resolve()), "mime": mime, "size": size})
    except Exception as e:
        return err("IO_ERROR", "get_current_tab_screenshot failed", {"exception": str(e)})


async def get_current_tab_screenshot_as_file(path: str = ".", name: str = "screenshot.png"):
    ok_, err_ = await get_browser_manager().ensure_browser()
    if not ok_:
        return err("NOT_CONNECTED", "browser not connected", {"exception": err_})
    try:
        p = get_dp().get_current_tab_screenshot_as_file(path=path, name=name)
        mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        size = None
        try:
            size = Path(p).stat().st_size
        except Exception:
            pass
        return ok({"path": str(Path(p).resolve()), "mime": mime, "size": size})
    except Exception as e:
        return err("IO_ERROR", "get_current_tab_screenshot_as_file failed", {"exception": str(e), "path": path, "name": name})
