# GraphRAG 知识图谱实现详解

> 基于实体-关系的智能文档问答系统实现原理

---

## 🎯 第一步：认识 GraphRAG 核心组件

GraphRAG 就像一个「智能图书馆管理系统」，由五个核心"部门"协同工作：

- **GraphRAGService（档案馆）**：整个系统的核心存储系统，像档案馆的库房（负责存储文档向量、实体索引、关系网络）
- **HybridEntityExtractor（提取员）**：实体和关系的智能提取专家，像档案馆的分类员（从文档中提取人名、地名、术语等实体，发现实体之间的关系）
- **KnowledgeBaseManager（图书馆长）**：知识库的整体管理者，像图书馆长（扫描文档、索引内容、管理知识库状态）
- **WordAligner（校对员）**：实体位置精确映射专家，像档案馆的校对员（将提取的实体精确映射回原文位置，支持溯源验证）
- **GraphRAGMiddleware（智能检索流水线）**：查询时的自动增强机制，像图书馆的智能推荐系统（自动分析用户查询，检索相关知识）

**为什么这样设计？**

想象你要管理一个大型图书馆：
- 如果所有功能都堆在一起，就像馆长又要整理书籍、又要回答读者问题、又要维护索引混乱不堪
- GraphRAG 的设计就像把图书馆分成多个专业部门：
  - 档案馆（GraphRAGService）专门负责存储
  - 分类员（HybridEntityExtractor）专门提取知识
  - 图书馆长（KnowledgeBaseManager）专门管理流程
  - 校对员（WordAligner）专门确保准确性
  - 智能推荐系统（GraphRAGMiddleware）专门提升检索质量

---

## 📊 第二步：组件协作关系图

```
[用户上传文档]
    |
    v
┌─────────────────────────────────────────────────────────┐
│          KnowledgeBaseManager（图书馆长）                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. 扫描知识库目录，发现新文档                      │  │
│  │  2. 读取文档内容                                  │  │
│  │  3. 调用 DocumentProcessor 分块                   │  │
│  │  4. 协调实体抽取和索引                             │  │
│  │  5. 调用 WordAligner 精确对齐                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────────────────┐
│      HybridEntityExtractor（实体提取员）                  │
│                                                          │
│  [词典匹配] → [规则匹配] → [LLM智能抽取] → [动态学习]    │
│       ↓              ↓            ↓           ↓         │
│   快速提取      模式识别       智能发现    增量学习      │
│                                                          │
└─────────────────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────────────────┐
│           GraphRAGService（档案馆）                       │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ 向量存储  │  │ 实体索引 │  │ 关系索引 │              │
│  │  (Chroma)│  │(内存Dict)│  │(内存List)│              │
│  └──────────┘  └──────────┘  └──────────┘            │
│       │              │              │                    │
│       └──────────────┼──────────────┘                    │
│                      v                                    │
│              ┌──────────────┐                             │
│              │ 持久化存储   │                             │
│              │ (JSON文件)   │                             │
│              └──────────────┘                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
    |
    v
┌─────────────────────────────────────────────────────────┐
│           WordAligner（校对员）                          │
│                                                          │
│  [精确匹配] → [归一化匹配] → [模糊匹配] → [去重验证]     │
│      ↓            ↓            ↓            ↓          │
│  完全一致       忽略标点      相似度匹配   保留最佳      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**用户查询时的检索流程**：

```
[用户查询]
    |
    v
┌─────────────────────────────────────────────────────────┐
│        GraphRAGMiddleware（智能检索流水线）                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. 提取查询中的实体（HybridEntityExtractor）    │  │
│  │  2. 实体索引查询（找到相关文档）                   │  │
│  │  3. 关系遍历扩展（1-2跳推理）                      │  │
│  │  4. 向量重排序（提升相关性）                       │  │
│  │  5. 返回增强后的上下文                            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**协作流程说明**：

1. **文档上传**：KnowledgeBaseManager 接收文档，读取并分块
2. **实体提取**：HybridEntityExtractor 从每块文本中提取实体和关系
3. **双重索引**：GraphRAGService 同时存储向量（语义搜索）和实体索引（关系推理）
4. **精确对齐**：WordAligner 将实体精确映射回原文位置
5. **查询增强**：用户查询时，Middleware 自动检索相关知识并注入上下文

---

## 📚 第三步：深入理解每个组件

### 一、GraphRAGService（档案馆）

