# LangExtract 核心 API 文档

## 概述

本文档详细介绍 LangExtract 的核心 API，包括主提取函数、可视化函数、数据模型和配置选项。

---

## 第一步：点出核心 API 组件概念

LangExtract API 由以下核心组件构成：

- **[lx.extract()](#lxextract)**：主提取函数，就像"总指挥"协调整个提取流程
- **[lx.visualize()](#lxvisualize)**：可视化函数，就像"画师"生成交互式报告
- **[lx.data](#lxdata)**：数据模型命名空间，包含所有数据结构定义，就像"表格模板"
- **[lx.providers](#lxproviders)**：LLM 提供者命名空间，支持多种模型，就像"万能适配器"

---

## 第二步：用图构建 API 关系

```
[用户代码]
    |
    v
+----------------------------------------------------------+
|                    公开 API 入口                          |
|                                                          |
|    import langextract as lx                             |
|                                                          |
|    lx.extract(...)     # 提取主函数                      |
|    lx.visualize(...)   # 可视化函数                       |
+----------------------------------------------------------+
    |                           |
    v                           v
+------------------+    +------------------+
|  lx.data         |    |  lx.providers    |
| 数据模型命名空间  |    | 提供者命名空间   |
+------------------+    +------------------+
| ExampleData      |    | GeminiProvider   |
| Extraction       |    | OpenAIProvider   |
| Document         |    | OllamaProvider   |
| AnnotatedDocument|    | ModelConfig      |
+------------------+    +------------------+
```

**API 关系说明**：用户代码像"顾客"，通过入口（lx.extract、lx.visualize）点餐。入口后面连接着两个"厨房"：数据厨房（lx.data）负责准备表格模板，提供者厨房（lx.providers）负责准备食材（调用 LLM）。

---

## 第三步：核心 API 详细说明

### lx.extract

**函数签名**：

```python
langextract.extract(
    text_or_documents: str | Document | Iterable[Document],
    prompt_description: str | None = None,
    examples: Sequence[ExampleData] | None = None,
    model_id: str = "gemini-2.5-flash",
    api_key: str | None = None,
    format_type: type[BaseModel] | FormatType | str | None = None,
    max_char_buffer: int = 1000,
    temperature: float | None = None,
    use_schema_constraints: bool = True,
    batch_length: int = 10,
    max_workers: int = 10,
    additional_context: str | None = None,
    resolver_params: dict | None = None,
    language_model_params: dict | None = None,
    debug: bool = False,
    model_url: str | None = None,
    extraction_passes: int = 1,
    context_window_chars: int | None = None,
    config: ModelConfig | None = None,
    model: BaseLanguageModel | None = None,
    *,
    fetch_urls: bool = True,
    prompt_validation_level: PromptValidationLevel = WARNING,
    prompt_validation_strict: bool = False,
    show_progress: bool = True,
    tokenizer: Tokenizer | None = None,
) -> list[AnnotatedDocument] | AnnotatedDocument
```

**功能说明**：

`extract` 是 LangExtract 的主入口函数，用于从文本中提取结构化信息。

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text_or_documents` | str / Document / Iterable[Document] | 必填 | 要处理的文本、URL 或文档列表 |
| `prompt_description` | str | None | 提取规则描述，告诉 LLM 要提取什么 |
| `examples` | Sequence[ExampleData] | None | few-shot 示例，帮助 LLM 理解任务 |
| `model_id` | str | "gemini-2.5-flash" | 使用的模型 ID |
| `api_key` | str | None | API 密钥，也可通过环境变量 `LANGEXTRACT_API_KEY` 设置 |
| `format_type` | type[BaseModel] / FormatType / str | None | 输出格式类型（JSON 或 YAML） |
| `max_char_buffer` | int | 1000 | 每次处理的最大字符数，影响 API 调用次数 |
| `temperature` | float | None | 采样温度，控制输出的随机性 |
| `use_schema_constraints` | bool | True | 是否使用模式约束验证 |
| `batch_length` | int | 10 | 每批处理的块数 |
| `max_workers` | int | 10 | 并行工作数 |
| `additional_context` | str | None | 额外上下文信息 |
| `resolver_params` | dict | None | 解析器参数 |
| `language_model_params` | dict | None | 语言模型额外参数 |
| `debug` | bool | False | 是否输出调试信息 |
| `model_url` | str | None | 自定义模型 URL（用于 Ollama 等） |
| `extraction_passes` | int | 1 | 提取轮次，多轮可提高召回率 |
| `context_window_chars` | int | None | 上下文窗口大小 |
| `config` | ModelConfig | None | 模型配置对象 |
| `model` | BaseLanguageModel | None | 自定义语言模型实例 |
| `fetch_urls` | bool | True | 是否自动获取 URL 内容 |
| `prompt_validation_level` | PromptValidationLevel | WARNING | 提示词验证级别 |
| `prompt_validation_strict` | bool | False | 是否严格验证提示词 |
| `show_progress` | bool | True | 是否显示进度条 |
| `tokenizer` | Tokenizer | None | 自定义分词器 |

**返回值**：

- `AnnotatedDocument`：单个文档的提取结果
- `list[AnnotatedDocument]`：多个文档的提取结果列表

**使用示例**：

```python
import langextract as lx
import textwrap

# 定义提取规则
prompt = textwrap.dedent("""\
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.""")

# 提供示例
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light through yonder window breaks?",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO"
            ),
            lx.data.Extraction(
                extraction_class="emotion",
                extraction_text="But soft!"
            )
        ]
    )
]

