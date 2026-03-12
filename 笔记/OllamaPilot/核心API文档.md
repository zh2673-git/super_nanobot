# OllamaPilot 核心API文档

> 快速上手和深入使用的API指南

---

## 🎯 第一步：认识三大核心API

OllamaPilot 的 API 设计就像一个简洁的工具箱，只有三个核心工具：

- **init_ollama_model**：初始化模型，像准备工具（选择合适的模型、配置参数）
- **create_agent**：创建Agent，像组装工具（连接模型、加载 Skill、配置中间件）
- **agent.invoke**：执行对话，像使用工具（发送查询、获取回复）

**为什么这么简洁？**

传统的 AI Agent 框架：
- 需要配置几十个参数
- 要理解复杂的类继承关系
- 调用流程繁琐
- 错误排查困难

OllamaPilot 的设计理念：
- **开箱即用**：默认配置开箱即用，覆盖 90% 使用场景
- **渐进式**：简单需求简单调用，复杂需求逐步配置
- **标准接口**：遵循 LangChain 标准，易于理解和扩展

---

## 📊 第二步：API 调用关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     API 调用层级                               │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  第一层：模型初始化                                        │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  model = init_ollama_model("qwen3.5:4b")             ││ │
│  │  │    ↓                                                  ││ │
│  │  │  - 连接 Ollama 服务                                   ││ │
│  │  │  - 加载模型                                           ││ │
│  │  │  - 配置参数（温度、上下文窗口等）                     ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  第二层：Agent 创建                                        │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  agent = create_agent(model, skills_dir="skills")    ││ │
│  │  │    ↓                                                  ││ │
│  │  │  - 加载 Skill                                         ││ │
│  │  │  - 配置中间件                                         ││ │
│  │  │  - 初始化工具                                         ││ │
│  │  │  - 设置记忆                                           ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  第三层：对话执行                                          │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  response = agent.invoke("你好")                     ││ │
│  │  │    ↓                                                  ││ │
│  │  │  - 选择 Skill                                         ││ │
│  │  │  - 模型推理                                           ││ │
│  │  │  - 工具调用                                           ││ │
│  │  │  - 返回结果                                           ││ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 第三步：核心API详解

### 一、init_ollama_model - 初始化模型

**专业定义**：初始化 Ollama 本地模型，返回 LangChain 的 ChatOllama 实例，针对小模型性能进行了优化配置。

**通俗解释与类比**：
这就像准备一个智能助手：
- 选择合适的助手（指定模型名称）
- 设置助手的工作模式（配置温度、上下文等参数）
- 确保助手已经准备好（连接 Ollama 服务）

**API 签名**：
```python
def init_ollama_model(
    model: str,
    temperature: float = 0.7,
    base_url: str = "http://localhost:11434",
    **kwargs
) -> ChatOllama
```

**参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| model | str | ✓ | - | 模型名称，如 "qwen3.5:4b" |
| temperature | float | ✗ | 0.7 | 温度参数，控制随机性（0-2） |
| base_url | str | ✗ | "http://localhost:11434" | Ollama 服务地址 |
| **kwargs | Any | ✗ | - | 其他参数传递给 ChatOllama |

**使用示例**：

```python
from ollamapilot import init_ollama_model

# 最简单使用（使用默认参数）
model = init_ollama_model("qwen3.5:4b")

# 自定义温度
model = init_ollama_model("qwen3.5:4b", temperature=0.5)

# 自定义 Ollama 服务地址
model = init_ollama_model("qwen3.5:4b", base_url="http://192.168.1.100:11434")

# 高级配置
model = init_ollama_model(
    "qwen3.5:4b",
    temperature=0.7,
    num_ctx=8192,       # 上下文窗口大小
    num_predict=2048,   # 最大生成长度
    top_p=0.9,          # 核采样参数
    top_k=40,           # TopK 采样参数
)
```

