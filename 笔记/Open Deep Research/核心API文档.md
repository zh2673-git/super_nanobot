# Open Deep Research 核心 API 文档

## 核心概念

- **[init_chat_model](init_chat_model.md)**：通用聊天模型初始化函数
- **[StateGraph](StateGraph.md)**：状态图构建器
- **[Command](Command.md)**：LangGraph 的节点跳转指令
- **[Configuration](Configuration.md)**：配置管理类
- **[get_all_tools](get_all_tools.md)**：获取可用搜索工具

## 核心 API

### 1. 模型初始化 API

#### init_chat_model

**位置**：LangChain 库

**功能**：初始化一个可配置的聊天模型

**用法**：
```python
from langchain.chat_models import init_chat_model

# 初始化可配置模型
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)
```

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| configurable_fields | tuple | 可配置的字段，支持 "model"、"max_tokens"、"api_key" |

**返回值**：可配置的聊天模型实例

**通俗解释**：这个函数像创建一个"万能遥控器"，可以通过配置参数来控制不同的模型（如 OpenAI GPT-4、Anthropic Claude 等），实现模型无关性。

### 2. 图构建 API

#### StateGraph

**位置**：LangGraph 库

**功能**：构建状态图，定义研究流程

**用法**：
```python
from langgraph.graph import START, END, StateGraph

# 创建状态图
graph = StateGraph(AgentState)

# 添加节点
graph.add_node("clarify_with_user", clarify_with_user)
graph.add_node("write_research_brief", write_research_brief)
graph.add_node("research_supervisor", research_supervisor)

# 添加边
graph.add_edge(START, "clarify_with_user")
graph.add_edge("clarify_with_user", "write_research_brief")
graph.add_edge("write_research_brief", "research_supervisor")

# 编译图
research_graph = graph.compile()
```

**核心方法**：
| 方法 | 说明 |
|------|------|
| add_node(name, func) | 添加节点 |
| add_edge(source, target) | 添加边 |
| add_conditional_edges(source, func) | 添加条件边 |
| compile() | 编译图 |

### 3. 状态流转 API

#### Command

**位置**：LangGraph 库

**功能**：在节点中控制流程跳转和状态更新

**用法**：
```python
from langgraph.types import Command

# 简单跳转
return Command(goto="next_node")

# 跳转并更新状态
return Command(
    goto="research_supervisor",
    update={
        "messages": [AIMessage(content="研究已开始")],
        "research_brief": research_brief,
    }
)

# 条件跳转
if need_clarification:
    return Command(goto=END, update={"messages": [AIMessage(content=question)]})
else:
    return Command(goto="write_research_brief", update={"messages": [AIMessage(content=verification)]})
```

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| goto | str 或 END | 下一个节点 |
| update | dict | 更新的状态 |

### 4. 配置管理 API

#### Configuration.from_runnable_config

**位置**：项目代码

**功能**：从运行时配置获取配置对象

**用法**：
```python
from langchain_core.runnables import RunnableConfig
from open_deep_research.configuration import Configuration

def some_node(state: AgentState, config: RunnableConfig):
    # 从配置中获取配置对象
    configurable = Configuration.from_runnable_config(config)
    
    # 访问配置项
    max_iterations = configurable.max_researcher_iterations
    search_api = configurable.search_api
```

### 5. 搜索工具 API

#### get_all_tools

**位置**：项目 utils.py

**功能**：获取所有可用的搜索工具

**用法**：
```python
from open_deep_research.utils import get_all_tools

# 获取搜索工具列表
tools = get_all_tools(configurable, model)
```

**返回值**：搜索工具列表（TavilySearch、openai_websearch、anthropic_websearch 等）

### 6. 结构化输出 API

#### with_structured_output

**功能**：为模型添加结构化输出能力

**用法**：
```python
from open_deep_research.state import ClarifyWithUser

# 创建结构化输出模型
clarification_model = (
    configurable_model
    .with_structured_output(ClarifyWithUser)  # 指定输出结构
    .with_retry(stop_after_attempt=3)         # 添加重试
    .with_config(model_config)
)
```

#### with_retry

**功能**：为模型添加自动重试能力

**用法**：
```python
model_with_retry = model.with_retry(
    stop_after_attempt=3,    # 最多重试次数
    wait_exponential_jitter=True  # 指数退避抖动
)
```

### 7. 消息处理 API

#### HumanMessage / AIMessage / ToolMessage

**位置**：LangChain Core

**功能**：创建不同类型的消息

**用法**：
```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 用户消息
user_msg = HumanMessage(content="帮我研究一下人工智能的发展历史")

# AI 消息
ai_msg = AIMessage(content="我来帮你研究这个问题")

# 工具消息
tool_msg = ToolMessage(content="搜索结果...", tool_call_id="xxx")
```

### 8. 工具调用 API

#### bind_tools

**功能**：为模型绑定工具，使其能够调用

**用法**：
```python
# 绑定搜索工具
model_with_tools = model.bind_tools(tools)

# 调用模型
response = await model_with_tools.ainvoke(messages)
```

## 常用配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| max_researcher_iterations | int | 6 | 最大研究迭代次数 |
| max_concurrent_research_units | int | 5 | 最大并发研究单元数 |
| allow_clarification | bool | True | 是否允许澄清问题 |
| search_api | SearchAPI | TAVILY | 搜索 API |
| research_model | str | openai:gpt-4.1 | 研究用模型 |
| summarization_model | str | openai:gpt-4.1-mini | 总结用模型 |
| final_report_model | str | openai:gpt-4.1 | 报告生成模型 |

## 搜索 API 枚举

```python
from open_deep_research.configuration import SearchAPI

# 可选的搜索 API
SearchAPI.TAVILY       # Tavily 搜索
SearchAPI.OPENAI       # OpenAI 原生搜索
SearchAPI.ANTHROPIC    # Anthropic 原生搜索
SearchAPI.NONE         # 无搜索
```

## 状态类型

```python
from open_deep_research.state import (
    AgentState,          # 全局状态
    SupervisorState,    # 监督者状态
    ResearcherState,    # 研究者状态
    ClarifyWithUser,    # 澄清结果
    ResearchQuestion,   # 研究问题
    ConductResearch,    # 研究执行
    ResearchComplete,   # 研究完成
)
```

## 提示词模板

```python
from open_deep_research.prompts import (
    research_system_prompt,              # 研究系统提示
    lead_researcher_prompt,              # 主导研究员提示
    final_report_generation_prompt,     # 最终报告生成提示
    compress_research_system_prompt,    # 研究压缩提示
    clarify_with_user_instructions,     # 澄清指令
    transform_messages_into_research_topic_prompt,  # 转换为研究主题
)
```
