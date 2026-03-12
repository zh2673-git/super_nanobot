---
created: 2026-03-01
updated: 2026-03-10
tags:
  - nanobot
  - tools
  - skills
---

# nanobot 内置工具与 Skill 详解

## 第一步：点出核心概念

nanobot 的能力体系由 **两大部分** 构成，就像人的"双手"和"知识库"：

- **内置工具（Tools）**：Agent 可以调用的具体操作能力，就像人的双手，能执行读取、写入、搜索等具体动作
- **Skills**：指导 Agent 如何使用工具和处理特定任务的知识，就像人的"技能手册"或"工作经验"

### 内置工具的分类

| 工具类别 | 工具名称 | 功能类比 |
|---------|---------|---------|
| 文件操作 | read_file, write_file, edit_file, list_dir | 就像文件柜管理员，负责文件的读取、整理 |
| 命令执行 | exec | 就像执行器，能运行各种命令行操作 |
| 网络功能 | web_search, web_fetch | 就像信息检索员，帮助查找和获取网上信息 |
| 消息发送 | message | 就像邮递员，负责把信息传递给用户 |
| 定时任务 | cron | 就像闹钟系统，可以定时提醒用户 |
| 子代理 | spawn | 就像主管，能分配任务给下属代理 |
| 外部扩展 | MCP tools | 就像插件系统，扩展更多能力 |

### Skill 的分类

| Skill 名称      | 功能        | 类比           |
| ------------- | --------- | ------------ |
| memory        | 双层记忆系统    | 就像人的长期记忆和日记本 |
| github        | GitHub 操作 | 就像 GitHub 助手 |
| weather       | 天气查询      | 就像天气预报员      |
| summarize     | 内容摘要      | 就像文摘编辑       |
| cron          | 定时任务管理    | 就像日程管理器      |
| clawhub       | 公共技能市场    | 就像技能商店       |
| tmux          | 终端会话管理    | 就像终端管理器      |
| skill-creator | 技能创建器     | 就像技能工厂       |

## 第二步：用图构建组件联系

```
┌─────────────────────────────────────────────────────────────────┐
│                     nanobot 能力体系                              │
└─────────────────────────────────────────────────────────────────┘

[用户请求]
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AgentLoop (大脑)                            │
│  ┌─────────────────┬─────────────────┬─────────────────┐        │
│  │  ContextBuilder │  ToolRegistry   │  SkillsLoader   │        │
│  │    上下文构建    │    工具注册表    │    技能加载器    │        │
│  └────────┬────────┴────────┬────────┴────────┬────────┘        │
└───────────┼─────────────────┼─────────────────┼──────────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
    │   内置工具     │  │   MCP 工具     │  │   Skills      │
    │               │  │               │  │               │
    │ read_file    │  │ filesystem    │  │ memory        │
    │ write_file   │  │ github        │  │ github        │
    │ exec         │  │ ...          │  │ weather       │
    │ web_search   │  │               │  │ ...           │
    │ message      │  │               │  │               │
    │ cron         │  │               │  │               │
    │ spawn        │  │               │  │               │
    └───────────────┘  └───────────────┘  └───────────────┘
```

**联系说明**：当用户发送请求时，AgentLoop（大脑）接收请求并处理。它通过 ContextBuilder 构建上下文，然后根据需求调用 ToolRegistry 中的工具或通过 SkillsLoader 加载相关 Skill。内置工具提供基础操作能力，MCP 工具扩展外部能力，Skills 则告诉 Agent 如何正确使用这些工具。

---

## 第三步：详细解释

### 一、内置工具详解

#### 1. 工具基类 (base.py)

所有工具都继承自 `Tool` 抽象基类，这就像一个"工具制造模具"：

```python
class Tool(ABC):
    """工具基类 - 所有工具的抽象基础"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称 - 就像人的名字"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述 - 就像简历中的工作职责"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """参数定义 - 就像工具的使用说明书"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """执行方法 - 就像真正做事的能力"""
        pass
```