**小模型优化配置详解**：
```python
# models.py 中的默认优化配置
ChatOllama(
    model=model,
    temperature=temperature,
    base_url=base_url,
    num_ctx=8192,       # 上下文窗口：8K tokens
                        # - 足够长的对话历史
                        # - 平衡内存和性能
    
    num_predict=2048,   # 最大生成长度：2K tokens
                        # - 限制输出长度
                        # - 防止生成过长无意义内容
    
    top_p=0.9,          # 核采样：90%
                        # - 过滤掉概率低的token
                        # - 提高生成质量
    
    top_k=40,           # TopK 采样：40
                        # - 只考虑概率最高的40个token
                        # - 减少计算量
    
    repeat_penalty=1.1, # 重复惩罚：1.1
                        # - 惩罚重复内容
                        # - 提高多样性
)
```

**常见问题**：

**Q：如何查看可用的模型？**
```python
from ollamapilot import list_ollama_models

models = list_ollama_models()
print(models)  # ['qwen3.5:4b', 'llama3.1:8b', ...]
```

**Q：如果 Ollama 服务未启动会怎样？**
```python
try:
    model = init_ollama_model("qwen3.5:4b")
except Exception as e:
    print(f"连接失败: {e}")
```

**Q：温度参数如何选择？**
- `temperature=0.1`：确定性高，适合事实性任务（如数据提取）
- `temperature=0.7`：平衡，适合通用对话（默认值）
- `temperature=1.5`：创意性高，适合创意写作

### 二、create_agent - 创建Agent

**专业定义**：创建 OllamaPilot Agent 实例，配置 Skill、中间件、工具、记忆等组件，返回可执行的 Agent 对象。

**通俗解释与类比**：
这就像组装一个完整的智能助手：
- 把模型连接到工具库（加载 Skill）
- 配置工作流程（设置中间件）
- 准备记忆笔记本（配置对话记忆）
- 测试助手是否正常（初始化检查）

**API 签名**：
```python
def create_agent(
    model: BaseChatModel,
    skills_dir: Optional[str] = None,
    enable_memory: bool = True,
    max_tool_calls: int = 50,
    verbose: bool = True,
    checkpointer=None,
    tools: Optional[List[BaseTool]] = None,
    **kwargs
) -> OllamaPilotAgent
```

**参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| model | BaseChatModel | ✓ | - | 模型实例（从 init_ollama_model 获取） |
| skills_dir | str | ✗ | None | Skill 目录路径 |
| enable_memory | bool | ✗ | True | 是否启用对话记忆 |
| max_tool_calls | int | ✗ | 50 | 最大工具调用次数 |
| verbose | bool | ✗ | True | 是否显示详细日志 |
| checkpointer | Any | ✗ | None | 自定义记忆存储 |
| tools | List[BaseTool] | ✗ | None | 自定义工具列表 |
| **kwargs | Any | ✗ | - | 其他参数 |

**使用示例**：

```python
from ollamapilot import init_ollama_model, create_agent

# 初始化模型
model = init_ollama_model("qwen3.5:4b")

# 最简单使用
agent = create_agent(model)

# 加载 Skill
agent = create_agent(model, skills_dir="skills")

# 禁用记忆
agent = create_agent(model, enable_memory=False)

# 限制工具调用次数
agent = create_agent(model, max_tool_calls=10)

# 关闭详细日志
agent = create_agent(model, verbose=False)

# 完整配置
agent = create_agent(
    model,
    skills_dir="skills",
    enable_memory=True,
    max_tool_calls=50,
    verbose=True
)
```

**创建后的初始化流程**：

```python
# agent.py 中的 __init__ 方法
def __init__(self, model, skills_dir, enable_memory, ...):
    # 1. 初始化 Skill 注册中心
    self.skill_registry = SkillRegistry()
    if skills_dir:
        count = self.skill_registry.discover_skills(skills_dir)
        print(f"📦 已加载 {count} 个 Skill")
    
    # 2. 收集内置工具
    self.builtin_tools = self._get_builtin_tools()
    
    # 3. 配置记忆
    if enable_memory:
        self.checkpointer = MemorySaver()
    else:
        self.checkpointer = None
    
    # 4. 构建中间件
    middleware = self._build_middleware(max_tool_calls)
    
    # 5. 创建 Agent
    self.agent = lc_create_agent(
        model=model.bind_tools(self.builtin_tools),
        tools=self.builtin_tools,
        middleware=middleware,
        checkpointer=self.checkpointer,
    )
```

