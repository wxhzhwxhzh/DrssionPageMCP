# DrissionPage MCP Server -- 骚神出品

基于DrissionPage和FastMCP的浏览器自动化MCP服务器，提供丰富的浏览器操作API供AI调用。

## 重要变更（vNext）

本项目已开始重构以提高 MCP 客户端兼容性和可维护性（tool 名称保持不变，但返回结构已升级）。

- 返回结构统一为 envelope：`{ ok, data/error }`（breaking change，需要更新你的提示词/调用方）。
- 截图/下载等涉及二进制的结果：统一“落盘返回 `{path, mime, size?}`”，禁止直接返回 bytes。
- DOM/Elements：禁止返回 DOM Element 等不可 JSON 序列化对象；输入元素信息改为返回 outerHTML 列表。

完整对外契约见：`docs/mcp-contract.md`。

## 项目简介
![logo](img/DrissionPageMCP-logo.png)

DrissionPage MCP  是一个基于 DrissionPage 和 FastMCP 的浏览器自动化MCP server服务器，它提供了一系列强大的浏览器操作 API，让您能够轻松通过AI实现网页自动化操作。

### 主要特性

- 支持浏览器的打开、关闭和连接管理
- 提供丰富的页面元素操作方法
- 支持 JavaScript 代码执行
- 支持 CDP 协议操作
- 提供便捷的文件下载功能
- 支持键盘按键模拟
- 支持页面截图功能
- 增加 网页后台监听数据包的功能
- 增加自动上传下载文件功能

#### Python要求
- Python >= 3.10
- pip（最新版本）
- uv （最新版本）


#### 浏览器要求
- Chrome 浏览器（推荐 90 及以上版本）


#### 必需的Python包
- drissionpage >= 4.1.0.18
- fastmcp >= 2.4.0
- uv

## 安装说明
- 把本仓库 `git clone` 到本地，核心启动文件是 `main.py`。
- 执行 `uv sync` 安装运行依赖。
- 如需运行测试，执行 `uv sync --extra dev` 安装开发依赖。
- 首先要进行 [💖 MCP 安装环境准备工作](./docs/guides/MCP安装教程.md)。

### 安装到Cursor编辑器

![安装说明](img/install_to_Cursor1.png)
![安装说明](img/install_to_cursor2.png)

### 安装到vscode编辑器

![安装说明](img/install_to_vscode0.png)
![安装说明](img/install_to_vscode1.png)
![安装说明](img/install_to_vscode2.png)


请将以下配置代码粘贴到编辑器的 `mcpServers` 设置中（请填写你自己电脑上 `main.py` 文件的绝对路径）：

```json
{
  "mcpServers": {
    "DrissionPageMCP": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "D:\\test10\\DrissionPageMCP", "run", "main.py"]
    }
  }
}
```
注意事项：
- 请根据实际路径修改 `args` 中的路径
- Windows 中路径中的反斜杠需要转义（使用 `\\`）
- 确保 `uv` 命令在系统 PATH 中可用
- [《MCP安装参考教程》](https://docs.trae.ai/ide/model-context-protocol)

## 推荐调用流程（强烈建议按顺序）

1. `connect_or_open_browser`（连接/启动浏览器）
2. `get` 或 `new_tab`（打开页面）
3. `getSimplifiedDomTree`（拿到可用的 DOM 结构，便于生成 xpath）
4. `click_by_xpath` / `input_by_xapth` / `send_key`（执行交互）
5. `get_body_text` / `get_current_tab_info` / 截图（验证结果）

## 端到端示例（2 个）

示例 1：打开页面并点击（返回统一 envelope）
```text
connect_or_open_browser({\"debug_port\":9222})
get({\"url\":\"https://example.com\"})
getSimplifiedDomTree()
click_by_xpath({\"xpath\":\"//a[contains(.,'More information')]\"})
get_body_text()
```

示例 2：截图（返回落盘 path + mime，禁止 bytes）
```text
connect_or_open_browser({\"debug_port\":9222})
get({\"url\":\"https://example.com\"})
get_current_tab_screenshot()
```

截图返回示例（大致结构）：
```json
{ \"ok\": true, \"data\": { \"path\": \"D:/.../dp_artifacts/screenshots/screenshot_....jpg\", \"mime\": \"image/jpeg\", \"size\": 12345 } }
```

## 工具说明补充

- `upload_file` 支持可选参数 `xpath`（默认 `//input[@type='file']`），用于指定触发上传的 input 元素。
- `save_dict_to_sqlite` 默认不再 DROP TABLE（append 模式）；需要覆盖写入时显式传 `mode=\"overwrite\"`。
- `connect_or_open_browser` 现支持 `address`（如 `127.0.0.1:9222`）与 `debug_port` 两种连接方式，且不会再用默认 `9222` 覆盖你传入的 `config.debug_port`。
- `get_current_tab_info` 会返回 `browser_address` 与 `active_connection`，用于排查“连接到 A 浏览器但操作落在 B 浏览器”的串线问题。

## 常见问题

- 如果你发现返回值无法被客户端解析：优先确认你是否已按 `docs/mcp-contract.md` 的新返回结构处理（envelope + JSON 可序列化）。
- 如果调用 tool 报 NOT_CONNECTED：先 `connect_or_open_browser`，或确认浏览器调试端口（默认 9222）是否可用。

## 本地测试（推荐）

在 `DrissionPageMCP/` 目录下：

```bash
uv sync --extra dev
uv run python -m pytest -q
```

## 调试命令

调试
```
npx -y @modelcontextprotocol/inspector uv run D:\\test10\\DrissionPageMCP\\main.py
```
或者
```
mcp dev  D:\\test10\\DrissionPageMCP\\main.py
```

## 更新日志
### v0.1.3
增加 自动上传下载文件功能
### v0.1.2
增加 网页后台监听数据包的功能

### v0.1.0

- 初始版本发布
- 实现基本的浏览器控制功能
- 提供元素操作 API