**专业定义**：Tool 是一个抽象基类，定义了所有工具必须实现的接口规范。它确保每个工具都有名称、描述、参数定义和执行方法。

**通俗解释与类比**：想象一个玩具工厂的模具。模具定义了所有玩具必须有头、身体和四肢。具体的玩具有的是熊，有的是兔子，但都遵循这个模具。Tool 基类就是这个"模具"，所有具体工具（read_file、exec 等）都遵循这个规范。

**在此项目中的具体体现**：每个内置工具都继承 Tool 基类并实现其四个核心方法，使得 Agent 可以用统一的方式调用所有工具。

---

#### 2. 文件系统工具 (filesystem.py)

文件操作是 Agent 最基础的能力，就像人需要读写文档一样。

##### ReadFileTool（读取文件）

```python
class ReadFileTool(Tool):
    """读取文件内容"""
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path."
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to read"}
            },
            "required": ["path"],
        }
    
    async def execute(self, path: str, **kwargs) -> str:
        file_path = _resolve_path(path, self._workspace, self._allowed_dir)
        content = file_path.read_text(encoding="utf-8")
        return content
```

**安全机制**：路径解析时会检查是否在允许的目录内，防止越权访问：

```python
def _resolve_path(path, workspace, allowed_dir):
    p = Path(path).expanduser()
    if not p.is_absolute() and workspace:
        p = workspace / p
    resolved = p.resolve()
    if allowed_dir:
        # 检查是否在允许目录内
        resolved.relative_to(allowed_dir.resolve())
    return resolved
```

##### WriteFileTool（写入文件）

```python
class WriteFileTool(Tool):
    """写入文件内容"""
    
    async def execute(self, path: str, content: str, **kwargs) -> str:
        file_path = _resolve_path(path, self._workspace, self._allowed_dir)
        file_path.parent.mkdir(parents=True, exist_ok=True)  # 自动创建目录
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} bytes to {file_path}"
```

**功能特点**：
- 自动创建父目录
- 支持相对路径（相对于工作空间）
- 写入前会进行安全检查

##### EditFileTool（编辑文件）

```python
class EditFileTool(Tool):
    """精确编辑文件 - 类似于"查找替换"功能"""
    
    async def execute(self, path: str, old_text: str, new_text: str, **kwargs) -> str:
        content = file_path.read_text(encoding="utf-8")
        
        if old_text not in content:
            return self._not_found_message(old_text, content, path)
        
        # 如果出现多次，提醒用户提供更多上下文
        count = content.count(old_text)
        if count > 1:
            return f"Warning: old_text appears {count} times. Please provide more context."
        
        new_content = content.replace(old_text, new_text, 1)
        file_path.write_text(new_content)
        return f"Successfully edited {file_path}"
```

**智能特性**：
- 当 old_text 找不到时，会尝试找到最相似的文本并显示差异
- 如果匹配多次，会提醒用户提供更多上下文避免误修改

##### ListDirTool（列出目录）

```python
class ListDirTool(Tool):
    """列出目录内容"""
    
    async def execute(self, path: str, **kwargs) -> str:
        items = []
        for item in sorted(dir_path.iterdir()):
            prefix = "📁 " if item.is_dir() else "📄 "
            items.append(f"{prefix}{item.name}")
        return "\n".join(items)
```

---

#### 3. Shell 工具 (shell.py)

exec 工具允许 Agent 执行命令行操作，就像给人一台电脑让他自由操作：

```python
class ExecTool(Tool):
    """执行 Shell 命令"""
    
    def __init__(
        self,
        timeout: int = 60,                    # 超时时间（秒）
        working_dir: str | None = None,      # 工作目录
        deny_patterns: list[str] = [...],     # 禁止的命令模式
        allow_patterns: list[str] = [],       # 允许的命令模式
        restrict_to_workspace: bool = False, # 是否限制在工作空间
    ):
        self.timeout = timeout
        # 危险命令黑名单
        self.deny_patterns = [
            r"\brm\s+-[rf]{1,2}\b",          # rm -r, rm -rf
            r"\bdel\s+/[fq]\b",              # del /f
            r"\bformat\b",                   # format
            r"\b(mkfs|diskpart)\b",          # 磁盘操作
            r"\bdd\s+if=\b",                 # dd
            r">\s*/dev/sd",                  # 写入设备
            r"\b(shutdown|reboot)\b",        # 关机重启
            r":\(\)\s*\{.*\};.*:",          # fork 炸弹
        ]
```

