#！/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compatibility shim.

Historically this repository started the MCP server directly from this file.
The server entry has been moved to `DrissionPageMCP/server.py` to keep `main.py`
small and avoid tool implementation drift.
"""

from server import main


if __name__ == "__main__":
    main()
