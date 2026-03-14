---
name: drission-page-skill
description: Use when handling browser automation tasks in this repository through MCP (navigation, DOM inspection, click/input, upload/download, screenshot, JS/CDP, listener analysis). Enforce unified tool namespace via mcp__DrissionPageMCP__* only, and apply deterministic workflow with retries, observability logs, error taxonomy, and completion checklist.
---

# drission-page-skill

通过 `DrissionPageMCP` 统一编排浏览器自动化，目标是“可重复执行 + 可排障 + 可审计”。

## 浏览器实例约束（新增强约束）

- 固定使用本机 Chrome：`C:\Program Files\Google\Chrome\Application\chrome.exe`
- 固定调试端口：`9223`
- 固定持久化目录：`D:\chrome-mcp-dp`
- 默认复用同一个已启动浏览器实例，不新建临时 profile，不默认走 headless。
- 浏览器启动优先使用 PowerShell 脚本：`assets/start-local-chrome-9223.ps1`
- `DrissionPageMCP` 负责“连接浏览器”，不是替你随手拉一个未知 profile 的新实例。

推荐启动命令：

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\shang\.codex\skills\drissionPage-skill\assets\start-local-chrome-9223.ps1"
```

## 0) 入口约束

- 仅调用 `mcp__DrissionPageMCP__*` 前缀工具。
- 不混用其他命名空间的浏览器工具。
- 在调用工具前，先声明当前阶段（`CONNECT` / `NAVIGATE` / `INSPECT` / `ACT` / `VERIFY`）。
- 交互失败后必须输出可执行补救动作，不允许只给错误文本。
- `CONNECT` 阶段默认连接 `127.0.0.1:9223`，显式调用：
  `mcp__DrissionPageMCP__connect_or_open_browser(address="127.0.0.1:9223")`
- 除非用户明确要求隔离环境，否则禁止改用其他调试端口或随机浏览器实例。
- 浏览器被用户关闭后，默认返回 `NOT_CONNECTED`，不要隐式自动补连。

## 1) 执行状态机（强约束）

按以下状态顺序执行，不跳步：

1. `CONNECT`：连接浏览器并拿到当前标签页信息。
2. `NAVIGATE`：打开目标页面或新建标签页。
3. `INSPECT`：读取 DOM / 输入控件 / 页面文本，确定可操作目标。
4. `ACT`：执行点击、输入、键盘、拖拽等交互。
5. `VERIFY`：验证结果（文本、截图、网络事件、响应监听）。
6. `PERSIST`（可选）：下载、上传、截图落盘、SQLite 持久化。
7. `CLOSE`（可选）：结束监听，输出最终执行报告。

若某一步失败，返回上一步重新建模，不直接硬闯后续步骤。

## 2) 工具分层（按职责调用）

### 2.1 Connect / Navigate

- `mcp__DrissionPageMCP__connect_or_open_browser`
- `mcp__DrissionPageMCP__get_current_tab_info`
- `mcp__DrissionPageMCP__new_tab`
- `mcp__DrissionPageMCP__get`
- `mcp__DrissionPageMCP__wait`

### 2.2 Inspect / Interaction

- `mcp__DrissionPageMCP__getSimplifiedDomTree`
- `mcp__DrissionPageMCP__getInputElementsInfo`
- `mcp__DrissionPageMCP__get_body_text`
- `mcp__DrissionPageMCP__click_by_xpath`
- `mcp__DrissionPageMCP__click_by_containing_text`
- `mcp__DrissionPageMCP__input_by_xapth`
- `mcp__DrissionPageMCP__send_key`
- `mcp__DrissionPageMCP__send_enter`
- `mcp__DrissionPageMCP__move_to`
- `mcp__DrissionPageMCP__drag`

拖拽补充约束：

- 默认使用 `mcp__DrissionPageMCP__drag(xpath, offset_x, offset_y, duration)` 做普通拖拽。
- 遇到滑块验证码、风控拖动条、明显依赖行为轨迹的场景时，升级为
  `mcp__DrissionPageMCP__drag(xpath, offset_x, offset_y, duration, human_like=true, seed=7)`。
- `human_like=true` 只在“线性拖拽容易被识别”时启用；不要把它当默认万能锤子。
- 需要复现实验时显式传 `seed`；只求更自然、不要求复现时可不传。

### 2.3 Debug / Network / File

- `mcp__DrissionPageMCP__run_js`
- `mcp__DrissionPageMCP__run_cdp`
- `mcp__DrissionPageMCP__listen_cdp_event`
- `mcp__DrissionPageMCP__get_cdp_event_data`
- `mcp__DrissionPageMCP__get_url_with_response_listener`
- `mcp__DrissionPageMCP__get_response_listener_data`
- `mcp__DrissionPageMCP__response_listener_stop`
- `mcp__DrissionPageMCP__download_file`
- `mcp__DrissionPageMCP__upload_file`
- `mcp__DrissionPageMCP__get_current_tab_screenshot`
- `mcp__DrissionPageMCP__get_current_tab_screenshot_as_file`
- `mcp__DrissionPageMCP__save_dict_to_sqlite`

更细分的工具选择、参数建议和常见误用见 `references/tool-catalog.md`。

跨标签页监听补充约束：

- 默认 `get_url_with_response_listener(tab_url, mimeType, url_include)` 只监听新开的种子标签页。
- 目标流程如果会继续 `window.open()` / 打开详情页 / OAuth 跳新页，必须显式加 `watch_new_tabs=true`。
- 需要把当前浏览器里已经存在的标签页一起纳入监听时，再加 `capture_existing_tabs=true`。
- 读取结果时优先检查 `get_response_listener_data()` 里的 `mode`、`attached_tab_count`、`attached_tabs[*].source`，别只盯着 `events`。

### 2.4 默认连接模板

首选固定模板：

```text
mcp__DrissionPageMCP__connect_or_open_browser(
  address="127.0.0.1:9223"
)
```

说明：

- 优先连接已由 PowerShell 拉起的真实 Chrome。
- 不依赖 `DrissionPageMCP` 默认的 `9222` 回退逻辑。
- 浏览器若不存在，应显式报错并提示先运行启动脚本。
- 若当前标签页已存在业务上下文，优先复用该标签页，避免 `new_tab` 打乱登录态。

## 3) 重试与幂等策略

- `connect` 类失败：重试 1 次，仍失败则返回 `NOT_CONNECTED` 并停止。
- 定位失败（XPath/文本）：先刷新 DOM（`getSimplifiedDomTree`）再重试 1 次。
- 页面未稳定：先 `wait` 再重试动作，不允许盲目连点。
- `drag` 失败：先重新读取 DOM 并确认元素仍在视口中；若普通拖拽失败且场景像滑块/风控，再切到 `human_like=true` 重试 1 次。
- 监听类调用（CDP/response）：流程结束前必须执行 `response_listener_stop`。
- 跨标签页监听开启后，先验证 `attached_tab_count` 是否符合预期，再判断是不是“没抓到数据”；别上来就说工具废了，很多时候是你压根没把新页挂进去。
- 文件操作（下载/上传/截图）需回传关键字段：`path`、`mime`、`size`（若有）。

## 4) 错误模型（必须归一化）

统一以以下错误码表达失败原因：

- `NOT_CONNECTED`
- `NO_ACTIVE_TAB`
- `TIMEOUT`
- `ELEMENT_NOT_FOUND`
- `INVALID_ARGUMENT`
- `IO_ERROR`
- `CDP_ERROR`
- `INTERNAL_ERROR`

详细判定与恢复动作见 `references/error-runbook.md`。

## 5) 观测与汇报规范

每轮流程输出结构化执行摘要，至少包含：

- `phase`：当前阶段（如 `INSPECT`）。
- `tool`：调用的 `mcp__DrissionPageMCP__*` 工具名。
- `result`：成功/失败。
- `key_fields`：`url` / `title` / `xpath` / `path` / `error.code` 等关键信息。
- `next_action`：下一步动作或恢复方案。

建议以简短三段式输出：

1. 做了什么（步骤 + 工具）
2. 得到什么（关键字段）
3. 接下来做什么（继续、重试、回退）

## 6) 安全与边界

- 不在未确认页面上下文时执行高风险动作（批量点击、下载覆盖等）。
- 上传/下载前显式校验目标路径与文件名。
- `run_js` / `run_cdp` 仅在常规工具无法满足时启用。
- 当请求与当前页面状态冲突时，先回报冲突再执行替代方案。

## 7) 完成定义（Definition of Done）

仅当以下条件都满足才视为任务完成：

- 已按状态机完成至少一个闭环（`CONNECT -> ... -> VERIFY`）。
- 输出中包含可验证证据（文本片段、截图路径、监听结果、数据库写入结果之一）。
- 所有临时监听已停止。
- 失败分支给出明确可执行的下一步。

## 8) 快速执行模板

最小可靠流程：

1. `mcp__DrissionPageMCP__connect_or_open_browser(address="127.0.0.1:9223")`
2. `mcp__DrissionPageMCP__get` 或 `mcp__DrissionPageMCP__new_tab`
3. `mcp__DrissionPageMCP__getSimplifiedDomTree`
4. `mcp__DrissionPageMCP__input_by_xapth` / `mcp__DrissionPageMCP__click_by_xpath`
5. `mcp__DrissionPageMCP__get_body_text` 或 `mcp__DrissionPageMCP__get_current_tab_screenshot_as_file`
6. （若启用监听）`mcp__DrissionPageMCP__response_listener_stop`

## 9) Human-like Drag 选择规则

当任务包含“拖动滑块”“拖拽验证码”“行为检测”“像真人一样拖过去”这类描述时，按下面顺序执行：

1. `CONNECT` / `NAVIGATE` 后，先 `getSimplifiedDomTree` 确认拖拽元素 XPath。
2. 首选普通拖拽，除非用户已明确要求真人轨迹，或你已知目标站点对直线拖拽敏感。
3. 若判断需要真人轨迹，调用：

```text
mcp__DrissionPageMCP__drag(
  xpath="//div[contains(@class,'slider')]",
  offset_x=180,
  offset_y=0,
  duration=900,
  human_like=true,
  seed=7
)
```

4. 验证返回里的 `data.mode == "human_like"`，并记录 `trajectory.point_count`、`trajectory.step_count`、`trajectory.actual_duration_ms`。
5. 若 human-like drag 仍失败，不要连续盲拖；回到 `INSPECT` 阶段重新确认元素、偏移量和页面状态。

## 10) 跨标签页响应监听

当任务包含“点开一个新页后继续抓接口”“多个标签页来回跳还要统一监听”“弹新标签页拿数据”这类描述时，按下面顺序执行：

1. `CONNECT` 后先确认浏览器实例固定在 `127.0.0.1:9223`，避免监听挂到别的 Chrome 上。
2. 调用：

```text
mcp__DrissionPageMCP__get_url_with_response_listener(
  tab_url="https://example.com",
  mimeType="application/json",
  url_include="api",
  watch_new_tabs=true,
  capture_existing_tabs=false
)
```

3. 让页面继续执行打开新标签页的动作后，调用 `mcp__DrissionPageMCP__get_response_listener_data`。
4. 先看 `data.mode == "cross_tab"`，再看 `data.attached_tab_count >= 2`，并检查 `data.attached_tabs[*].source` 是否出现 `auto_attached`。
5. 如果已经看到 `auto_attached`，但 `data.events` 还是空的，先别下结论。很多站点在新页刚打开时不会立刻产生命中过滤条件的响应，这时应对该 auto-attached 目标页再触发一次明确的网络动作，比如 reload 同一 URL。
6. 再读取 `data.events[*].tab`，确认具体是哪一个标签页发出的响应。
7. 流程结束必须执行 `mcp__DrissionPageMCP__response_listener_stop(clear_data=true)`，避免下一个任务吃到上一次的脏缓冲。

实测通过的一条最小链路：

- 种子页：`https://example.com`
- 打开新页：`window.open('https://jsonplaceholder.typicode.com/todos/1?from_window_open=3', '_blank')`
- 第一次验证：`attached_tab_count = 2`，且新页 `source = auto_attached`
- 第二次验证：对 JSON 新页 reload 一次后，`events[*].tab.url` 命中该新页 URL