**常见问题**：

**Q：如何添加自定义 Skill？**
```python
# 方式一：放入 skills 目录
# 创建 skills/my_skill/SKILL.md
agent = create_agent(model, skills_dir="skills")

# 方式二：Python Skill
from ollamapilot import Skill

class MySkill(Skill):
    name = "my_skill"
    description = "我的 Skill"
    triggers = ["关键词"]
    
    def get_tools(self):
        return [...]

# 注册到全局
from ollamapilot import SkillRegistry
registry = SkillRegistry()
registry.register(MySkill)
```

**Q：如何不加载任何 Skill？**
```python
# 不传递 skills_dir 参数
agent = create_agent(model)
# 仅使用 Default Skill
```

**Q：如何自定义中间件？**
```python
from langchain.agents.middleware import AgentMiddleware

class MyMiddleware(AgentMiddleware):
    def before_model(self, state, runtime):
        # 在模型调用前的处理
        return None

agent = OllamaPilotAgent(
    model,
    middleware=[MyMiddleware()]
)
```

### 三、agent.invoke - 执行对话

**专业定义**：执行用户查询，经过 Skill 选择、模型推理、工具调用等流程，返回最终回复。

**通俗解释与类比**：
这就像向智能助手提问：
- 告诉助手你的问题（输入查询）
- 助手分析问题、查找资料（Skill 选择、工具调用）
- 助手整理答案（生成回复）
- 记录这次对话（保存记忆）

**API 签名**：
```python
def invoke(
    self,
    query: str,
    thread_id: Optional[str] = None
) -> str
```

**参数说明**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | str | ✓ | - | 用户查询 |
| thread_id | str | ✗ | "default" | 对话线程ID，用于区分不同对话 |

**使用示例**：

```python
from ollamapilot import init_ollama_model, create_agent

model = init_ollama_model("qwen3.5:4b")
agent = create_agent(model, skills_dir="skills")

# 单轮对话
response = agent.invoke("明天苏州天气怎么样？")
print(response)

# 多轮对话（同一个 thread_id）
response1 = agent.invoke("你好，我叫张三", thread_id="session_1")
response2 = agent.invoke("你还记得我的名字吗？", thread_id="session_1")
# AI 会记得"张三"

# 不同的对话（不同的 thread_id）
response3 = agent.invoke("你好", thread_id="session_2")
# AI 不知道"张三"
```

**对话记忆管理**：

```python
# 获取对话历史
history = agent.get_history(thread_id="session_1")
print(f"对话历史: {len(history)} 条消息")

# 清除对话历史
agent.clear_history(thread_id="session_1")
```

**流式输出**：

```python
# 流式生成回复
for chunk in agent.stream("写一首诗", thread_id="session_1"):
    print(chunk, end="", flush=True)
```

**执行流程详解**：

```python
# agent.py 中的 invoke 方法
def invoke(self, query: str, thread_id: Optional[str] = None) -> str:
    # 1. 显示用户输入
    if self.verbose:
        print(f"🤖 用户: {query}")
    
    # 2. 选择并显示 Skill
    skill = self._select_skill_for_query(query)
    if skill and self.verbose:
        print(f"🎯 激活 Skill: {skill.name}")
    
    # 3. 配置对话 ID
    config = {"configurable": {"thread_id": thread_id or "default"}}
    
    # 4. 执行 Agent
    result = self.agent.invoke(
        {"messages": [HumanMessage(content=query)]},
        config
    )
    
    # 5. 提取回复
    messages = result.get("messages", [])
    last_message = messages[-1]
    return last_message.content
```

