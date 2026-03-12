# OllamaPilot API 配置指南

> **目标**: 清晰说明哪些API需要配置，哪些是免费的，以及配置方法

---

## 一、配置总览

### 1.1 配置优先级

| 优先级 | 配置项 | 说明 |
|-------|--------|------|
| 🔴 **必须** | Ollama服务 | 本地运行，无需额外配置 |
| 🟡 **推荐** | SearXNG | 本地部署，无限额度 |
| 🟢 **可选** | GitHub Token | 代码搜索更稳定 |
| 🔵 **高级** | 其他搜索API | 提升搜索质量 |

### 1.2 配置位置

**所有API配置都统一放在 `.env` 文件中**

```bash
.env 文件位置: d:\self_test\project\trae\agent\OllamaPilot\.env
```

---

## 二、详细配置说明

### 2.1 【必须】Ollama 服务配置

```bash
# ============================================
# Ollama 服务配置（必须）
# ============================================
OLLAMA_BASE_URL=http://localhost:11434
```

**说明**:
- Ollama 必须在本地运行
- 无需API Key
- 国内完全可用

**检查命令**:
```bash
ollama list  # 查看已下载的模型
```

---

### 2.2 【推荐】SearXNG 配置

```bash
# ============================================
# SearXNG 配置（推荐本地部署）
# ============================================
SEARXNG_URL=http://localhost:8080
SEARXNG_AUTO_START=true
```

**说明**:
- **额度**: 无限（本地部署）
- **费用**: 完全免费
- **国内访问**: ✅ 完全可用
- **质量**: ⭐⭐⭐⭐⭐ 聚合多个搜索引擎

**部署步骤**:
```bash
# 1. 安装 Docker
# 2. 克隆仓库
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker

# 3. 启动服务
docker-compose up -d

# 4. 访问 http://localhost:8080
```

**不配置的影响**:
- 系统会自动使用 DuckDuckGo（免费，但质量略低）

---

### 2.3 【可选】GitHub API 配置

```bash
# ============================================
# GitHub API 配置（可选）
# ============================================
GITHUB_TOKEN=your_github_token_here
```

**说明**:
- **额度**: 500次/小时
- **费用**: 免费
- **国内访问**: ✅ 可用（偶尔不稳定）
- **用途**: 代码搜索

**申请步骤**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 和 `read:org` 权限
4. 复制生成的Token

**不配置的影响**:
- 代码搜索会自动降级到 Gitee（无限额度，国内更快）

---

### 2.4 【可选】Serper.dev 配置

```bash
# ============================================
# Serper.dev 配置（可选）
# ============================================
SERPER_API_KEY=your_serper_key_here
```

**说明**:
- **额度**: 2500次/月
- **费用**: 免费
- **国内访问**: ✅ 可用
- **用途**: Google搜索结果

**申请步骤**:
1. 访问 https://serper.dev
2. 注册账号
3. 在 Dashboard 获取 API Key

**不配置的影响**:
- 使用 SearXNG 或 DuckDuckGo（免费替代）

---

### 2.5 【可选】Bing Search API 配置

```bash
# ============================================
# Bing Search API 配置（可选）
# ============================================
BING_API_KEY=your_bing_key_here
```

**说明**:
- **额度**: 1000次/月
- **费用**: 免费
- **国内访问**: ✅ 可用
- **用途**: 必应搜索结果

**申请步骤**:
1. 访问 https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
2. 注册 Azure 账号
3. 创建 Bing Search v7 资源
4. 获取 API Key

**不配置的影响**:
- 使用 SearXNG 或 DuckDuckGo（免费替代）

---

### 2.6 【可选】Brave Search API 配置

```bash
# ============================================
# Brave Search API 配置（可选）
# ============================================
BRAVE_API_KEY=your_brave_key_here
```

**说明**:
- **额度**: 2000次/月
- **费用**: 免费
- **国内访问**: ✅ 可用
- **用途**: Brave搜索引擎结果

**申请步骤**:
1. 访问 https://brave.com/search/api/
2. 注册账号
3. 创建 API Key

**不配置的影响**:
- 使用 SearXNG 或 DuckDuckGo（免费替代）

---

### 2.7 【深度研究可选】Tavily API 配置

```bash
# ============================================
# Tavily API 配置（深度研究可选）
# ============================================
TAVILY_API_KEY=your_tavily_key_here
```

**说明**:
- **额度**: 1000次/月
- **费用**: 免费
- **国内访问**: ✅ 可用
- **用途**: 深度研究专用搜索

**申请步骤**:
1. 访问 https://tavily.com
2. 注册账号
3. 获取 API Key

**不配置的影响**:
- 深度研究会使用 SearXNG + DuckDuckGo 组合（免费替代）

---

### 2.8 【深度研究可选】OpenAI API 配置

```bash
# ============================================
# OpenAI API 配置（深度研究可选）
# ============================================
OPENAI_API_KEY=your_openai_key_here
```