# 运行提取
result = lx.extract(
    text_or_documents="Juliet gazed at the stars...",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    api_key="your-api-key"
)
```

---

### lx.visualize

**函数签名**：

```python
langextract.visualize(
    annotated_documents: AnnotatedDocument | list[AnnotatedDocument],
    output_path: str = "extraction_report.html",
    title: str = "Extraction Report",
    colors: dict | None = None,
    show_text: bool = True,
    height: int | None = None,
    width: str | None = None,
    pattern: str | None = None,
    patterns: dict | None = None,
    overwrite: bool = True,
    open_in_browser: bool = True,
    open_in_tab: bool = True,
) -> str
```

**功能说明**：

`visualize` 函数生成交互式 HTML 可视化报告，展示提取结果在原文中的位置。

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `annotated_documents` | AnnotatedDocument / list[AnnotatedDocument] | 必填 | 提取结果 |
| `output_path` | str | "extraction_report.html" | 输出文件路径 |
| `title` | str | "Extraction Report" | 报告标题 |
| `colors` | dict | None | 自定义颜色映射 |
| `show_text` | bool | True | 是否显示原文文本 |
| `height` | int | None | 报告高度 |
| `width` | str | None | 报告宽度 |
| `pattern` | str | None | 高亮样式模式 |
| `patterns` | dict | None | 多个高亮样式 |
| `overwrite` | bool | True | 是否覆盖已存在的文件 |
| `open_in_browser` | bool | True | 是否在浏览器中打开 |
| `open_in_tab` | bool | True | 是否在新标签页打开 |

**返回值**：

返回生成的文件路径（str）。

**使用示例**：

```python
import langextract as lx

# 提取数据
result = lx.extract(...)

# 生成可视化报告
output_file = lx.visualize(
    result,
    output_path="extraction_report.html",
    title="My Extraction Report"
)
```

---

### lx.data

**命名空间说明**：

`lx.data` 命名空间包含所有核心数据模型，用于定义输入和输出数据的结构。

**核心数据模型**：

#### ExampleData

```python
class ExampleData:
    """示例数据，用于 few-shot 学习。"""
    
    text: str  # 输入文本
    extractions: list[Extraction]  # 期望的提取结果
