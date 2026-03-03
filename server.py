# -*- coding: utf-8 -*-

"""
Central MCP server entry.

This module owns FastMCP initialization and tool registration.
Tool implementations live in DrissionPageMCP/tools/*.
"""

from mcp.server.fastmcp import FastMCP

from core import 提示
from tools import browser, dom, files, input as input_tools, meta, network, storage


def build_mcp() -> FastMCP:
    mcp = FastMCP("DrissionPageMCP", log_level="ERROR", instructions=提示)

    # Meta
    mcp.add_tool(meta.get_version)
    mcp.add_tool(meta.get_DrissionPage_code_guide)

    # Browser / tab
    mcp.add_tool(browser.connect_or_open_browser)
    mcp.add_tool(browser.new_tab)
    mcp.add_tool(browser.wait)
    mcp.add_tool(browser.get)
    mcp.add_tool(browser.get_current_tab_info)

    # Files
    mcp.add_tool(files.download_file)
    mcp.add_tool(files.upload_file)
    mcp.add_tool(files.get_current_tab_screenshot)
    mcp.add_tool(files.get_current_tab_screenshot_as_file)

    # DOM/text
    mcp.add_tool(dom.getInputElementsInfo)
    mcp.add_tool(dom.getSimplifiedDomTree)
    mcp.add_tool(dom.get_body_text)

    # Input/interaction
    mcp.add_tool(input_tools.send_enter)
    mcp.add_tool(input_tools.click_by_xpath)
    mcp.add_tool(input_tools.click_by_containing_text)
    mcp.add_tool(input_tools.input_by_xapth)
    mcp.add_tool(input_tools.send_key)
    mcp.add_tool(input_tools.move_to)
    mcp.add_tool(input_tools.drag)

    # JS/CDP/network
    mcp.add_tool(network.run_js)
    mcp.add_tool(network.run_cdp)
    mcp.add_tool(network.listen_cdp_event)
    mcp.add_tool(network.get_cdp_event_data)
    mcp.add_tool(network.get_url_with_response_listener)
    mcp.add_tool(network.response_listener_stop)
    mcp.add_tool(network.get_response_listener_data)

    # Storage
    mcp.add_tool(storage.save_dict_to_sqlite)

    return mcp


def main() -> None:
    # MCP stdio transport uses stdout for protocol frames only.
    # Any plain-text print here can break client/server handshake.
    build_mcp().run(transport="stdio")


if __name__ == "__main__":
    main()
