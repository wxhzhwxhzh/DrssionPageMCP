# Tool Catalog (mcp_router)

本文件用于在 `drission-page-skill` 中做快速选型，避免工具误用。

## A. 页面进入与基础状态

- `mcp__mcp_router__connect_or_open_browser`：连接或启动浏览器，会话入口。
- `mcp__mcp_router__get_current_tab_info`：读取当前页状态（`url`、`title`）。
- `mcp__mcp_router__new_tab`：新建标签页并打开 URL。
- `mcp__mcp_router__get`：在当前标签页打开 URL。
- `mcp__mcp_router__wait`：显式等待页面稳定。

## B. 页面结构与交互

- `mcp__mcp_router__getSimplifiedDomTree`：获取可用于定位的 DOM 结构。
- `mcp__mcp_router__getInputElementsInfo`：聚焦输入类控件。
- `mcp__mcp_router__get_body_text`：提取页面正文。
- `mcp__mcp_router__click_by_xpath`：精确定位点击。
- `mcp__mcp_router__click_by_containing_text`：按文本匹配点击。
- `mcp__mcp_router__input_by_xapth`：向 XPath 元素输入文本。
- `mcp__mcp_router__send_key` / `mcp__mcp_router__send_enter`：键盘操作。
- `mcp__mcp_router__move_to` / `mcp__mcp_router__drag`：鼠标移动与拖拽。

## C. 调试、监听、文件

- `mcp__mcp_router__run_js`：执行 JS，适合读取复杂运行时状态。
- `mcp__mcp_router__run_cdp`：执行 CDP 命令，适合底层浏览器调试。
- `mcp__mcp_router__listen_cdp_event` + `mcp__mcp_router__get_cdp_event_data`：CDP 事件链路。
- `mcp__mcp_router__get_url_with_response_listener` + `mcp__mcp_router__get_response_listener_data`：响应监听链路。
- `mcp__mcp_router__response_listener_stop`：停止监听并清理状态（必收尾）。
- `mcp__mcp_router__download_file` / `mcp__mcp_router__upload_file`：文件传输。
- `mcp__mcp_router__get_current_tab_screenshot` / `mcp__mcp_router__get_current_tab_screenshot_as_file`：截图与落盘。
- `mcp__mcp_router__save_dict_to_sqlite`：结果持久化。

## D. 常见误用与修正

- 误用：未连接直接 `get`/`click`。  
  修正：先 `connect_or_open_browser`，再 `get_current_tab_info`。

- 误用：定位失败后重复相同点击。  
  修正：先 `getSimplifiedDomTree` 更新结构，再调整定位表达式。

- 误用：开启监听不关闭。  
  修正：流程结束前始终调用 `response_listener_stop`。
