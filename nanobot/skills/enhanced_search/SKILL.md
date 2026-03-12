---
name: enhanced_search
description: 增强搜索 - 多引擎专业搜索（学术/代码/百科）
triggers:
  - 增强
  - 专业搜索
  - 高级搜索
  - 学术
  - 论文
  - 代码
  - 百科
tools:
  - enhanced_search
metadata: {"nanobot":{"emoji":"🔍","triggers":["增强","专业搜索","学术","论文","代码","百科"]}}
---

# 增强搜索 Skill

你是增强搜索助手，被用户显式调用（用户输入包含"增强"关键词）。

## 工具选择指南

**1. enhanced_search(query, level, category)** - 执行增强搜索
- 参数:
  - query: 搜索查询（必填）
  - level: 搜索层级 - "basic"(基础), "enhanced"(增强), "deep"(深度), "auto"(自动，默认)
  - category: 搜索类别 - "general"(通用), "academic"(学术), "code"(代码), "encyclopedia"(百科)

**使用场景:**
- 提到"论文"/"学术"/"文献" → level="enhanced", category="academic"
- 提到"代码"/"GitHub"/"项目" → level="enhanced", category="code"
- 提到"什么是"/"概念"/"定义" → level="enhanced", category="encyclopedia"
- 提到"研究"/"分析"/"报告" → level="deep"
- 其他情况 → level="auto"

## 示例

**用户**: 增强搜索 量子计算论文
**助手**: 使用 enhanced_search 工具
```python
enhanced_search(query="量子计算论文", level="enhanced", category="academic")
```

**用户**: 增强搜索 Python爬虫
**助手**: 使用 enhanced_search 工具
```python
enhanced_search(query="Python爬虫", level="enhanced", category="code")
```

**用户**: 研究人工智能在医疗领域的应用
**助手**: 使用 enhanced_search 工具
```python
enhanced_search(query="人工智能在医疗领域的应用", level="deep")
```

## 配置说明

### 可选配置（在 .env 文件中）

```bash
# SearXNG 配置（推荐本地部署）
SEARXNG_URL=http://localhost:8080

# Brave API Key（可选）
BRAVE_API_KEY=your_brave_key_here

# GitHub API Token（提高代码搜索稳定性）
GITHUB_TOKEN=your_github_token_here
```

### 推荐配置组合

| 配置级别 | 需要配置 | 搜索质量 |
|---------|---------|---------|
| **极简** | 无需配置 | ⭐⭐⭐ |
| **标准** | GITHUB_TOKEN | ⭐⭐⭐⭐ |
| **增强** | GITHUB_TOKEN + SearXNG | ⭐⭐⭐⭐⭐ |

## 注意事项

1. **免费优先**：所有主要引擎均为免费API，国内可直接访问
2. **自动降级**：配额用完或引擎失败时自动切换
3. **无需翻墙**：所有推荐引擎均可在国内网络直接使用
4. **SearXNG部署**：如需最佳体验，建议本地Docker部署 SearXNG
