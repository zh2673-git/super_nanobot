# MiroFish 核心API文档

## 🎯 第一步：点出核心API模块

在深入了解API设计之前，让我们先认识它的核心"接口积木块"：

- **[图谱API (/api/graph)]：负责构建知识网络（像"图书馆建设"接口）**
- **[模拟API (/api/simulation)]：负责运行模拟（像"电影拍摄"接口）**
- **[报告API (/api/report)]：负责生成分析报告（像"影评写作"接口）**

---

## 🗺️ 第二步：用图构建API关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MiroFish API 架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                                    用户
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
           │ /api/graph  │  │ /api/simulation   │ /api/report │
           │  (图谱API)   │  │ (模拟API)    │  │ (报告API)   │
           └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                  │                 │                 │
    ┌─────────────┼─────────────┐   │          ┌────┴────────┐
    │             │             │   │          │             │
    ▼             ▼             ▼   ▼          ▼             ▼
┌────────┐  ┌────────┐   ┌──────────┐ ┌──────────┐    ┌──────────┐
│项目    │  │任务    │   │实体      │ │模拟      │    │报告      │
│管理    │  │查询    │   │读取      │ │管理      │    │生成      │
└────────┘  └────────┘   └──────────┘ └──────────┘    └──────────┘
    │             │             │          │
    └─────────────┼─────────────┴──────────┘
                  │
                  ▼
         ┌────────────────┐
         │   外部服务      │
         │ LLM / Zep / OASIS│
         └────────────────┘
```

---

## 📖 第三步：详细API文档

### 一、图谱构建 API (`/api/graph`)

#### 1.1 生成本体定义

**接口**: `POST /api/graph/ontology/generate`

**功能**: 上传文档，分析生成本体定义（实体类型、关系类型）

**请求**:
```javascript
// Content-Type: multipart/form-data
{
    files: File[],           // 上传的文件（PDF/MD/TXT），可多个
    simulation_requirement: string,  // 模拟需求描述（必填）
    project_name: string,    // 项目名称（可选）
    additional_context: string  // 额外说明（可选）
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "project_id": "proj_xxxxxxxxxxxx",
        "project_name": "我的项目",
        "ontology": {
            "entity_types": [
                {"name": "Student", "description": "...", "attributes": [...]},
                {"name": "Person", "description": "..."},  // 兜底类型
                {"name": "Organization", "description": "..."}  // 兜底类型
                // ... 共10个
            ],
            "edge_types": [
                {"name": "STUDIES_AT", "source_targets": [...]}
                // ... 6-10个
            ]
        },
        "analysis_summary": "本文讲述...",
        "files": [{"filename": "xxx.pdf", "size": 12345}],
        "total_text_length": 50000
    }
}
```

**示例**:
```bash
curl -X POST http://localhost:5001/api/graph/ontology/generate \
  -F "files=@document.pdf" \
  -F "simulation_requirement=预测这个事件会如何发酵" \
  -F "project_name=舆情分析项目"
