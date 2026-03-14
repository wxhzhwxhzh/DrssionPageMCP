# Error Runbook

将执行异常统一映射为错误码，并给出建议恢复动作。

## `NOT_CONNECTED`

- 触发信号：浏览器未初始化、会话断开。
- 恢复动作：
  1. 确认本机 Chrome 已通过 `assets/start-local-chrome-9223.ps1` 启动
  2. 调用 `mcp__DrissionPageMCP__connect_or_open_browser(address="127.0.0.1:9223")`
  3. 调用 `mcp__DrissionPageMCP__get_current_tab_info` 验证连接
  4. 重试原动作 1 次

## `NO_ACTIVE_TAB`

- 触发信号：当前无有效标签页。
- 恢复动作：
  1. 调用 `mcp__DrissionPageMCP__new_tab` 或 `mcp__DrissionPageMCP__get`
  2. 再次读取 `get_current_tab_info`

## `TIMEOUT`

- 触发信号：页面加载、元素等待或网络事件超时。
- 恢复动作：
  1. `mcp__DrissionPageMCP__wait`
  2. 若涉及元素，先 `getSimplifiedDomTree` 再重试
  3. 若超时发生在滑块/风控拖拽场景，可把 `drag` 升级为 `human_like=true` 后重试 1 次

## `ELEMENT_NOT_FOUND`

- 触发信号：XPath/文本定位失败。
- 恢复动作：
  1. `mcp__DrissionPageMCP__getSimplifiedDomTree`
  2. 更新定位策略（XPath 或文本索引）
  3. 重试 1 次
  4. 若失败发生在拖拽链路，重新确认滑块元素是否重渲染，必要时改用新的 XPath 再执行 `drag`

## `INVALID_ARGUMENT`

- 触发信号：参数格式错误（如 XPath、路径、键值类型）。
- 恢复动作：
  1. 输出参数摘要（避免全量敏感信息）
  2. 修正后重试

## `IO_ERROR`

- 触发信号：上传/下载/落盘失败。
- 恢复动作：
  1. 校验路径与文件名
  2. 重新执行文件操作
  3. 返回 `path`、`mime`、`size`（若有）

## `CDP_ERROR`

- 触发信号：CDP 命令执行失败。
- 恢复动作：
  1. 校验 `cmd` 与 `cmd_args`
  2. 缩小命令范围并最小化重放

## `INTERNAL_ERROR`

- 触发信号：未知异常。
- 恢复动作：
  1. 输出 `phase` + `tool` + `key_fields`
  2. 回退到上一个稳定阶段重试
  3. 若重复失败，提供替代路径（截图验收、文本验收或手工步骤）
