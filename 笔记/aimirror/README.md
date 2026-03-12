# aimirror 项目笔记

> 本笔记基于"理解坡度"学习法编写，帮助零基础用户平滑过渡到复杂内容。

---

## 一、项目概览：这个项目是做什么的？

### 第一步：点出项目的核心概念

aimirror 是一个**AI时代的下载镜像加速器**。在深入理解它之前，让我们先认识它的5个组件概念：

- **下载代理**：像一个"中间人"，帮你从远程服务器获取文件并转发给你（就像你让朋友帮忙去商店买东西）
- **并行下载**：把大文件分成多个小块同时下载，就像多人同时搬运货物，比一个人搬运快很多
- **智能缓存**：像背包一样，把下载过的文件存起来，下次需要时直接从背包里拿，不用再去商店买
- **动态路由**：像导航软件，根据文件大小自动选择最快的下载路线（小文件走直连，大文件走并行）
- **多源支持**：一个服务就能加速多种包管理器，就像一个万能翻译器，能听懂多种语言

### 第二步：用图展示项目架构和模块关系

```
[客户端请求]
    |
    v
[main.py：服务入口]
    |-> 加载配置（config.yaml）
    |-> 初始化路由器（Router）
    |-> 初始化缓存管理器（CacheManager）
    |-> 初始化HTTP客户端（httpx.AsyncClient）
    |-> 启动FastAPI服务
    |
    v
[router.py：路由匹配器]
    |-> 根据URL匹配规则（rules）
    |-> 选择下载策略（proxy 或 parallel）
    |-> 特殊处理分发（handlers）
    |
    v
[handlers/docker.py：Docker特殊处理]
    |-> 认证请求处理（/v2/auth）
    |-> 官方镜像重定向（library/*）
    |-> WWW-Authenticate改写
    |
    v
[downloader.py：并行下载器]
    |-> 获取文件大小
    |-> 分割下载分片
    |-> 并发下载（aiohttp）
    |-> 实时写入文件
    |-> 流式返回数据
    |
    v
[cache.py：缓存管理器]
    |-> 检查缓存命中
    |-> 存入缓存（硬链接）
    |-> LRU淘汰策略
    |-> SQLite元数据管理
```

**联系说明**：用户像客户一样发起请求，服务入口（main.py）像前台接待员，先检查配置和缓存；路由器（router.py）像导航员，根据目的地（URL）选择最佳路线；特殊处理器（handlers）像专业翻译，处理Docker等复杂协议；下载器（downloader.py）像快递员，负责从远程服务器获取数据；缓存管理器（cache.py）像仓库管理员，负责存储和管理文件。

### 第三步：项目核心功能详解

#### 1. 为什么需要这个项目？

**专业解释**：aimirror 解决的是AI时代开发者面临的"下载慢"问题。在AI开发中，PyPI包、Docker镜像、HuggingFace模型等文件动辄GB级别，国内网络环境下下载速度往往只有几百KB/s，严重影响开发效率。

**通俗解释与类比**：想象你要搬家，需要搬运很多大箱子（PyPI包、Docker镜像、HuggingFace模型）。这些箱子很重（文件体积大），而且快递员只给你一个人搬运（单线程下载）。结果就是，你可能要花一整天才能搬完。

aimirror 就像是给你请了一队搬运工（并行下载），每个人负责一部分（分片下载），而且还有一个仓库（缓存），如果你之前搬过的箱子下次还要用，直接从仓库拿就行，不用再跑一趟。

**实际应用**：
- `pip install torch`：原本下载几百MB的wheel包要30分钟，用aimirror后只需80秒
- `docker pull nvidia/cuda`：几GB的镜像层，并行下载加速数十倍
- `huggingface-cli download`：模型文件从蜗牛速度变成飞行速度

#### 2. 核心技术原理

**并行下载原理**：
- **HTTP Range请求**：告诉服务器"我只要文件的第1001-2000字节"，服务器就只返回这部分数据
- **多线程并发**：开启多个线程，每个线程下载文件的不同部分，最后合并
- **实时写入**：边下载边写入磁盘，不用等所有分片下载完才开始写入

