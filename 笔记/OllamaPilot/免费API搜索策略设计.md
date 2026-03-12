# OllamaPilot 免费API搜索策略设计

> **版本**: v0.2.7
> **设计目标**: 优先使用国内可免费使用的API，实现智能降级和配额管理

---

## 一、免费API资源调研

### 1.1 国内可用免费API（无需翻墙）

| API名称 | 类型 | 免费额度 | 限制 | 国内访问 | 推荐指数 |
|---------|------|----------|------|----------|----------|
| **Tavily** | 通用搜索 | 1000次/月 | 需API Key | ✅ 完全可用 | ⭐⭐⭐⭐⭐ |
| **SearXNG** | 聚合搜索 | 无限 | 需自建 | ✅ 完全可用 | ⭐⭐⭐⭐⭐ |
| **PubMed** | 学术文献 | 无限 | 无限制 | ✅ 完全可用 | ⭐⭐⭐⭐⭐ |
| **百度百科** | 百科知识 | 无限 | 需爬虫 | ✅ 完全可用 | ⭐⭐⭐⭐ |
| **GitHub** | 代码仓库 | 500次/小时 | 需Token | ✅ 完全可用 | ⭐⭐⭐⭐⭐ |
| **Gitee** | 代码仓库 | 无限 | 国内友好 | ✅ 完全可用 | ⭐⭐⭐⭐ |
| **arXiv** | 学术论文 | 无限 | 无限制 | ⚠️ 偶尔不稳定 | ⭐⭐⭐ |
| **Wikipedia** | 百科知识 | 无限 | 无限制 | ⚠️ 需代理 | ⭐⭐ |

### 1.2 需要API Key的免费服务

| API名称 | 类型 | 免费额度 | 申请难度 | 国内访问 | 推荐指数 |
|---------|------|----------|----------|----------|----------|
| **Serper (Google)** | 通用搜索 | 2500次/月 | 简单 | ✅ 可用 | ⭐⭐⭐⭐ |
| **Bing Search** | 通用搜索 | 1000次/月 | 中等 | ✅ 可用 | ⭐⭐⭐⭐ |
| **DuckDuckGo** | 通用搜索 | 无限 | 无需Key | ✅ 可用 | ⭐⭐⭐⭐ |
| **Brave Search** | 通用搜索 | 2000次/月 | 简单 | ✅ 可用 | ⭐⭐⭐⭐ |

---

## 二、三层搜索架构的API策略

### 2.1 第一层：web_search（基础搜索）

**策略**: 优先使用高质量API，智能降级

```
优先级队列:
1. Tavily (API) - 1000次/月，专为AI设计，质量最佳 ⭐推荐
2. SearXNG (本地Docker) - 无限额度，本地部署
3. Serper (API) - 2500次/月，Google结果
4. Bing (API) - 1000次/月
5. Brave (API) - 2000次/月
6. DuckDuckGo (API) - 无限额度，兜底
```

**实现方案**:
- 优先尝试 Tavily（专为AI应用设计，搜索质量最高）
- Tavily 不可用或配额用完时，降级到 SearXNG
- SearXNG 不可用时，依次尝试 Serper → Bing → Brave → DuckDuckGo
- 即使不配置任何API，DuckDuckGo 也能正常工作（零配置可用）

### 2.2 第二层：enhanced_search（增强搜索）

**策略**: 按领域选择最合适的免费API

```
学术领域:
1. PubMed - 医学文献，无限额度
2. arXiv - 学术论文，无限额度（不稳定时降级）

代码领域:
1. GitHub - 500次/小时，需Token
2. Gitee - 无限额度，国内友好

百科领域:
1. 百度百科 - 无限额度，中文优化
2. Wikipedia - 无限额度（不稳定时降级）

通用聚合:
1. SearXNG - 多引擎聚合
2. DuckDuckGo - 备用
```

**配额管理**:
- GitHub 达到限额时自动切换到 Gitee
- arXiv 不稳定时跳过
- Wikipedia 不可用时使用百度百科

### 2.3 第三层：deep_research（深度研究）

**策略**: 多轮迭代，智能选择引擎

```
研究流程:
1. 需求分析 → 确定需要的领域
2. 第一轮搜索 → 使用最相关的引擎
3. 第二轮搜索 → 补充其他引擎
4. 结果整合 → 去重、排序

引擎选择策略:
- 医学主题 → PubMed + 百度百科
- 技术主题 → GitHub + SearXNG
- 学术主题 → arXiv + PubMed
- 通用主题 → SearXNG + DuckDuckGo
```

---

## 三、API配额管理与自动降级

### 3.1 配额监控设计

```python
class APIQuotaManager:
    """API配额管理器"""
    
    def __init__(self):
        self.quotas = {
            "tavily": {"limit": 1000, "window": 2592000, "used": 0},  # 1000次/月
            "github": {"limit": 500, "window": 3600, "used": 0},  # 500次/小时
            "serper": {"limit": 2500, "window": 2592000, "used": 0},  # 2500次/月
            "bing": {"limit": 1000, "window": 2592000, "used": 0},  # 1000次/月
            "brave": {"limit": 2000, "window": 2592000, "used": 0},  # 2000次/月
        }
    
    def can_use(self, api_name: str) -> bool:
        """检查API是否还有配额"""
        quota = self.quotas.get(api_name)
        if not quota:
            return True  # 无限额度
        return quota["used"] < quota["limit"]
    
    def use(self, api_name: str):
        """记录API使用"""
        if api_name in self.quotas:
            self.quotas[api_name]["used"] += 1
```

### 3.2 自动降级策略

