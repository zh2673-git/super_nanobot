# Sirchmunk 项目笔记

> 本笔记详细介绍 Sirchmunk 项目的整体结构、核心概念和技术实现。

---

## 一、项目概述

### 1.1 项目定位

**Sirchmunk** 是一个创新的**智能搜索与知识管理平台**，它能够直接从原始数据中提取信息，实现**实时、自主进化的智能分析**。

**通俗解释**：想象你有一个超级聪明的图书管理员，他不是简单地帮你找书，而是能够：
- 理解你的问题意图
- 在海量文件中快速找到相关内容
- 自动整理和关联知识
- 随着使用不断学习和进化

这就是 Sirchmunk —— 一个不同于传统搜索的**新一代智能系统**。

### 1.2 核心技术特点

| 特性 | 说明 | 类比 |
|------|------|------|
| **无向量数据库** | 直接处理原始数据，无需预先构建向量索引 | 就像直接在文件中搜索，而不是先转换成数字 |
| **自主进化** | 索引会随数据变化实时更新 | 就像一个会自己更新的百科全书 |
| **大规模实时搜索** | 支持海量数据和高吞吐量 | 像一个永不疲倦的搜索机器人 |
| **Agentic Search** | 智能代理驱动的搜索方式 | 像一个理解你意图的私人助理 |

---

## 二、技术栈概览

### 2.1 后端技术

```
┌─────────────────────────────────────────────────────────────┐
│                      后端架构                                │
├─────────────────────────────────────────────────────────────┤
│  Python 3.10+  ──► FastAPI ──► API 接口                    │
│                                                              │
│  核心模块：                                                  │
│  ├── search.py       (智能搜索核心)                          │
│  ├── doc_qa.py       (文档问答)                              │
│  ├── storage/        (数据存储，DuckDB)                     │
│  ├── retrieve/       (文本检索)                             │
│  ├── learnings/      (知识学习)                             │
│  ├── agentic/        (智能代理)                             │
│  └── llm/            (大语言模型集成)                        │
└─────────────────────────────────────────────────────────────┘
```

**技术组件说明**：

- **FastAPI**：高性能 Python Web 框架，负责提供 API 服务
- **DuckDB**：轻量级分析型数据库，用于存储搜索结果和知识
- **OpenAI API**：集成大语言模型能力，实现智能理解
- **MCP (Model Context Protocol)**：模型上下文协议，支持 AI Agent 扩展

### 2.2 前端技术