---

## 🔧 第四步：Skill 开发API

### Skill 基类

**专业定义**：所有 Skill 的抽象基类，定义了 Skill 的标准接口和元数据结构。

**通俗解释与类比**：
这就像一个"技能模板"，规定了每个技能必须包含的信息：
- 技能名称（name）
- 技能描述（description）
- 触发条件（triggers）
- 技能工具（tools）
- 技能说明（system_prompt）

**API 签名**：
```python
from ollamapilot import Skill

class MySkill(Skill):
    # 元数据
    name: str = "my_skill"
    description: str = "我的自定义技能"
    tags: List[str] = ["实用工具"]
    version: str = "1.0.0"
    author: str = "Your Name"
    triggers: List[str] = ["关键词1", "关键词2"]
    
    # 必须实现
    def get_tools(self) -> List[BaseTool]:
        """返回 Skill 提供的工具"""
        return [...]
    
    # 可选实现
    def get_system_prompt(self) -> Optional[str]:
        """返回系统提示词"""
        return "你是..."
```

**完整示例**：

```python
from langchain_core.tools import tool
from ollamapilot import Skill

class WeatherSkill(Skill):
    """天气查询 Skill"""
    
    name = "weather"
    description = "查询城市天气信息"
    tags = ["实用工具", "天气"]
    version = "1.0.0"
    author = "OllamaPilot"
    triggers = ["天气", "温度", "下雨", "weather"]
    
    @tool
    def get_weather(city: str) -> str:
        """
        获取城市天气
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息
        """
        # 实际实现...
        return f"{city}明天晴，温度6-14℃"
    
    def get_tools(self) -> List[BaseTool]:
        return [self.get_weather]
    
    def get_system_prompt(self) -> str:
        return """你是天气查询专家，帮助用户获取天气信息。

工作流程：
1. 使用 get_weather 工具查询天气
2. 整理信息返回给用户

注意事项：
- 确认城市名称
- 提供准确的天气信息"""
```

### Markdown Skill（SKILL.md）

**专业定义**：基于 Markdown 配置文件的 Skill，无需编写 Python 代码，通过 YAML Front Matter 定义元数据，Markdown 正文定义系统提示词。

**通俗解释与类比**：
这就像填写一个"技能申请表"，只需填写信息，无需写代码：
- 基本信息（name、description、triggers）
- 所需工具（tools）
- 工作说明（系统提示词）

**文件格式**：
```yaml
---
name: weather
description: 查询天气信息
tags: [实用工具, 天气]
version: 1.0.0
author: OllamaPilot
triggers: [天气, 温度, 下雨]
tools:
  - web_search
  - web_fetch
---

# 天气查询助手

你是天气查询专家，帮助用户获取天气信息。

## 工作流程
1. 使用 web_search 搜索城市天气
2. 使用 web_fetch 获取详细页面
3. 整理天气信息返回给用户

## 注意事项
- 确认城市名称准确
- 提供温度、天气状况、空气质量等信息
```

**工具类型详解**：

```yaml
tools:
  # 1. 内置工具（直接使用名称）
  - web_search      # 网络搜索
  - web_fetch       # 获取网页
  - python_exec     # 执行 Python
  - read_file       # 读文件
  - write_file      # 写文件
  - list_directory  # 列目录
  - search_files    # 搜索文件
  - shell_exec      # 执行命令
  - shell_script    # 执行脚本
  
  # 2. MCP 工具（需要配置 MCP 服务器）
  - mcp://weather_api/get_current
  - mcp://weather_api/get_forecast
  
  # 3. 自定义工具（从当前目录加载）
  - custom://local_tool.py:get_weather
```

---

## 🛠️ 第五步：内置工具API

### 文件操作工具

#### read_file - 读取文件

