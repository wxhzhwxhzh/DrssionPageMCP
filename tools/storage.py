# -*- coding: utf-8 -*-

from typing import Any, Literal

from utils.toolbox import save_dict_to_sqlite as _save_dict_to_sqlite

from utils.contract import err, ok

__all__ = ["save_dict_to_sqlite"]


def save_dict_to_sqlite(
    data: dict[str, Any] | list[dict[str, Any]] | str,
    db_path: str = "data.db",
    table_name: str = "my_table",
    mode: Literal["append", "overwrite"] = "append",
):
    if mode not in ("append", "overwrite"):
        return err("INVALID_ARGUMENT", "mode must be one of: append, overwrite", {"mode": mode})

    try:
        r = _save_dict_to_sqlite(data=data, db_path=db_path, table_name=table_name, mode=mode)
        return ok({"result": r, "db_path": db_path, "table_name": table_name, "mode": mode})
    except ValueError as e:
        return err("INVALID_ARGUMENT", "save_dict_to_sqlite invalid input", {"exception": str(e), "db_path": db_path, "table_name": table_name, "mode": mode})
    except Exception as e:
        return err("IO_ERROR", "save_dict_to_sqlite failed", {"exception": str(e), "db_path": db_path, "table_name": table_name, "mode": mode})
