<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="500">
  <h1>super_nanobot: Ultra-Lightweight AI with OllamaPilot Powers</h1>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/Feishu-Group-E9DBFC?style=flat&logo=feishu&logoColor=white" alt="Feishu"></a>
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/WeChat-Group-C5EAB4?style=flat&logo=wechat&logoColor=white" alt="WeChat"></a>
    <a href="https://discord.gg/MnCvHqpUGB"><img src="https://img.shields.io/badge/Discord-Community-5865F2?style=flat&logo=discord&logoColor=white" alt="Discord"></a>
  </p>
</div>

🐈 **super_nanobot** 是一个**超轻量级**的个人 AI 助手，基于 [nanobot](https://github.com/HKUDS/nanobot) 构建，并完整集成了 [OllamaPilot](https://github.com/ollamapilot/ollamapilot) 的核心功能。

⚡️ 在保持 nanobot **99% 精简代码**的同时，获得了 OllamaPilot 的三层搜索、GraphRAG 知识图谱、小模型优化等强大功能。

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| 🪶 **超轻量级** | 核心代码仅 ~4,000 行，启动快、资源占用低 |
| 🧠 **小模型优化** | 针对 4B 小模型优化，支持 temperature、top_p、repeat_penalty 等参数 |
| 🔍 **三层搜索** | 基础搜索 → 增强搜索 → 深度研究，智能选择搜索层级 |
| 🧩 **GraphRAG** | 知识图谱驱动的文档问答，支持实体抽取和关系推断 |
| 🚀 **SearXNG 部署** | 一键自动部署 SearXNG 元搜索引擎 |
| 💬 **多渠道支持** | Telegram、Discord、飞书、钉钉、Slack、QQ、微信等 8+ 平台 |
| 🎯 **Skill 路由** | 基于触发词的智能 Skill 选择 |
| 🔄 **工具增强** | 自动重试、日志记录、错误处理 |

## 🏗️ 架构

```
super_nanobot 架构:
┌─────────────────────────────────────────┐
│  ChannelManager (多渠道支持)             │
├─────────────────────────────────────────┤
│  MessageBus (异步消息队列)               │
├─────────────────────────────────────────┤
│  AgentLoop (自研Agent核心)               │
│  ├── ContextBuilder (上下文构建)         │
│  ├── ToolRegistry (工具注册表)           │
│  ├── SkillsLoader (Skill加载器)          │
│  └── SkillRouter (智能路由) ⭐新增        │
├─────────────────────────────────────────┤
│  LiteLLMProvider (多模型支持)            │
│  └── 小模型优化配置 ⭐新增                │
├─────────────────────────────────────────┤
│  工具层 ⭐新增                           │
│  ├── EnhancedSearchTool (三层搜索)       │
│  ├── GraphRAGTool (知识图谱)             │
│  └── SearXNGDeployer (自动部署)          │
└─────────────────────────────────────────┘
```

## 📦 安装

**从源码安装**（推荐，获取最新功能）

```bash
git clone https://github.com/zh2673-git/super_nanobot.git
cd super_nanobot
pip install -e .
```

**依赖项**

```bash
# 基础依赖
pip install httpx>=0.27.0 numpy>=1.24.0

# 如果需要使用 Chroma 向量库（可选）
pip install chromadb>=0.4.0

# Docker（用于 SearXNG 部署）
# 请确保已安装 Docker
```

## 🚀 快速开始

### 1. 初始化配置

```bash
nanobot onboard
```

### 2. 配置模型

编辑 `~/.nanobot/config.json`：

**使用 Ollama 本地模型（推荐小模型场景）**

```json
{
  "providers": {
    "ollama": {
      "apiBase": "http://localhost:11434",
      "defaultModel": "qwen3.5:4b",
      "smallModelMode": true,
      "smallModelConfig": {
        "temperature": 0.7,
        "topP": 0.9,
        "topK": 40,
        "repeatPenalty": 1.1,
        "numCtx": 8192,
        "maxTokens": 2048
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen3.5:4b",
      "provider": "ollama"
    }
  }
}
```

> **注意**: OllamaPilot 默认使用 `qwen3.5:4b` 作为对话模型，`qwen3-embedding:0.6b` 作为嵌入模型。

**使用 OpenRouter（云端模型）**

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  }
}
```

### 3. 启动对话

```bash
nanobot agent
```

## 🔍 三层搜索功能

super_nanobot 实现了 OllamaPilot 的三层搜索架构：

### 第一层：基础搜索

适合日常查询、简单信息获取

```
用户: "搜索 Python 教程"
→ 使用 SearXNG / Brave / DuckDuckGo 搜索
```

### 第二层：增强搜索

针对专业领域的深度搜索

```
用户: "学术搜索 量子计算"
→ 使用 PubMed、arXiv 等学术引擎

用户: "代码搜索 FastAPI 示例"
→ 使用 GitHub、Gitee 搜索

用户: "百科搜索 人工智能"
→ 使用 百度百科、Wikipedia
```

### 第三层：深度研究

复杂主题的多轮研究分析

```
用户: "研究人工智能在医疗领域的应用现状"
→ 自动多轮搜索
→ 生成综合分析报告
```

### 配置搜索

```json
{
  "tools": {
    "enhanced_search": {
      "braveApiKey": "YOUR_BRAVE_API_KEY",
      "searxngUrl": "http://localhost:8080"
    }
  }
}
```

### 部署 SearXNG

```python
from nanobot.utils.searxng_deploy import ensure_searxng

