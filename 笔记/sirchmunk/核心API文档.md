# 核心API文档

> 本文档详细介绍 Sirchmunk 的 API 接口，包括请求参数、响应格式和使用示例。

---

## 一、API 概览

### 1.1 接口列表

| 接口路径 | 方法 | 功能 | 认证 |
|----------|------|------|------|
| `/search` | POST | 执行搜索 | 需要 |
| `/chat` | WebSocket | 聊天对话 | 需要 |
| `/knowledge` | POST | 添加知识 | 需要 |
| `/knowledge/query` | POST | 查询知识 | 需要 |
| `/knowledge/list` | GET | 知识列表 | 需要 |
| `/history` | GET | 搜索历史 | 需要 |
| `/settings` | GET/PUT | 设置管理 | 需要 |
| `/monitor` | GET | 系统监控 | 需要 |

### 1.2 Base URL

```
开发环境: http://localhost:8000
生产环境: https://your-domain.com
```

---

## 二、搜索接口

### 2.1 执行搜索

**接口路径**: `/search`

**请求方法**: `POST`

**请求体**:
```json
{
  "query": "Python 异步编程",
  "mode": "search",
  "k": 10,
  "paths": ["/path/to/search"],
  "include_summary": true
}
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索查询内容 |
| `mode` | string | 否 | 搜索模式: `search`(搜索) 或 `chat`(聊天) |
| `k` | integer | 否 | 返回结果数量，默认 10 |
| `paths` | array | 否 | 搜索路径列表 |
| `include_summary` | boolean | 否 | 是否包含 LLM 总结 |

**响应示例**:
```json
{
  "query": "Python 异步编程",
  "results": [
    {
      "file_path": "/path/to/file.py",
      "line_number": 10,
      "content": "async def main(): ...",
      "score": 0.95
    }
  ],
  "summary": "根据搜索结果，Python 异步编程主要使用 async/await 语法...",
  "total": 10,
  "took": 1.23
}
```

---

## 三、聊天接口

### 3.1 WebSocket 连接

**接口路径**: `/chat/ws`

**连接方式**: WebSocket

**URL 格式**:
```
ws://localhost:8000/chat/ws?token=YOUR_TOKEN
```

**消息格式**:

**发送消息**:
```json
{
  "type": "message",
  "content": "如何实现 Python 异步编程？",
  "mode": "chat"
}
```

**接收消息**:
```json
{
  "type": "chunk",
  "content": "Python 的异步编程主要使用"
}
{
  "type": "done",
  "content": "完整回答内容"
}
```

### 3.2 聊天参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | string | 消息类型: `message`, `done` |
| `content` | string | 消息内容 |
| `mode` | string | 模式: `chat` |

---

## 四、知识管理接口

### 4.1 添加知识

**接口路径**: `/knowledge`

**请求方法**: `POST`

**请求体**:
```json
{
  "content": "Python 的 async/await 语法用于异步编程",
  "source": "https://docs.python.org",
  "metadata": {
    "language": "zh",
    "tags": ["python", "async"]
  }
}
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 知识内容 |
| `source` | string | 否 | 来源 |
| `metadata` | object | 否 | 元数据 |

**响应示例**:
```json
{
  "id": "kn_123456",
  "status": "success",
  "message": "Knowledge added successfully"
}
```

### 4.2 查询知识

**接口路径**: `/knowledge/query`

**请求方法**: `POST`

**请求体**:
```json
{
  "query": "Python 异步",
  "k": 5
}
```

**响应示例**:
```json
{
  "query": "Python 异步",
  "results": [
    {
      "id": "kn_123456",
      "content": "Python 的 async/await 语法用于异步编程",
      "score": 0.92,
      "source": "https://docs.python.org"
    }
  ]
}
```

### 4.3 知识列表

**接口路径**: `/knowledge/list`

**请求方法**: `GET`

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | integer | 页码，默认 1 |
| `page_size` | integer | 每页数量，默认 20 |

**响应示例**:
```json
{
  "items": [
    {
      "id": "kn_123456",
      "content": "Python 的 async/await 语法用于异步编程",
      "source": "https://docs.python.org",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

## 五、历史记录接口

### 5.1 获取历史

**接口路径**: `/history`

**请求方法**: `GET`

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | integer | 页码，默认 1 |
| `page_size` | integer | 每页数量，默认 20 |
| `query` | string | 搜索查询（用于过滤） |

**响应示例**:
```json
{
  "items": [
    {
      "id": "hist_123456",
      "query": "Python 异步编程",
      "results_count": 10,
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### 5.2 历史详情

**接口路径**: `/history/{id}`

**请求方法**: `GET`

**响应示例**:
```json
{
  "id": "hist_123456",
  "query": "Python 异步编程",
  "results": [...],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 六、设置接口

### 6.1 获取设置

**接口路径**: `/settings`

**请求方法**: `GET`

**响应示例**:
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "search": {
    "default_k": 10,
    "max_file_size": 10485760
  }
}
```

### 6.2 更新设置

**接口路径**: `/settings`

**请求方法**: `PUT`

**请求体**:
```json
{
  "llm": {
    "temperature": 0.5
  }
}
```

---

## 七、监控接口

### 7.1 系统状态

**接口路径**: `/monitor`

**请求方法**: `GET`

**响应示例**:
```json
{
  "status": "healthy",
  "uptime": 3600,
  "cpu_usage": 0.25,
  "memory_usage": 0.60,
  "disk_usage": 0.45
}
```

### 7.2 搜索统计

**接口路径**: `/monitor/stats`

**请求方法**: `GET`

**响应示例**:
```json
{
  "total_searches": 1000,
  "total_queries": 500,
  "avg_response_time": 1.23,
  "cache_hit_rate": 0.35
}
```

---

## 八、MCP 接口

### 8.1 MCP 工具列表

MCP 服务器提供的工具：

| 工具名称 | 功能 | 参数 |
|----------|------|------|
| `search` | 执行搜索 | `query`, `k`, `paths` |
| `scan_directory` | 扫描目录 | `path`, `recursive` |
| `query_knowledge` | 查询知识库 | `query`, `k` |
| `add_knowledge` | 添加知识 | `content`, `source` |

### 8.2 MCP 工具使用示例

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": {
      "query": "Python async",
      "k": 5
    }
  }
}
```

---

## 九、错误响应

### 9.1 错误格式

所有错误响应遵循以下格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### 9.2 错误代码

| 错误代码 | 说明 | HTTP 状态码 |
|----------|------|-------------|
| `INVALID_REQUEST` | 请求参数无效 | 400 |
| `UNAUTHORIZED` | 未授权 | 401 |
| `FORBIDDEN` | 禁止访问 | 403 |
| `NOT_FOUND` | 资源不存在 | 404 |
| `INTERNAL_ERROR` | 服务器内部错误 | 500 |
| `RATE_LIMIT` | 请求频率超限 | 429 |

---

## 十、使用示例

### 10.1 Python 示例

```python
import requests

# 搜索
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "Python 异步编程",
        "k": 10
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

print(response.json())
```

### 10.2 JavaScript 示例

```javascript
// 搜索
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    query: 'Python 异步编程',
    k: 10
  })
});

const data = await response.json();
console.log(data);
```

---

## 十一、相关文档

- [[README]] - 项目概述
- [[架构分析]] - 系统架构设计
- [[运行逻辑]] - 程序执行流程
- [[源码解析]] - 核心代码详解
- [[核心算法分析]] - 核心算法详解
