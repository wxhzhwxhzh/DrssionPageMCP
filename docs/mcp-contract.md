# DrissionPageMCP Tool Contract

这份文档定义当前 `DrissionPageMCP` 的对外 tool contract。

它不是历史迁移笔记，也不是脑补中的未来规划，基准只有三个：

- [server.py](../server.py) 实际注册的 tool
- 当前代码实现返回的 envelope 结构
- 现阶段已经落地并验证过的能力边界

## 基本原则

### 统一返回结构

所有 tool 都返回 envelope。

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

字段约束：

- `data`：成功 payload，必须可 JSON 序列化
- `error.code`：稳定、机器可读的错误码
- `error.message`：面向人类的简短说明
- `error.detail`：补充上下文，必须可 JSON 序列化

### 文件返回规范

所有截图、下载、落盘类结果统一返回：

```json
{ "path": "<string>", "mime": "<string>", "size": 123 }
```

约束：

- `path`：建议绝对路径
- `mime`：例如 `image/png`、`image/jpeg`、`application/octet-stream`
- `size`：可选，但建议提供

### 统一错误码

最小错误码集合：

- `NOT_CONNECTED`
- `NO_ACTIVE_TAB`
- `TIMEOUT`
- `ELEMENT_NOT_FOUND`
- `INVALID_ARGUMENT`
- `IO_ERROR`
- `CDP_ERROR`
- `INTERNAL_ERROR`

## Tool 清单

以下内容以 [server.py](../server.py) 当前注册结果为准。

### Meta

#### `get_version()`

- 输入：无
- 成功返回：

```json
{ "ok": true, "data": { "version": "1.0.4" } }
```

#### `get_DrissionPage_code_guide()`

- 输入：无
- 成功返回：

```json
{ "ok": true, "data": { "markdown": "..." } }
```

### Browser / Tab

#### `connect_or_open_browser(config)`

- 输入：

```json
{
  "debug_port": 9222,
  "address": "127.0.0.1:9223",
  "browser_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "headless": false
}
```

- 成功 `data` 至少包含：
  - `browser_address`
  - `latest_tab_title`
  - `latest_tab_id`
  - `active_connection`

#### `new_tab(url)`

- 输入：`{ "url": "https://..." }`
- 成功 `data`：

```json
{
  "title": "...",
  "tab_id": "...",
  "url": "...",
  "dom": {}
}
```

#### `get(url)`

- 输入：`{ "url": "https://..." }`
- 成功 `data`：同 `new_tab(url)`

#### `wait(a)`

- 输入：`{ "a": 3 }`
- 成功 `data`：

```json
{ "waited_seconds": 3 }
```

#### `get_current_tab_info()`

- 输入：无
- 成功 `data`：

```json
{
  "url": "...",
  "title": "...",
  "id": "...",
  "browser_address": "...",
  "active_connection": {}
}
```

### DOM / Text

#### `getSimplifiedDomTree()`

- 输入：无
- 成功 `data`：

```json
{ "dom": {} }
```

约束：

- 必须返回 object
- 不应返回 JSON 字符串

#### `get_body_text()`

- 输入：无
- 成功 `data`：

```json
{ "body_text": "..." }
```

### Interaction

#### `click_by_xpath(xpath)`

- 输入：`{ "xpath": "//..." }`
- 成功 `data`：

```json
{ "locator": "xpath://..." }
```

#### `click_by_containing_text(content, index?)`

- 输入：`{ "content": "登录", "index": 0 }`
- 成功 `data`：

```json
{ "clicked": true }
```

#### `input_by_xapth(xpath, input_value, clear_first?)`

- 输入：

```json
{
  "xpath": "//input[@name='q']",
  "input_value": "hello",
  "clear_first": true
}
```

- 成功 `data`：

```json
{ "locator": "xpath://..." }
```

#### `send_enter()`

- 输入：无
- 成功 `data`：

```json
{ "sent": "Enter" }
```

#### `send_key(key)`

- 输入：`{ "key": "Enter" }`
- 成功 `data`：

```json
{ "sent": "Enter" }
```

#### `move_to(xpath)`

- 输入：`{ "xpath": "//..." }`
- 成功 `data`：

```json
{ "locator": "xpath://..." }
```

#### `drag(xpath, offset_x, offset_y, duration?, human_like?, seed?)`

- 输入：

```json
{
  "xpath": "//div[contains(@class,'slider')]",
  "offset_x": 180,
  "offset_y": 0,
  "duration": 900,
  "human_like": true,
  "seed": 7
}
```

- 成功 `data`：

```json
{
  "mode": "linear | human_like",
  "offset_x": 180,
  "offset_y": 0,
  "requested_duration": 900,
  "trajectory": {
    "human_like": true,
    "seed": 7,
    "point_count": 68,
    "step_count": 52,
    "actual_duration_ms": 734,
    "start": { "x": 412.5, "y": 388.0 },
    "end": { "x": 602.5, "y": 390.0 }
  }
}
```

说明：

- `human_like=false` 时为兼容模式，走传统线性拖拽
- `human_like=true` 时，返回中应包含 `trajectory` 摘要
- `seed` 用于复现轨迹，不传则每次轨迹允许略有差异

### JS / CDP

#### `run_js(js_code, as_expr?)`

- 输入：

```json
{
  "js_code": "return document.title",
  "as_expr": false
}
```

- 成功 `data`：

```json
{ "result": "Example Domain" }
```

说明：

- 默认按函数体执行，需要显式 `return`
- `as_expr=true` 时按表达式求值，不需要写 `return`
- 若返回不可 JSON 序列化对象，应转换后返回，或返回 `INVALID_ARGUMENT`

#### `run_cdp(cmd, cmd_args?)`

