"""Skill router for automatic skill selection based on user input."""

import json
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

            # 如果没有 triggers，尝试从 name 和 description 推断
            if not triggers:
                triggers = self._infer_triggers(name, meta.get("description", ""))

            if triggers:
                self._skill_triggers[name] = triggers
                for trigger in triggers:
                    self._trigger_index[trigger.lower()] = name

    def _infer_triggers(self, name: str, description: str) -> List[str]:
        """从 Skill 名称和描述推断触发词"""
        triggers = [name.lower()]

        # 常见关键词映射
        keyword_map = {
            "weather": ["天气", "温度", "下雨", "晴天"],
            "github": ["github", "代码", "仓库", "repo"],
            "memory": ["记忆", "记住", "回忆"],
            "summarize": ["总结", "摘要", "概括"],
            "cron": ["定时", "提醒", "计划", "schedule"],
            "tmux": ["tmux", "终端", "session"],
            "clawhub": ["clawhub", "skill"],
            "skill-creator": ["创建skill", "新建skill"],
        }

        name_lower = name.lower()
        if name_lower in keyword_map:
            triggers.extend(keyword_map[name_lower])

        return triggers

    def select_skill(self, query: str) -> Optional[str]:
        """
        根据用户查询选择最合适的 Skill

        Args:
            query: 用户输入

        Returns:
            Skill 名称，如果没有匹配返回 None
        """
        query_lower = query.lower()

        # 1. 精确匹配（触发词在查询中）
        for trigger, skill_name in sorted(self._trigger_index.items(), key=lambda x: -len(x[0])):
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

    def get_skill_triggers(self, skill_name: str) -> List[str]:
        """获取 Skill 的触发词列表"""
        return self._skill_triggers.get(skill_name, [])

    def list_available_skills(self) -> List[Dict[str, str]]:
        """列出所有可用的 Skill 及其触发词"""
        result = []
        for name, triggers in self._skill_triggers.items():
            meta = self.skills_loader.get_skill_metadata(name) or {}
            result.append({
                "name": name,
                "description": meta.get("description", ""),
                "triggers": triggers,
            })
        return result

    def _parse_nanobot_metadata(self, raw: str) -> dict:
        """解析 metadata JSON"""
        try:
            data = json.loads(raw)
            return data.get("nanobot", data.get("openclaw", {})) if isinstance(data, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def reload(self):
        """重新加载 Skill 索引"""
        self._trigger_index.clear()
        self._skill_triggers.clear()
        self._build_index()
