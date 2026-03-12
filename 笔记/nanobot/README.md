# nanobot 项目笔记集合

> 📚 基于 v0.1.4.post4 的完整分析笔记（更新于 2026-03-10）

## 🐄 项目简介

**nanobot** 是一个**超轻量级个人 AI 助手框架**，核心代码仅约 4,000 行，比 Clawdbot 的 430k+ 行代码小了 99%。

### 核心设计理念

类比为一台**精密的瑞士军刀**：
- **小而精**：只保留最核心的功能
- **可扩展**：通过 Skills 系统扩展功能
- **多渠道接入**：支持 9+ 聊天平台

### 四大核心组件

| 组件 | 类比 | 职责 |
|------|------|------|
| Agent Loop | 大脑 | 接收消息、调用 LLM、执行工具、返回响应 |
| Message Bus | 脊髓 | 连接渠道和 Agent 的神经中枢 |
| Tool Registry | 双手 | 管理 Agent 可用的所有工具 |
| Provider Registry | 知识库 | 管理 LLM 提供商 |

## 📋 文件说明

### 🏗️ 架构和运行
- **架构分析.md** - 整体架构设计分析
- **运行逻辑.md** - 程序执行流程详解

### 💻 源码和API
- **源码解析.md** - 核心源码深度分析
- **核心API文档.md** - 关键API参考文档

## ✨ v0.1.4.post4 新特性

- **更安全的默认设置**：改进的访问控制和更安全的默认值
- **更好的多实例支持**：改进的多实例运行稳定性
- **更健壮的 MCP**：MCP 协议支持的增强和稳定性改进
- **渠道和提供商重大改进**：多个渠道（Telegram、Feishu、WhatsApp提供、QQ）和商的稳定性增强

## 📢 历史版本 (v0.1.4.post3)

- **MCP 支持**：支持 Model Context Protocol，可连接外部工具服务器
- **OAuth 登录**：支持 OpenAI Codex 和 GitHub Copilot 的 OAuth 认证
- **新渠道**：Slack、Email、QQ、Matrix 支持
- **新提供商**：MiniMax、AiHubMix、SiliconFlow、OpenAI Codex、GitHub Copilot、VolcEngine
- **进度流式输出**：工具执行时实时显示进度
- **思考模式**：支持 reasoning_effort 配置，启用 LLM 思考模式
- **会话历史强化**：保留 reasoning_content 和 thinking_blocks
- **Cron 自动重载**：外部修改 jobs.json 后自动重载
- **飞书富文本消息**：支持解析 post wrapper payload
- **多平台稳定性**：Windows 路径保护、WhatsApp 去重、Mistral 兼容

## 🔗 相关资源

- [项目GitHub](https://github.com/HKUDS/nanobot)
- [PyPI页面](https://pypi.org/project/nanobot-ai/)

## 📝 使用说明

这些笔记按逻辑顺序组织，建议从 README → 架构分析 → 运行逻辑 → 源码解析 → API 的顺序学习。

---

*生成日期：2026-03-10*
*基于版本：v0.1.4.post4*