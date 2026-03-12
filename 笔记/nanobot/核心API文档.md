---
created: 2026-02-09
updated: 2026-03-10
tags:
  - nanobot
  - api
  - documentation
---

# nanobot 核心 API 文档

## 第一步：点出核心命令概念

nanobot 的 CLI 命令可以分为 **4 个类别**：

- **初始化命令**：`onboard` —— 就像首次使用新设备的设置向导
- **交互命令**：`agent` —— 就像和 AI 助手对话的聊天窗口
- **服务命令**：`gateway` —— 就像启动一个后台服务
- **管理命令**：`status`、`cron`、`channels`、`provider` —— 就像管理工具

## 第二步：用图构建命令联系

```
┌─────────────────────────────────────────────────────────────────┐
│                       nanobot CLI 命令                           │
└─────────────────────────────────────────────────────────────────┘

[初始化]                              [交互]
nanobot onboard  ───────────────→  nanobot agent
    │                                    │
    │ 创建配置、工作空间                   │ 单次对话或交互模式
    │                                    │
    ▼                                    ▼
[配置 API Key]                    [与 AI 对话]
    │                                    │
    │                                    │
    └──────────────┬─────────────────────┘
                   │
                   ▼
              [服务模式]
           nanobot gateway
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
[渠道管理]    [定时任务]      [状态查看]
channels      cron           status
    │              │              │
    ▼              ▼              ▼
login         add/list/remove  显示配置状态
status        enable/run
```

**联系说明**：用户首先通过 `onboard` 初始化配置，然后可以选择 `agent` 直接交互或 `gateway` 启动服务模式。服务模式下，可以通过 `channels`、`cron`、`provider` 等命令管理各种功能。

## CLI 命令详解

### nanobot onboard

初始化配置和工作空间。

```bash
nanobot onboard
```

**功能**：
- 创建 `~/.nanobot/config.json` 配置文件
- 创建 `~/.nanobot/workspace/` 工作目录
- 生成默认引导文件：
  - `AGENTS.md` - Agent 角色定义
  - `SOUL.md` - 核心价值观
  - `USER.md` - 用户信息
  - `memory/MEMORY.md` - 长期记忆
  - `memory/HISTORY.md` - 历史日志
  - `skills/` - 技能目录

---

### nanobot agent

与 Agent 对话。

```bash
# 单次对话
nanobot agent -m "What is 2+2?"

# 交互模式
nanobot agent

# 显示运行日志
nanobot agent --logs

# 纯文本输出
nanobot agent --no-markdown
```

**参数**：
| 参数 | 描述 |
|------|------|
| `-m, --message` | 发送单条消息 |
| `-s, --session` | 会话 ID |
| `--markdown/--no-markdown` | 是否渲染 Markdown |
| `--logs/--no-logs` | 是否显示运行日志 |

**交互模式退出命令**：`exit`、`quit`、`/exit`、`/quit`、`:q`、`Ctrl+D`

---

### nanobot gateway

启动 Gateway 服务。

```bash
nanobot gateway
nanobot gateway --port 18790 --verbose
```

**选项**：
| 选项 | 描述 |
|------|------|
| `--port` | 服务端口 (默认: 18790) |
| `--verbose` | 启用详细日志 |

**启动的组件**：
- MessageBus（消息总线）
- AgentLoop（代理循环）
- ChannelManager（渠道管理器）
- CronService（定时任务服务）
- HeartbeatService（心跳服务）

---

### nanobot status

显示当前状态。

```bash
nanobot status
```

**输出**：
- 配置文件路径和状态
- 工作空间位置
- 当前模型
- 各提供商 API Key 配置状态

---

### nanobot channels

管理聊天渠道。

```bash
# 查看渠道状态
nanobot channels status

# WhatsApp 登录（扫描二维码）
nanobot channels login
```

---

### nanobot cron

管理定时任务。

```bash
# 列出所有任务
nanobot cron list

# 包含禁用的任务
nanobot cron list --all

# 添加周期性任务（每 3600 秒）
nanobot cron add -n "hourly" -m "Check status" --every 3600

# 添加 cron 任务（每天 9:00）
nanobot cron add -n "daily" -m "Good morning!" --cron "0 9 * * *"

# 带时区的 cron 任务
nanobot cron add -n "daily" -m "早安！" --cron "0 9 * * *" --tz "Asia/Shanghai"

# 添加发送到渠道的任务
nanobot cron add -n "reminder" -m "Meeting in 1 hour" --cron "0 14 * * *" --deliver --to "123456" --channel telegram

# 删除任务
nanobot cron remove <job_id>

# 启用/禁用任务
nanobot cron enable <job_id>
nanobot cron enable <job_id> --disable

# 手动运行任务
nanobot cron run <job_id>
nanobot cron run <job_id> --force  # 即使禁用也运行
```

