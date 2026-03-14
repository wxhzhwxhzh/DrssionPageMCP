# Tool Catalog (DrissionPageMCP)

本文件用于在 `drission-page-skill` 中做快速选型，避免工具误用。

## A. 页面进入与基础状态

- `mcp__DrissionPageMCP__connect_or_open_browser`：连接或启动浏览器，会话入口。
- `mcp__DrissionPageMCP__get_current_tab_info`：读取当前页状态（`url`、`title`）。
- `mcp__DrissionPageMCP__new_tab`：新建标签页并打开 URL。
- `mcp__DrissionPageMCP__get`：在当前标签页打开 URL。
- `mcp__DrissionPageMCP__wait`：显式等待页面稳定。

默认连接模板：

```text
mcp__DrissionPageMCP__connect_or_open_browser(
  address="127.0.0.1:9223"
)
```

说明：

- 默认连接由 PowerShell 启动的真实 Chrome。
- 对应持久化目录固定为 `D:\chrome-mcp-dp`。
- 不依赖工具内部的默认 `9222` 回退。
- 浏览器关闭后，后续工具调用应返回 `NOT_CONNECTED`，要求显式重连。

## B. 页面结构与交互

- `mcp__DrissionPageMCP__getSimplifiedDomTree`：获取可用于定位的 DOM 结构。
- `mcp__DrissionPageMCP__getInputElementsInfo`：聚焦输入类控件。
- `mcp__DrissionPageMCP__get_body_text`：提取页面正文。
- `mcp__DrissionPageMCP__click_by_xpath`：精确定位点击。
- `mcp__DrissionPageMCP__click_by_containing_text`：按文本匹配点击。
- `mcp__DrissionPageMCP__input_by_xapth`：向 XPath 元素输入文本。
- `mcp__DrissionPageMCP__send_key` / `mcp__DrissionPageMCP__send_enter`：键盘操作。
- `mcp__DrissionPageMCP__move_to`：鼠标移动悬停。
- `mcp__DrissionPageMCP__drag`：拖拽元素；默认线性拖拽，遇到滑块/风控场景可传 `human_like=true` 启用人类轨迹模拟，并可用 `seed` 固定轨迹。

## C. 调试、监听、文件

- `mcp__DrissionPageMCP__run_js`：执行 JS，适合读取复杂运行时状态。
- `mcp__DrissionPageMCP__run_cdp`：执行 CDP 命令，适合底层浏览器调试。
- `mcp__DrissionPageMCP__listen_cdp_event` + `mcp__DrissionPageMCP__get_cdp_event_data`：CDP 事件链路。
- `mcp__DrissionPageMCP__get_url_with_response_listener` + `mcp__DrissionPageMCP__get_response_listener_data`：响应监听链路；需要跨标签页时传 `watch_new_tabs=true`，需要补挂当前已有标签页时再传 `capture_existing_tabs=true`。
- `mcp__DrissionPageMCP__response_listener_stop`：停止监听并清理状态（必收尾）。
- `mcp__DrissionPageMCP__download_file` / `mcp__DrissionPageMCP__upload_file`：文件传输。
- `mcp__DrissionPageMCP__get_current_tab_screenshot` / `mcp__DrissionPageMCP__get_current_tab_screenshot_as_file`：截图与落盘。
- `mcp__DrissionPageMCP__save_dict_to_sqlite`：结果持久化。

## D. 常见误用与修正

- 误用：未连接直接 `get`/`click`。  
  修正：先按固定模板执行 `connect_or_open_browser(address="127.0.0.1:9223")`，再 `get_current_tab_info`。

- 误用：定位失败后重复相同点击。  
  修正：先 `getSimplifiedDomTree` 更新结构，再调整定位表达式。

- 误用：任何拖拽都默认开 `human_like=true`。  
  修正：普通拖拽先走默认模式，只有滑块验证码、风控拖动条、行为检测场景才切 human-like。

- 误用：开启监听不关闭。  
  修正：流程结束前始终调用 `response_listener_stop`。

- 误用：明明流程会打开新标签页，还按默认参数调用响应监听。  
  修正：显式传 `watch_new_tabs=true`，再从 `get_response_listener_data()` 里核对 `mode` 和 `attached_tab_count`。

- 误用：看见 `events` 为空就断定监听失效。  
  修正：先确认 `attached_tabs[*].source` 是否出现 `auto_attached` / `existing_tab`，很多时候是监听压根没挂到目标标签页上。

- 误用：`attached_tab_count` 已经涨了，但还是把“还没抓到事件”当成“auto-attach 没成功”。  
  修正：先把“新页已挂载”和“新页已发生命中过滤条件的网络动作”分开判断；必要时对 auto-attached 的目标页 reload 一次，再看 `events[*].tab`。