```python
@tool
def read_file(file_path: str, limit: int = 1000) -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径（相对或绝对）
        limit: 最大读取行数，默认1000行
        
    Returns:
        文件内容
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用
agent.invoke("读取 main.py 文件的前 50 行")

# 直接调用工具
from ollamapilot.tools.builtin import read_file
content = read_file.invoke({"file_path": "main.py", "limit": 50})
```

#### write_file - 写入文件

```python
@tool
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    写入文件内容
    
    Args:
        file_path: 文件路径
        content: 文件内容
        append: 是否追加模式，默认False（覆盖）
        
    Returns:
        操作结果
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用
agent.invoke("创建 test.txt 文件，内容是 Hello World")

# 直接调用工具
from ollamapilot.tools.builtin import write_file
result = write_file.invoke({
    "file_path": "test.txt",
    "content": "Hello World"
})
```

#### list_directory - 列出目录

```python
@tool
def list_directory(dir_path: str = ".", recursive: bool = False) -> str:
    """
    列出目录内容
    
    Args:
        dir_path: 目录路径，默认当前目录
        recursive: 是否递归列出子目录，默认False
        
    Returns:
        目录内容列表
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用
agent.invoke("列出当前目录下的所有文件")

# 直接调用工具
from ollamapilot.tools.builtin import list_directory
result = list_directory.invoke({"dir_path": ".", "recursive": False})
```

### 网络工具

#### web_search - 网络搜索

```python
@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    在互联网上搜索信息
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数，默认5条
        
    Returns:
        搜索结果列表
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用（Weather Skill 会调用）
agent.invoke("明天苏州天气怎么样？")

# 直接调用工具
from ollamapilot.tools.builtin import web_search
results = web_search.invoke({"query": "LangChain 教程", "max_results": 10})
```

#### web_fetch - 获取网页

```python
@tool
def web_fetch(url: str) -> str:
    """
    获取网页内容
    
    Args:
        url: 网页URL
        
    Returns:
        网页内容（Markdown格式）
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用（Weather Skill 会调用）
agent.invoke("明天苏州天气怎么样？")

# 直接调用工具
from ollamapilot.tools.builtin import web_fetch
content = web_fetch.invoke({"url": "https://www.langchain.com"})
```

### 执行工具

#### python_exec - 执行 Python 代码

```python
@tool
def python_exec(code: str) -> str:
    """
    执行 Python 代码
    
    Args:
        code: Python 代码字符串
        
    Returns:
        执行结果
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用
agent.invoke("计算 1+2+3+4+5 等于多少")

# 直接调用工具
from ollamapilot.tools.builtin import python_exec
result = python_exec.invoke({"code": "print(sum([1,2,3,4,5]))"})
```

#### shell_exec - 执行 Shell 命令

```python
@tool
def shell_exec(command: str, timeout: int = 30) -> str:
    """
    执行 Shell 命令
    
    Args:
        command: Shell 命令
        timeout: 超时时间（秒），默认30秒
        
    Returns:
        命令输出
    """
```

**使用示例**：
```python
# 通过 Agent 自动调用
agent.invoke("查看当前目录下有哪些 Python 文件")

# 直接调用工具
from ollamapilot.tools.builtin import shell_exec
result = shell_exec.invoke({"command": "ls *.py"})
```

---

## 🆕 v0.2.6 新增工具

### 知识库分类搜索工具

#### search_knowledge_base - 在指定分类中搜索知识

```python
@tool
def search_knowledge_base(
    category: str,
    query: str,
    num_results: int = 5
) -> str:
    """
    在指定知识库分类中搜索
    
    Args:
        category: 分类名称（如"中医经典"、"中医经典/伤寒论"）
        query: 搜索查询
        num_results: 返回结果数量（默认5）
        
    Returns:
        搜索结果
    """
```

**使用场景**：
- 搜索特定领域的知识（如只在"中医经典"中搜索）
- 避免跨领域知识污染
- 提高搜索精确度

**使用示例**：
```python
# 搜索整个分类（包含所有子目录）
search_knowledge_base(category="中医经典", query="麻黄汤")

# 搜索子分类
search_knowledge_base(category="中医经典/伤寒论", query="太阳病")

# 搜索现代医学分类
search_knowledge_base(category="现代医学", query="高血压治疗")
```

