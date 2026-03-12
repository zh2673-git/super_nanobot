# Open Deep Research 项目笔记

> 一个可配置的、完全开源的深度研究代理，支持多种模型提供商、搜索工具和 MCP 服务器

## 项目概述

本项目是 LangChain 团队开源的深度研究代理系统，它能够自动分析用户的研究需求，通过多轮搜索和信息整合，生成专业的研究报告。该项目在 Deep Research Bench 排行榜上取得了优秀成绩，综合得分达到 0.4344。

## 核心概念

- **[LangGraph](LangGraph.md)**：工作流编排框架，负责管理整个研究流程的节点和边
- **[深度研究代理](深度研究代理.md)**：能够自主进行多轮搜索、整合信息、生成报告的智能代理
- **[多模型支持](多模型支持.md)**：支持 OpenAI、Anthropic、Google、Groq、DeepSeek 等多种 LLM 提供商
- **[搜索 API](搜索API.md)**：集成 Tavily、OpenAI、Anthropic 原生搜索等多种搜索工具
- **[MCP 服务器](MCP服务器.md)**：支持 Model Context Protocol 扩展能力

## 项目结构

```
open_deep_research/
├── src/open_deep_research/
│   ├── deep_researcher.py      # 核心 LangGraph 实现
│   ├── configuration.py       # 配置管理
│   ├── state.py                # 状态定义
│   ├── prompts.py              # 提示词模板
│   └── utils.py                # 工具函数
├── tests/                       # 测试和评估代码
└── examples/                    # 使用示例
```

## 技术栈

- **编程语言**：Python
- **核心框架**：LangGraph、LangChain
- **依赖管理**：UV
- **配置格式**：Pydantic

## 快速开始

```bash
# 克隆项目
git clone https://github.com/langchain-ai/open_deep_research.git
cd open_deep_research

# 创建虚拟环境
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
uv sync

# 复制配置
cp .env.example .env

# 启动开发服务器
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

## 配置选项

### 模型配置

| 用途 | 默认模型 | 说明 |
|------|---------|------|
| 总结 | openai:gpt-4.1-mini | 总结搜索结果 |
| 研究 | openai:gpt-4.1 | 驱动搜索代理 |
| 压缩 | openai:gpt-4.1 | 压缩研究发现 |
| 最终报告 | openai:gpt-4.1 | 撰写最终报告 |

### 搜索 API

支持多种搜索工具：
- **Tavily**（默认）：专业的 AI 搜索 API
- **OpenAI Native Web Search**：OpenAI 原生搜索
- **Anthropic Native Web Search**：Anthropic 原生搜索

## 相关文档

- [[架构分析]] - 深入了解系统架构设计
- [[运行逻辑]] - 程序执行流程详解
- [[源码解析]] - 核心源码分析
- [[核心API文档]] - API 接口文档
- [[核心算法分析]] - 核心算法解析
