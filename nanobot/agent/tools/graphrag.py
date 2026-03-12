"""GraphRAG tool for knowledge graph-based document Q&A."""

import hashlib
import json
import math
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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
    relation: str
    confidence: float = 1.0
    doc_id: str = ""

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "confidence": self.confidence,
            "doc_id": self.doc_id
        }


@dataclass
class Document:
    """文档"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class SimpleVectorStore:
    """
    简单向量存储 - 原项目实现

    使用 SQLite 存储文档元数据，内存中存储向量。
    支持按 Embedding 模型隔离存储。
    """

    def __init__(self, persist_dir: str = "./data/graphrag", collection_name: str = "default"):
        """
        初始化

        Args:
            persist_dir: 持久化目录
            collection_name: 集合名称（用于区分不同的 Embedding 模型）
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        # 初始化 SQLite（按集合分表）
        self.db_path = self.persist_dir / "vectors.db"
        self._init_db()

        # 内存中的向量存储
        self.vectors: Dict[str, List[float]] = {}

        # 加载已有数据
        self._load_vectors()

    def _init_db(self):
        """初始化数据库（按集合创建表）"""
        with sqlite3.connect(self.db_path) as conn:
            # 为每个集合创建独立的表
            table_name = self._get_table_name()
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)
            # 创建集合元数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_meta (
                    name TEXT PRIMARY KEY,
                    doc_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _get_table_name(self) -> str:
        """获取当前集合的表名"""
        # 清理集合名称，确保是有效的 SQL 标识符
        safe_name = "".join(c if c.isalnum() else "_" for c in self.collection_name)
        return f"docs_{safe_name}"

    def _load_vectors(self):
        """加载向量（向量存储在单独的 JSON 文件中，按集合隔离）"""
        vectors_path = self.persist_dir / f"vectors_{self.collection_name}.json"
        if vectors_path.exists():
            try:
                with open(vectors_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vectors = {k: v for k, v in data.items()}
                logger.info(f"加载了 {len(self.vectors)} 个向量")
            except Exception as e:
                logger.warning(f"加载向量失败: {e}")
                self.vectors = {}

    def _save_vectors(self):
        """保存向量"""
        vectors_path = self.persist_dir / f"vectors_{self.collection_name}.json"
        try:
            with open(vectors_path, 'w', encoding='utf-8') as f:
                json.dump(self.vectors, f)
        except Exception as e:
            logger.warning(f"保存向量失败: {e}")

    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict],
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        添加文档

        Args:
            ids: 文档ID列表
            documents: 文档文本列表
            metadatas: 元数据列表
            embeddings: embedding 向量列表
        """
        table_name = self._get_table_name()
        with sqlite3.connect(self.db_path) as conn:
            for i, doc_id in enumerate(ids):
                text = documents[i]
                metadata = metadatas[i]

                # 插入或更新文档
                conn.execute(
                    f"INSERT OR REPLACE INTO {table_name} (id, text, metadata) VALUES (?, ?, ?)",
                    (doc_id, text, json.dumps(metadata, ensure_ascii=False))
                )

                # 存储向量
                if embeddings and i < len(embeddings):
                    self.vectors[doc_id] = embeddings[i]

            conn.commit()

        # 保存向量
        self._save_vectors()

    def get(self, ids: List[str], include: Optional[List[str]] = None) -> Dict:
        """
        获取文档

        Args:
            ids: 文档ID列表
            include: 包含的字段

        Returns:
            文档数据字典
        """
        result = {
            "ids": [],
            "documents": [],
            "metadatas": [],
            "embeddings": []
        }

        include_embeddings = include is None or "embeddings" in include
        table_name = self._get_table_name()

        with sqlite3.connect(self.db_path) as conn:
            for doc_id in ids:
                row = conn.execute(
                    f"SELECT text, metadata FROM {table_name} WHERE id = ?",
                    (doc_id,)
                ).fetchone()

                if row:
                    result["ids"].append(doc_id)
                    result["documents"].append(row[0])
                    result["metadatas"].append(json.loads(row[1]))

                    if include_embeddings:
                        result["embeddings"].append(self.vectors.get(doc_id))

        return result

    def query(
        self,
        query_embeddings: Optional[List[List[float]]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 5
    ) -> Dict:
        """
        查询文档

        Args:
            query_embeddings: 查询向量
            query_texts: 查询文本（不使用，仅保持接口一致）
            n_results: 返回结果数量

        Returns:
            查询结果
        """
        if not query_embeddings or not self.vectors:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        query_vec = query_embeddings[0]

        # 计算余弦相似度
        similarities = []
        for doc_id, vec in self.vectors.items():
            similarity = self._cosine_similarity(query_vec, vec)
            similarities.append((doc_id, similarity))

        # 排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k = similarities[:n_results]

        # 获取文档内容
        result = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

        table_name = self._get_table_name()
        with sqlite3.connect(self.db_path) as conn:
            for doc_id, similarity in top_k:
                row = conn.execute(
                    f"SELECT text, metadata FROM {table_name} WHERE id = ?",
                    (doc_id,)
                ).fetchone()

                if row:
                    result["ids"][0].append(doc_id)
                    result["documents"][0].append(row[0])
                    result["metadatas"][0].append(json.loads(row[1]))
                    result["distances"][0].append(1 - similarity)  # 转换为距离

        return result

    def count(self) -> int:
        """获取文档数量"""
        table_name = self._get_table_name()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return row[0] if row else 0

    def get_all_ids(self) -> List[str]:
        """获取所有文档 ID"""
        table_name = self._get_table_name()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(f"SELECT id FROM {table_name}").fetchall()
            return [row[0] for row in rows]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class HybridEntityExtractor:
    """混合实体抽取器"""

    def __init__(self):
        # 内置词典
        self.dictionaries = {
            "PERSON": ["张三", "李四", "王五"],
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

        # 3. 推断关系
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

    def _infer_relations(self, entities: List[Entity], text: str) -> List[Relation]:
        """推断实体间关系"""
        relations = []

        # 简单规则：同一句话中的实体可能存在关系
        sentences = re.split(r'[。！？\n]', text)
        for sent in sentences:
            sent_entities = [e for e in entities if e.name in sent]
            if len(sent_entities) >= 2:
                # 创建关系
                for i in range(len(sent_entities)):
                    for j in range(i + 1, len(sent_entities)):
                        relations.append(Relation(
                            source=sent_entities[i].name,
                            target=sent_entities[j].name,
                            relation="相关",
                            confidence=0.5
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
            key = (r.source, r.target, r.relation)
            if key not in seen:
                seen.add(key)
                result.append(r)
        return result


class OllamaEmbeddingFunction:
    """Ollama Embedding 函数"""

    def __init__(self, url: str = "http://localhost:11434/api/embeddings",
                 model_name: str = "qwen3-embedding:0.6b", timeout: int = 120):
        self.url = url
        self.model_name = model_name
        self.timeout = timeout

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """调用 Ollama 生成 embedding"""
        import requests
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    self.url,
                    json={"model": self.model_name, "prompt": text},
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", [])
                if embedding:
                    embeddings.append(embedding)
                else:
                    embeddings.append([0.0] * 768)
            except Exception as e:
                logger.error(f"Embedding 生成失败: {e}")
                embeddings.append([0.0] * 768)
        return embeddings


class GraphRAGService:
    """GraphRAG 核心服务"""

    def __init__(
        self,
        persist_dir: str = "./data/graphrag",
        embedding_model: Optional[str] = None,
        collection_name: str = "default"
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_model_name = embedding_model

        # 根据 embedding 模型名称生成集合名称
        if embedding_model:
            safe_name = "".join(c if c.isalnum() else "_" for c in embedding_model)
            self.collection_name = safe_name
        else:
            self.collection_name = collection_name

        # 初始化向量存储 - 使用原项目实现
        self.collection = SimpleVectorStore(
            persist_dir=persist_dir,
            collection_name=self.collection_name
        )

        # 初始化 embedding 函数
        if embedding_model:
            self._embedding_fn = OllamaEmbeddingFunction(
                url="http://localhost:11434/api/embeddings",
                model_name=embedding_model,
                timeout=120
            )
        else:
            self._embedding_fn = None

        # 实体索引
        self.entity_index: Dict[str, Dict] = {}

        # 关系索引
        self.relations: List[Relation] = []

        # 加载已有数据
        self._load_index()

    def add_document(
        self,
        text: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        entities: Optional[List[Entity]] = None
    ) -> str:
        """添加文档到图谱"""
        import time

        if doc_id is None:
            doc_id = hashlib.md5(text.encode()).hexdigest()[:16]

        # 1. 准备元数据
        doc_metadata = metadata or {}
        doc_metadata["doc_id"] = doc_id

        # 2. 如果没有提供实体，自动抽取
        if entities is None:
            extractor = HybridEntityExtractor()
            entities, relations = extractor.extract(text, use_llm=False)
        else:
            relations = []

        # 3. 生成 embedding
        embedding = None
        if self._embedding_fn:
            try:
                embeddings = self._embedding_fn([text])
                embedding = embeddings[0] if embeddings else None
                logger.info(f"Embedding 生成成功，维度: {len(embedding) if embedding else 0}")
            except Exception as e:
                logger.warning(f"Embedding 生成失败: {e}")

        # 4. 存储到向量存储
        try:
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[doc_metadata],
                embeddings=[embedding] if embedding else None
            )
        except Exception as e:
            logger.error(f"存储失败: {e}")
            raise

        # 5. 更新实体索引
        if entities:
            for entity in entities:
                self._index_entity(entity, doc_id)

        # 6. 推断关系
        if entities and len(entities) > 1:
            self._infer_relations(entities, doc_id)

        # 7. 持久化
        self._save_index()

        logger.info(f"添加文档: {doc_id}, 实体: {len(entities)}, 关系: {len(relations)}")

        return doc_id

    def _index_entity(self, entity: Entity, doc_id: str):
        """索引实体"""
        if entity.name not in self.entity_index:
            self.entity_index[entity.name] = {
                "type": entity.type,
                "doc_ids": set()
            }
        self.entity_index[entity.name]["doc_ids"].add(doc_id)

    def _infer_relations(self, entities: List[Entity], doc_id: str):
        """推断实体间关系"""
        entity_names = [e.name for e in entities]

        # 简单的共现关系
        for i, source in enumerate(entity_names):
            for target in entity_names[i+1:]:
                relation = Relation(
                    source=source,
                    target=target,
                    relation="CO_OCCUR",
                    confidence=0.5,
                    doc_id=doc_id
                )
                self.relations.append(relation)

    def query(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """查询知识库"""
        if not self._embedding_fn:
            return {"documents": [], "total_found": 0}

        try:
            query_embeddings = self._embedding_fn([query])
            query_embedding = query_embeddings[0] if query_embeddings else None

            if query_embedding:
                vector_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )

                documents = []
                for i, doc_id in enumerate(vector_results["ids"][0]):
                    documents.append({
                        "id": doc_id,
                        "content": vector_results["documents"][0][i],
                        "source": vector_results["metadatas"][0][i].get("source", "")
                    })

                return {"documents": documents, "total_found": len(documents)}
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return {"documents": [], "total_found": 0}

    def _save_index(self):
        """保存索引到文件"""
        index_path = self.persist_dir / f"index_{self.collection_name}.json"
        index_data = {
            "entity_index": {
                name: {"type": info["type"], "doc_ids": list(info["doc_ids"])}
                for name, info in self.entity_index.items()
            },
            "relations": [r.to_dict() for r in self.relations]
        }
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    def _load_index(self):
        """从文件加载索引"""
        index_path = self.persist_dir / f"index_{self.collection_name}.json"
        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.entity_index = {
                    name: {"type": info["type"], "doc_ids": set(info["doc_ids"])}
                    for name, info in data.get("entity_index", {}).items()
                }

                self.relations = [
                    Relation(**r) for r in data.get("relations", [])
                ]
            except Exception as e:
                logger.warning(f"索引加载失败: {e}")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_documents": self.collection.count(),
            "total_entities": len(self.entity_index),
            "total_relations": len(self.relations),
            "entity_types": list(set(
                info["type"] for info in self.entity_index.values()
            )) if self.entity_index else []
        }


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

    def __init__(
        self,
        workspace: Path,
        persist_dir: str = "./data/graphrag",
        embedding_model: Optional[str] = None
    ):
        self.workspace = workspace
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model
        self.services: Dict[str, GraphRAGService] = {}

    def _get_service(self, collection: str) -> GraphRAGService:
        """获取或创建服务"""
        if collection not in self.services:
            self.services[collection] = GraphRAGService(
                persist_dir=self.persist_dir,
                collection_name=collection,
                embedding_model=self.embedding_model
            )
        return self.services[collection]

    async def _execute(self, action: str, **kwargs) -> str:
        """执行操作"""
        collection = kwargs.get("collection", "default")
        service = self._get_service(collection)

        if action == "index":
            content = kwargs.get("content", "")
            source = kwargs.get("source", "unknown")
            if not content:
                return "错误: 请提供文档内容"
            doc_id = service.add_document(content, metadata={"source": source})
            return f"文档已索引: {doc_id} (集合: {collection})"

        elif action == "query":
            query = kwargs.get("query", "")
            if not query:
                return "错误: 请提供查询内容"
            results = service.query(query)
            return self._format_query_results(query, results)

        elif action == "status":
            stats = service.get_stats()
            return (
                f"GraphRAG 状态 (集合: {collection}):\n"
                f"- 文档数: {stats['total_documents']}\n"
                f"- 实体数: {stats['total_entities']}\n"
                f"- 关系数: {stats['total_relations']}\n"
                f"- 实体类型: {', '.join(stats['entity_types']) if stats['entity_types'] else '无'}"
            )

        return f"未知操作: {action}"

    def _format_query_results(self, query: str, results: Dict) -> str:
        """格式化查询结果"""
        lines = [
            f"GraphRAG 查询: {query}",
            "",
        ]

        documents = results.get("documents", [])
        total_found = results.get("total_found", 0)

        lines.append(f"找到 {len(documents)} 个相关文档 (共 {total_found} 个候选):")
        lines.append("")

        for i, doc in enumerate(documents, 1):
            lines.append(f"--- 文档 {i} ---")
            lines.append(f"来源: {doc.get('source', 'unknown')}")
            content = doc.get('content', '')
            lines.append(f"内容: {content[:300]}..." if len(content) > 300 else f"内容: {content}")
            lines.append("")

        return "\n".join(lines)