#### list_knowledge_categories - 列出所有知识库分类

```python
@tool
def list_knowledge_categories() -> str:
    """
    列出所有知识库分类
    
    Returns:
        分类列表（JSON格式）
    """
```

**使用场景**：
- 查看当前有哪些知识库分类
- 了解知识库组织结构

**使用示例**：
```python
# 查看所有分类
categories = list_knowledge_categories.invoke({})
# 返回：["中医经典", "现代医学", "法律法规", ...]
```

---

## 🆕 v0.2.5 新增工具

### 三层搜索工具体系

OllamaPilot v0.2.5 引入了三层搜索架构，从基础到专业：

```
┌─────────────────────────────────────────────────────────────┐
│  第三层：deep_research (深度研究)                            │
│  触发词："研究 xxx"                                          │
│  输出：Markdown 研究报告                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第二层：enhanced_search (增强搜索)                          │
│  触发词："增强搜索 xxx"                                       │
│  类型：学术/代码/百科/综合                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第一层：web_search (基础搜索)                               │
│  触发词："搜索 xxx"                                          │
│  特点：简单快速，基础通用                                    │
└─────────────────────────────────────────────────────────────┘
```

#### academic_search - 学术文献搜索

```python
@tool
def academic_search(
    query: str,
    num_results: int = 10
) -> str:
    """
    搜索学术论文和文献（来源：PubMed）
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认10）
        
    Returns:
        论文列表（标题、摘要、链接）
    """
```

**使用示例**：
```python
# 搜索医学论文
agent.invoke("增强搜索 量子计算论文")
# 等同于调用 academic_search(query="quantum computing", num_results=10)
```

#### code_search - 代码仓库搜索

```python
@tool
def code_search(
    query: str,
    num_results: int = 10,
    language: str = None
) -> str:
    """
    搜索开源代码仓库（来源：GitHub）
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认10）
        language: 编程语言过滤（可选）
        
    Returns:
        项目列表（名称、描述、链接、星标）
    """
```

**使用示例**：
```python
# 搜索 Python 项目
agent.invoke("增强搜索 Python 爬虫框架")

# 搜索特定语言
code_search(query="machine learning", language="python", num_results=5)
```

#### encyclopedia_search - 百科知识搜索

```python
@tool
def encyclopedia_search(
    query: str,
    num_results: int = 10
) -> str:
    """
    搜索百科知识（来源：百度百科）
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认10）
        
    Returns:
        百科条目（标题、摘要、链接）
    """
```

**使用示例**：
```python
# 搜索百科知识
agent.invoke("增强搜索 什么是区块链")
# 等同于调用 encyclopedia_search(query="区块链")
```

#### multi_engine_search - 多引擎聚合搜索

```python
@tool
def multi_engine_search(
    query: str,
    num_results: int = 10,
    engines: list = None
) -> str:
    """
    多引擎聚合搜索
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认10）
        engines: 指定搜索引擎列表（可选）
        
    Returns:
        聚合搜索结果
    """
```

#### execute_deep_research - 深度研究

```python
@tool
def execute_deep_research(
    topic: str,
    max_iterations: int = 6
) -> str:
    """
    执行深度研究，生成专业报告
    
    Args:
        topic: 研究主题
        max_iterations: 最大迭代次数（默认6）
        
    Returns:
        Markdown 格式的研究报告
    """
```

**使用示例**：
```python
# 深度研究
agent.invoke("研究 人工智能在医疗诊断中的应用")
# 自动生成完整的研究报告，保存到 ./reports/
```

---

## 📚 相关文档

- [[架构分析]] - 理解系统架构
- [[运行逻辑]] - 理解执行流程
- [[源码解析]] - 深入代码实现

---

**创建时间**：2026-03-08  
**标签**：#API文档 #使用指南 #Skill开发