```python
class SearchEngineRouter:
    """搜索引擎路由器 - 实现自动降级"""
    
    def __init__(self):
        self.quota_manager = APIQuotaManager()
        self.engines = {
            "general": ["tavily", "searxng", "serper", "bing", "brave", "duckduckgo"],
            "academic": ["pubmed", "arxiv"],
            "code": ["github", "gitee"],
            "encyclopedia": ["baidu_baike", "wikipedia"],
        }
    
    async def search(self, query: str, category: str) -> List[SearchResult]:
        """智能选择引擎并搜索"""
        engine_list = self.engines.get(category, self.engines["general"])
        
        for engine_name in engine_list:
            # 检查配额
            if not self.quota_manager.can_use(engine_name):
                print(f"⚠️ {engine_name} 配额已用完，尝试下一个引擎")
                continue
            
            # 检查可用性
            engine = SearchEngineFactory.create(engine_name)
            if not engine or not engine.is_available():
                continue
            
            try:
                results = await engine.search(query)
                self.quota_manager.use(engine_name)
                return results
            except Exception as e:
                print(f"❌ {engine_name} 搜索失败: {e}")
                continue
        
        return []  # 所有引擎都失败
```

---

## 四、.env 配置文件设计

### 4.1 推荐配置

```bash
# ==========================================
# OllamaPilot 免费API配置 (v0.2.7)
# ==========================================

# ---- 第1优先：Tavily（专为AI设计，质量最佳）----
# 申请地址: https://tavily.com (1000次/月)
TAVILY_API_KEY=your_tavily_key_here

# ---- 第2优先：SearXNG（本地部署）----
SEARXNG_URL=http://localhost:8080
SEARXNG_AUTO_START=true

# ---- 其他可选API----
# Serper.dev API（2500次/月）
# 申请地址: https://serper.dev
SERPER_API_KEY=your_serper_key_here

# Bing Search API（1000次/月）
# 申请地址: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
BING_API_KEY=your_bing_key_here

# Brave Search API（2000次/月）
# 申请地址: https://brave.com/search/api/
BRAVE_API_KEY=your_brave_key_here

# GitHub API（500次/小时）
# 申请地址: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# ---- 配额管理配置 ----
# 是否启用配额管理
ENABLE_QUOTA_MANAGEMENT=true

# 配额警告阈值（百分比）
QUOTA_WARNING_THRESHOLD=80

# 自动降级策略
AUTO_FALLBACK=true
```

### 4.2 配置优先级

```
1. 如果配置了 API Key → 使用该API（有配额管理）
2. 如果没有 API Key 或配额用完 → 降级到免费引擎
3. 免费引擎优先级: Tavily > SearXNG > Serper > Bing > Brave > DuckDuckGo
```

---

## 五、各搜索层级推荐配置

### 5.1 推荐配置组合

| 使用场景 | 推荐配置 | 说明 |
|---------|---------|------|
| **极简模式** | 仅 DuckDuckGo | 完全免费，无需任何API Key |
| **标准模式** | Tavily | 专为AI设计，质量最佳（1000次/月） |
| **增强模式** | Tavily + GitHub Token | 通用搜索+代码搜索 |
| **完整模式** | 所有API都配置 | 最佳搜索体验 |

### 5.2 质量对比

| 搜索类型 | 仅DuckDuckGo | +Tavily | +Serper | 完整配置 |
|---------|---------------|---------|---------|----------|
| 通用搜索 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 代码搜索 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 学术搜索 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 百科搜索 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 六、实现建议

### 6.1 增强搜索工具改进

修改 `skills/enhanced_search/tools.py`:

```python
async def multi_engine_search(query: str, num_results: int = 10) -> str:
    """
    多引擎搜索 - 智能选择可用引擎，自动降级
    """
    router = SearchEngineRouter()
    
    # 根据查询内容确定类别
    category = _detect_category(query)
    
    # 使用路由器搜索（自动处理降级）
    results = await router.search(query, category)
    
    if not results:
        # 所有引擎都失败，使用兜底方案
        results = await _fallback_search(query)
    
    return format_results(results)
```

### 6.2 深度研究工具改进

修改 `skills/deep_research/tools.py`:

```python
def execute_deep_research(topic: str) -> str:
    """
    执行深度研究 - 多轮迭代，智能选择引擎
    """
    # 1. 分析主题确定需要的领域
    domains = _analyze_topic_domains(topic)
    
    # 2. 为每个领域选择最佳引擎
    engines = []
    for domain in domains:
        engine = _select_best_engine(domain)
        engines.append(engine)
    
    # 3. 多轮搜索
    findings = []
    for i in range(3):  # 3轮搜索
        for engine in engines:
            results = engine.search(topic)
            findings.extend(results)
    
    # 4. 生成报告
    return generate_report(findings)
```

---

## 七、总结

### 7.1 核心原则

1. **免费优先**: 优先使用完全免费的API（SearXNG、PubMed、百度百科）
2. **智能降级**: API配额用完或不可用时，自动降级到备用引擎
3. **配额管理**: 监控API使用情况，避免超额
4. **国内友好**: 所有推荐API均可在国内直接访问

### 7.2 实施步骤

1. **阶段1**: 完善 SearXNG 支持（已完成 ✅）
2. **阶段2**: 添加 DuckDuckGo 作为备用（已完成 ✅）
3. **阶段3**: 实现配额管理系统（已完成 ✅）
4. **阶段4**: 添加可选API支持（GitHub、Serper等）（已完成 ✅）
5. **阶段5**: 添加Tavily支持，专为AI设计的搜索（已完成 ✅ v0.2.7）
6. **阶段6**: 优化深度研究的多轮搜索策略（进行中 🔄）

---

**创建时间**: 2026-03-12  
**最后更新**: 2026-03-12  
**版本**: v0.2.7  
**标签**: #API #免费 #搜索策略 #配额管理 #Tavily