**专业定义**：GraphRAGService 是 GraphRAG 的核心服务类，提供混合存储能力，整合向量存储（用于语义搜索）、实体索引（用于快速查找）和关系索引（用于图推理）。

**通俗解释与类比**：

想象一个现代化档案馆：
- **向量存储**（ChromaDB/SimpleVectorStore）：就像档案馆的检索系统，可以通过关键词的含义找到相关文档（不只是字面匹配）
- **实体索引**（内存Dict）：就像档案馆的卡片目录，按人名、地名、主题分类存储，快速找到某人或某地相关的所有档案
- **关系索引**（内存List）：就像档案馆的关系图谱，记录"谁认识谁"、"什么导致什么"

**在项目中的具体体现**：

GraphRAGService 的核心功能：

1. **初始化配置**：
   ```python
   # 服务初始化（graphrag_service.py:62-107）
   self.collection = SimpleVectorStore(...)  # 向量存储
   self.entity_index = {}                    # 实体索引：{实体名: {类型, 文档ID集合}}
   self.relations = []                       # 关系列表
   ```

2. **文档添加流程**：
   - 生成文档向量（调用 Embedding 模型）
   - 存储到向量数据库
   - 索引提取的实体
   - 推断实体间关系

3. **增强检索**（enhanced_search）：
   - 步骤1：实体索引查询，找到包含查询实体的文档
   - 步骤2：关系遍历扩展（1-2跳），找到相关实体
   - 步骤3：向量重排序，提升结果相关性

4. **数据持久化**：
   - 索引保存到 JSON 文件（按模型隔离）
   - 本体定义保存到 ontology.json

### 二、HybridEntityExtractor（实体提取员）

**专业定义**：HybridEntityExtractor 是混合模式实体抽取器，结合词典匹配、规则匹配和 LLM 智能抽取三种方式，支持动态学习和人工干预。

**通俗解释与类比**：

想象一个超级图书管理员：
- **词典匹配**：手里有一本常用词汇表，看到匹配的词就勾选出来（快速、高置信度）
- **规则匹配**：根据语法规则识别新词汇（模式识别）
- **LLM 智能抽取**：请教专家（大型语言模型）发现词汇表中没有的新实体（智能发现）
- **动态学习**：把专家发现的新词汇更新到自己的词汇表中（增量学习）

**在项目中的具体体现**：

HybridEntityExtractor 的工作流程（entity_extractor.py:144-199）：

1. **词典匹配**（快速路径）：
   - 加载全局预设词典（config/dictionaries/）
   - 加载文档私有词典（data/graphrag/{doc_id}/dictionary.json）
   - 在文本中查找词典中的词条

2. **规则匹配**（补充路径）：
   - 使用正则表达式识别模式
   - 如人名、组织、地点等
   - 过滤停用词和误匹配

3. **LLM 智能抽取**（智能路径）：
   - 构建实体抽取提示词
   - 调用 LLM 识别新实体
   - 解析返回的 JSON 结果

4. **动态学习**：
   - 将 LLM 发现的高置信度新实体加入文档私有词典
   - 下次检索时自动包含

**词典架构**：
```
config/dictionaries/           # 全局预设词典（用户维护，只读）
    ├── medical.json           # 医学领域词典
    ├── legal.json            # 法律领域词典
    └── ...

data/graphrag/{doc_id}/       # 文档私有词典（LLM学习，可写）
    └── dictionary.json       # 该文档特有的词汇
```

### 三、KnowledgeBaseManager（图书馆长）

**专业定义**：KnowledgeBaseManager 是知识库管理器，负责自动扫描、索引和管理知识库文档，协调实体抽取和索引流程，集成 WordAligner 提供精确位置映射。

**通俗解释与类比**：

想象一个图书馆长的工作日常：
- **扫描目录**：每天检查有没有新书进来
- **编目索引**：给每本书分类、贴标签、编目录
- **协调工作**：安排提取员（EntityExtractor）处理内容，安排校对员（WordAligner）验证准确性

**在项目中的具体体现**：

KnowledgeBaseManager 的核心流程（knowledge_base.py:72-121）：

1. **扫描知识库**：
   ```python
   # 扫描目录获取所有支持的文档
   files = self._scan_directory(kb_path)  # 支持 .txt, .md, .pdf, .docx, .doc
   ```

2. **增量索引**：
   - 检查文档是否已索引
   - 只处理新文档或修改过的文档

