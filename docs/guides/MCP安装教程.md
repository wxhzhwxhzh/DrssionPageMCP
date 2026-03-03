# DrissionPageMCP 简单操作指南
快速完成项目搭建、测试与配置，共6步。


## 1. 装 uv（包管理工具）
打开命令行，输下面的命令：
```bash
pip install uv
```


## 2. 克隆项目仓库
继续输命令，拉取项目文件：
```bash
git clone https://github.com/wxhzhwxhzh/DrissionPageMCP
```


## 3. 进入项目文件夹
输命令切换到项目目录（后续操作都在这）：
```bash
cd DrissionPageMCP
```


## 4. 装项目需要的库
输命令自动安装依赖：
```bash
uv sync
```


## 5. 测试程序能不能跑
输命令启动主程序，出现 *DrissionPage MCP server is running...* 说明程序正常：
```bash
uv run main.py
```


## 6. 写 MCP 配置文件
1. MCP对应的JSON配置文件的"mcpServers"项新增子项"DrssionPageMCP"；
2. 把 `D:\test4\DrissionPageMCP` 改成你电脑上 `main.py` 所在的绝对路径（比如你项目放 `E:\DrissionPageMCP`，就改这个） 
3. Windows中路径用双反斜杠  '\\\\'，Linux中用单反斜杠 '/'；

```json
{
  "mcpServers": {
    "DrissionPageMCP": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "D:\\test4\\DrissionPageMCP", "run", "main.py"]
    }
  }
}
```

## 如何找到MCP配置文件  
[查看帮助](./README.md)