```

---

#### 1.2 构建图谱

**接口**: `POST /api/graph/build`

**功能**: 根据project_id构建知识图谱（异步任务）

**请求**:
```javascript
{
    "project_id": "proj_xxxxxxxxxxxx",  // 必填，来自接口1
    "graph_name": "图谱名称",           // 可选
    "chunk_size": 500,                  // 可选，默认500
    "chunk_overlap": 50                 // 可选，默认50
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "project_id": "proj_xxxxxxxxxxxx",
        "task_id": "task_xxxxxxxxxxxx",
        "message": "图谱构建任务已启动，请通过 /task/{task_id} 查询进度"
    }
}
```

---

#### 1.3 查询任务状态

**接口**: `GET /api/graph/task/<task_id>`

**功能**: 查询图谱构建进度

**响应**:
```javascript
{
    "success": true,
    "data": {
        "task_id": "task_xxxxxxxxxxxx",
        "status": "processing",  // pending / processing / completed / failed
        "progress": 45,
        "message": "正在添加文本块...",
        "result": {
            "project_id": "proj_xxxxxxxxxxxx",
            "graph_id": "mirofish_xxx",
            "node_count": 150,
            "edge_count": 300
        }
    }
}
```

---

#### 1.4 获取图谱数据

**接口**: `GET /api/graph/data/<graph_id>`

**功能**: 获取构建好的图谱数据（节点、边）

**响应**:
```javascript
{
    "success": true,
    "data": {
        "graph_id": "mirofish_xxx",
        "node_count": 150,
        "edge_count": 300,
        "nodes": [
            {"uuid": "...", "type": "Student", "name": "张三", ...},
            ...
        ],
        "edges": [
            {"source": "...", "target": "...", "type": "STUDIES_AT"},
            ...
        ]
    }
}
```

---

#### 1.5 项目管理

| 接口 | 方法 | 功能 |
|-----|------|-----|
| `/api/graph/project/<project_id>` | GET | 获取项目详情 |
| `/api/graph/project/list` | GET | 列出所有项目 |
| `/api/graph/project/<project_id>` | DELETE | 删除项目 |
| `/api/graph/project/<project_id>/reset` | POST | 重置项目状态 |
| `/api/graph/delete/<graph_id>` | DELETE | 删除图谱 |

---

### 二、模拟运行 API (`/api/simulation`)

#### 2.1 创建模拟

**接口**: `POST /api/simulation/create`

**功能**: 创建新的模拟

**请求**:
```javascript
{
    "project_id": "proj_xxxxxxxxxxxx",  // 必填
    "graph_id": "mirofish_xxx",         // 可选，如不提供则从project获取
    "enable_twitter": true,             // 可选，默认true
    "enable_reddit": true              // 可选，默认true
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxxxxxxxxxxx",
        "project_id": "proj_xxxxxxxxxxxx",
        "graph_id": "mirofish_xxx",
        "status": "created",
        "enable_twitter": true,
        "enable_reddit": true,
        "created_at": "2024-12-01T10:00:00"
    }
}
```

---

#### 2.2 准备模拟环境

**接口**: `POST /api/simulation/prepare`

**功能**: 准备模拟环境（生成Agent人设、模拟配置），异步执行

**请求**:
```javascript
{
    "simulation_id": "sim_xxxxxxxxxxxx",  // 必填
    "entity_types": ["Student", "Professor"],  // 可选，指定实体类型
    "use_llm_for_profiles": true,           // 可选，是否用LLM生成人设
    "parallel_profile_count": 5,            // 可选，并行生成人设数量
    "force_regenerate": false               // 可选，强制重新生成
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxxxxxxxxxxx",
        "task_id": "task_xxxxxxxxxxxx",
        "status": "preparing",
        "message": "准备任务已启动，请通过 /api/simulation/prepare/status 查询进度"
    }
}
```

---

#### 2.3 查询准备状态

**接口**: `POST /api/simulation/prepare/status`

**功能**: 查询模拟准备进度

**请求**:
```javascript
{
    "task_id": "task_xxxxxxxxxxxx",    // 可选
    "simulation_id": "sim_xxxxxxxxxxxx"  // 可选
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "task_id": "task_xxxxxxxxxxxx",
        "status": "processing",  // not_started / processing / completed / ready
        "progress": 65,
        "message": "[2/4] 生成Agent人设: 30/93 - 正在生成张三的人设",
        "progress_detail": {
            "current_stage": "generating_profiles",
            "current_stage_name": "生成Agent人设",
            "stage_index": 2,
            "total_stages": 4,
            "current_item": 30,
            "total_items": 93
        }
    }
}
```

---

#### 2.4 获取图谱实体

**接口**: `GET /api/simulation/entities/<graph_id>`

**功能**: 获取图谱中的所有实体（已过滤）

**Query参数**:
- `entity_types`: 逗号分隔的实体类型列表（可选）
- `enrich`: 是否获取相关边信息（默认true）

**响应**:
```javascript
{
    "success": true,
    "data": {
        "entity_types": ["Student", "Professor", "University"],
        "filtered_count": 68,
        "entities": [
            {
                "uuid": "...",
                "name": "张三",
                "type": "Student",
                "attributes": {"major": "计算机"},
                "edges": [
                    {"target": "山东大学", "type": "STUDIES_AT"}
                ]
            },
            ...
        ]
    }
}
```

---

#### 2.5 获取Agent人设

**接口**: `GET /api/simulation/<simulation_id>/profiles`

**Query参数**:
- `platform`: 平台类型（reddit/twitter，默认reddit）

**响应**:
```javascript
{
    "success": true,
    "data": {
        "platform": "reddit",
        "count": 68,
        "profiles": [
            {
                "agent_name": "张三",
                "username": "student_zhang_sdu",
                "persona": "一名关注学术诚信的...",
                "stance": "support",
                ...
            },
            ...
        ]
    }
}
```

---

#### 2.6 获取模拟配置

**接口**: `GET /api/simulation/<simulation_id>/config`

**功能**: 获取LLM智能生成的模拟配置

**响应**:
```javascript
{
    "success": true,
    "data": {
        "time_config": {
            "total_simulation_hours": 24,
            "minutes_per_round": 30,
            "peak_hours": [9, 12, 18, 21],
            "trough_hours": [2, 3, 4, 5]
        },
        "agent_configs": [...],
        "event_config": {
            "initial_posts": [...],
            "hot_topics": [...]
        },
        "platform_config": {...},
        "generation_reasoning": "..."
    }
}
```

---

#### 2.7 启动模拟

**接口**: `POST /api/simulation/<simulation_id>/run`

**功能**: 启动OASIS模拟运行

**请求**:
```javascript
{
    "max_rounds": 48,    // 最大轮数（可选，默认根据配置）
    "platforms": ["twitter", "reddit"]  // 可选，默认两者都运行
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxxxxxxxxxxx",
        "status": "running",
        "current_round": 0,
        "total_rounds": 48,
        "message": "模拟已开始运行"
    }
}
```

---

#### 2.8 查询模拟状态

**接口**: `GET /api/simulation/<simulation_id>`

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxxxxxxxxxxx",
        "project_id": "proj_xxxxxxxxxxxx",
        "status": "running",  // created / preparing / ready / running / completed / stopped / failed
        "current_round": 25,
        "total_rounds": 48,
        "runner_status": "running",  // idle / running / paused / completed
        "entities_count": 68,
        "profiles_count": 68,
        "entity_types": ["Student", "Professor", ...],
        "created_at": "2024-12-01T10:00:00",
        "updated_at": "2024-12-01T12:30:00"
    }
}
```