3. **文档处理流水线**：
   - 读取文档全文
   - 分块（默认 2000 字符/块，200 字符重叠）
   - 实体抽取（每块独立）
   - 添加到图谱
   - WordAligner 对齐

4. **索引状态管理**：
   - 记录已索引文档 ID
   - 提供统计信息

### 四、WordAligner（校对员）

**专业定义**：WordAligner 是文本对齐器，移植自 LangExtract 的算法，提供将提取的实体精确映射回原文位置的能力，支持精确匹配、部分匹配和模糊匹配三种模式。

**通俗解释与类比**：

想象一个古籍校对专家：
- **精确匹配**：原文是"张仲景"，抽取出也是"张仲景"，完全一致（✓）
- **归一化匹配**：原文是"太阳病，"，抽取出是"太阳病"，忽略标点差异（~）
- **模糊匹配**：原文是"桂枝汤"，抽取出是"桂枝汤加减"，通过相似度算法找到最佳匹配（≈）

**在项目中的具体体现**：

WordAligner 的对齐算法（word_aligner.py:161-196）：

1. **精确匹配**：
   ```python
   # 直接在原文中查找
   exact_pos = source_text.find(extraction_text, search_start)
   if exact_pos != -1:
       return (exact_pos, exact_pos + len(extraction_text), "exact", 1.0)
   ```

2. **归一化匹配**：
   - 移除标点、空格、大小写差异
   - 在归一化后的文本中查找
   - 映射回原始位置

3. **模糊匹配**：
   - 滑动窗口遍历所有可能位置
   - 使用 SequenceMatcher 计算相似度
   - 阈值默认 0.75

4. **对齐状态统计**：
   - 精确匹配（exact）：文本完全一致
   - 部分匹配（lesser）：归一化后匹配
   - 模糊匹配（fuzzy）：相似度 ≥ 阈值
   - 未匹配（unmatched）：无法找到匹配

### 五、GraphRAGMiddleware（智能检索流水线）

**专业定义**：GraphRAGMiddleware 是 LangChain Agent 中间件，在用户查询时自动触发知识检索，将相关实体、关系和文档注入到上下文中，提升回答质量。

**通俗解释与类比**：

想象一个智能图书馆助理：
- 用户问"张三得的什么病？"
- 助理先分析问题，提取关键词"张三"
- 快速查找"张三"相关的所有档案
- 查找与"张三"相关的其他人物、疾病、治疗方案
- 把找到的相关信息整理好，递给图书管理员

**在项目中的具体体现**：

GraphRAGMiddleware 的检索流程（middleware.py）：

1. **实体提取**：从查询中提取实体
2. **实体索引查询**：找到包含这些实体的文档
3. **关系遍历**（1-2跳）：
   - 1跳：找到直接相关的实体
   - 2跳：找到相关实体的相关实体
4. **向量重排序**：使用余弦相似度重新排序候选文档
5. **上下文增强**：将检索结果注入到 prompt 中

---

## 🔧 核心技术实现

### 一、向量存储（SimpleVectorStore）

**实现原理**：
- 使用 SQLite 存储文档和元数据
- 内存中存储向量（支持批量添加）
- 按 embedding 模型名称隔离数据

**核心代码**（simple_vector_store.py）：
```python
class SimpleVectorStore:
    def add(self, ids, documents, metadatas, embeddings):
        # 存储到 SQLite
        # 存储向量到内存
        pass
    
    def query(self, query_embeddings, n_results):
        # 计算余弦相似度
        # 返回 top-k 结果
        pass
```

### 二、实体索引结构

**存储格式**：
```python
{
    "张仲景": {
        "type": "人名",
        "doc_ids": {"doc1_chunk0", "doc2_chunk3"},
        "positions": [(100, 104), (500, 504)],
        "alignment_status": "exact",
        "similarity": 1.0
    },
    "桂枝汤": {
        "type": "方剂",
        "doc_ids": {"doc1_chunk1", "doc1_chunk2"},
        ...
    }
}
```

### 三、关系推断算法

**共现关系**：
```python
# 同一文档/段落中出现的实体，推断为相关
for i, source in enumerate(entity_names):
    for target in entity_names[i+1:]:
        relations.append(Relation(
            source=source,
            target=target,
            relation="CO_OCCUR",  # 共现关系
            confidence=0.5
        ))
```

### 四、批量处理优化