```
┌─────────────────────────────────────────────────────────────┐
│                      前端架构                                │
├─────────────────────────────────────────────────────────────┤
│  Next.js 14  ──► React 组件  ──► 用户界面                   │
│                                                              │
│  技术栈：                                                    │
│  ├── Next.js 14     (React 框架)                            │
│  ├── Tailwind CSS   (样式框架)                              │
│  ├── TypeScript     (类型安全)                              │
│  └── API 客户端    (与后端通信)                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 基础设施

| 组件 | 用途 | 备注 |
|------|------|------|
| **ripgrep-all (rga)** | 全文本搜索工具 | 支持多种文件格式的全文检索 |
| **Docker** | 容器化部署 | 提供完整运行环境 |
| **uvicorn** | ASGI 服务器 | 运行 FastAPI 应用 |

---

## 三、目录结构

### 3.1 项目整体结构

```
sirchmunk/
├── src/sirchmunk/              # 核心源代码
│   ├── api/                    # FastAPI 接口
│   │   ├── main.py             # 主应用入口
│   │   ├── chat.py             # 聊天接口
│   │   ├── search.py           # 搜索接口
│   │   ├── knowledge.py        # 知识管理接口
│   │   └── ...
│   ├── search.py               # 搜索核心逻辑 (AgenticSearch)
│   ├── doc_qa.py               # 文档问答
│   ├── storage/                # 数据存储层
│   │   ├── duckdb.py           # DuckDB 封装
│   │   └── knowledge_storage.py
│   ├── retrieve/                # 检索模块
│   │   └── text_retriever.py   # 文本检索
│   ├── learnings/               # 知识学习
│   │   ├── knowledge_base.py   # 知识库
│   │   └── evidence_processor.py
│   ├── agentic/                # 智能代理
│   │   ├── react_agent.py      # ReAct Agent
│   │   └── tools.py            # 工具集
│   ├── llm/                    # LLM 集成
│   │   ├── openai_chat.py      # OpenAI 聊天
│   │   └── prompts.py          # 提示词模板
│   ├── scan/                   # 文件扫描
│   │   ├── dir_scanner.py      # 目录扫描
│   │   ├── file_scanner.py     # 文件扫描
│   │   └── web_scanner.py      # 网页扫描
│   ├── schema/                 # 数据模型
│   ├── utils/                  # 工具函数
│   └── cli/                    # 命令行工具
│
├── src/sirchmunk_mcp/          # MCP 服务器实现
│   ├── server.py               # MCP 服务端
│   ├── service.py              # 服务层
│   └── tools.py                # MCP 工具
│
├── web/                        # Next.js 前端
│   ├── app/                    # Next.js 页面
│   │   ├── page.tsx            # 首页
│   │   ├── chat/               # 聊天页面
│   │   ├── knowledge/          # 知识库页面
│   │   ├── history/            # 历史记录
│   │   └── monitor/            # 监控页面
│   ├── components/             # React 组件
│   ├── lib/                    # 工具库
│   └── hooks/                  # 自定义 Hooks
│
├── config/                     # 配置文件
├── docker/                     # Docker 配置
├── scripts/                    # 脚本工具
└── requirements/               # 依赖文件
    ├── core.txt                # 核心依赖
    ├── web.txt                 # Web 依赖
    ├── mcp.txt                 # MCP 依赖
    └── tests.txt               # 测试依赖
```

### 3.2 核心模块功能说明

#### 后端核心模块

| 模块 | 位置 | 功能说明 |
|------|------|----------|
| **AgenticSearch** | `search.py` | 智能搜索核心类，负责处理搜索请求、协调各组件 |
| **DocQA** | `doc_qa.py` | 文档问答，处理自然语言问题回答 |
| **KnowledgeBase** | `learnings/knowledge_base.py` | 知识库管理，维护知识集群和证据 |
| **GrepRetriever** | `retrieve/text_retriever.py` | 基于 ripgrep 的文本检索 |
| **DuckDBStorage** | `storage/duckdb.py` | 数据库存储封装 |
| **ReActAgent** | `agentic/react_agent.py` | 推理行动代理 |

#### API 接口模块

| 模块 | 功能 |
|------|------|
| `api/main.py` | FastAPI 主应用，聚合所有路由 |
| `api/chat.py` | 聊天接口 |
| `api/search.py` | 搜索接口 |
| `api/knowledge.py` | 知识库管理接口 |
| `api/history.py` | 历史记录接口 |
| `api/monitor.py` | 监控指标接口 |
| `api/settings.py` | 设置接口 |

---

## 四、快速开始

### 4.1 环境要求

- Python 3.10+
- Node.js 18+ (用于前端)
- Docker (可选，用于容器部署)

### 4.2 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/modelscope/sirchmunk.git
cd sirchmunk

# 2. 安装 Python 依赖
pip install -e ".[all]"

# 3. 配置环境变量
cp config/env.example ~/.sirchmunk/.env
# 编辑 .env 文件，填入 API Key

# 4. 启动服务
sirchmunk web serve     # 启动 Web 服务
sirchmunk api start    # 启动 API 服务
```

### 4.3 Docker 部署

```bash
cd docker
docker-compose up -d
```

---

## 五、相关文档

- [[架构分析]] - 详细架构设计说明
- [[运行逻辑]] - 程序执行流程分析
- [[源码解析]] - 核心代码详解
- [[核心API文档]] - API 接口文档
- [[核心算法分析]] - 核心算法解析

---

## 六、参考资料

- 官方网站：https://github.com/modelscope/sirchmunk
- 文档：https://modelscope.github.io/sirchmunk-web/