- 输入：

```json
{
  "cmd": "Page.navigate",
  "cmd_args": { "url": "https://example.com" }
}
```

- 成功 `data`：

```json
{ "result": {} }
```

#### `listen_cdp_event(event_name)`

- 输入：`{ "event_name": "Network.responseReceived" }`
- 成功 `data`：

```json
{
  "listening": true,
  "listener_id": "cdp:Network.responseReceived",
  "event_name": "Network.responseReceived",
  "buffer": { "maxlen": 500, "dropped": 0 }
}
```

#### `get_cdp_event_data()`

- 输入：无
- 成功 `data`：

```json
{
  "listener_id": "cdp:Network.responseReceived",
  "event_name": "Network.responseReceived",
  "maxlen": 500,
  "dropped": 0,
  "events": []
}
```

### Network Response Listener

#### `get_url_with_response_listener(tab_url, mimeType, url_include?, watch_new_tabs?, capture_existing_tabs?)`

- 输入：

```json
{
  "tab_url": "https://example.com",
  "mimeType": "application/json",
  "url_include": "api",
  "watch_new_tabs": true,
  "capture_existing_tabs": false
}
```

- 成功 `data`：

```json
{
  "listening": true,
  "listener_id": "resp:1740000000000",
  "tab_url": "https://example.com",
  "mimeType": "application/json",
  "url_include": "api",
  "mode": "single_tab | cross_tab",
  "watch_new_tabs": true,
  "capture_existing_tabs": false,
  "attached_tab_count": 1,
  "buffer": { "maxlen": 500, "dropped": 0 }
}
```

说明：

- 默认会新开一个种子标签页访问 `tab_url` 并监听它
- `watch_new_tabs=true` 时，服务端会自动附加未来新开的 page 标签页
- `capture_existing_tabs=true` 时，会把当前浏览器里已经存在的标签页也纳入监听会话

#### `get_response_listener_data()`

- 输入：无
- 成功 `data`：

```json
{
  "listener_id": "resp:1740000000000",
  "active": true,
  "mode": "cross_tab",
  "watch_new_tabs": true,
  "capture_existing_tabs": false,
  "attached_tab_count": 2,
  "attached_tabs": [
    { "tab_id": "A1", "title": "Example Domain", "url": "https://example.com", "source": "seed_tab" },
    { "tab_id": "A2", "title": "jsonplaceholder...", "url": "https://jsonplaceholder.typicode.com/todos/1", "source": "auto_attached" }
  ],
  "events": [
    {
      "event_name": "Network.responseReceived",
      "event_data": {},
      "tab": { "tab_id": "A2", "url": "https://jsonplaceholder.typicode.com/todos/1", "source": "auto_attached" }
    }
  ]
}
```

这里最容易误判，得说透：

- `attached_tabs` 用来证明“监听已经挂到哪些标签页上”
- `events` 用来证明“这些标签页里已经出现了命中过滤条件的响应事件”
- 这两个阶段不要混为一谈

推荐验证顺序：

1. 先看 `mode`
2. 再看 `attached_tab_count`
3. 再看 `attached_tabs[*].source` 是否出现 `auto_attached`
4. 若仍需验证事件链路，再对该标签页触发一次明确网络动作，例如 reload
5. 最后再看 `events[*].tab`

#### `response_listener_stop(clear_data?)`

- 输入：`{ "clear_data": true }`
- 成功 `data`：

```json
{
  "stopped": true,
  "cleared": true,
  "had_active_listener": true,
  "previous_mode": "cross_tab"
}
```

### Files / Storage

#### `download_file(url, path, rename)`

- 输入：

```json
{
  "url": "https://example.com/file.zip",
  "path": "D:/downloads",
  "rename": "file.zip"
}
```

- 成功 `data`：

```json
{
  "path": "D:/downloads/file.zip",
  "mime": "application/octet-stream",
  "size": 12345
}
```

#### `upload_file(file_path, xpath?)`

- 输入：

```json
{
  "file_path": "D:/tmp/demo.txt",
  "xpath": "//input[@type='file']"
}
```

- 成功 `data`：

```json
{ "uploaded": true }
```

#### `get_current_tab_screenshot()`

- 输入：无
- 成功 `data`：

```json
{
  "path": "D:/.../screenshot.jpg",
  "mime": "image/jpeg",
  "size": 12345
}
```

#### `get_current_tab_screenshot_as_file(path?, name?)`

- 输入：

```json
{
  "path": ".",
  "name": "screenshot.png"
}
```

- 成功 `data`：

```json
{
  "path": "D:/.../screenshot.png",
  "mime": "image/png",
  "size": 12345
}
```

#### `save_dict_to_sqlite(data, db_path?, table_name?, mode?)`

- 输入：

```json
{
  "data": { "a": 1 },
  "db_path": "data.db",
  "table_name": "records",
  "mode": "append"
}
```

- 成功 `data`：

```json
{
  "db_path": "data.db",
  "table_name": "records"
}
```

说明：

- 默认 `mode = append`
- 如需覆盖写入，显式传 `mode = overwrite`

## 迁移说明

如果你的调用方还停留在老版本心智里，这里给你一句人话总结：

- 旧版常见返回：裸 `dict`、裸 `str`、甚至 `bytes`
- 当前版本统一返回 envelope
- 截图与下载类结果不再直接回传二进制，而是返回落盘路径

示例：

旧：

```json
{ "body_text": "..." }
```

新：

```json
{ "ok": true, "data": { "body_text": "..." } }
```

旧：

```text
<bytes>
```

新：

```json
{
  "ok": true,
  "data": {
    "path": "D:/.../screenshot.jpg",
    "mime": "image/jpeg",
    "size": 12345
  }
}
```