**安全机制**：

1. **命令黑名单**：阻止危险命令如删除系统文件、格式化磁盘等
2. **工作目录限制**：在 restrict_to_workspace 模式下，防止访问工作空间外的文件
3. **超时保护**：默认 60 秒超时，防止命令卡死
4. **输出截断**：超长输出自动截断到 10000 字符

**使用示例**：
```json
{
  "name": "exec",
  "arguments": {
    "command": "git status",
    "working_dir": "/path/to/project"
  }
}
```

---

#### 4. Web 工具 (web.py)

##### WebSearchTool（网络搜索）

使用 Brave Search API 进行网络搜索：

```python
class WebSearchTool(Tool):
    """使用 Brave Search API 搜索网页"""
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {"type": "integer", "description": "Results (1-10)", "minimum": 1, "maximum": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str, count: int = 5, **kwargs) -> str:
        # 调用 Brave Search API
        r = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": n},
            headers={"X-Subscription-Token": self.api_key}
        )
        
        results = r.json().get("web", {}).get("results", [])
        # 返回格式化的搜索结果
```

**配置方式**：
```json
{
  "tools": {
    "web": {
      "search": { "apiKey": "BSA-..." }
    }
  }
}
```

##### WebFetchTool（获取网页）

获取网页内容并提取正文：

```python
class WebFetchTool(Tool):
    """获取并提取网页内容"""
    
    @property
    def name(self) -> str:
        return "web_fetch"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "extractMode": {"type": "string", "enum": ["markdown", "text"]},
                "maxChars": {"type": "integer", "minimum": 100}
            },
            "required": ["url"]
        }
```

**功能特点**：
- 使用 Readability 库提取网页正文
- 自动转换为 Markdown 格式
- 支持 JSON 和 HTML 响应
- 自动截断超长内容

---

#### 5. 消息工具 (message.py)

让 Agent 可以主动发送消息给用户：

```python
class MessageTool(Tool):
    """发送消息到聊天渠道"""
    
    async def execute(
        self,
        content: str,
        channel: str | None = None,
        chat_id: str | None = None,
        media: list[str] | None = None,
        **kwargs
    ) -> str:
        msg = OutboundMessage(
            channel=channel,
            chat_id=chat_id,
            content=content,
            media=media or [],
        )
        await self._send_callback(msg)
        return f"Message sent to {channel}:{chat_id}"
```

**使用场景**：
- Agent 完成后台任务后通知用户
- 定时任务触发时发送提醒
- 子代理完成任务后返回结果

---

#### 6. 定时任务工具 (cron.py)

管理定时提醒和周期性任务：

```python
class CronTool(Tool):
    """定时任务管理"""
    
    async def execute(
        self,
        action: str,                    # add/list/remove
        message: str = "",              # 提醒消息
        every_seconds: int | None = None,  # 间隔（秒）
        cron_expr: str | None = None,   # cron 表达式
        tz: str | None = None,          # 时区
        at: str | None = None,         # 一次性时间
        job_id: str | None = None,     # 任务ID（删除用）
        **kwargs
    ) -> str:
        if action == "add":
            # 添加任务
            schedule = CronSchedule(kind="every", every_ms=every_seconds * 1000)
            # 或
            schedule = CronSchedule(kind="cron", expr=cron_expr, tz=tz)
            # 或
            schedule = CronSchedule(kind="at", at_ms=at_ms)
            job = self._cron.add_job(...)
        elif action == "list":
            return self._list_jobs()
        elif action == "remove":
            return self._remove_job(job_id)
```

**调度类型**：
- **every**：固定间隔，如每 3600 秒
- **cron**：标准 cron 表达式，如 `0 9 * * *`（每天 9 点）
- **at**：一次性任务，指定具体时间

