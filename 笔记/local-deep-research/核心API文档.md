# Local Deep Research 核心API文档

> 本笔记整理项目提供的核心API接口，帮助开发者快速上手集成。

---

## 第一步：点出API的核心组件概念

- **[Python客户端（Python Client）]：项目提供的"易用工具包"，让Python开发者能几行代码完成研究，就像"自动档汽车"比"手动档"更容易开**
- **[REST API（HTTP接口）]：项目的"通用语言"，任何能发HTTP请求的编程语言都能用，就像"USB接口"是所有电脑都认识的标准**
- **[命令行工具（CLI）]：项目的"快捷方式"，在终端输入命令就能执行研究，就像"语音助手"说句话就能办事**
- **[MCP服务器（MCP Protocol）]：AI助手的"插件"，让Claude等AI能直接调用研究功能，就像给手机"安装APP"**

---

## 第二步：用图构建API组件之间的联系

```
[用户/开发者]
    |
    +---> [Python客户端] ----> [REST API]
    |           |
    |           +---> quick_query()  --> POST /api/quick_summary
    |           +---> detailed_research() --> POST /api/detailed_research
    |           +---> generate_report() --> POST /api/generate_report
    |
    +---> [REST API] <-----------------+
    |           |
    |           +---> /api/start_research
    |           +---> /api/research/{id}
    |           +---> /api/library/*
    |
    +---> [CLI工具] ----> [命令行接口]
    |           |
    |           +---> ldr research "问题"
    |           +---> ldr-web
    |
    +---> [MCP服务器] <--> [Claude Desktop]
                |
                +---> search()
                +---> quick_research()
                +---> detailed_research()
```

**联系说明**：API就像项目的"多语言服务台"：
- **Python客户端** = 会说Python语的接待员
- **REST API** = 会说HTTP语的接待员（所有语言都能对话）
- **CLI** = 只会听命令行话的接待员
- **MCP服务器** = AI助手的专属接待员

---

## 第三步：详细解释API使用

### 1. Python客户端

**专业定义**：项目提供的Python客户端库，封装了REST API的调用，提供简洁的Python接口。

**通俗解释与类比**：就像"自动档汽车"：
- 手动档（直接调用REST API）需要自己控制离合、换挡
- 自动档（Python客户端）踩油门就走，踩刹车就停
- 适合不想了解底层细节的用户

**安装和使用**：
```bash
# 安装
pip install local-deep-research
```

**快速开始**：
```python
from local_deep_research.api import LDRClient, quick_query

# 方法1：最简单的——一行代码研究
result = quick_query(
    username="your_username",
    password="your_password",
    query="什么是量子计算？"
)
print(result["summary"])

# 方法2：使用客户端（更多功能）
client = LDRClient()

# 登录
client.login("username", "password")

# 快速研究
result = client.quick_research("量子计算的最新进展")
print(result["summary"])

# 详细研究
result = client.detailed_research("人工智能在医疗领域的应用")
print(result["findings"])

# 生成报告
result = client.generate_report("气候变化的影响", format="pdf")
# result 包含 PDF 文件内容
```

**Python客户端主要方法**：
| 方法 | 说明 | 参数 | 返回值 |
|-----|------|------|-------|
| `quick_query()` | 快速研究 | username, password, query | 摘要结果 |
| `quick_research()` | 快速研究 | query | 研究结果 |
| `detailed_research()` | 详细研究 | query | 详细报告 |
| `generate_report()` | 生成报告 | query, format | 报告内容 |
| `analyze_documents()` | 分析文档 | query, collection_id | 分析结果 |
| `list_engines()` | 列出搜索引擎 | - | 引擎列表 |
| `list_strategies()` | 列出研究策略 | - | 策略列表 |

---

### 2. REST API

**专业定义**：基于HTTP的编程接口，支持所有能发送HTTP请求的编程语言。

**通俗解释与类比**：就像"USB接口"：
- 不管你用Windows、Mac还是Linux
- 不管你用Python、Java还是JavaScript
- 都能通过USB（HTTP）接口连接

**基础URL**：
```
http://localhost:5000
```

**认证方式**：
```python
import requests
from bs4 import BeautifulSoup

# 1. 获取登录页面的CSRF token
session = requests.Session()
login_page = session.get("http://localhost:5000/auth/login")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

# 2. 登录
session.post(
    "http://localhost:5000/auth/login",
    data={
        "username": "your_username",
        "password": "your_password",
        "csrf_token": csrf_token
    }
)

# 3. 获取API的CSRF token
api_csrf = session.get("http://localhost:5000/auth/csrf-token").json()["csrf_token"]
```

**主要API端点**：

#### 快速研究
```http
POST /api/quick_summary
Content-Type: application/json
X-CSRF-Token: {csrf_token}

Request:
{
    "query": "量子计算的最新进展"
}

Response:
{
    "id": "research_123",
    "summary": "量子计算是一种...",
    "sources": [...]
}
```

