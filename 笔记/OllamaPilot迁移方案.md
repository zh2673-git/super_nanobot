---
created: 2026-03-12
updated: 2026-03-12
tags:
  - nanobot
  - OllamaPilot
  - migration
  - small-model
---

# OllamaPilot 功能迁移至 nanobot 完整方案

> 目标：将 OllamaPilot 的核心功能完整迁移到 nanobot，保持 nanobot 简洁架构的同时，实现小模型优化和增强功能

---

## 📋 目录

1. [项目背景与目标](#一项目背景与目标)
2. [架构对比分析](#二架构对比分析)
3. [迁移策略总览](#三迁移策略总览)
4. [详细迁移方案](#四详细迁移方案)
5. [实施路线图](#五实施路线图)
6. [技术细节](#六技术细节)
7. [风险与对策](#七风险与对策)

---

## 一、项目背景与目标

### 1.1 项目背景

**nanobot** 是一个极简主义的 AI Agent 框架：
- 仅 ~4,000 行代码
- 支持 8+ 聊天渠道（Telegram/Discord/飞书等）
- 自研 AgentLoop，性能优异
- 基于 Markdown 的 Skill 系统

**OllamaPilot** 是一个针对小模型优化的本地 Agent 框架：
- 基于 LangChain 1.0+ 构建
- 三层搜索架构（基础/增强/深度）
- GraphRAG 知识图谱
- 免费 API 智能降级
- 针对 4B 小模型优化

### 1.2 迁移目标

| 目标 | 说明 |
|------|------|
| **功能完整迁移** | 三层搜索、GraphRAG、免费 API 策略全部实现 |
| **保持简洁架构** | 不引入 LangChain 依赖，保持 nanobot 轻量级 |
| **小模型优化** | 4B 模型也能稳定执行复杂任务 |
| **即插即用** | Skill 复制即可使用，无需修改核心代码 |
| **性能不降** | 保持 nanobot 的高性能优势 |

### 1.3 项目约束与交付要求

#### 1.3.1 代码仓库
- **目标仓库**: `https://github.com/zh2673-git/super_nanobot`
- **版本管理**: 从 v0.0.1 开始迭代
- **提交规范**: 每个 Phase 完成后提交，通过测试后方可推送

#### 1.3.2 测试要求
- **自主测试**: 所有功能需自行测试通过后方可提交
- **测试环境**: 使用提供的 OllamaPilot 模型、API 和向量化知识库
- **测试内容**:
  - 本地知识库索引功能
  - 网络搜索功能（三层搜索）
  - 小模型（4B）稳定性和准确性
- **迭代流程**: 开发 → 测试 → 修复 → 提交，直至功能完整

#### 1.3.3 资源支持
用户提供以下测试资源：
- OllamaPilot 完整源码（参考实现）
- 已测试的向量化知识库
- 必要的 API 密钥（.env 文件）
- 推荐的模型配置（参考ollamapilot中用的项目）

**使用原则**: 基于提供的资源跑通功能，确保与 OllamaPilot 效果一致

#### 1.3.4 仓库管理规范

**排除文件**（不提交到仓库）:
```
# 笔记和文档
笔记/
*.md

# 环境配置
.env
.env.local
.env.*.local

# 发布相关
release/
dist/
build/
*.spec

# 测试数据（大文件）
*.bin
*.pt
*.pth
*.onnx
data/graphrag/*/embeddings/

# 临时文件
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
```

**提交内容**:
- 核心源代码
- 配置文件（不含敏感信息）
- 单元测试
- 必要的文档（README、安装说明）

---

## 二、架构对比分析

### 2.1 核心架构对比

```
nanobot 架构:
┌─────────────────────────────────────────┐
│  ChannelManager (多渠道支持)             │
├─────────────────────────────────────────┤
│  MessageBus (异步消息队列)               │
├─────────────────────────────────────────┤
│  AgentLoop (自研Agent核心)               │
│  ├── ContextBuilder (上下文构建)         │
│  ├── ToolRegistry (工具注册表)           │
│  └── SkillsLoader (Skill加载器)          │
├─────────────────────────────────────────┤
│  LiteLLMProvider (多模型支持)            │
└─────────────────────────────────────────┘

OllamaPilot 架构:
┌─────────────────────────────────────────┐
│  CLI / Python API                       │
├─────────────────────────────────────────┤
│  OllamaPilotAgent (LangChain包装)        │
│  ├── SkillSelectorMiddleware            │
│  ├── ToolLoggingMiddleware              │
│  ├── ToolRetryMiddleware                │
│  └── ToolCallLimitMiddleware            │
├─────────────────────────────────────────┤
│  SkillRegistry (Skill注册表)             │
├─────────────────────────────────────────┤
│  LangChain create_agent                 │
│  └── MemorySaver (内存记忆)              │
└─────────────────────────────────────────┘
```

### 2.2 性能对比

| 指标 | nanobot | OllamaPilot | 差距 |
|------|---------|-------------|------|
| 冷启动时间 | 0.5-1s | 2-4s | nanobot 快 3-4 倍 |
| 单次请求延迟 | +2-5ms | +20-50ms | nanobot 快 10 倍 |
| 内存占用(空闲) | 50MB | 150MB | nanobot 省 66% |
| 并发会话数 | 100+ | 10-20 | nanobot 高 5-10 倍 |
| 代码行数 | ~4,000 | ~8,000+ | nanobot 简洁 50% |

### 2.3 功能对比

| 功能 | nanobot | OllamaPilot | 迁移优先级 |
|------|---------|-------------|-----------|
| 多渠道支持 | ✅ 8+ | ❌ CLI only | 保持 |
| MCP 支持 | ✅ | ✅ | 保持 |
| 三层搜索 | ⚠️ 基础 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| GraphRAG | ❌ | ✅ | ⭐⭐⭐⭐ |
| 免费 API 策略 | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| 小模型优化 | ⚠️ 部分 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| Skill 系统 | ✅ Markdown | ✅ Python+MD | 增强 |
| 记忆系统 | ✅ 文件 | ✅ 内存 | 保持 |

---

## 三、迁移策略总览

### 3.1 核心策略：**Skill + Tool 混合模式**

```
┌─────────────────────────────────────────┐
│  Skill 层 (指导 Agent 如何使用)           │
│  ├── enhanced_search/SKILL.md           │
│  ├── graphrag/SKILL.md                  │
│  └── smart_router/SKILL.md              │
├─────────────────────────────────────────┤
│  Tool 层 (具体功能实现)                   │
│  ├── EnhancedSearchTool                 │
│  ├── GraphRAGTool                       │
│  └── SmartSearchRouter                  │
├─────────────────────────────────────────┤
│  nanobot 核心 (保持不变)                  │
│  ├── AgentLoop                          │
│  ├── ContextBuilder                     │
│  └── ToolRegistry                       │
└─────────────────────────────────────────┘
```

### 3.2 迁移原则

1. **零架构改动** - 不修改 nanobot 核心代码
2. **渐进式迁移** - 分阶段实施，每阶段可独立使用
3. **性能优先** - 保持 nanobot 的高性能优势
4. **小模型友好** - 所有功能针对 4B 模型优化

### 3.3 功能映射表

| OllamaPilot 功能 | nanobot 实现方式 | 文件位置 |
|-----------------|-----------------|---------|
| `init_ollama_model()` | `LiteLLMProvider` 配置增强 | `providers/litellm_provider.py` |
| `create_agent()` | 保持 `AgentLoop` | `agent/loop.py` |
| `SkillRegistry` | 复用 `SkillsLoader` | `agent/skills.py` |
| `SkillSelectorMiddleware` | 新增 `SkillRouter` | `agent/skill_router.py` |
| `ToolLoggingMiddleware` | 增强 `Tool` 基类 | `agent/tools/base.py` |
| `ToolRetryMiddleware` | 增强 `Tool` 基类 | `agent/tools/base.py` |
| `ToolCallLimitMiddleware` | 保持 `max_iterations` | `agent/loop.py` |
| `web_search` | 增强 `WebSearchTool` | `agent/tools/web.py` |
| `enhanced_search` | 新增 `EnhancedSearchTool` | `agent/tools/enhanced_search.py` |
| `deep_research` | 新增 `DeepResearchTool` | `agent/tools/deep_research.py` |
| `GraphRAGService` | 新增 `GraphRAGTool` | `agent/tools/graphrag.py` |
| `MemorySaver` | 保持文件持久化 | `agent/memory.py` |

---

## 四、详细迁移方案

### 4.1 Phase 1: 小模型优化配置

#### 4.1.1 目标
实现 OllamaPilot 的小模型优化参数配置

#### 4.1.2 实现方案

```python
# nanobot/providers/litellm_provider.py

class LiteLLMProvider:
    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        default_model: str = "anthropic/claude-opus-4-5",
        extra_headers: dict[str, str] | None = None,
        provider_name: str | None = None,
        small_model_mode: bool = False,  # 新增
        small_model_config: dict | None = None,  # 新增
    ):
        # ... 原有代码 ...
        self.small_model_mode = small_model_mode
        self.small_model_config = small_model_config or {}
        
    def _get_completion_params(self, model: str) -> dict:
        """获取模型调用参数，小模型优化"""
        params = {
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        if self.small_model_mode:
            # OllamaPilot 小模型优化配置
            params.update({
                "temperature": self.small_model_config.get("temperature", 0.7),
                "max_tokens": self.small_model_config.get("max_tokens", 2048),
                "top_p": self.small_model_config.get("top_p", 0.9),
                "top_k": self.small_model_config.get("top_k", 40),
                "repeat_penalty": self.small_model_config.get("repeat_penalty", 1.1),
                "num_ctx": self.small_model_config.get("num_ctx", 8192),
            })
            
        return params
```

#### 4.1.3 配置示例

```json
// ~/.nanobot/config.json
{
  "provider": {
    "name": "ollama",
    "apiBase": "http://localhost:11434",
    "defaultModel": "qwen2.5:4b",
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
}
```

#### 4.1.4 工作量
- **时间**: 1-2 天
- **文件修改**: 1 个
- **新增代码**: ~50 行

---

### 4.2 Phase 2: 工具基类增强

#### 4.2.1 目标
在 Tool 基类中添加日志和重试机制，替代 OllamaPilot 的中间件

#### 4.2.2 实现方案

```python
# nanobot/agent/tools/base.py

import asyncio
import functools
from abc import ABC, abstractmethod
from typing import Any
from loguru import logger


class Tool(ABC):
    """工具基类 - 增强版，支持日志和重试"""
    
    # 重试配置
    max_retries: int = 2
    retry_delay: float = 1.0
    
    # 日志配置
    enable_logging: bool = True
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        pass
    
    async def execute(self, **kwargs: Any) -> str:
        """执行工具，带日志和重试"""
        if self.enable_logging:
            logger.info(f"🔧 执行工具: {self.name}({self._format_args(kwargs)})")
        
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._execute(**kwargs)
                
                if self.enable_logging:
                    preview = result[:200] + "..." if len(result) > 200 else result
                    logger.info(f"   ✅ 结果: {preview}")
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(f"   ⚠️  第 {attempt + 1} 次失败: {e}，{self.retry_delay}秒后重试...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"   ❌ 工具执行失败 (已重试 {self.max_retries} 次): {e}")
        
        return f"Error: {last_error}"
    
    @abstractmethod
    async def _execute(self, **kwargs: Any) -> str:
        """实际执行逻辑，子类实现"""
        pass
    
    def _format_args(self, kwargs: dict) -> str:
        """格式化参数用于日志"""
        items = []
        for k, v in kwargs.items():
            v_str = str(v)
            if len(v_str) > 50:
                v_str = v_str[:50] + "..."
            items.append(f"{k}={v_str}")
        return ", ".join(items)
```

#### 4.2.3 工作量
- **时间**: 1 天
- **文件修改**: 1 个
- **新增代码**: ~60 行

---

### 4.3 Phase 3: Skill 智能路由

#### 4.3.1 目标
实现 OllamaPilot 的 Skill 自动选择功能

#### 4.3.2 实现方案

```python
# nanobot/agent/skill_router.py

import re
from pathlib import Path
from typing import Dict, List, Optional

from nanobot.agent.skills import SkillsLoader


class SkillRouter:
    """Skill 智能路由器 - 根据用户输入自动选择 Skill"""
    
    def __init__(self, skills_loader: SkillsLoader):
        self.skills_loader = skills_loader
        self._trigger_index: Dict[str, str] = {}  # trigger -> skill_name
        self._skill_triggers: Dict[str, List[str]] = {}  # skill_name -> triggers
        self._build_index()
    
    def _build_index(self):
        """构建触发词索引"""
        skills = self.skills_loader.list_skills(filter_unavailable=True)
        
        for skill_info in skills:
            name = skill_info["name"]
            meta = self.skills_loader.get_skill_metadata(name) or {}
            
            # 从 metadata 中提取触发词
            nanobot_meta = self._parse_nanobot_metadata(meta.get("metadata", ""))
            triggers = nanobot_meta.get("triggers", [])
            
            if triggers:
                self._skill_triggers[name] = triggers
                for trigger in triggers:
                    self._trigger_index[trigger.lower()] = name
    
    def select_skill(self, query: str) -> Optional[str]:
        """
        根据用户查询选择最合适的 Skill
        
        Args:
            query: 用户输入
            
        Returns:
            Skill 名称，如果没有匹配返回 None
        """
        query_lower = query.lower()
        
        # 1. 精确匹配
        for trigger, skill_name in self._trigger_index.items():
            if trigger in query_lower:
                return skill_name
        
        # 2. 关键词匹配（可选：使用更复杂的算法）
        # TODO: 可以添加语义匹配、分类器等
        
        return None
    
    def get_skill_prompt(self, skill_name: str) -> Optional[str]:
        """获取 Skill 的系统提示词"""
        content = self.skills_loader.load_skill(skill_name)
        if content:
            return self.skills_loader._strip_frontmatter(content)
        return None
    
    def _parse_nanobot_metadata(self, raw: str) -> dict:
        """解析 metadata JSON"""
        import json
        try:
            data = json.loads(raw)
            return data.get("nanobot", data.get("openclaw", {})) if isinstance(data, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}


# 在 ContextBuilder 中集成
# nanobot/agent/context.py

class ContextBuilder:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory = MemoryStore(workspace)
        self.skills = SkillsLoader(workspace)
        self.skill_router = SkillRouter(self.skills)  # 新增
    
    def build_messages(
        self,
        history: list[dict[str, Any]],
        current_message: str,
        skill_names: list[str] | None = None,
        auto_select_skill: bool = True,  # 新增
        **kwargs
    ) -> list[dict[str, Any]]:
        """构建消息列表，支持自动 Skill 选择"""
        
        # 自动选择 Skill
        if auto_select_skill and not skill_names:
            selected_skill = self.skill_router.select_skill(current_message)
            if selected_skill:
                skill_names = [selected_skill]
        
        # ... 原有代码 ...
```

#### 4.3.3 SKILL.md 格式扩展

```yaml
---
name: weather
description: 获取天气信息
triggers:
  - 天气
  - 温度
  - 下雨
  - 晴天
metadata: {"nanobot":{"emoji":"🌤️","triggers":["天气","温度","下雨"],"requires":{"bins":["curl"]}}}
---

# Weather

你是天气查询专家...
```

#### 4.3.4 工作量
- **时间**: 2 天
- **新增文件**: 1 个
- **修改文件**: 1 个
- **新增代码**: ~100 行

---

### 4.4 Phase 4: 三层搜索架构

#### 4.4.1 目标
实现 OllamaPilot 的三层搜索：基础搜索、增强搜索、深度研究

#### 4.4.2 架构设计

```
三层搜索架构:
┌─────────────────────────────────────────┐
│  第一层: WebSearchTool (基础)            │
│  ├── Brave API (已有)                   │
│  ├── SearXNG (新增)                     │
│  └── DuckDuckGo (新增)                  │
├─────────────────────────────────────────┤
│  第二层: EnhancedSearchTool (增强)       │
│  ├── 学术搜索: PubMed / arXiv           │
│  ├── 代码搜索: GitHub / Gitee           │
│  └── 百科搜索: 百度百科 / Wikipedia     │
├─────────────────────────────────────────┤
│  第三层: DeepResearchTool (深度研究)     │
│  ├── 需求分析                           │
│  ├── 多轮搜索                           │
│  ├── 结果整合                           │
│  └── 报告生成                           │
└─────────────────────────────────────────┘
```

#### 4.4.3 实现方案

```python
# nanobot/agent/tools/enhanced_search.py

import os
from typing import Any, List, Optional
from urllib.parse import quote

import httpx
from loguru import logger

from nanobot.agent.tools.base import Tool


class EnhancedSearchTool(Tool):
    """增强搜索工具 - 三层搜索架构"""
    
    name = "enhanced_search"
    description = """执行增强搜索，支持基础/增强/深度三个层级。
    
    使用场景:
    - 基础搜索: 日常查询、简单信息
    - 增强搜索: 专业领域（学术、代码、百科）
    - 深度研究: 复杂主题、需要多轮分析
    """
    
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询"
            },
            "level": {
                "type": "string",
                "enum": ["basic", "enhanced", "deep", "auto"],
                "description": "搜索层级: basic(基础), enhanced(增强), deep(深度), auto(自动)",
                "default": "auto"
            },
            "category": {
                "type": "string",
                "enum": ["general", "academic", "code", "encyclopedia"],
                "description": "搜索类别（用于增强搜索）",
                "default": "general"
            }
        },
        "required": ["query"]
    }
    
    def __init__(
        self,
        brave_api_key: str | None = None,
        searxng_url: str = "http://localhost:8080",
        proxy: str | None = None,
        auto_fallback: bool = True,
    ):
        self.brave_api_key = brave_api_key
        self.searxng_url = searxng_url
        self.proxy = proxy
        self.auto_fallback = auto_fallback
        
        # 搜索引擎配置
        self.engines = {
            "general": ["searxng", "brave", "duckduckgo"],
            "academic": ["pubmed", "arxiv"],
            "code": ["github", "gitee"],
            "encyclopedia": ["baidu_baike", "wikipedia"],
        }
    
    async def _execute(
        self,
        query: str,
        level: str = "auto",
        category: str = "general",
        **kwargs
    ) -> str:
        """执行搜索"""
        
        # 自动检测层级
        if level == "auto":
            level = self._detect_level(query)
            logger.info(f"自动检测搜索层级: {level}")
        
        # 根据层级执行不同搜索
        if level == "basic":
            return await self._basic_search(query)
        elif level == "enhanced":
            return await self._enhanced_search(query, category)
        else:  # deep
            return await self._deep_research(query)
    
    def _detect_level(self, query: str) -> str:
        """智能检测搜索层级"""
        query_lower = query.lower()
        
        # 深度研究关键词
        deep_keywords = [
            "研究", "分析", "报告", "综述", "现状", "趋势",
            "调研", "总结", "深度", "详细", "全面"
        ]
        
        # 增强搜索关键词
        enhanced_keywords = [
            "学术", "论文", "文献", "期刊",
            "代码", "github", "git", "仓库",
            "百科", "定义", "概念", "是什么"
        ]
        
        if any(kw in query_lower for kw in deep_keywords):
            return "deep"
        elif any(kw in query_lower for kw in enhanced_keywords):
            return "enhanced"
        return "basic"
    
    async def _basic_search(self, query: str) -> str:
        """基础搜索 - 使用通用搜索引擎"""
        results = []
        
        # 尝试 SearXNG
        try:
            result = await self._search_searxng(query)
            if result:
                results.append(("SearXNG", result))
        except Exception as e:
            logger.warning(f"SearXNG 搜索失败: {e}")
        
        # 如果失败且配置了 Brave，尝试 Brave
        if not results and self.brave_api_key:
            try:
                result = await self._search_brave(query)
                if result:
                    results.append(("Brave", result))
            except Exception as e:
                logger.warning(f"Brave 搜索失败: {e}")
        
        # 最后尝试 DuckDuckGo
        if not results:
            try:
                result = await self._search_duckduckgo(query)
                if result:
                    results.append(("DuckDuckGo", result))
            except Exception as e:
                logger.warning(f"DuckDuckGo 搜索失败: {e}")
        
        if not results:
            return "搜索失败，所有引擎都不可用"
        
        # 合并结果
        return self._merge_results(results, query)
    
    async def _enhanced_search(
        self,
        query: str,
        category: str
    ) -> str:
        """增强搜索 - 按类别使用专业引擎"""
        
        engines = self.engines.get(category, self.engines["general"])
        results = []
        
        for engine in engines:
            try:
                if engine == "pubmed":
                    result = await self._search_pubmed(query)
                elif engine == "arxiv":
                    result = await self._search_arxiv(query)
                elif engine == "github":
                    result = await self._search_github(query)
                elif engine == "gitee":
                    result = await self._search_gitee(query)
                elif engine == "baidu_baike":
                    result = await self._search_baidu_baike(query)
                elif engine == "wikipedia":
                    result = await self._search_wikipedia(query)
                else:
                    continue
                
                if result:
                    results.append((engine, result))
                    
            except Exception as e:
                logger.warning(f"{engine} 搜索失败: {e}")
        
        if not results:
            # 降级到基础搜索
            logger.info("增强搜索失败，降级到基础搜索")
            return await self._basic_search(query)
        
        return self._merge_results(results, query, enhanced=True)
    
    async def _deep_research(self, query: str) -> str:
        """深度研究 - 多轮搜索生成报告"""
        
        # 1. 需求分析 - 提取关键主题
        themes = self._extract_themes(query)
        logger.info(f"深度研究主题: {themes}")
        
        # 2. 多轮搜索
        all_results = []
        
        # 第一轮：基础搜索
        basic_result = await self._basic_search(query)
        all_results.append(("基础搜索", basic_result))
        
        # 第二轮：针对每个主题的增强搜索
        for theme in themes[:3]:  # 限制主题数量
            enhanced_result = await self._enhanced_search(
                theme,
                category=self._detect_category(theme)
            )
            all_results.append((f"主题: {theme}", enhanced_result))
        
        # 3. 整合结果
        return self._generate_research_report(query, themes, all_results)
    
    # 具体搜索引擎实现...
    async def _search_searxng(self, query: str) -> str:
        """SearXNG 搜索"""
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            response = await client.get(
                f"{self.searxng_url}/search",
                params={"q": query, "format": "json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                return ""
            
            lines = [f"SearXNG 搜索结果 ({len(results)} 条):"]
            for i, r in enumerate(results[:5], 1):
                lines.append(f"{i}. {r.get('title', '')}")
                lines.append(f"   {r.get('url', '')}")
                if snippet := r.get('content', ''):
                    lines.append(f"   {snippet[:150]}...")
            
            return "\n".join(lines)
    
    async def _search_brave(self, query: str) -> str:
        """Brave 搜索"""
        if not self.brave_api_key:
            return ""
        
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 5},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.brave_api_key
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("web", {}).get("results", [])
            if not results:
                return ""
            
            lines = [f"Brave 搜索结果 ({len(results)} 条):"]
            for i, r in enumerate(results[:5], 1):
                lines.append(f"{i}. {r.get('title', '')}")
                lines.append(f"   {r.get('url', '')}")
                if desc := r.get('description', ''):
                    lines.append(f"   {desc[:150]}...")
            
            return "\n".join(lines)
    
    async def _search_duckduckgo(self, query: str) -> str:
        """DuckDuckGo 搜索（无需 API Key）"""
        # 使用 DuckDuckGo 的 HTML 接口
        # 注意：实际实现可能需要使用 duckduckgo-search 库
        return "DuckDuckGo 搜索实现..."
    
    async def _search_pubmed(self, query: str) -> str:
        """PubMed 学术搜索"""
        # 使用 NCBI E-utilities API
        return "PubMed 搜索实现..."
    
    async def _search_arxiv(self, query: str) -> str:
        """arXiv 论文搜索"""
        # 使用 arXiv API
        return "arXiv 搜索实现..."
    
    async def _search_github(self, query: str) -> str:
        """GitHub 代码搜索"""
        token = os.environ.get("GITHUB_TOKEN")
        headers = {"Authorization": f"token {token}"} if token else {}
        
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            response = await client.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc"},
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                return ""
            
            lines = [f"GitHub 搜索结果 ({len(items)} 个仓库):"]
            for i, item in enumerate(items[:5], 1):
                lines.append(f"{i}. {item.get('full_name', '')} ⭐{item.get('stargazers_count', 0)}")
                lines.append(f"   {item.get('html_url', '')}")
                if desc := item.get('description', ''):
                    lines.append(f"   {desc[:150]}...")
            
            return "\n".join(lines)
    
    async def _search_gitee(self, query: str) -> str:
        """Gitee 代码搜索"""
        # Gitee API
        return "Gitee 搜索实现..."
    
    async def _search_baidu_baike(self, query: str) -> str:
        """百度百科搜索"""
        # 百度百科 API 或爬虫
        return "百度百科搜索实现..."
    
    async def _search_wikipedia(self, query: str) -> str:
        """Wikipedia 搜索"""
        # Wikipedia API
        return "Wikipedia 搜索实现..."
    
    def _detect_category(self, query: str) -> str:
        """检测搜索类别"""
        query_lower = query.lower()
        
        academic_keywords = ["论文", "文献", "期刊", "学术", "研究", "pubmed", "arxiv"]
        code_keywords = ["代码", "github", "git", "仓库", "repo", "library"]
        encyclopedia_keywords = ["百科", "定义", "概念", "是什么", "wiki"]
        
        if any(kw in query_lower for kw in academic_keywords):
            return "academic"
        elif any(kw in query_lower for kw in code_keywords):
            return "code"
        elif any(kw in query_lower for kw in encyclopedia_keywords):
            return "encyclopedia"
        return "general"
    
    def _extract_themes(self, query: str) -> List[str]:
        """从查询中提取研究主题"""
        # 简单实现：按标点分割
        # 实际可以使用 NLP 进行关键词提取
        import re
        themes = re.split(r'[，,、和与及；;]', query)
        return [t.strip() for t in themes if len(t.strip()) > 2]
    
    def _merge_results(
        self,
        results: List[tuple],
        query: str,
        enhanced: bool = False
    ) -> str:
        """合并多个搜索结果"""
        lines = [f"搜索: {query}", ""]
        
        for engine_name, result in results:
            lines.append(f"【{engine_name}】")
            lines.append(result)
            lines.append("")
        
        if enhanced:
            lines.append("---")
            lines.append("提示：这是增强搜索结果，综合了多个专业引擎。")
        
        return "\n".join(lines)
    
    def _generate_research_report(
        self,
        query: str,
        themes: List[str],
        results: List[tuple]
    ) -> str:
        """生成研究报告"""
        lines = [
            f"# 深度研究报告: {query}",
            "",
            f"## 研究主题",
            "",
        ]
        
        for i, theme in enumerate(themes, 1):
            lines.append(f"{i}. {theme}")
        
        lines.extend([
            "",
            "## 搜索结果汇总",
            "",
        ])
        
        for source, result in results:
            lines.append(f"### {source}")
            lines.append(result[:500] + "..." if len(result) > 500 else result)
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "**注意**: 这是自动生成的研究报告，建议进一步验证关键信息。",
        ])
        
        return "\n".join(lines)
```

#### 4.4.4 Skill 文档

```markdown
---
name: enhanced_search
description: 三层搜索架构 - 基础/增强/深度研究
triggers:
  - 搜索
  - 查
  - 找
  - 研究
  - 分析
  - 调研
metadata: {"nanobot":{"emoji":"🔍","triggers":["搜索","查","找","研究","分析"]}}
---

# Enhanced Search

你是搜索专家，帮助用户获取网络信息。

## 搜索层级

1. **基础搜索** - 日常查询
   - 触发词: "搜索 xxx"
   - 引擎: SearXNG / Brave / DuckDuckGo

2. **增强搜索** - 专业领域
   - 触发词: "学术搜索 xxx", "代码搜索 xxx"
   - 学术: PubMed, arXiv
   - 代码: GitHub, Gitee
   - 百科: 百度百科, Wikipedia

3. **深度研究** - 复杂主题
   - 触发词: "研究 xxx", "分析 xxx"
   - 自动多轮搜索
   - 生成研究报告

## 使用示例

```
用户: "搜索 Python 教程"
→ 使用基础搜索

用户: "学术搜索 量子计算"
→ 使用增强搜索 (学术引擎)

用户: "研究人工智能在医疗领域的应用"
→ 使用深度研究
```

## 工具调用

- `enhanced_search` - 执行搜索
  - query: 搜索查询
  - level: "basic" | "enhanced" | "deep" | "auto"
  - category: "general" | "academic" | "code" | "encyclopedia"
```

#### 4.4.5 工作量
- **时间**: 4-5 天
- **新增文件**: 1 个主文件 + 1 个 Skill
- **新增代码**: ~500 行

---

### 4.5 Phase 5: GraphRAG 知识图谱

#### 4.5.1 目标
实现 OllamaPilot 的 GraphRAG 功能

#### 4.5.2 架构设计

```
GraphRAG 架构:
┌─────────────────────────────────────────┐
│  GraphRAGTool (入口)                     │
├─────────────────────────────────────────┤
│  GraphRAGService (核心服务)              │
│  ├── 向量存储 (Chroma/Simple)            │
│  ├── 实体索引 (内存 Dict)                 │
│  └── 关系索引 (内存 List)                 │
├─────────────────────────────────────────┤
│  HybridEntityExtractor (实体抽取)        │
│  ├── 词典匹配                            │
│  ├── 规则匹配                            │
│  └── LLM 抽取                            │
├─────────────────────────────────────────┤
│  KnowledgeBaseManager (知识库管理)       │
│  ├── 文档扫描                            │
│  ├── 分块处理                            │
│  └── 索引构建                            │
└─────────────────────────────────────────┘
```

#### 4.5.3 实现方案

```python
# nanobot/agent/tools/graphrag.py

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

import httpx
from loguru import logger

from nanobot.agent.tools.base import Tool


@dataclass
class Entity:
    """实体"""
    name: str
    type: str
    positions: List[Tuple[int, int]] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "positions": self.positions
        }


@dataclass
class Relation:
    """关系"""
    source: str
    target: str
    type: str
    evidence: str = ""
    
    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "evidence": self.evidence
        }


@dataclass
class Document:
    """文档"""
    id: str
    content: str
    source: str
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    embedding: Optional[List[float]] = None


class SimpleVectorStore:
    """简单向量存储 - 用于小模型场景"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.documents: Dict[str, Document] = {}
        
    def add(self, doc_id: str, content: str, embedding: List[float], metadata: dict):
        """添加文档"""
        self.documents[doc_id] = Document(
            id=doc_id,
            content=content,
            source=metadata.get("source", ""),
            embedding=embedding
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Document]:
        """向量搜索 - 使用余弦相似度"""
        import numpy as np
        
        if not self.documents:
            return []
        
        query_vec = np.array(query_embedding)
        scores = []
        
        for doc in self.documents.values():
            if doc.embedding:
                doc_vec = np.array(doc.embedding)
                # 余弦相似度
                similarity = np.dot(query_vec, doc_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
                )
                scores.append((doc, similarity))
        
        # 按相似度排序
        scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scores[:top_k]]


class HybridEntityExtractor:
    """混合实体抽取器"""
    
    def __init__(self):
        # 内置词典
        self.dictionaries = {
            "PERSON": ["张三", "李四", "王五"],  # 可扩展
            "ORG": ["Google", "Microsoft", "Apple"],
            "TECH": ["Python", "JavaScript", "AI", "机器学习"],
        }
        
        # 规则模式
        self.patterns = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "URL": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
            "PHONE": r"\b1[3-9]\d{9}\b",
        }
    
    def extract(self, text: str, use_llm: bool = False) -> Tuple[List[Entity], List[Relation]]:
        """抽取实体和关系"""
        entities = []
        relations = []
        
        # 1. 词典匹配
        dict_entities = self._extract_by_dictionary(text)
        entities.extend(dict_entities)
        
        # 2. 规则匹配
        rule_entities = self._extract_by_rules(text)
        entities.extend(rule_entities)
        
        # 3. LLM 抽取 (可选，小模型场景可禁用)
        if use_llm:
            llm_entities, llm_relations = self._extract_by_llm(text)
            entities.extend(llm_entities)
            relations.extend(llm_relations)
        
        # 4. 推断关系
        inferred_relations = self._infer_relations(entities, text)
        relations.extend(inferred_relations)
        
        # 去重
        entities = self._deduplicate_entities(entities)
        relations = self._deduplicate_relations(relations)
        
        return entities, relations
    
    def _extract_by_dictionary(self, text: str) -> List[Entity]:
        """基于词典的实体抽取"""
        entities = []
        for entity_type, terms in self.dictionaries.items():
            for term in terms:
                if term in text:
                    # 找到所有位置
                    positions = []
                    start = 0
                    while True:
                        idx = text.find(term, start)
                        if idx == -1:
                            break
                        positions.append((idx, idx + len(term)))
                        start = idx + 1
                    
                    if positions:
                        entities.append(Entity(
                            name=term,
                            type=entity_type,
                            positions=positions
                        ))
        return entities
    
    def _extract_by_rules(self, text: str) -> List[Entity]:
        """基于规则的实体抽取"""
        import re
        entities = []
        
        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    name=match.group(),
                    type=entity_type,
                    positions=[(match.start(), match.end())]
                ))
        
        return entities
    
    def _extract_by_llm(self, text: str) -> Tuple[List[Entity], List[Relation]]:
        """基于 LLM 的实体抽取"""
        # 小模型场景可简化或禁用
        return [], []
    
    def _infer_relations(self, entities: List[Entity], text: str) -> List[Relation]:
        """推断实体间关系"""
        relations = []
        
        # 简单规则：同一句话中的实体可能存在关系
        sentences = text.split("。")
        for sent in sentences:
            sent_entities = [e for e in entities if e.name in sent]
            if len(sent_entities) >= 2:
                # 创建关系
                for i in range(len(sent_entities)):
                    for j in range(i + 1, len(sent_entities)):
                        relations.append(Relation(
                            source=sent_entities[i].name,
                            target=sent_entities[j].name,
                            type="相关",
                            evidence=sent[:100]
                        ))
        
        return relations
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """实体去重"""
        seen = set()
        result = []
        for e in entities:
            key = (e.name, e.type)
            if key not in seen:
                seen.add(key)
                result.append(e)
        return result
    
    def _deduplicate_relations(self, relations: List[Relation]) -> List[Relation]:
        """关系去重"""
        seen = set()
        result = []
        for r in relations:
            key = (r.source, r.target, r.type)
            if key not in seen:
                seen.add(key)
                result.append(r)
        return result


class GraphRAGService:
    """GraphRAG 核心服务"""
    
    def __init__(self, workspace: Path, collection_name: str = "default"):
        self.workspace = workspace
        self.collection_name = collection_name
        self.vector_store = SimpleVectorStore(collection_name)
        self.entity_index: Dict[str, Dict] = {}  # entity_name -> {type, doc_ids}
        self.relations: List[Relation] = []
        
        # 数据目录
        self.data_dir = workspace / "graphrag" / collection_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载已有数据
        self._load_data()
    
    async def add_document(self, content: str, source: str, doc_id: str | None = None):
        """添加文档到知识库"""
        if not doc_id:
            doc_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # 1. 生成 embedding (简化版，实际应调用 embedding 模型)
        embedding = await self._get_embedding(content)
        
        # 2. 抽取实体和关系
        extractor = HybridEntityExtractor()
        entities, relations = extractor.extract(content, use_llm=False)
        
        # 3. 创建文档
        doc = Document(
            id=doc_id,
            content=content,
            source=source,
            entities=entities,
            relations=relations
        )
        
        # 4. 存储到向量库
        self.vector_store.add(doc_id, content, embedding, {"source": source})
        
        # 5. 更新实体索引
        for entity in entities:
            if entity.name not in self.entity_index:
                self.entity_index[entity.name] = {
                    "type": entity.type,
                    "doc_ids": set()
                }
            self.entity_index[entity.name]["doc_ids"].add(doc_id)
        
        # 6. 更新关系
        self.relations.extend(relations)
        
        # 7. 持久化
        self._save_data()
        
        logger.info(f"添加文档: {doc_id}, 实体: {len(entities)}, 关系: {len(relations)}")
        
        return doc_id
    
    async def query(self, query: str, top_k: int = 5) -> str:
        """查询知识库"""
        # 1. 获取查询的 embedding
        query_embedding = await self._get_embedding(query)
        
        # 2. 向量搜索
        vector_results = self.vector_store.search(query_embedding, top_k)
        
        # 3. 实体搜索
        extractor = HybridEntityExtractor()
        query_entities, _ = extractor.extract(query, use_llm=False)
        
        entity_doc_ids = set()
        for entity in query_entities:
            if entity.name in self.entity_index:
                entity_doc_ids.update(self.entity_index[entity.name]["doc_ids"])
        
        # 4. 合并结果
        all_doc_ids = set()
        for doc in vector_results:
            all_doc_ids.add(doc.id)
        all_doc_ids.update(entity_doc_ids)
        
        # 5. 获取完整文档
        results = []
        for doc_id in list(all_doc_ids)[:top_k]:
            if doc_id in self.vector_store.documents:
                results.append(self.vector_store.documents[doc_id])
        
        # 6. 格式化输出
        return self._format_results(query, results, query_entities)
    
    async def _get_embedding(self, text: str) -> List[float]:
        """获取文本 embedding"""
        # 简化实现：使用简单的哈希向量
        # 实际应调用 Ollama embedding 模型
        import numpy as np
        
        # 生成确定性随机向量
        np.random.seed(int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32))
        return np.random.randn(384).tolist()  # 384维向量
    
    def _format_results(
        self,
        query: str,
        results: List[Document],
        query_entities: List[Entity]
    ) -> str:
        """格式化搜索结果"""
        lines = [
            f"GraphRAG 查询: {query}",
            "",
            f"查询实体: {[e.name for e in query_entities]}",
            "",
            f"找到 {len(results)} 个相关文档:",
            "",
        ]
        
        for i, doc in enumerate(results, 1):
            lines.append(f"--- 文档 {i} ---")
            lines.append(f"来源: {doc.source}")
            lines.append(f"内容: {doc.content[:300]}...")
            if doc.entities:
                lines.append(f"实体: {[e.name for e in doc.entities[:5]]}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _save_data(self):
        """持久化数据"""
        data = {
            "entity_index": {
                k: {**v, "doc_ids": list(v["doc_ids"])}
                for k, v in self.entity_index.items()
            },
            "relations": [r.to_dict() for r in self.relations],
        }
        
        with open(self.data_dir / "index.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """加载数据"""
        index_file = self.data_dir / "index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.entity_index = {
                k: {**v, "doc_ids": set(v["doc_ids"])}
                for k, v in data.get("entity_index", {}).items()
            }
            self.relations = [
                Relation(**r) for r in data.get("relations", [])
            ]


class GraphRAGTool(Tool):
    """GraphRAG 知识图谱工具"""
    
    name = "graphrag"
    description = """GraphRAG 知识图谱工具 - 智能文档问答。
    
    功能:
    - 文档索引: 将文档添加到知识库
    - 知识查询: 基于知识图谱的问答
    
    适用于需要深度理解文档内容的场景。
    """
    
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["index", "query", "status"],
                "description": "操作类型: index(索引文档), query(查询), status(状态)"
            },
            "content": {
                "type": "string",
                "description": "文档内容 (index 时使用)"
            },
            "source": {
                "type": "string",
                "description": "文档来源 (index 时使用)"
            },
            "query": {
                "type": "string",
                "description": "查询内容 (query 时使用)"
            },
            "collection": {
                "type": "string",
                "description": "知识库名称",
                "default": "default"
            }
        },
        "required": ["action"]
    }
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.services: Dict[str, GraphRAGService] = {}
    
    def _get_service(self, collection: str) -> GraphRAGService:
        """获取或创建服务"""
        if collection not in self.services:
            self.services[collection] = GraphRAGService(self.workspace, collection)
        return self.services[collection]
    
    async def _execute(self, action: str, **kwargs) -> str:
        """执行操作"""
        collection = kwargs.get("collection", "default")
        service = self._get_service(collection)
        
        if action == "index":
            content = kwargs.get("content", "")
            source = kwargs.get("source", "unknown")
            doc_id = await service.add_document(content, source)
            return f"文档已索引: {doc_id} (集合: {collection})"
        
        elif action == "query":
            query = kwargs.get("query", "")
            if not query:
                return "错误: 请提供查询内容"
            return await service.query(query)
        
        elif action == "status":
            return (
                f"GraphRAG 状态 (集合: {collection}):\n"
                f"- 文档数: {len(service.vector_store.documents)}\n"
                f"- 实体数: {len(service.entity_index)}\n"
                f"- 关系数: {len(service.relations)}"
            )
        
        return f"未知操作: {action}"
```

#### 4.5.4 Skill 文档

```markdown
---
name: graphrag
description: GraphRAG 知识图谱 - 智能文档问答
triggers:
  - 知识库
  - 文档分析
  - 智能问答
  - 图谱
metadata: {"nanobot":{"emoji":"🧠","triggers":["知识库","文档分析","图谱"]}}
---

# GraphRAG

你是知识图谱专家，帮助用户构建和查询知识库。

## 功能

1. **文档索引** - 将文档添加到知识库
2. **知识查询** - 基于知识图谱的智能问答
3. **实体关系** - 自动提取实体和关系

## 使用流程

1. 索引文档
   ```
   graphrag(action="index", content="文档内容", source="文档来源")
   ```

2. 查询知识
   ```
   graphrag(action="query", query="你的问题")
   ```

3. 查看状态
   ```
   graphrag(action="status")
   ```

## 示例

```
用户: "帮我分析这篇论文"
→ 读取文件 → graphrag(action="index", content=论文内容, source="paper.pdf")

用户: "这篇论文的主要观点是什么？"
→ graphrag(action="query", query="主要观点")
```
```

#### 4.5.5 工作量
- **时间**: 5-7 天
- **新增文件**: 1 个主文件 + 1 个 Skill
- **新增代码**: ~600 行

---

### 4.6 Phase 6: SearXNG 自动部署

#### 4.6.1 目标
实现 SearXNG 的自动部署脚本

#### 4.6.2 实现方案

```python
# nanobot/utils/searxng_deploy.py

import subprocess
import time
from pathlib import Path

from loguru import logger


class SearXNGDeployer:
    """SearXNG 自动部署器"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.container_name = "nanobot-searxng"
    
    def check_docker(self) -> bool:
        """检查 Docker 是否安装"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def is_running(self) -> bool:
        """检查 SearXNG 是否已运行"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.container_name in result.stdout
        except Exception:
            return False
    
    def deploy(self) -> bool:
        """部署 SearXNG"""
        if not self.check_docker():
            logger.error("Docker 未安装，请先安装 Docker")
            return False
        
        if self.is_running():
            logger.info(f"SearXNG 已运行在端口 {self.port}")
            return True
        
        logger.info("正在部署 SearXNG...")
        
        try:
            # 拉取镜像
            subprocess.run(
                ["docker", "pull", "searxng/searxng"],
                check=True,
                timeout=120
            )
            
            # 启动容器
            subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", self.container_name,
                    "--restart", "unless-stopped",
                    "-p", f"{self.port}:8080",
                    "-v", f"{self._get_config_dir()}:/etc/searxng",
                    "searxng/searxng"
                ],
                check=True,
                timeout=30
            )
            
            # 等待服务就绪
            logger.info("等待 SearXNG 启动...")
            time.sleep(5)
            
            if self.is_running():
                logger.info(f"SearXNG 部署成功: http://localhost:{self.port}")
                return True
            else:
                logger.error("SearXNG 启动失败")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"部署失败: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("部署超时")
            return False
    
    def stop(self) -> bool:
        """停止 SearXNG"""
        try:
            subprocess.run(
                ["docker", "stop", self.container_name],
                check=True,
                timeout=10
            )
            return True
        except Exception as e:
            logger.error(f"停止失败: {e}")
            return False
    
    def _get_config_dir(self) -> str:
        """获取配置目录"""
        config_dir = Path.home() / ".nanobot" / "searxng"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir)


def ensure_searxng(port: int = 8080) -> str | None:
    """确保 SearXNG 可用，返回 URL"""
    deployer = SearXNGDeployer(port)
    
    if deployer.deploy():
        return f"http://localhost:{port}"
    return None
```

#### 4.6.3 工作量
- **时间**: 1-2 天
- **新增文件**: 1 个
- **新增代码**: ~150 行

---

## 五、实施路线图

### 5.1 时间规划与里程碑

```
Week 1: 基础优化 (v0.0.1)
├── Day 1-2: Phase 1 - 小模型优化配置
├── Day 3:   Phase 2 - 工具基类增强
└── Day 4-5: Phase 3 - Skill 智能路由
    └── 里程碑: v0.0.1 发布 - 基础优化完成
    └── 提交: https://github.com/zh2673-git/super_nanobot v0.0.1

Week 2: 核心功能 (v0.0.2)
├── Day 1-2: Phase 4 - 三层搜索架构 (基础+增强)
├── Day 3:   Phase 4 - 三层搜索架构 (深度研究)
└── Day 4-5: 测试 + 修复
    └── 里程碑: v0.0.2 发布 - 三层搜索完成
    └── 提交: https://github.com/zh2673-git/super_nanobot v0.0.2

Week 3: 高级功能 (v0.0.3)
├── Day 1-3: Phase 5 - GraphRAG 完整实现
├── Day 4:   Phase 6 - SearXNG 自动部署
└── Day 5:   集成测试 + Bug 修复
    └── 里程碑: v0.0.3 发布 - GraphRAG 完成
    └── 提交: https://github.com/zh2673-git/super_nanobot v0.0.3

Week 4: 完善与发布 (v0.1.0)
├── Day 1-2: 性能优化 + 完整测试
├── Day 3:   文档编写 + README
└── Day 4-5: 最终测试 + v0.1.0 发布
    └── 里程碑: v0.1.0 发布 - 完整功能版
    └── 提交: https://github.com/zh2673-git/super_nanobot v0.1.0
```

### 5.2 版本发布计划

| 版本 | 功能范围 | 测试要求 | 预计时间 |
|------|---------|---------|---------|
| **v0.0.1** | 小模型优化 + 工具增强 + Skill路由 | 基础功能可用 | Week 1 结束 |
| **v0.0.2** | 三层搜索完整实现 | 搜索功能与OllamaPilot效果一致 | Week 2 结束 |
| **v0.0.3** | GraphRAG + SearXNG部署 | 知识库索引和查询正常 | Week 3 结束 |
| **v0.1.0** | 完整功能 + 性能优化 | 所有测试通过 | Week 4 结束 |

### 5.3 测试与提交流程

```
每个 Phase 的开发流程:

1. 开发实现
   └── 编写代码
   └── 本地初步测试

2. 功能测试 (使用提供的资源)
   └── 配置 .env (本地使用，不提交)
   └── 使用提供的向量化知识库测试
   └── 使用 qwen2.5:4b 等模型测试
   └── 验证与 OllamaPilot 效果一致性

3. 问题修复
   └── 记录测试结果
   └── 修复发现的问题
   └── 重新测试直至通过

4. 代码提交
   └── 更新 .gitignore (排除笔记、.env、release)
   └── 清理临时文件
   └── 提交到 super_nanobot 仓库
   └── 打版本标签 (v0.0.x)

5. 版本发布
   └── 编写 Release Notes
   └── 记录已知问题和限制
```

### 5.4 文件变更清单

#### 修改文件

| 文件 | 修改内容 | 工作量 | 版本 |
|------|---------|--------|------|
| `providers/litellm_provider.py` | 添加小模型优化配置 | 1-2 天 | v0.0.1 |
| `agent/tools/base.py` | 添加日志和重试机制 | 1 天 | v0.0.1 |
| `agent/context.py` | 集成 SkillRouter | 1 天 | v0.0.1 |
| `agent/loop.py` | 可选：调整迭代限制 | 0.5 天 | v0.0.1 |

#### 新增文件

| 文件 | 功能 | 工作量 | 版本 |
|------|------|--------|------|
| `agent/skill_router.py` | Skill 智能路由 | 2 天 | v0.0.1 |
| `agent/tools/enhanced_search.py` | 三层搜索 | 4-5 天 | v0.0.2 |
| `agent/tools/graphrag.py` | GraphRAG | 5-7 天 | v0.0.3 |
| `utils/searxng_deploy.py` | SearXNG 部署 | 1-2 天 | v0.0.3 |
| `skills/enhanced_search/SKILL.md` | 搜索 Skill | 0.5 天 | v0.0.2 |
| `skills/graphrag/SKILL.md` | GraphRAG Skill | 0.5 天 | v0.0.3 |

#### 仓库配置文件

```
# .gitignore (新增/更新)
# 排除列表
笔记/
*.md
.env
.env.local
.env.*.local
release/
dist/
build/
*.spec
*.bin
*.pt
*.pth
*.onnx
data/graphrag/*/embeddings/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/

# 允许提交
!README.md
!LICENSE
!requirements.txt
!pyproject.toml
```

### 5.3 依赖项

```
# requirements.txt 新增

# 增强搜索
httpx>=0.27.0

# GraphRAG (可选，使用简化版可不需要)
# numpy>=1.24.0
# chromadb>=0.4.0  # 如需使用 Chroma 向量库

# SearXNG 部署
# docker 命令行工具 (系统依赖)
```

---

## 六、技术细节

### 6.1 小模型优化要点

```python
# 关键配置参数
{
    "temperature": 0.7,      # 控制随机性，小模型建议 0.5-0.8
    "top_p": 0.9,            # 核采样，过滤低概率 token
    "top_k": 40,             # TopK 采样，减少计算量
    "repeat_penalty": 1.1,   # 重复惩罚，防止循环
    "num_ctx": 8192,         # 上下文窗口，平衡内存和性能
    "max_tokens": 2048,      # 最大生成长度，防止过长输出
}
```

### 6.2 工具调用优化

```python
# 小模型友好的工具描述
tool_description = """
执行增强搜索，支持三个层级：
- basic: 基础搜索，适合日常查询
- enhanced: 增强搜索，适合专业领域
- deep: 深度研究，适合复杂主题

参数：
- query: 搜索查询（必填）
- level: 搜索层级，默认 auto 自动选择
- category: 搜索类别（enhanced 时使用）
"""
```

### 6.3 错误处理策略

```python
# 小模型容易出错，需要健壮的错误处理
async def execute_with_fallback(**kwargs):
    try:
        return await primary_execute(**kwargs)
    except Exception as e:
        logger.warning(f"主执行失败: {e}")
        try:
            return await fallback_execute(**kwargs)
        except Exception as e2:
            return f"执行失败: {e2}"
```

---

## 七、风险与对策

### 7.1 技术风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 小模型调用工具失败率高 | 功能不可用 | 添加重试机制，简化工具描述 |
| GraphRAG 性能问题 | 响应慢 | 使用简化版向量存储，延迟加载 |
| 免费 API 限制 | 功能不稳定 | 实现自动降级，多引擎备份 |
| 依赖冲突 | 安装失败 | 使用可选依赖，隔离功能模块 |

### 7.2 项目风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 开发周期延长 | 延期 | 分阶段交付，每阶段可独立使用 |
| 代码复杂度增加 | 维护难 | 保持模块化，每个功能独立 |
| 性能下降 | 体验差 | 持续性能测试，及时优化 |

### 7.3 测试策略

```
单元测试:
├── 每个 Tool 独立测试
├── SkillRouter 匹配测试
└── 小模型参数验证

集成测试:
├── 端到端搜索流程
├── GraphRAG 索引+查询
└── 多轮对话测试

性能测试:
├── 冷启动时间
├── 内存占用
└── 并发能力
```

---

## 八、总结

### 8.1 迁移收益

| 方面 | 收益 |
|------|------|
| **功能** | 获得三层搜索、GraphRAG、免费 API 等核心功能 |
| **性能** | 保持 nanobot 的高性能，优于 OllamaPilot 3-10 倍 |
| **架构** | 保持简洁，代码量增加 < 2000 行 |
| **兼容性** | 支持更多模型（通过 LiteLLM） |
| **渠道** | 保留 8+ 聊天渠道支持 |

### 8.2 关键成功因素

1. **保持架构简洁** - 不引入 LangChain 依赖
2. **分阶段交付** - 每个 Phase 可独立使用
3. **小模型优先** - 所有功能针对 4B 模型优化
4. **性能监控** - 持续测试确保不降级

### 8.3 下一步行动

1. **立即开始** - Phase 1: 小模型优化配置
2. **并行开发** - 三层搜索和 GraphRAG 可并行
3. **持续集成** - 每完成一个 Phase 进行测试
4. **文档同步** - 更新使用文档和示例

---

## 附录

### A. 参考文档

- [OllamaPilot 架构分析](架构分析.md)
- [OllamaPilot 运行逻辑](运行逻辑.md)
- [OllamaPilot 源码解析](源码解析.md)
- [nanobot 架构分析](../nanobot/架构分析.md)
- [nanobot 运行逻辑](../nanobot/运行逻辑.md)

### B. 相关项目

- [OllamaPilot](https://github.com/ollamapilot/ollamapilot) - 源项目
- [nanobot](https://github.com/coleam00/nanobot) - 目标项目
- [LangChain](https://github.com/langchain-ai/langchain) - 参考实现

### C. 术语表

| 术语 | 说明 |
|------|------|
| **Skill** | 指导 Agent 如何完成特定任务的文档或代码 |
| **Tool** | Agent 可调用的具体功能实现 |
| **GraphRAG** | 基于知识图谱的检索增强生成 |
| **SearXNG** | 开源元搜索引擎 |
| **小模型** | 参数量 < 10B 的 LLM，如 qwen2.5:4b |

---

## 九、确认与启动

### 9.1 方案确认清单

请在开始实施前确认以下内容：

- [ ] **仓库权限** - 已确认可写入 `https://github.com/zh2673-git/super_nanobot`
- [ ] **测试资源** - 已准备好 OllamaPilot 源码、向量化知识库、.env 文件
- [ ] **模型配置** - 已确认测试用模型（qwen2.5:4b 等）
- [ ] **版本规划** - 认可 v0.0.1 → v0.0.2 → v0.0.3 → v0.1.0 的发布计划
- [ ] **仓库规范** - 认可 .gitignore 排除规则（笔记、.env、release 不提交）
- [ ] **测试标准** - 认可"功能与 OllamaPilot 效果一致"的测试标准
- [ ] **时间规划** - 认可约 4 周的开发周期

### 9.2 启动前准备

**需要用户提供**:
1. OllamaPilot 完整源码路径
2. 向量化知识库文件路径
3. .env 文件（含 API 密钥）
4. 推荐的模型名称和配置
5. super_nanobot 仓库的写入权限

**我会准备**:
1. 开发环境配置
2. 测试用例设计
3. 版本发布流程
4. 每日进度同步

### 9.3 沟通机制

- **每日进度** - 每个工作日结束时同步进展
- **版本发布** - 每个里程碑完成后提交并通知
- **问题反馈** - 遇到阻塞问题立即沟通
- **代码审查** - 关键提交前可安排审查

---

**文档版本**: 1.1  
**创建时间**: 2026-03-12  
**最后更新**: 2026-03-12  
**作者**: AI Assistant  
**状态**: 待确认启动