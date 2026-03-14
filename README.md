# DrissionPageMCP
![](https://img.shields.io/badge/python-3.9-brightgreen)
![](https://img.shields.io/github/watchers/wxhzhwxhzh/DrissionPageMCP?style=social)
![](https://img.shields.io/github/stars/wxhzhwxhzh/DrissionPageMCP?style=social)
![](https://img.shields.io/github/forks/wxhzhwxhzh/DrissionPageMCP?style=social)

基于 `DrissionPage` 和 `FastMCP` 的浏览器自动化 MCP Server。

这仓库现在的定位很明确：通过 MCP 暴露一组稳定、可 JSON 序列化、便于大模型调用的浏览器自动化工具，覆盖页面导航、DOM 读取、点击输入、截图落盘、CDP 调试、响应监听，以及跨标签页网络监听这类稍微有点技术含量的场景。

![logo](img/DrissionPageMCP-logo.png)

## 当前状态

当前仓库和最早的原始版本已经不是一回事了，几个关键点先说透，免得一上来就踩坑：

- 所有 tool 统一返回 envelope：`{ ok, data/error }`
- 截图、下载等二进制结果统一落盘，返回 `path + mime + size`
- 不再返回不可 JSON 序列化的 DOM 对象
- 已支持跨标签页响应监听，能自动附加未来新开的标签页
- 已支持 `drag(..., human_like=true, seed=7)` 这种更自然的拖拽轨迹模式

完整对外契约见 [docs/mcp-contract.md](docs/mcp-contract.md)。

## 能力概览

### 浏览器与标签页

- 连接或接管已有 Chrome 调试实例
- 在当前标签页打开 URL
- 新建标签页并导航
- 获取当前标签页信息

### 页面读取与交互

- 获取简化版 DOM 树
- 获取输入控件信息
- 提取页面正文
- XPath 点击
- 按文本点击
- XPath 输入
- 键盘按键发送
- 鼠标悬停与拖拽

### 调试与监听

- 执行 JavaScript
- 执行 CDP 命令
- 监听 CDP 事件
- 监听响应数据包
- 跨标签页自动附加响应监听

### 文件与持久化

- 上传文件
- 下载文件
- 当前页面截图
- 结果写入 SQLite

## Tool 清单

当前 `server.py` 实际注册的 tool 如下：

### Meta

- `get_version`
- `get_DrissionPage_code_guide`

### Browser / Tab

- `connect_or_open_browser`
- `new_tab`
- `wait`
- `get`
- `get_current_tab_info`

### DOM / Text

- `getInputElementsInfo`
- `getSimplifiedDomTree`
- `get_body_text`

### Input / Interaction

- `send_enter`
- `click_by_xpath`
- `click_by_containing_text`
- `input_by_xapth`
- `send_key`
- `move_to`
- `drag`

### JS / CDP / Network

- `run_js`
- `run_cdp`
- `listen_cdp_event`
- `get_cdp_event_data`
- `get_url_with_response_listener`
- `response_listener_stop`
- `get_response_listener_data`

### Files / Storage

- `download_file`
- `upload_file`
- `get_current_tab_screenshot`
- `get_current_tab_screenshot_as_file`
- `save_dict_to_sqlite`

## 环境要求

### Python

- `Python >= 3.10`
- 推荐使用 `uv`

### 浏览器

- Chrome
- 需要能通过远程调试端口接管

### 依赖

核心依赖见 [pyproject.toml](pyproject.toml)：

- `drissionpage >= 4.1.0.18`
- `fastmcp >= 2.4.0`

开发测试依赖：

- `pytest >= 7.0.0`

## 安装

```bash
uv sync
```

如果要跑测试：

```bash
uv sync --extra dev
```

## 启动

项目入口是 [main.py](main.py)，实际会转发到 [server.py](server.py) 中的 MCP server。

直接启动：

```bash
uv run python main.py
```

## MCP 配置示例

把下面配置放进编辑器的 `mcpServers` 设置里，并把路径改成你本机仓库路径：

```json
{
  "mcpServers": {
    "DrissionPageMCP": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "D:\\mcp\\DrissionPageMCP", "run", "main.py"]
    }
  }
}
```

注意：

- Windows 路径里的反斜杠要写成 `\\`
- `uv` 需要在系统 `PATH` 中可用
- 这套配置走的是 stdio transport，不要在 server 启动阶段乱 `print`

安装相关参考：

- [docs/guides/MCP安装教程.md](docs/guides/MCP安装教程.md)

## 推荐调用顺序

别上来就点点点，浏览器自动化最怕的就是不看上下文乱抡工具。推荐顺序：

1. `connect_or_open_browser`
2. `get` 或 `new_tab`
3. `getSimplifiedDomTree`
4. `click_by_xpath` / `input_by_xapth` / `send_key`
5. `get_body_text` / `get_current_tab_info` / 截图
6. 如果启用了监听，最后执行 `response_listener_stop`

## 返回结构

所有 tool 统一返回：

成功：

```json
{ "ok": true, "data": {} }
```

失败：

```json
{
  "ok": false,
  "error": {
    "code": "NOT_CONNECTED",
    "message": "browser not connected",
    "detail": {}
  }
}
```

这不是矫情，这是为了让调用方别再被 `bytes`、不可序列化对象和乱七八糟的半结构化返回狠狠干翻。

## 快速示例

### 1. 打开页面并读取正文

```text
connect_or_open_browser({"address":"127.0.0.1:9223"})
get({"url":"https://example.com"})
getSimplifiedDomTree()
get_body_text()
```

### 2. 截图

```text
connect_or_open_browser({"address":"127.0.0.1:9223"})
get({"url":"https://example.com"})
get_current_tab_screenshot()
```

截图返回大致形态：

```json
{
  "ok": true,
  "data": {
    "path": "D:/.../dp_artifacts/screenshots/screenshot_xxx.jpg",
    "mime": "image/jpeg",
    "size": 12345
  }
}
```

### 3. Human-like Drag

当目标站点对直线拖拽比较敏感时，可以启用更自然的轨迹模式：

```text
connect_or_open_browser({"address":"127.0.0.1:9223"})
getSimplifiedDomTree()
drag({
  "xpath":"//div[contains(@class,'slider')]",
  "offset_x":180,
  "offset_y":0,
  "duration":900,
  "human_like":true,
  "seed":7
})
```

返回里会带上 `mode` 和 `trajectory` 摘要，用于区分这次到底是普通线性拖拽，还是人类轨迹模式。

### 4. 跨标签页响应监听

这是当前仓库里最容易被误用、也最值得单独讲清楚的一块。

默认情况下，`get_url_with_response_listener()` 会新开一个种子标签页并监听它。若页面后续还会打开新标签页，需要显式开启：

```text
connect_or_open_browser({"address":"127.0.0.1:9223"})
get_url_with_response_listener({
  "tab_url":"https://example.com",
  "mimeType":"application/json",
  "url_include":"jsonplaceholder.typicode.com/todos/1?from_window_open=3",
  "watch_new_tabs":true,
  "capture_existing_tabs":false
})
```

### 跨标签页监听的正确验证顺序

别只盯着 `events`。正确顺序是：

1. 先确认返回里 `mode == "cross_tab"`
2. 触发真实的新标签页动作，比如：

```text
run_js({
  "js_code":"window.open('https://jsonplaceholder.typicode.com/todos/1?from_window_open=3', '_blank'); return 'opened';"
})
```

3. 调用 `get_response_listener_data()`，先看：
   - `attached_tab_count` 是否从 `1` 增长到 `2` 以上
   - `attached_tabs[*].source` 是否出现 `auto_attached`
4. 如果新页已经挂上了，但 `events` 还是空的，先别急着下结论。这通常表示“新页已挂载，但还没发生符合过滤条件的网络动作”
5. 对 auto-attached 的目标页再触发一次明确网络动作，比如重载同一 URL
6. 再次读取 `get_response_listener_data()`，此时再看 `events[*].tab`

### 已实测通过的一条最小链路

- 种子页：`https://example.com`
- 新页动作：`window.open('https://jsonplaceholder.typicode.com/todos/1?from_window_open=3', '_blank')`
- 第一次验证：`attached_tab_count = 2`，且新页 `source = auto_attached`
- 第二次验证：对 JSON 新页重载一次后，`events[*].tab.url` 命中该新页 URL

## 常见问题

### `NOT_CONNECTED`

先调用 `connect_or_open_browser`，或者确认浏览器调试端口可用。

### 返回值客户端解析不了

优先确认调用方是否已经按 envelope 结构处理，而不是还拿老版本的裸 `dict` / `bytes` 心智在那儿硬套。

### 开了跨标签页监听，但没抓到新页响应

先查三件事：

1. 是否传了 `watch_new_tabs=true`
2. `attached_tab_count` 有没有增长
3. `attached_tabs[*].source` 有没有出现 `auto_attached`

如果 `auto_attached` 已经出现，但 `events` 为空，先判断是不是“已挂载但尚未发生命中过滤条件的网络动作”，别把这两件事混成一个结论。

## 本地开发与测试

运行测试：

```bash
uv run python -m pytest -q
```

只做语法级检查：

```bash
python -m py_compile core.py server.py tools\\network.py
```

## 调试

### MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector uv run D:\\mcp\\DrissionPageMCP\\main.py
```

### MCP Dev

```bash
mcp dev D:\\mcp\\DrissionPageMCP\\main.py
```

## 相关文档

- [docs/mcp-contract.md](docs/mcp-contract.md)
- [docs/guides/MCP安装教程.md](docs/guides/MCP安装教程.md)
- [docs/guides/DrissionPage使用教程.md](docs/guides/DrissionPage使用教程.md)
- [docs/guides/DrissionPage_code_guide.md](docs/guides/DrissionPage_code_guide.md)

## 仓库说明

如果你是从原仓库 README 的历史描述一路看过来的，最好把旧心智扔一扔。当前这份 README 以 `server.py` 实际注册的 tools、`docs/mcp-contract.md` 当前契约、以及已经做过的真实跨标签页监听验证为准。老描述要是和这里冲突，按这里来，别跟过期文档谈恋爱。