# 自动部署 SearXNG
url = ensure_searxng(port=8080)
print(f"SearXNG 已部署: {url}")
```

## 🧩 GraphRAG 知识图谱

基于知识图谱的智能文档问答系统：

### 功能特性

- 📄 **文档索引** - 将文档添加到知识库
- 🔍 **智能查询** - 基于向量和实体关系的混合搜索
- 🏷️ **实体抽取** - 自动识别文档中的实体
- 🔗 **关系推断** - 自动推断实体间关系
- 💾 **持久化存储** - SQLite + JSON 存储方案

### 使用方法

```python
from nanobot.agent.tools.graphrag import GraphRAGTool
from pathlib import Path

# 创建工具实例
graphrag = GraphRAGTool(workspace=Path("./data"))

# 索引文档
await graphrag.execute(
    action="index",
    content="文档内容...",
    source="document.pdf",
    collection="my_knowledge"
)

# 查询知识库
result = await graphrag.execute(
    action="query",
    query="文档的主要观点是什么？",
    collection="my_knowledge"
)
print(result)

# 查看状态
status = await graphrag.execute(
    action="status",
    collection="my_knowledge"
)
print(status)
```

### 使用 Skill

在对话中直接使用：

```
用户: "帮我分析这篇论文"
→ Agent 自动调用 graphrag 索引文档

用户: "这篇论文的主要观点是什么？"
→ Agent 自动查询知识图谱
```

## 🎯 Skill 智能路由

基于触发词的自动 Skill 选择：

### 配置触发词

在 `SKILL.md` 中添加触发词：

```yaml
---
name: weather
description: 获取天气信息
triggers:
  - 天气
  - 温度
  - 下雨
  - 晴天
metadata: {"nanobot":{"emoji":"🌤️","triggers":["天气","温度","下雨"]}}
---
```

### 工作原理

```python
from nanobot.agent.skill_router import SkillRouter

router = SkillRouter(skills_loader)

# 自动选择 Skill
skill_name = router.select_skill("今天天气怎么样？")
# 返回: "weather"

# 获取 Skill 提示词
prompt = router.get_skill_prompt("weather")
```

## 🛠️ 工具增强

所有工具都支持日志记录和自动重试：

```python
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "My tool description"
    
    # 重试配置
    max_retries = 2
    retry_delay = 1.0
    
    # 日志配置
    enable_logging = True
    
    async def _execute(self, **kwargs):
        # 实际执行逻辑
        return "result"
```

## 💬 聊天渠道

super_nanobot 支持多种聊天平台：

| 渠道 | 说明 |
|------|------|
| Telegram | 推荐，稳定可靠 |
| Discord | 支持富媒体 |
| WhatsApp | 扫码登录 |
| 飞书 | 企业办公 |
| 钉钉 | 企业办公 |
| Slack | 团队协作 |
| QQ | 国内用户 |
| 微信 | 企业微信 |
| Email | 邮件交互 |

### 启动网关

```bash
nanobot gateway
```

## ⚙️ 配置参考

完整配置示例 `~/.nanobot/config.json`：

```json
{
  "providers": {
    "ollama": {
      "apiBase": "http://localhost:11434",
      "defaultModel": "qwen3.5:4b",
      "smallModelMode": true,
      "smallModelConfig": {
        "temperature": 0.7,
        "topP": 0.9,
        "topK": 40,
        "repeatPenalty": 1.1,
        "numCtx": 8192,
        "maxTokens": 2048
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen3.5:4b",
      "provider": "ollama",
      "skills": ["enhanced_search", "graphrag"]
    }
  },
  "tools": {
    "enhanced_search": {
      "braveApiKey": "YOUR_BRAVE_API_KEY",
      "searxngUrl": "http://localhost:8080"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

## 📁 项目结构

```
super_nanobot/
├── nanobot/
│   ├── agent/
│   │   ├── tools/
│   │   │   ├── base.py              # 工具基类（增强版）
│   │   │   ├── enhanced_search.py   # 三层搜索 ⭐
│   │   │   └── graphrag.py          # GraphRAG ⭐
│   │   ├── skill_router.py          # Skill 路由 ⭐
│   │   └── ...
│   ├── skills/
│   │   ├── enhanced_search/         # 搜索 Skill ⭐
│   │   └── graphrag/                # GraphRAG Skill ⭐
│   ├── utils/
│   │   └── searxng_deploy.py        # SearXNG 部署 ⭐
│   └── ...
├── tests/                           # 测试文件
├── README.md                        # 本文档
└── pyproject.toml                   # 项目配置
```

## 🔄 迁移自 OllamaPilot

如果你之前使用 OllamaPilot，迁移到 super_nanobot 非常简单：

| OllamaPilot 功能 | super_nanobot 对应 |
|-----------------|-------------------|
| 三层搜索 | `EnhancedSearchTool` |
| GraphRAG | `GraphRAGTool` |
| Skill 路由 | `SkillRouter` |
| 小模型优化 | `LiteLLMProvider.small_model_mode` |
| SearXNG 部署 | `SearXNGDeployer` |

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

## 🙏 致谢

- [nanobot](https://github.com/HKUDS/nanobot) - 基础框架
- [OllamaPilot](https://github.com/ollamapilot/ollamapilot) - 功能参考

---

<div align="center">
  <p>Made with ❤️ by super_nanobot team</p>
</div>
