# LangExtract 项目笔记

## 项目概述

**LangExtract** 是由 Google 开发的一个 Python 库，专门用于从非结构化文本中使用大语言模型（LLM）提取结构化信息。它可以帮助用户从临床笔记、报告等材料中识别和整理关键细节，同时确保提取的数据与源文本对应。

**项目地址**：https://github.com/google/langextract

**版本**：1.1.1

**许可证**：Apache-2.0

**Python 版本要求**：>=3.10

---

## 第一步：点出核心组件概念

在深入了解 LangExtract 之前，让我们先认识它的 7 个核心"积木块"：

- **[提取函数（extract）](#提取函数extract)**：整个库的核心入口，就像一个"总指挥"，负责协调整个提取流程
- **[提示词模块（prompting）](#提示词模块prompting）**：负责构建发送给 LLM 的指令，就像"翻译官"，把用户的需求翻译成 LLM 能理解的语言
- **[推理模块（inference）](#推理模块inference）**：负责与各种 LLM 服务交互，就像"外交官"，与外部 API 沟通获取答案
- **[分词器（tokenizer）](#分词器tokenizer）**：负责将长文本切分成小块，就像"裁缝"，把大布料剪成小布料方便处理
- **[数据模块（data）](#数据模块data）**：定义提取结果的数据结构，就像"表格模板"，规定好要填什么内容
- **[模式约束（schema）](#模式约束schema）**：负责验证提取结果是否符合要求，就像"质检员"，确保结果格式正确
- **[可视化模块（visualization）](#可视化模块visualization）**：生成交互式 HTML 报告，就像"画师"，把提取结果以可视化方式展示

---

## 第二步：用图构建组件概念之间的联系

```
[用户输入：文本 + 提取规则]
    |
    v
[提取函数 extract：总指挥]
    |-> 调用 [分词器 tokenizer：裁缝]
    |   |-> 将长文本切分成小块（chunks）
    |   |
    |-> 调用 [提示词模块 prompting：翻译官]
    |   |-> 构建提取指令
    |   |-> 附加示例（few-shot）
    |   |
    |-> 调用 [推理模块 inference：外交官]
    |   |-> 调用 LLM API（Gemini/OpenAI/Ollama）
    |   |-> 获取结构化提取结果
    |   |
    |-> 调用 [模式约束 schema：质检员]
    |   |-> 验证提取结果格式
    |   |-> 确保符合预定义模式
    |   |
    |-> 调用 [数据模块 data：表格模板]
    |   |-> 将结果整理成标准格式
    |   |-> 记录每个提取的位置信息
    |
    v
[输出：结构化提取结果]
    |
    v
[可视化模块 visualization：画师]
    |-> 生成交互式 HTML 报告
    |-> 高亮显示提取内容在原文中的位置
```

**联系说明**：整个提取流程就像一条流水线：用户输入原材料（文本和提取规则），总指挥（extract 函数）协调各个环节，裁缝（tokenizer）把大布料剪成小布料，翻译官（prompting）把需求翻译成指令，外交官（inference）去外部获取答案，质检员（schema）检查质量，表格模板（data）整理结果，最后画师（visualization）生成漂亮的可视化报告。

---

## 第三步：详细解释核心组件

### 提取函数 extract

**专业定义**：`extract` 是 LangExtract 的主入口函数，负责协调整个信息提取流程。

**通俗解释与类比**：想象你要做一道菜，extract 就像厨房里的"总厨师长"。它不会自己切菜或炒菜，但它会指挥切菜工（tokenizer）、调味师（prompting）、灶台（inference）等各个岗位，最后把一道完整的菜（结构化结果）端上桌。

**在此项目中的具体体现**：

```python
import langextract as lx

# 定义提取规则
prompt = "Extract characters and emotions from the text."

# 提供示例
examples = [lx.data.ExampleData(...)]  # 这里填入示例数据

# 运行提取
result = lx.extract(
    text_or_documents="Your input text here",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash"
)
```

这个函数支持很多参数，包括：
- `text_or_documents`：要处理的文本或文档
- `prompt_description`：提取规则描述
- `examples`：few-shot 示例
- `model_id`：使用的模型（如 "gemini-2.5-flash"）
- `max_char_buffer`：每次处理的最大字符数
- `extraction_passes`：提取轮次（多轮提取提高召回率）

---

### 提示词模块 prompting

**专业定义**：prompting 模块负责构建发送给大语言模型的提示词，包括提取规则、示例和上下文。

**通俗解释与类比**：prompting 就像一个"翻译官"或"秘书"。用户想要提取"人物"和"情感"，但 LLM 不懂这些专业术语，秘书需要把它们翻译成 LLM 能理解的"语言"（提示词），同时还要附上几个"例子"让 LLM 知道该怎么做。

**在此项目中的具体体现**：

prompting 模块会根据用户提供的 `prompt_description` 和 `examples` 构建一个完整的提示词，包含：
- 任务描述（要提取什么）
- 示例数据（few-shot learning）
- 输出格式要求
- 约束条件

---

### 推理模块 inference

**专业定义**：inference 模块负责与各种大语言模型服务进行交互，包括 Google Gemini、OpenAI、Ollama 等。

**通俗解释与类比**：inference 就像一个"外交官"或"中间人"。当厨房（LangExtract）需要知道某种食材的味道时，它不会自己跑去问供应商，而是派外交官（inference）去 API 市场（Gemini/OpenAI/Ollama）询问，然后带回答案（结构化结果）。

**在此项目中的具体体现**：

inference 模块支持多种 LLM 提供商：
- **Gemini**：Google 的 LLM 服务
- **OpenAI**：OpenAI 的 GPT 系列
- **Ollama**：本地运行的 LLM
- **其他社区提供者**：通过插件系统支持

---

### 分词器 tokenizer

**专业定义**：tokenizer 负责将长文本切分成较小的块（chunks），以便处理超出模型上下文限制的长文档。

**通俗解释与类比**：tokenizer 就像一个"裁缝"或"分解师"。当你有一大块布料（长文本）但缝纫机一次只能处理一小块时，裁缝需要先把大布料剪成小块，分批处理，最后再拼接起来。

**在此项目中的具体体现**：

LangExtract 使用 `RegexTokenizer` 作为默认分词器，支持：
- 按句子切分
- 按段落切分
- 按字符数限制切分
- 保持块之间的上下文连贯性

---

### 数据模块 data

**专业定义**：data 模块定义了提取结果的数据结构，包括 `Extraction`（单个提取结果）、`ExampleData`（示例数据）、`AnnotatedDocument`（带标注的文档）等。

**通俗解释与类比**：data 就像一个"表格模板"或"填写说明"。就像报销需要填特定的表格一样，提取结果也需要按照预定义的格式来组织，这样后续处理才能统一处理这些数据。

**在此项目中的具体体现**：

核心数据结构包括：
- `Extraction`：单个提取结果，包含提取类别、文本、属性、位置信息等
- `ExampleData`：示例输入和期望的提取结果
- `AnnotatedDocument`：完整的文档，包含所有提取结果

---

### 模式约束 schema

**专业定义**：schema 模块负责定义和验证提取结果的模式约束，确保输出符合预定义的结构。

**通俗解释与类比**：schema 就像一个"质检员"或"门卫"。工厂生产产品需要符合规格，提取结果也需要符合"规格"（模式），质检员会检查产品是否符合要求，不符合的会打回重做。

**在此项目中的具体体现**：

schema 模块提供：
- 模式定义（定义提取结果的格式）
- 约束类型（字符串、枚举、列表等）
- 验证逻辑（检查提取结果是否合法）

---

### 可视化模块 visualization

**专业定义**：visualization 模块负责生成交互式的 HTML 可视化报告，展示提取结果在原文中的位置。

**通俗解释与类比**：visualization 就像一个"画师"或"展示师"。当提取完成后，用户需要"看得见"结果，画师会把原文和提取结果画成一幅直观的图画，高亮显示每条提取在原文中的位置，让人一目了然。

**在此项目中的具体体现**：

```python
import langextract as lx

# 生成可视化报告
lx.visualize(
    annotated_documents=result,  # 提取结果
    output_path="extraction_report.html"  # 输出文件
)
```

这会生成一个独立的 HTML 文件，可以在浏览器中打开查看。

---

## 核心功能特点

### 1. 精确的源文本映射

LangExtract 能够将每个提取结果映射到源文本中的确切位置，实现可视化高亮显示，方便追溯和验证。

### 2. 可靠的结构化输出

通过 few-shot 示例和模式约束，确保提取结果符合预定义格式，利用受控生成技术保证输出质量。

### 3. 长文档优化

通过智能文本分块、并行处理和多轮提取，解决"大海捞针"问题，提高长文档提取的召回率。

### 4. 灵活的 LLM 支持

支持 Google Gemini、OpenAI、Ollama（本地模型）等多种 LLM，用户可以根据需求选择。

### 5. 交互式可视化

生成独立的交互式 HTML 文件，方便查看和审核大量提取结果。

### 6. Vertex AI 批量处理

支持使用 Vertex AI Batch API 进行大规模批量处理，可显著降低成本。只需在参数中启用 `language_model_params={"vertexai": True, "batch": {"enabled": True}}`。

### 7. RadExtract 实时演示

提供基于 HuggingFace Spaces 的 RadExtract 实时演示，可以直接在浏览器中体验 radiology report（放射学报告）结构化的功能，无需任何设置。

---

## 相关文档

- [[langextract/架构分析|架构分析]] - 深入了解系统架构设计
- [[langextract/运行逻辑|运行逻辑]] - 了解程序执行流程
- [[langextract/源码解析|源码解析]] - 深入分析核心源码
- [[langextract/核心API文档|核心API文档]] - API 使用详解
