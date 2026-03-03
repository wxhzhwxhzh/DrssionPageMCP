---
name: drission-page-skill
description: Use when handling browser automation tasks in this repository through MCP (navigation, DOM inspection, click/input, upload/download, screenshot, JS/CDP, listener analysis). Enforce unified tool namespace via mcp__mcp_router__* only, and apply deterministic workflow with retries, observability logs, error taxonomy, and completion checklist.
---

# drission-page-skill

通过 `mcp_router` 统一编排浏览器自动化，目标是“可重复执行 + 可排障 + 可审计”。

## 0) 入口约束

- 仅调用 `mcp__mcp_router__*` 前缀工具。
- 不混用其他命名空间的浏览器工具。
- 在调用工具前，先声明当前阶段（`CONNECT` / `NAVIGATE` / `INSPECT` / `ACT` / `VERIFY`）。
- 交互失败后必须输出可执行补救动作，不允许只给错误文本。

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

- `mcp__mcp_router__connect_or_open_browser`
- `mcp__mcp_router__get_current_tab_info`
- `mcp__mcp_router__new_tab`
- `mcp__mcp_router__get`
- `mcp__mcp_router__wait`

### 2.2 Inspect / Interaction

- `mcp__mcp_router__getSimplifiedDomTree`
- `mcp__mcp_router__getInputElementsInfo`
- `mcp__mcp_router__get_body_text`
- `mcp__mcp_router__click_by_xpath`
- `mcp__mcp_router__click_by_containing_text`
- `mcp__mcp_router__input_by_xapth`
- `mcp__mcp_router__send_key`
- `mcp__mcp_router__send_enter`
- `mcp__mcp_router__move_to`
- `mcp__mcp_router__drag`

### 2.3 Debug / Network / File

- `mcp__mcp_router__run_js`
- `mcp__mcp_router__run_cdp`
- `mcp__mcp_router__listen_cdp_event`
- `mcp__mcp_router__get_cdp_event_data`
- `mcp__mcp_router__get_url_with_response_listener`
- `mcp__mcp_router__get_response_listener_data`
- `mcp__mcp_router__response_listener_stop`
- `mcp__mcp_router__download_file`
- `mcp__mcp_router__upload_file`
- `mcp__mcp_router__get_current_tab_screenshot`
- `mcp__mcp_router__get_current_tab_screenshot_as_file`
- `mcp__mcp_router__save_dict_to_sqlite`

更细分的工具选择、参数建议和常见误用见 `references/tool-catalog.md`。

## 3) 重试与幂等策略

- `connect` 类失败：重试 1 次，仍失败则返回 `NOT_CONNECTED` 并停止。
- 定位失败（XPath/文本）：先刷新 DOM（`getSimplifiedDomTree`）再重试 1 次。
- 页面未稳定：先 `wait` 再重试动作，不允许盲目连点。
- 监听类调用（CDP/response）：流程结束前必须执行 `response_listener_stop`。
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
- `tool`：调用的 `mcp__mcp_router__*` 工具名。
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

1. `mcp__mcp_router__connect_or_open_browser`
2. `mcp__mcp_router__get` 或 `mcp__mcp_router__new_tab`
3. `mcp__mcp_router__getSimplifiedDomTree`
4. `mcp__mcp_router__input_by_xapth` / `mcp__mcp_router__click_by_xpath`
5. `mcp__mcp_router__get_body_text` 或 `mcp__mcp_router__get_current_tab_screenshot_as_file`
6. （若启用监听）`mcp__mcp_router__response_listener_stop`