**分批策略**：
- 每批处理 5 个文本块
- 批量调用 LLM，减少 API 调用
- 每 20 块暂停一次，给系统喘息时间
- 每 50 块保存一次索引，防止数据丢失

---

## 📁 目录结构

```
skills/graphrag/
├── skill.py                           # GraphRAG Skill 入口
├── knowledge_base.py                  # 知识库管理器
├── word_aligner.py                    # 文本对齐器
├── entity_extractor.py                # 混合实体抽取器
├── graphrag_service.py                # 核心服务
├── dictionary_manager.py              # 词典管理器
├── llm_client.py                      # LLM 客户端
├── middleware.py                      # 自动检索中间件
├── document_manager.py                # 文档管理器
├── word_aligner.py                    # 词对齐器
├── services/
│   ├── __init__.py
│   ├── graphrag_service.py           # 服务层
│   ├── entity_extractor.py           # 实体抽取
│   ├── simple_vector_store.py        # 向量存储
│   ├── simple_embedding.py           # Embedding 函数
│   └── embedding_function.py         # Ollama Embedding
├── utils/
│   ├── __init__.py
│   └── document_processor.py         # 文档处理
└── config/
    └── dictionaries/                 # 全局词典目录
```

---

---

## 🆕 v0.2.6 新增功能：多级分类知识库

### 功能概述

OllamaPilot v0.2.6 新增了多级分类知识库支持，允许用户将知识库按分类组织，实现精准搜索，避免知识污染。

#### 核心特性

- ✅ **多级文件夹结构**：支持一级分类/二级分类/三级分类...
- ✅ **分类搜索**：可搜索整个分类（包含所有子目录）
- ✅ **子分类搜索**：可搜索指定子分类
- ✅ **自定义命名**：完全由用户自定义分类名称

#### 为什么需要分类知识库？

想象你在管理一个大型图书馆：
- **无分类**：所有书混在一起，找书时要翻遍整个图书馆
- **有分类**：医学书放医学区，法律书放法律区，精准定位

GraphRAG 的分类知识库也是如此：
- **无分类**：搜索"麻黄汤"可能返回中医、西医、法律等多领域结果
- **有分类**：在"中医经典"分类中搜索，只返回中医相关结果

### 文件夹结构

```
data/graphrag/
├── 中医经典/                    # 一级分类
│   ├── 伤寒论_qwen3-embedding_0.6b/     # 文档存储
│   ├── 金匮要略_qwen3-embedding_0.6b/
│   └── 伤寒论/                  # 二级分类（子文件夹）
│       ├── 原文_qwen3-embedding_0.6b/
│       └── 注解_qwen3-embedding_0.6b/
├── 现代医学/
│   ├── 内科学_qwen3-embedding_0.6b/
│   └── 外科学_qwen3-embedding_0.6b/
└── 法律法规/
    ├── 刑法_qwen3-embedding_0.6b/
    └── 民法_qwen3-embedding_0.6b/
```

### 新增工具

#### search_knowledge_base - 分类搜索

```python
# 在指定分类中搜索
search_knowledge_base(category="中医经典", query="麻黄汤")

# 在子分类中搜索
search_knowledge_base(category="中医经典/伤寒论", query="太阳病")

# 在现代医学分类中搜索
search_knowledge_base(category="现代医学", query="高血压治疗")
```

#### list_knowledge_categories - 列出分类

```python
# 列出所有分类
categories = list_knowledge_categories()
# 返回：["中医经典", "现代医学", "法律法规", ...]
```

### 创建分类知识库

**步骤一：索引文档**

```bash
# 在 CLI 中索引文档
>>> /index ./knowledge_base/伤寒论.txt
```

**步骤二：创建分类文件夹**

```powershell
# 创建一级分类
mkdir "data/graphrag/中医经典"

# 创建二级分类
mkdir "data/graphrag/中医经典/伤寒论"
```

**步骤三：移动文档存储**

```powershell
# 将文档存储移动到分类中
move "data/graphrag/伤寒论_qwen3-embedding_0.6b" "data/graphrag/中医经典/"
```

**步骤四：搜索验证**

```
# 在 CLI 中搜索
你: 在中医经典分类中搜索麻黄汤
助手: 🔧 执行工具: search_knowledge_base(category='中医经典', query='麻黄汤')
   ✅ 结果: 找到3条相关记录
   📚 来源: 伤寒论 | 相关度: 0.85
```

### 搜索范围规则（重要）

GraphRAG 的分类搜索遵循明确的范围规则：