#### 详细研究
```http
POST /api/detailed_research
Content-Type: application/json
X-CSRF-Token: {csrf_token}

Request:
{
    "query": "人工智能在医疗领域的应用",
    "mode": "detailed",
    "iterations": 5
}

Response:
{
    "id": "research_456",
    "status": "completed",
    "findings": [...],
    "report": "## 摘要\n\n..."
}
```

#### 生成报告
```http
POST /api/generate_report
Content-Type: application/json
X-CSRF-Token: {csrf_token}

Request:
{
    "query": "气候变化的影响",
    "format": "pdf"  // 或 "markdown"
}

Response:
{
    "report": "base64编码的PDF内容",
    "filename": "report.pdf"
}
```

#### 获取研究历史
```http
GET /api/research/history
X-CSRF-Token: {csrf_token}

Response:
{
    "researches": [
        {
            "id": "research_123",
            "query": "量子计算",
            "created_at": "2024-01-01T12:00:00",
            "status": "completed"
        }
    ]
}
```

---

### 3. 命令行工具

**专业定义**：项目提供的命令行接口，适合在终端中快速使用。

**通俗解释与类比**：就像"语音助手"：
- 不用动手敲代码
- 说话下命令就能办事
- 适合快速测试和脚本集成

**安装后获得的命令**：
```bash
# 启动Web界面
ldr-web

# 运行基准测试
ldr simpleqa --examples 50
ldr browsecomp --examples 20

# 查看配置
ldr config show

# 管理速率限制
ldr rate-limit status
ldr rate-limit reset
```

**详细命令**：
```bash
# 启动Web服务器
ldr-web
# 默认 http://localhost:5000

# 运行SimpleQA基准测试
python -m local_deep_research.benchmarks \
    --dataset simpleqa \
    --examples 50

# 运行自定义基准测试
python -m local_deep_research.benchmarks \
    --dataset your_dataset \
    --config your_config.json
```

---

### 4. MCP服务器

**专业定义**：Model Context Protocol服务器，让AI助手（如Claude Desktop）能够直接调用研究功能。

**通俗解释与类比**：就像给手机"安装APP"：
- MCP = APP商店
- Claude = 你的手机
- LDR MCP = 一个叫"深度研究"的APP
- 安装后，Claude就能使用深度研究功能

**安装**：
```bash
pip install "local-deep-research[mcp]"
```

**配置（Claude Desktop）**：
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "local-deep-research": {
      "command": "ldr-mcp",
      "env": {
        "LDR_LLM_PROVIDER": "openai",
        "LDR_LLM_OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

**MCP可用工具**：
| 工具名 | 说明 | 示例 |
|-------|------|------|
| `search` | 直接搜索某个引擎 | `search("量子计算", engine="arxiv")` |
| `quick_research` | 快速研究 | `quick_research("量子计算最新进展")` |
| `detailed_research` | 详细研究 | `detailed_research("AI医疗应用")` |
| `generate_report` | 生成报告 | `generate_report("气候变化", format="pdf")` |
| `analyze_documents` | 分析文档 | `analyze_documents("我的研究", collection_id=1)` |
| `list_search_engines` | 列出搜索引擎 | `list_search_engines()` |
| `list_strategies` | 列出策略 | `list_strategies()` |

**使用示例**：
```
用户: "用quick_research搜索量子计算的最新进展"
Claude调用: quick_research(query="量子计算的最新进展")
结果: 返回研究摘要

用户: "生成一份关于气候变化的详细报告"
Claude调用: generate_report(query="气候变化的影响", format="markdown")
结果: 返回Markdown格式报告
```

---

## API使用对比

| 方式 | 难度 | 灵活性 | 适用场景 |
|-----|------|-------|---------|
| Python客户端 | ⭐ 简单 | ⭐⭐⭐ | 快速集成 |
| REST API | ⭐⭐ 中等 | ⭐⭐⭐⭐ | 跨语言集成 |
| CLI | ⭐ 简单 | ⭐⭐ | 快速测试 |
| MCP | ⭐⭐ 中等 | ⭐⭐⭐⭐⭐ | AI助手集成 |

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 401 | 未认证 | 检查用户名密码 |
| 403 | CSRF错误 | 刷新CSRF token |
| 429 | 速率限制 | 等待后重试 |
| 500 | 服务器错误 | 查看日志 |

### Python客户端错误处理
```python
from local_deep_research.api import LDRClient
from local_deep_research.exceptions import LDRException

try:
    client = LDRClient()
    result = client.quick_research("测试查询")
except LDRException as e:
    print(f"研究失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 相关文档

- [[README]] - 项目概述
- [[架构分析]] - 系统架构设计
- [[运行逻辑]] - 程序执行流程
- [[源码解析]] - 核心代码分析
