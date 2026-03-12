"""Enhanced search tool with three-tier architecture (basic/enhanced/deep)."""

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
        verify_ssl: bool = True,
    ):
        self.brave_api_key = brave_api_key or os.environ.get("BRAVE_API_KEY")
        self.searxng_url = searxng_url or os.environ.get("SEARXNG_URL", "http://localhost:8080")
        self.proxy = proxy
        self.auto_fallback = auto_fallback
        self.verify_ssl = verify_ssl

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

    # 具体搜索引擎实现
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
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                # 使用 NCBI E-utilities API
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmode": "json",
                    "retmax": 5
                }

                response = await client.get(search_url, params=search_params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                idlist = data.get("esearchresult", {}).get("idlist", [])
                if not idlist:
                    return "PubMed: 未找到相关文献"

                # 获取摘要
                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(idlist),
                    "retmode": "json"
                }

                summary_response = await client.get(summary_url, params=summary_params, timeout=10.0)
                summary_data = summary_response.json()

                lines = [f"PubMed 搜索结果 ({len(idlist)} 篇):"]
                for pmid in idlist[:5]:
                    doc = summary_data.get("result", {}).get(pmid, {})
                    title = doc.get("title", "无标题")
                    lines.append(f"- {title}")
                    lines.append(f"  PMID: {pmid}")

                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"PubMed 搜索失败: {e}")
            return ""

    async def _search_arxiv(self, query: str) -> str:
        """arXiv 论文搜索"""
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                # 使用 arXiv API
                url = f"http://export.arxiv.org/api/query?search_query=all:{quote(query)}&start=0&max_results=5"

                response = await client.get(url, timeout=10.0)
                response.raise_for_status()

                # 简单解析 XML
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                entries = root.findall("atom:entry", ns)
                if not entries:
                    return "arXiv: 未找到相关论文"

                lines = [f"arXiv 搜索结果 ({len(entries)} 篇):"]
                for entry in entries[:5]:
                    title = entry.find("atom:title", ns)
                    title_text = title.text.strip() if title is not None else "无标题"
                    lines.append(f"- {title_text}")

                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"arXiv 搜索失败: {e}")
            return ""

    async def _search_github(self, query: str) -> str:
        """GitHub 代码搜索"""
        token = os.environ.get("GITHUB_TOKEN")
        headers = {"Authorization": f"token {token}"} if token else {}

        async with httpx.AsyncClient(proxy=self.proxy, verify=self.verify_ssl) as client:
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
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                response = await client.get(
                    "https://gitee.com/api/v5/search/repositories",
                    params={"q": query, "sort": "stars_count", "order": "desc", "per_page": 5},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                items = data if isinstance(data, list) else []
                if not items:
                    return ""

                lines = [f"Gitee 搜索结果 ({len(items)} 个仓库):"]
                for i, item in enumerate(items[:5], 1):
                    lines.append(f"{i}. {item.get('full_name', '')} ⭐{item.get('stargazers_count', 0)}")
                    lines.append(f"   {item.get('html_url', '')}")
                    if desc := item.get('description', ''):
                        lines.append(f"   {desc[:150]}...")

                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Gitee 搜索失败: {e}")
            return ""

    async def _search_baidu_baike(self, query: str) -> str:
        """百度百科搜索"""
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                # 使用百度百科 API
                url = f"https://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key={quote(query)}&bk_length=600"

                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                if data.get("errno") != 0:
                    return ""

                card = data.get("card", [])
                if not card:
                    return ""

                item = card[0]
                title = item.get("name", "")
                desc = item.get("description", "")
                url = item.get("url", "")

                return f"百度百科: {title}\n{desc}\n{url}"
        except Exception as e:
            logger.warning(f"百度百科搜索失败: {e}")
            return ""

    async def _search_wikipedia(self, query: str) -> str:
        """Wikipedia 搜索"""
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                # 使用 Wikipedia API
                url = "https://zh.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                    "srlimit": 5
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                search_results = data.get("query", {}).get("search", [])
                if not search_results:
                    return ""

                lines = [f"Wikipedia 搜索结果 ({len(search_results)} 条):"]
                for item in search_results[:5]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                    lines.append(f"- {title}: {snippet[:100]}...")

                return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Wikipedia 搜索失败: {e}")
            return ""

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