#### 规则一：用户指定了分类

**行为**：只在用户指定的分类中搜索

```
用户: 根据伤寒论知识库，搜索肺气肿的治疗
调用: search_knowledge_base(category="伤寒论", query="肺气肿治疗")
禁止: 再调用 search_all_documents（这是重复搜索）
```

#### 规则二：用户没说具体分类

**行为**：使用全局搜索

```
用户: 搜索肺气肿的治疗方法
调用: search_all_documents(query="肺气肿治疗方法")
```

#### 规则三：用户问有哪些分类

**行为**：列出所有可用分类

```
用户: 有哪些知识库分类？
调用: list_knowledge_categories()
返回: ["中医经典", "现代医学", "法律法规", ...]
```

### 与全局搜索的关系

| 搜索类型 | 工具 | 范围 | 使用场景 |
|---------|------|------|---------|
| 全局搜索 | `search_all_documents` | 所有文档 | 不确定分类、需要全面搜索 |
| 分类搜索 | `search_knowledge_base` | 指定分类 | 确定分类、需要精准结果 |

### 技术实现

分类知识库的核心实现在 `skills/graphrag/tools.py`：

```python
# skills/graphrag/tools.py

def search_knowledge_base(
    category: str,
    query: str,
    num_results: int = 5
) -> str:
    """
    在指定知识库分类中搜索
    
    实现原理：
    1. 扫描 data/graphrag/{category}/ 目录
    2. 递归查找所有 chroma 子目录
    3. 在每个文档存储中搜索
    4. 合并结果并排序
    """
    # 扫描分类目录
    category_path = Path(f"data/graphrag/{category}")
    
    # 递归查找文档存储
    doc_stores = []
    for chroma_dir in category_path.rglob("chroma"):
        doc_stores.append(chroma_dir.parent)
    
    # 在每个存储中搜索
    results = []
    for store in doc_stores:
        search_result = _search_single_store(store, query)
        results.extend(search_result)
    
    # 合并并排序
    sorted_results = _merge_and_sort(results)
    
    return sorted_results
```

### 向后兼容

原有的 `search_knowledge`（全局搜索）仍然保留：

```python
# 旧的方式：搜索所有文档
results = search_knowledge(query="张仲景治疗太阳病的方剂")

# 新的方式：搜索指定分类
results = search_knowledge_base(category="中医经典", query="麻黄汤")
```

---

## 📖 笔记导航

### 核心文档

1. **[[README]]** - 项目总体介绍
2. **[[架构分析]]** - 系统架构设计
3. **[[运行逻辑]]** - 程序执行流程
4. **[[源码解析]]** - 核心代码分析
5. **[[核心API文档]]** - API 使用指南

### GraphRAG 专题

- **GraphRAG 实现详解** - 本文档，深入理解知识图谱原理
- **实体对齐质量** - WordAligner 对齐统计和使用

---

## 🚀 快速开始

### 添加文档到知识库

```python
from skills.graphrag.tools import upload_document

# 上传文档（自动索引）
upload_document(file_path="./knowledge_base/伤寒论.txt")
```

### 搜索知识

```python
from skills.graphrag.tools import search_knowledge

# 语义搜索
results = search_knowledge(query="张仲景治疗太阳病的方剂")
```

### 查看图谱统计

```python
from skills.graphrag.tools import query_graph_stats

stats = query_graph_stats()
# 返回：文档数、实体数、关系数、实体类型分布
```

---

## 💡 核心优势

| 优势 | 说明 | 生活类比 |
|------|------|---------|
| 混合存储 | 向量+实体+关系三位一体 | 图书馆既有检索系统，又有卡片目录，还有关系图谱 |
| 轻量抽取 | 规则+词典匹配，适合小模型 | 不用请教专家，常识问题自己就能处理 |
| 精确对齐 | WordAligner 溯源验证 | 每条信息都能找到原文出处 |
| 自动增强 | Middleware 透明注入 | 读者问问题，助理自动递上相关资料 |

---

## 📅 笔记信息

- **创建时间**：2026-03-11
- **最近更新**：2026-03-12
- **项目版本**：OllamaPilot v0.2.6（最新）
- **相关组件**：LangChain、Ollama、ChromaDB
- **标签**：#知识图谱 #RAG #GraphRAG #实体抽取 #分类知识库

---

**下一步阅读**：[[源码解析]] - 深入理解核心代码实现 →