**智能缓存原理**：
- **SHA256去重**：用URL的SHA256哈希值作为文件名，相同的文件只存一份
- **LRU淘汰**：最近最少使用的文件会被清理，确保缓存不溢出
- **SQLite元数据**：用数据库记录文件的访问时间、大小等信息

**动态路由原理**：
- **大小判断**：先发HEAD请求获取文件大小，小于min_size的直接代理
- **策略选择**：大文件走并行下载，小文件走直连代理

#### 3. 项目主要模块

| 模块 | 文件 | 核心职责 |
|------|------|----------|
| 服务入口 | `main.py` | FastAPI服务启动、生命周期管理、请求入口 |
| 路由匹配 | `router.py` | URL规则匹配、策略选择、目标URL构建 |
| 并行下载 | `downloader.py` | 分片下载、并发控制、文件写入 |
| 缓存管理 | `cache.py` | 缓存查找、存储、LRU淘汰 |
| Docker处理 | `handlers/docker.py` | Registry认证、官方镜像重定向 |

---

## 二、快速开始

### 安装方式

```bash
# 方式一：pip安装（推荐）
pip install aimirror
aimirror

# 方式二：源码安装
git clone https://github.com/livehl/aimirror.git
cd aimirror
pip install -r requirements.txt
python main.py
```

### 客户端配置

**pip/uv配置**：
```bash
# 临时使用
pip install torch --index-url http://localhost:8081/simple --trusted-host localhost:8081

# 全局配置
pip config set global.index-url http://localhost:8081/simple
pip config set global.trusted-host localhost:8081
```

**Docker配置**：
```bash
# 修改 daemon.json
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": ["http://localhost:8081"]
}
EOF
sudo systemctl restart docker
```

**HuggingFace配置**：
```bash
export HF_ENDPOINT=http://localhost:8081
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf
```

---

## 三、性能数据

### 实测加速效果

| 模式 | 下载速度 | 总耗时 | 加速比 |
|------|---------|--------|--------|
| 仅代理 | 900KB/s | ~31分钟 | 1x |
| aimirror | 170MB/s | ~80秒 | **23x** |

### 缓存命中效果

| 场景 | 耗时 | 速度 |
|------|------|------|
| 首次下载 | 80s | 170MB/s |
| 缓存命中 | <1s | **3000+ MB/s** |

---

## 四、项目结构

```
aimirror/
├── main.py                    # 服务入口
├── router.py                  # 路由匹配器
├── downloader.py              # 并行下载器
├── cache.py                   # 缓存管理器
├── config.yaml                # 配置文件
├── handlers/
│   ├── __init__.py
│   └── docker.py              # Docker特殊处理
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明
```

---

## 五、相关笔记导航

- [[架构分析]]：深入理解项目架构设计和模块关系
- [[运行逻辑]]：了解请求处理流程和状态管理
- [[源码解析]]：逐行解析核心代码实现
- [[核心API文档]]：查看关键API用法和参数说明
- [[核心算法分析]]：学习并行下载、缓存淘汰等算法

---

## 六、常见问题

### Q1: 为什么缓存速度能达到3000+ MB/s？

缓存命中时，文件已存储在本地磁盘（或SSD），读取速度取决于磁盘I/O性能和文件系统。现代SSD的读取速度可达3000MB/s以上，远超网络下载速度。

### Q2: 并行下载的分片大小如何设置？

- `chunk_size > 0`：固定分片大小（适合大多数场景）
- `chunk_size = 0`：自动模式，chunk_size = 文件总大小 / 并发数（适合超大文件）

### Q3: Docker镜像拉取为什么会慢？

Docker镜像层的文件通常很大（GB级别），且Docker Registry的token有过期时间。自动模式会根据文件大小动态调整分片大小，减少token超时概率。

---

**更新日期**：2026-03-12