---

#### 2.9 模拟历史列表

**接口**: `GET /api/simulation/history`

**Query参数**:
- `limit`: 返回数量限制（默认20）

**响应**:
```javascript
{
    "success": true,
    "data": [
        {
            "simulation_id": "sim_xxx",
            "project_id": "proj_xxx",
            "project_name": "武大舆情分析",
            "simulation_requirement": "如果武汉大学发布...",
            "status": "completed",
            "entities_count": 68,
            "current_round": 120,
            "total_rounds": 120,
            "report_id": "report_xxx",
            "created_date": "2024-12-10"
        },
        ...
    ],
    "count": 7
}
```

---

### 三、报告生成 API (`/api/report`)

#### 3.1 生成预测报告

**接口**: `POST /api/report/generate`

**功能**: 分析模拟结果，生成预测报告

**请求**:
```javascript
{
    "simulation_id": "sim_xxxxxxxxxxxx",  // 必填
    "requirement": "预测这个事件的发展趋势",  // 必填，你的问题
    "platforms": ["twitter", "reddit"]   // 可选，分析哪些平台
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "report_id": "report_xxxxxxxxxxxx",
        "simulation_id": "sim_xxxxxxxxxxxx",
        "requirement": "预测这个事件的发展趋势",
        "report": "## 预测报告\n\n### 事件概述\n...\n\n### 各方反应\n...\n\n### 趋势预测\n...",
        "created_at": "2024-12-01T15:00:00"
    }
}
```