**参数**：
| 参数 | 描述 |
|------|------|
| `-n, --name` | 任务名称 |
| `-m, --message` | 任务消息 |
| `--every` | 执行间隔 (秒) |
| `--cron` | Cron 表达式 |
| `--tz` | 时区 (IANA 格式) |
| `--at` | 一次性任务时间 (ISO 格式) |
| `-d, --deliver` | 是否发送到渠道 |
| `--to` | 接收者 |
| `--channel` | 渠道类型 |

---

### nanobot provider

管理提供商（OAuth 登录）。

```bash
# OpenAI Codex 登录
nanobot provider login openai-codex

# GitHub Copilot 登录
nanobot provider login github-copilot
```

## 配置文件 API

### 配置文件位置

```
~/.nanobot/config.json
```

### 完整配置结构

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "workspace": "~/.nanobot/workspace",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 20,
      "memoryWindow": 50,
      "reasoningEffort": "high"
    }
  },
  "providers": {
    "custom": { "apiKey": "...", "apiBase": "https://your-api.com/v1" },
    "openrouter": { "apiKey": "sk-or-..." },
    "anthropic": { "apiKey": "sk-ant-..." },
    "openai": { "apiKey": "sk-..." },
    "deepseek": { "apiKey": "..." },
    "groq": { "apiKey": "gsk-..." },
    "gemini": { "apiKey": "..." },
    "zhipu": { "apiKey": "..." },
    "dashscope": { "apiKey": "..." },
    "moonshot": { "apiKey": "...", "apiBase": "https://api.moonshot.ai/v1" },
    "minimax": { "apiKey": "...", "apiBase": "https://api.minimax.io/v1" },
    "volcengine": { "apiKey": "...", "apiBase": "https://ark.cn-beijing.volces.com/api/v3" },
    "aihubmix": { "apiKey": "...", "extraHeaders": { "APP-Code": "..." } },
    "siliconflow": { "apiKey": "..." },
    "vllm": { "apiKey": "dummy", "apiBase": "http://localhost:8000/v1" }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "123456:ABC...",
      "allowFrom": ["123456789"],
      "proxy": null
    },
    "discord": {
      "enabled": false,
      "token": "...",
      "allowFrom": []
    },
    "whatsapp": {
      "enabled": false,
      "bridgeUrl": "ws://localhost:3001",
      "bridgeToken": "",
      "allowFrom": []
    },
    "feishu": {
      "enabled": false,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": []
    },
    "dingtalk": {
      "enabled": false,
      "clientId": "...",
      "clientSecret": "...",
      "allowFrom": []
    },
    "slack": {
      "enabled": false,
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "groupPolicy": "mention",
      "dm": { "enabled": true, "policy": "open" }
    },
    "email": {
      "enabled": false,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "bot@gmail.com",
      "imapPassword": "app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "bot@gmail.com",
      "smtpPassword": "app-password",
      "fromAddress": "bot@gmail.com",
      "allowFrom": []
    },
    "qq": {
      "enabled": false,
      "appId": "...",
      "secret": "...",
      "allowFrom": []
    },
    "mochat": {
      "enabled": false,
      "baseUrl": "https://mochat.io",
      "clawToken": "claw_xxx",
      "agentUserId": "..."
    },
    "matrix": {
      "enabled": false,
      "homeserver": "https://matrix.org",
      "userId": "@bot:matrix.org",
      "token": "..."
    }
  },
  "tools": {
    "web": {
      "search": { "apiKey": "BSA-..." }
    },
    "exec": { "timeout": 60 },
    "restrictToWorkspace": false,
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
      }
    }
  }
}
```

---

## 工具 API

### 文件系统工具

#### read_file

读取文件内容。

```json
{
  "name": "read_file",
  "arguments": {
    "file_path": "/path/to/file.md",
    "offset": 1,
    "limit": 2000
  }
}
```

| 参数 | 类型 | 描述 |
|------|------|------|
| file_path | string | 文件绝对路径（必需） |
| offset | integer | 起始行号（1-indexed） |
| limit | integer | 最大行数 |

**返回值**：带行号的文件内容

---

#### write_file

写入文件内容。

```json
{
  "name": "write_file",
  "arguments": {
    "file_path": "/path/to/file.md",
    "content": "# Hello World"
  }
}
```

**返回值**：`Successfully wrote to /path/to/file.md`

---

#### edit_file

精确编辑文件。

```json
{
  "name": "edit_file",
  "arguments": {
    "file_path": "/path/to/file.md",
    "old_string": "old content",
    "new_string": "new content"
  }
}
```

**返回值**：`Successfully edited /path/to/file.md`

---

#### list_files

列出目录内容。

```json
{
  "name": "list_files",
  "arguments": {
    "path": "/path/to/directory"
  }
}
```

**返回值**：
```
📁 src
📄 README.md
📄 config.json
```

---

### Shell 工具

#### exec

执行 Shell 命令。

```json
{
  "name": "exec",
  "arguments": {
    "command": "ls -la",
    "timeout": 60
  }
}
```

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| command | string | 命令字符串 | - |
| timeout | integer | 超时时间 (秒) | 60 |

**返回值**：命令输出字符串

---

### Web 工具

#### web_search

搜索网页（使用 Brave Search API）。

```json
{
  "name": "web_search",
  "arguments": {
    "query": "nanobot AI assistant",
    "numResults": 5
  }
}
```

**返回值**：
```json
[
  {
    "title": "Result Title",
    "url": "https://...",
    "snippet": "Result snippet..."
  }
]
```

---

#### web_fetch

获取网页内容。

```json
{
  "name": "web_fetch",
  "arguments": {
    "url": "https://github.com/HKUDS/nanobot",
    "format": "markdown"
  }
}
```

| format | 描述 |
|--------|------|
| markdown | 提取正文为 Markdown |
| text | 纯文本 |
| html | 原始 HTML |

**返回值**：网页正文内容

---

### 消息工具

#### message

发送消息到渠道。

```json
{
  "name": "message",
  "arguments": {
    "channel": "telegram",
    "chat_id": "123456789",
    "content": "Hello from nanobot!"
  }
}
```

---

### 子代理工具

#### spawn

创建子 Agent 执行后台任务。

```json
{
  "name": "spawn",
  "arguments": {
    "task": "Research the latest AI developments",
    "workspace": "/tmp/research"
  }
}
```

**参数**：
| 参数 | 描述 |
|------|------|
| task | 任务描述 |
| workspace | 工作目录 |

---

### 定时任务工具

#### cron

管理定时任务。

```json
{
  "name": "cron",
  "arguments": {
    "action": "add",
    "name": "daily reminder",
    "message": "Good morning!",
    "cron": "0 9 * * *"
  }
}
```

| action | 描述 |
|--------|------|
| add | 添加任务 |
| list | 列出任务 |
| remove | 删除任务 |
| enable | 启用/禁用任务 |

---

## 消息格式

### InboundMessage（入站消息）

```python
@dataclass
class InboundMessage:
    """入站消息：用户 → Agent"""
    channel: str           # 渠道类型 (telegram, discord, etc.)
    sender_id: str         # 发送者标识
    chat_id: str           # 聊天 ID（用于回复）
    content: str           # 消息内容
    media: list[str] | None = None  # 媒体文件路径
    metadata: dict | None = None    # 额外信息
    
    @property
    def session_key(self) -> str:
        """会话标识"""
        return f"{self.channel}:{self.chat_id}"