**说明**:
- **费用**: 按量付费
- **国内访问**: ⚠️ 需要代理
- **用途**: GPT-4 模型 + OpenAI搜索

**申请步骤**:
1. 访问 https://platform.openai.com
2. 注册账号并绑定支付方式
3. 获取 API Key

**不配置的影响**:
- 深度研究会使用本地 Ollama 模型（免费，无需翻墙）

---

## 三、推荐配置组合

### 3.1 极简模式（零配置）

**需要配置**: 无

**可用功能**:
- ✅ 基础搜索（DuckDuckGo）
- ✅ 学术搜索（PubMed + arXiv）
- ✅ 百科搜索（百度百科）
- ✅ 代码搜索（Gitee）
- ✅ 知识库搜索

**搜索质量**: ⭐⭐⭐

---

### 3.2 标准模式（推荐）

**需要配置**:
```bash
# 仅配置 GitHub Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

**可用功能**:
- ✅ 所有极简模式功能
- ✅ 代码搜索（GitHub + Gitee）
- ✅ 更好的代码搜索结果

**搜索质量**: ⭐⭐⭐⭐

---

### 3.3 增强模式

**需要配置**:
```bash
# 1. 部署 SearXNG（本地Docker）
# 2. 配置 GitHub Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
SEARXNG_URL=http://localhost:8080
```

**可用功能**:
- ✅ 所有标准模式功能
- ✅ 聚合搜索（SearXNG）
- ✅ 更好的通用搜索质量

**搜索质量**: ⭐⭐⭐⭐⭐

---

### 3.4 完整模式

**需要配置**:
```bash
# 所有可选API
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
SEARXNG_URL=http://localhost:8080
SERPER_API_KEY=xxxxxxxx
BING_API_KEY=xxxxxxxx
BRAVE_API_KEY=xxxxxxxx
TAVILY_API_KEY=xxxxxxxx
```

**可用功能**:
- ✅ 所有增强模式功能
- ✅ 多引擎聚合
- ✅ 最佳搜索质量
- ✅ 深度研究增强

**搜索质量**: ⭐⭐⭐⭐⭐

---

## 四、配置检查清单

### 4.1 快速检查命令

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 检查 SearXNG 是否运行（如果已部署）
curl http://localhost:8080

# 检查 GitHub Token 是否有效
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

### 4.2 配置验证

启动 OllamaPilot 后，可以运行以下命令检查配置:

```
你: 检查搜索引擎

助手: 使用 check_search_engine_availability() 工具
```

输出示例:
```
🔍 搜索引擎可用性检查
==================================================
✅ 通用搜索: searxng, duckduckgo
✅ 学术搜索: pubmed, arxiv
✅ 代码搜索: github, gitee
✅ 百科搜索: baidu_baike, wikipedia

💡 提示: 使用 .env 文件配置API Key可解锁更多引擎
```

---

## 五、常见问题

### Q1: 不配置任何API能用吗？

**A**: 完全可以！系统会自动使用免费引擎:
- 通用搜索: DuckDuckGo
- 学术搜索: PubMed + arXiv
- 代码搜索: Gitee
- 百科搜索: 百度百科

### Q2: 哪些API是国内不能用的？

**A**: 以下API需要代理:
- OpenAI API (gpt-4o-search)
- Google Custom Search (直接访问)

**国内可用**:
- SearXNG (本地部署)
- DuckDuckGo
- PubMed
- GitHub
- Gitee
- 百度百科
- Serper.dev
- Bing Search
- Brave Search
- Tavily

### Q3: 配额用完了怎么办？

**A**: 系统会自动降级:
- GitHub 用完 → 自动使用 Gitee
- Serper 用完 → 自动使用 SearXNG/DuckDuckGo
- 所有API用完 → 使用免费引擎兜底

### Q4: 如何查看配额使用情况？

**A**: 运行命令:
```
你: 查看搜索配额

助手: 使用 get_search_quota_report() 工具
```

---

## 六、配置模板

### 6.1 复制即用模板

```bash
# ============================================
# OllamaPilot 配置模板
# 根据需求取消注释并填写
# ============================================

# ---- 基础配置（必须）----
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=qwen3.5:4b
EMBEDDING_MODEL=qwen3-embedding:0.6b

# ---- SearXNG（推荐）----
# SEARXNG_URL=http://localhost:8080

# ---- GitHub（可选）----
# GITHUB_TOKEN=your_token_here

# ---- 其他搜索API（可选）----
# SERPER_API_KEY=your_key_here
# BING_API_KEY=your_key_here
# BRAVE_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here

# ---- 配额管理 ----
ENABLE_QUOTA_MANAGEMENT=true
AUTO_FALLBACK=true
```

---

## 七、更新日志

- **2026-03-12**: 创建API配置指南
- 整理所有需要配置的API
- 明确免费和付费API
- 提供配置优先级建议

---

**文档版本**: v1.0  
**适用版本**: OllamaPilot v0.2.6+  
**最后更新**: 2026-03-12