```

#### Extraction

```python
class Extraction:
    """单个提取结果。"""
    
    extraction_class: str  # 提取类别（如 "character"、"emotion"）
    extraction_text: str  # 提取的文本
    attributes: dict[str, Any] | None = None  # 附加属性
    source_start: int | None = None  # 原文起始位置
    source_end: int | None = None  # 原文结束位置
```

#### Document

```python
class Document:
    """待处理的文档。"""
    
    text: str  # 文档文本
    id: str | None = None  # 文档 ID
    metadata: dict[str, Any] | None = None  # 元数据
```

#### AnnotatedDocument

```python
class AnnotatedDocument:
    """带标注的文档（提取结果）。"""
    
    text: str  # 原始文本
    extractions: list[Extraction]  # 提取结果列表
    document_id: str | None = None  # 文档 ID
    metadata: dict[str, Any] | None = None  # 元数据
```

---

### lx.providers

**命名空间说明**：

`lx.providers` 命名空间包含各种 LLM 提供者的实现和配置。

#### ModelConfig

```python
class ModelConfig:
    """模型配置。"""
    
    model_id: str  # 模型 ID
    provider: str  # 提供者名称（"gemini"、"openai"、"ollama" 等）
    api_key: str | None = None  # API 密钥
    model_url: str | None = None  # 自定义模型 URL
    default_params: dict | None = None  # 默认参数
```

#### 内置模型 ID

LangExtract 支持以下内置模型 ID：

| 模型 ID | 提供者 | 说明 |
|---------|--------|------|
| `gemini-2.5-flash` | Google Gemini | 默认模型 |
| `gemini-2.0-flash` | Google Gemini | Gemini 2.0 |
| `gemini-1.5-pro` | Google Gemini | Gemini 1.5 Pro |
| `gemini-1.5-flash` | Google Gemini | Gemini 1.5 Flash |
| `gpt-4o` | OpenAI | GPT-4 Omni |
| `gpt-4o-mini` | OpenAI | GPT-4 Omni Mini |
| `gpt-4-turbo` | OpenAI | GPT-4 Turbo |
| `gpt-3.5-turbo` | OpenAI | GPT-3.5 Turbo |
| `ollama/*` | Ollama | Ollama 本地模型 |

#### 自定义 Ollama 模型

```python
import langextract as lx

# 使用本地 Ollama 模型
result = lx.extract(
    text_or_documents="Your text here",
    prompt_description="Extract information.",
    model_id="ollama/llama2",  # 使用 Ollama 的 llama2 模型
    model_url="http://localhost:11434"  # Ollama 服务地址
)
```

---

## 高级用法

### 使用自定义模型

```python
from langextract.providers import MyCustomProvider

# 创建自定义提供者
custom_provider = MyCustomProvider(api_key="...")

# 使用自定义模型
result = lx.extract(
    text_or_documents="Your text here",
    prompt_description="Extract information.",
    model=custom_provider
)
```

### 使用模式约束

```python
from langextract.core.schema import BaseSchema, Constraint, ConstraintType

# 定义输出模式
class MySchema(BaseSchema):
    characters: list[str]
    emotions: list[str]

# 使用模式约束
result = lx.extract(
    text_or_documents="Your text here",
    prompt_description="Extract characters and emotions.",
    format_type=MySchema,
    use_schema_constraints=True
)
```

### 多轮提取提高召回率

```python
# 使用多轮提取
result = lx.extract(
    text_or_documents="Very long document...",
    prompt_description="Extract all entities.",
    examples=examples,
    extraction_passes=2,  # 两轮提取
    max_char_buffer=500   # 较小的块大小
)
```

---

## 相关文档

- [[langextract/README|项目概述]] - 了解项目整体定位
- [[langextract/架构分析|架构分析]] - 深入了解系统架构设计
- [[langextract/运行逻辑|运行逻辑]] - 了解程序执行流程
- [[langextract/源码解析|源码解析]] - 深入分析核心源码
