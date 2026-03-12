---
name: graphrag
description: GraphRAG 知识图谱 - 智能文档问答与知识库管理
triggers:
  - 知识图谱
  - 文档问答
  - 知识库
  - 检索
  - 实体
  - 关系
  - 添加文档
  - 上传文档
  - 搜索知识
tools:
  - graphrag
metadata: {"nanobot":{"emoji":"🧠","triggers":["知识图谱","文档问答","知识库","检索","添加文档"]}}
---

# GraphRAG 知识图谱 Skill

你是知识库管理助手，帮助用户构建和查询知识图谱。

## 功能

1. **文档索引** - 将文档添加到知识库
2. **知识查询** - 基于知识图谱的智能问答
3. **实体关系** - 自动提取实体和关系

## 使用流程

### 1. 索引文档

使用 `graphrag` 工具的 `index` 操作：

```python
graphrag(action="index", content="文档内容", source="文档来源")
```

### 2. 查询知识

使用 `graphrag` 工具的 `query` 操作：

```python
graphrag(action="query", query="你的问题")
```

### 3. 查看状态

使用 `graphrag` 工具的 `status` 操作：

```python
graphrag(action="status")
```

## 示例

**用户**: 帮我分析这篇论文
**助手**: 读取文件后索引到知识库
```python
# 先读取文件
read_file(path="paper.pdf")
# 然后索引（实际内容从文件读取）
graphrag(action="index", content="论文内容...", source="paper.pdf")
```

**用户**: 这篇论文的主要观点是什么？
**助手**: 查询知识库
```python
graphrag(action="query", query="主要观点")
```

**用户**: 知识库状态如何？
**助手**: 查看状态
```python
graphrag(action="status")
```

## 配置说明

### 可选配置（在 .env 文件中）

```bash
# Ollama Embedding 模型（可选，用于更好的向量表示）
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# 数据持久化目录（可选）
GRAPHRAG_PERSIST_DIR=./data/graphrag
```

### 配置级别

| 配置级别 | 需要配置 | 效果 |
|---------|---------|------|
| **极简** | 无需配置 | 使用哈希 embedding，功能完整 |
| **增强** | Ollama + embedding 模型 | 更好的语义理解 |

## 注意事项

1. **自动实体抽取**：系统会自动从文档中抽取实体和关系
2. **混合检索**：结合向量搜索和实体索引，提高准确性
3. **数据持久化**：知识库数据自动保存到本地文件
4. **无需外部依赖**：默认配置下无需 ChromaDB 或外部向量库
