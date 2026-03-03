# DrissionPageMCP Tool Contract (vNext)

本文件定义 DrissionPageMCP 的 MCP tools 对外契约（contract）。你已确认的关键决策：
- Python: >= 3.10
- Screenshot: 统一落盘返回 path + mime（禁止 bytes）
- Tool 名称保持不变，但返回结构升级为统一 envelope（breaking change，需迁移说明）

## 1. 总体约定

### 1.1 响应 Envelope（所有 tools 通用）

成功：
```json
{ "ok": true, "data": {} }
```

失败：
```json
{ "ok": false, "error": { "code": "<string>", "message": "<string>", "detail": {} } }
```

- `data`：成功时 payload，类型必须可 JSON 序列化。
- `error.code`：稳定的机器可读错误码（见 1.3）。
- `error.message`：面向人类的简短描述。
- `error.detail`：可选，补充上下文（例如 xpath、url、exception 类型、trace id 等）；必须可 JSON 序列化。

### 1.2 路径与文件返回规范

所有“生成文件/截图/下载”的工具，统一返回：
```json
{ "path": "<string>", "mime": "<string>", "size": 123 }
```

- `path`：建议返回绝对路径；如果返回相对路径，必须以 MCP Server 工作目录为基准，并在文档中说明。
- `mime`：例如 `image/png`、`image/jpeg`、`application/octet-stream`。
- `size`：可选（字节数），但建议提供。

### 1.3 统一错误码（建议最小集合）

- `NOT_CONNECTED`：未连接/未初始化浏览器。
- `NO_ACTIVE_TAB`：无法获取有效标签页。
- `TIMEOUT`：等待元素/加载超时。
- `ELEMENT_NOT_FOUND`：元素不存在（xpath/text 等定位失败）。
- `INVALID_ARGUMENT`：参数非法（key/mimeType/path 等）。
- `IO_ERROR`：文件读写/下载失败。
- `CDP_ERROR`：CDP 命令执行失败。
- `INTERNAL_ERROR`：未知异常。

### 1.4 Schema 版本策略（不改 tool 名）

- Tool 名称保持不变。
- Schema 升级通过返回字段表达：本次统一引入 envelope（`ok/data/error`）。
- 迁移期可选：在 `data.legacy` 中临时承载旧返回结构（可选项，是否保留由实现任务决定）。

## 2. Tool 清单与参数/返回（以 `server.py` 中 `build_mcp()` 当前注册为准）

说明：下列工具名称保持不变，但返回统一 envelope；旧版直接返回 dict/str/bytes 的行为视为 deprecated。

### 2.1 Meta / 文档

#### get_version()
- 输入：无
- 成功 data：`{ "version": "1.0.4" }`

#### get_DrissionPage_code_guide()
- 输入：无
- 成功 data：`{ "markdown": "..." }`

### 2.2 Browser / Tab

#### connect_or_open_browser(config)
- 输入：`{ "debug_port"?: 9222, "address"?: "host:port", "browser_path"?: "...", "headless"?: false }`
- 成功 data：包含 `browser_address`、`latest_tab_title`、`latest_tab_id`、`active_connection` 等。

#### new_tab(url)
- 输入：`{ "url": "https://..." }`
- 成功 data：`{ "title": "...", "tab_id": "...", "url": "...", "dom": <object> }`

#### get(url)
- 输入：`{ "url": "https://..." }`
- 成功 data：同 `new_tab`

#### wait(a)
- 输入：`{ "a": 3 }`
- 成功 data：`{ "waited_seconds": 3 }`

#### get_current_tab_info()
- 输入：无
- 成功 data：`{ "url": "...", "title": "...", "id": "...", "browser_address": "...", "active_connection": {...} }`

### 2.3 DOM / 文本

#### getSimplifiedDomTree()
- 输入：无
- 成功 data：`{ "dom": <object> }`
- 约束：不得返回 JSON 字符串，必须返回已解析 object。

#### get_body_text()
- 输入：无
- 成功 data：`{ "body_text": "..." }`

### 2.4 交互

#### click_by_xpath(xpath)
- 输入：`{ "xpath": "//..." }`
- 成功 data：`{ "locator": "xpath://..." }`

#### click_by_containing_text(content, index?)
- 输入：`{ "content": "登录", "index"?: 0 }`
- 成功 data：`{ "clicked": true }`