---

#### 7. 子代理工具 (spawn.py)

创建子代理执行后台任务：

```python
class SpawnTool(Tool):
    """创建子代理处理后台任务"""
    
    async def execute(
        self,
        task: str,              # 任务描述
        label: str | None = None,  # 任务标签
        **kwargs
    ) -> str:
        return await self._manager.spawn(
            task=task,
            label=label,
            origin_channel=self._origin_channel,
            origin_chat_id=self._origin_chat_id,
        )
```

**使用场景**：
- 需要同时执行多个独立任务
- 耗时较长的任务不阻塞主对话
- 并行收集多个来源的信息

---

#### 8. MCP 工具 (mcp.py)

MCP（Model Context Protocol）允许扩展外部工具：

```python
async def connect_mcp_servers(mcp_servers, registry, stack):
    """连接 MCP 服务器并注册工具"""
    
    for name, cfg in mcp_servers.items():
        if cfg.command:
            # Stdio 连接（本地进程）
            params = StdioServerParameters(command=cfg.command, args=cfg.args)
            read, write = await stdio_client(params)
        elif cfg.url:
            # HTTP 连接（远程服务）
            read, write, _ = await streamable_http_client(cfg.url)
        
        session = await ClientSession(read, write)
        await session.initialize()
        
        # 发现并注册工具
        tools = await session.list_tools()
        for tool_def in tools.tools:
            wrapper = MCPToolWrapper(session, name, tool_def)
            registry.register(wrapper)
```

**MCP 配置示例**：
```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
      },
      "remote": {
        "url": "https://mcp.example.com/sse"
      }
    }
  }
}
```

---

### 二、Skill 系统详解

#### 1. Skill 加载机制

SkillsLoader 负责加载和管理所有 Skill：

```python
class SkillsLoader:
    """Skill 加载器"""
    
    def __init__(self, workspace: Path, builtin_skills_dir: Path | None = None):
        self.workspace = workspace
        self.workspace_skills = workspace / "skills"  # 用户自定义 Skill
        self.builtin_skills = builtin_skills_dir     # 内置 Skill
    
    def list_skills(self, filter_unavailable: bool = True) -> list[dict]:
        """列出所有可用 Skill"""
        # 优先加载工作空间的 Skill
        # 其次加载内置 Skill
        # 检查依赖要求是否满足
```

#### 2. Skill 元数据格式

Skill 使用 YAML 前置元数据：

```yaml
---
name: skill-name          # Skill 名称
description: 描述文字       # Skill 功能描述
always: true              # 是否总是加载到上下文
homepage: https://...     # 相关链接
metadata:                 # 扩展元数据（JSON 格式）
  nanobot:
    emoji: 🐙             # 显示图标
    requires:             # 依赖要求
      bins: ["gh"]       # 需要的命令行工具
      env: ["API_KEY"]   # 需要的环境变量
    install:             # 安装说明
      - id: brew
        kind: brew
        formula: gh
---

# Skill 内容...
```

#### 3. Skill 渐进式加载

nanobot 使用"渐进式加载"策略：

1. **Always-loaded**：标记为 `always: true` 的 Skill 完整加载到上下文
2. **Available**：其他 Skill 只加载摘要，Agent 需要时用 read_file 读取完整内容

```python
def build_skills_summary(self) -> str:
    """构建 Skill 摘要（XML 格式）"""
    lines = ["<skills>"]
    for s in all_skills:
        lines.append(f"<skill available=\"{available}\">")
        lines.append(f"  <name>{name}</name>")
        lines.append(f"  <description>{desc}</description>")
        lines.append(f"  <location>{path}</location>")
    lines.append("</skills>")
    return "\n".join(lines)
```

---

### 三、内置 Skill 详解

#### 1. memory Skill（双层记忆系统）