```

### OutboundMessage（出站消息）

```python
@dataclass
class OutboundMessage:
    """出站消息：Agent → 用户"""
    channel: str           # 目标渠道
    chat_id: str           # 目标聊天 ID
    content: str           # 响应内容
    metadata: dict | None = None  # 额外信息（如 Slack thread_ts）
```

---

## LLM 提供商和模型

### 支持的提供商

| 提供商 | 类型 | 特点 | 配置字段 |
|--------|------|------|---------|
| OpenRouter | Gateway | 推荐，支持所有模型 | openrouter |
| Anthropic | 标准 | Claude 直连 | anthropic |
| OpenAI | 标准 | GPT 直连 | openai |
| DeepSeek | 标准 | 国产优质模型 | deepseek |
| Gemini | 标准 | Google 模型 | gemini |
| Groq | 标准 | 支持 Whisper 语音转写 | groq |
| Zhipu | 标准 | 智谱 GLM | zhipu |
| DashScope | 标准 | 通义千问 | dashscope |
| Moonshot | 标准 | Kimi | moonshot |
| MiniMax | 标准 | MiniMax | minimax |
| VolcEngine | 标准 | 火山引擎 | volcengine |
| AiHubMix | Gateway | API 网关 | aihubmix |
| SiliconFlow | Gateway | 硅基流动 | siliconflow |
| vLLM | 本地 | 本地部署 | vllm |
| Custom | 直连 | 任何 OpenAI 兼容 API | custom |
| OpenAI Codex | OAuth | ChatGPT Plus/Pro | openai_codex |
| GitHub Copilot | OAuth | Copilot 订阅 | github_copilot |

### 常用模型

| 提供商 | 模型名称 |
|--------|---------|
| OpenRouter | anthropic/claude-opus-4-5 |
| OpenRouter | anthropic/claude-sonnet-4-5 |
| OpenRouter | openai/gpt-4o |
| Anthropic | claude-opus-4-5 |
| OpenAI | gpt-4o |
| DeepSeek | deepseek-chat |
| DeepSeek | deepseek-reasoner |
| Gemini | gemini-2.0-flash |
| Groq | llama-3.3-70b-versatile |
| Moonshot | kimi-k2.5 |
| MiniMax | MiniMax-M2.1 |
| vLLM | meta-llama/Llama-3.1-8B-Instruct |

---

## MCP（Model Context Protocol）

### 配置 MCP 服务器

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      },
      "remote-server": {
        "url": "https://mcp.example.com/sse"
      }
    }
  }
}
```

### 传输模式

| 模式 | 配置 | 描述 |
|------|------|------|
| Stdio | command + args | 本地进程 |
| HTTP | url | 远程端点 |

MCP 工具会在启动时自动发现并注册，LLM 可以像使用内置工具一样使用它们。