#### input_by_xapth(xpath, input_value, clear_first?)
- 输入：`{ "xpath": "//...", "input_value": "...", "clear_first"?: true }`
- 成功 data：`{ "locator": "xpath://..." }`

#### send_enter()
- 输入：无
- 成功 data：`{ "sent": "Enter" }`

#### send_key(key)
- 输入：`{ "key": "Enter" }`
- 成功 data：`{ "sent": "Enter" }`
- 备注：实现需修正/兼容当前 Literal 标注错误，contract 以字符串枚举为准。

#### move_to(xpath)
- 输入：`{ "xpath": "//..." }`
- 成功 data：`{ "locator": "xpath://..." }`

#### drag(xpath, offset_x, offset_y, duration?)
- 输入：`{ "xpath": "//...", "offset_x": 10, "offset_y": 20, "duration"?: 1000 }`
- 成功 data：`{ "offset_x": 10, "offset_y": 20, "duration": 1000 }`

### 2.5 JS / CDP

#### run_js(js_code, as_expr?)
- 输入：`{ "js_code": "return document.title", "as_expr"?: false }`
- 成功 data：`{ "result": <json-serializable> }`
- 约束：若 JS 返回不可序列化对象，必须在实现层做转换（例如 outerHTML/textContent）或返回 `INVALID_ARGUMENT`。
- 说明：默认按函数体执行（需要显式 `return` 才有结果）。当 `as_expr=true` 时按表达式求值（无需 `return`）。

#### run_cdp(cmd, cmd_args?)
- 输入：`{ "cmd": "Page.navigate", "cmd_args"?: { "url": "..." } }`
- 成功 data：`{ "result": <object> }`

#### listen_cdp_event(event_name)
- 输入：`{ "event_name": "Network.responseReceived" }`
- 成功 data：`{ "listening": true }`

#### get_cdp_event_data()
- 输入：无
- 成功 data：`{ "events": [ ... ] }`

### 2.6 Network response listener

#### get_url_with_response_listener(tab_url, mimeType, url_include?)
- 输入：`{ "tab_url": "...", "mimeType": "application/json", "url_include"?: "." }`
- 成功 data：`{ "listening": true }`

#### get_response_listener_data()
- 输入：无
- 成功 data：`{ "events": [ ... ] }`

#### response_listener_stop(clear_data?)
- 输入：`{ "clear_data"?: false }`
- 成功 data：`{ "stopped": true, "cleared": false }`

### 2.7 文件：下载/上传/截图

#### download_file(url, path, rename)
- 输入：`{ "url": "...", "path": "...", "rename": "..." }`
- 成功 data：`{ "path": "...", "mime": "application/octet-stream", "size"?: 123, "raw_result"?: "..." }`

#### upload_file(file_path, xpath?)
- 输入：`{ "file_path": "...", "xpath"?: "//input[@type='file']" }`
- 成功 data：`{ "uploaded": true }`

#### get_current_tab_screenshot()
- 新行为：落盘返回 `{ "path": "...", "mime": "image/jpeg", "size"?: 12345 }`（禁止 bytes）

#### get_current_tab_screenshot_as_file(path?, name?)
- 输入：`{ "path"?: ".", "name"?: "screenshot.png" }`
- 成功 data：`{ "path": "...", "mime": "image/png", "size"?: 123 }`（mime 以实际写入格式为准）

### 2.8 Storage

#### save_dict_to_sqlite(data, db_path?, table_name?)
- 输入：`{ "data": <object|string>, "db_path"?: "data.db", "table_name"?: "my_table" }`
- 成功 data：`{ "db_path": "...", "table_name": "..." }`
- 备注：vNext 默认不 DROP 表（append），仅在显式 overwrite 时覆盖（避免破坏性默认行为）。

## 3. 迁移说明（旧返回 -> 新返回）

### 3.1 通用迁移

- 旧：tool 可能直接返回 `dict` / `str` / `bytes`。
- 新：统一返回 envelope：
  - 成功：`resp.ok == true`，原返回放入 `resp.data`。
  - 失败：`resp.ok == false`，错误信息在 `resp.error`。

### 3.2 示例：get_body_text

旧：
```json
{ "body_text": "..." }
```

新：
```json
{ "ok": true, "data": { "body_text": "..." } }
```

### 3.3 示例：get_current_tab_screenshot

旧：`<bytes>`

新：
```json
{ "ok": true, "data": { "path": "D:/.../screenshot.jpg", "mime": "image/jpeg", "size": 12345 } }
```