---

#### 3.2 与模拟世界互动

**接口**: `POST /api/report/interview`

**功能**: 与模拟世界中的任意Agent对话

**请求**:
```javascript
{
    "simulation_id": "sim_xxxxxxxxxxxx",  // 必填
    "agent_name": "张三",                  // 必填，要对话的Agent名称
    "question": "你对这件事怎么看？",        // 必填，问题
    "platform": "reddit"                   // 可选，平台
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxx",
        "agent_name": "张三",
        "platform": "reddit",
        "question": "你对这件事怎么看？",
        "response": "作为一名关注学术诚信的研究生，我认为...",
        "timestamp": "2024-12-01T15:30:00"
    }
}
```

---

#### 3.3 批量采访Agent

**接口**: `POST /api/report/interview/batch`

**功能**: 批量采访多个Agent

**请求**:
```javascript
{
    "simulation_id": "sim_xxxxxxxxxxxx",
    "agent_names": ["张三", "李四", "王五"],
    "question": "你们对这件事的整体看法是什么？",
    "platform": "reddit"
}
```

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxx",
        "question": "你们对这件事的整体看法是什么？",
        "responses": [
            {"agent_name": "张三", "response": "..."},
            {"agent_name": "李四", "response": "..."},
            {"agent_name": "王五", "response": "..."}
        ]
    }
}
```

---

#### 3.4 获取报告

**接口**: `GET /api/report/<report_id>`

**响应**:
```javascript
{
    "success": true,
    "data": {
        "report_id": "report_xxx",
        "simulation_id": "sim_xxx",
        "requirement": "...",
        "report": "## 预测报告\n\n...",
        "created_at": "2024-12-01T15:00:00"
    }
}
```

---

#### 3.5 获取互动历史

**接口**: `GET /api/report/interview/history`

**Query参数**:
- `simulation_id`: 模拟ID

**响应**:
```javascript
{
    "success": true,
    "data": {
        "simulation_id": "sim_xxx",
        "interviews": [
            {
                "agent_name": "张三",
                "question": "你对这件事怎么看？",
                "response": "...",
                "timestamp": "2024-12-01T15:30:00"
            },
            ...
        ]
    }
}
```

---

## 📊 完整使用流程

```
1. 上传文档，生成本体
   POST /api/graph/ontology/generate
   → 返回 project_id

2. 构建图谱
   POST /api/graph/build
   → 返回 task_id
   GET /api/graph/task/{task_id} (轮询)
   → 图谱构建完成

3. 创建模拟
   POST /api/simulation/create
   → 返回 simulation_id

4. 准备模拟环境（生成人设+配置）
   POST /api/simulation/prepare
   → 返回 task_id
   POST /api/simulation/prepare/status (轮询)
   → 准备完成

5. 启动模拟
   POST /api/simulation/{simulation_id}/run
   → 开始运行

6. 查询模拟状态
   GET /api/simulation/{simulation_id} (轮询)
   → 模拟完成

7. 生成预测报告
   POST /api/report/generate
   → 返回报告

8. 深度互动
   POST /api/report/interview
   → 与Agent对话
```

---

## 🔧 错误响应格式

所有接口的错误响应格式统一：

```javascript
{
    "success": false,
    "error": "错误描述",
    "traceback": "详细堆栈信息（仅开发环境）"
}
```

常见HTTP状态码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

---

## 📚 相关文档

- [[github/MiroFish/README]] - 项目概述
- [[github/MiroFish/架构分析]] - 系统架构设计
- [[github/MiroFish/运行逻辑]] - 程序执行流程详解
- [[github/MiroFish/源码解析]] - 核心代码实现分析

---

*文档创建于2026-03-09*