```yaml
---
name: memory
description: Two-layer memory system with grep-based recall.
always: true
---

# Memory

## Structure

- `memory/MEMORY.md` — 长期记忆（事实、偏好、项目背景）
- `memory/HISTORY.md` — 事件日志（可搜索）

## Search Past Events

使用 grep 搜索历史：
```bash
grep -i "keyword" memory/HISTORY.md
```
```

**核心概念**：
- **MEMORY.md**：长期记忆，类似人的持久记忆，重要事实会永久保存
- **HISTORY.md**：历史日志，类似人的日记本，记录所有事件

#### 2. github Skill（GitHub 操作）

```yaml
---
name: github
description: Interact with GitHub using the `gh` CLI.
metadata: {"requires":{"bins":["gh"]}}
---

# GitHub Skill

## Pull Requests
gh pr checks 55 --repo owner/repo

## Workflow Runs
gh run list --repo owner/repo --limit 10

## API Queries
gh api repos/owner/repo/pulls/55 --jq '.title'
```

**功能**：
- PR 检查和状态
- Workflow 运行管理
- GitHub API 高级查询

#### 3. weather Skill（天气查询）

```yaml
---
name: weather
description: Get current weather and forecasts (no API key required).
metadata: {"requires":{"bins":["curl"]}}
---

# Weather

## wttr.in (主要)
curl -s "wttr.in/London?format=3"
# 输出: London: ⛅️ +8°C

## Open-Meteo (备选，JSON)
curl -s "https://api.open-mete.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```

**特点**：
- 无需 API Key
- 支持多种格式输出
- 包含天气预报

#### 4. summarize Skill（内容摘要）

```yaml
---
name: summarize
description: Summarize or extract text/transcripts from URLs.
metadata: {"requires":{"bins":["summarize"]}}
---

# Summarize

## 使用场景
- "summarize this URL"
- "what's this link about?"
- "transcribe this YouTube/video"

## 命令示例
summarize "https://example.com" --model google/gemini-3-flash-preview
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

#### 5. cron Skill（定时任务）

Skill 版本的定时任务管理，与 cron 工具配合使用。

#### 6. clawhub Skill（公共技能市场）

```yaml
---
name: clawhub
description: Search and install agent skills from ClawHub.
homepage: https://clawhub.ai
---

# ClawHub

## Search
npx --yes clawhub@latest search "web scraping"

## Install
npx --yes clawhub@latest install <slug> --workdir ~/.nanobot/workspace

## Update
npx --yes clawhub@latest update --all --workdir ~/.nanobot/workspace
```

**功能**：
- 搜索公共 Skill
- 安装到工作空间
- 更新已安装的 Skill

---

### 四、工具注册与使用

#### 工具注册表

```python
class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
    
    def get_definitions(self) -> list[dict]:
        """获取所有工具定义（OpenAI 格式）"""
        return [tool.to_schema() for tool in self._tools.values()]
    
    async def execute(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        return await tool.execute(**params)
```

#### 默认工具注册

AgentLoop 启动时注册所有内置工具：

```python
def _register_default_tools(self) -> None:
    # 文件工具
    self.tools.register(ReadFileTool(allowed_dir=allowed_dir))
    self.tools.register(WriteFileTool(allowed_dir=allowed_dir))
    self.tools.register(EditFileTool(allowed_dir=allowed_dir))
    self.tools.register(ListDirTool(allowed_dir=allowed_dir))
    
    # Shell 工具
    self.tools.register(ExecTool(...))
    
    # Web 工具
    self.tools.register(WebSearchTool(api_key=brave_api_key))
    self.tools.register(WebFetchTool())
    
    # 消息工具
    self.tools.register(MessageTool(...))
    
    # 子代理工具
    self.tools.register(SpawnTool(...))
    
    # 定时任务工具
    if self.cron_service:
        self.tools.register(CronTool(self.cron_service))
```

---

## 相关笔记

- [[github/nanobot/架构分析]] - 整体架构设计
- [[github/nanobot/运行逻辑]] - 程序执行流程
- [[github/nanobot/源码解析]] - 核心源码分析
- [[github/nanobot/核心API文档]] - API 参考
- [[github/nanobot/README]] - 项目概述
