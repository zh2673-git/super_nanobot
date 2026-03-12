# 核心API文档

> 本笔记介绍 aimirror 的关键API和使用方法，帮助零基础用户快速上手。

---

## 一、API概述

### 第一步：点出核心API

aimirror 提供2类API：

- **代理端点**：处理客户端的下载请求，转发到上游服务器或并行下载
- **管理端点**：健康检查、缓存统计等服务管理

### 第二步：用图展示API层次

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端请求                              │
│  pip / docker / huggingface-cli / R / npm                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    aimirror 服务                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  代理端点                                            │  │
│  │  GET/HEAD/POST/PUT/DELETE /{full_path:path}         │  │
│  │  - 路由匹配: router.match(path)                      │  │
│  │  - 策略选择: proxy / parallel                        │  │
│  │  - 缓存检查: cache.get(url)                          │  │
│  │  - 并发下载: ParallelDownloader                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  管理端点                                            │  │
│  │  GET /health  - 健康检查                            │  │
│  │  GET /stats   - 缓存统计                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、代理端点

### GET/HEAD/POST/PUT/DELETE /{full_path:path}

**功能**：统一代理入口，根据路由规则分发请求。

#### 请求示例

**测试PyPI代理**：
```bash
curl -o /dev/null "http://localhost:8081/packages/fb/d7/71b982339efc4fff3c622c6fefecddfd3e0b35b60c5f822872d5b806bb71/torch-1.0.0-cp27-cp27m-manylinux1_x86_64.whl" \
  -w "HTTP: %{http_code}, Size: %{size_download}, Time: %{time_total}s\n"
```

**测试HuggingFace代理**：
```bash
export HF_ENDPOINT=http://localhost:8081
huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q4_K_M.gguf
```

**测试Docker Registry代理**：
```bash
# 获取token
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/nginx:pull" \
  | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# 下载blob
curl -o /dev/null "http://localhost:8081/v2/library/nginx/blobs/sha256:abc123" \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP: %{http_code}, Size: %{size_download}, Time: %{time_total}s\n"
```

#### 响应说明

**成功响应（200）**：
- 缓存命中：直接返回文件流
- 首次下载：返回下载的文件流

**重试响应（302）**：
- 文件正在下载中：返回302让客户端重试
- Location: 原始请求URL

**错误响应（404）**：
- 未找到匹配的路由规则

**错误响应（502）**：
- 下载失败

---

## 三、管理端点

### GET /health

**功能**：健康检查，返回服务状态。

#### 请求示例

```bash
curl http://localhost:8081/health
```

#### 响应格式

```json
{
  "status": "ok",
  "active_downloads": 0,
  "downloads": []
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 服务状态，`ok` 表示正常运行 |
| `active_downloads` | int | 当前正在进行的下载任务数 |
| `downloads` | array | 正在下载的文件列表（缓存key） |

### GET /stats

**功能**：返回缓存统计信息。

#### 请求示例

```bash
curl http://localhost:8081/stats | jq
```

#### 响应格式

```json
{
  "cache": {
    "count": 100,
    "size_bytes": 1073741824,
    "size_gb": 1.0,
    "first_cached": "2024-01-01 00:00:00",
    "last_accessed": "2024-01-02 12:00:00"
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `cache.count` | int | 缓存文件数量 |
| `cache.size_bytes` | int | 缓存总大小（字节） |
| `cache.size_gb` | float | 缓存总大小（GB） |
| `cache.first_cached` | string | 首次缓存时间 |
| `cache.last_accessed` | string | 最后访问时间 |

---

## 四、客户端配置

### pip/uv配置

**临时使用**：
```bash
pip install torch --index-url http://localhost:8081/simple --trusted-host localhost:8081
```

**全局配置**：
```bash
pip config set global.index-url http://localhost:8081/simple
pip config set global.trusted-host localhost:8081
```

**使用环境变量**：
```bash
export HTTPS_PROXY=http://localhost:8081
pip install torch
```

**使用uv**：
```bash
uv pip install torch --index-url http://localhost:8081/simple
```

### Docker配置

**方式一：修改daemon.json**：
```bash
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": ["http://localhost:8081"]
}
EOF
sudo systemctl restart docker
```

**方式二：命令行指定**：
```bash
docker pull --registry-mirror=http://localhost:8081 nginx
```

### HuggingFace配置

**环境变量**：
```bash
export HF_ENDPOINT=http://localhost:8081
```

**Python代码**：
```python
import os
os.environ["HF_ENDPOINT"] = "http://localhost:8081"

from huggingface_hub import hf_hub_download, snapshot_download

# 下载单个文件
hf_hub_download(repo_id="TheBloke/Llama-2-7B-GGUF", filename="llama-2-7b.Q4_K_M.gguf")

# 下载整个仓库
snapshot_download(repo_id="meta-llama/Llama-2-7b-hf", local_dir="./models")
```

### R (CRAN)配置

**在R控制台**：
```r
options(repos = c(CRAN = "http://localhost:8081"))
```

**在.Rprofile中永久配置**：
```r
cat('options(repos = c(CRAN = "http://localhost:8081"))\n', file = "~/.Rprofile")
```

### Conda配置

```bash
cat >> ~/.condarc <<EOF
channels:
  - http://localhost:8081/conda-forge
  - http://localhost:8081/bioconda
EOF
```

### npm/yarn配置

**临时使用**：
```bash
npm install --registry http://localhost:8081/registry/npm
```

**全局配置**：
```bash
npm config set registry http://localhost:8081/registry/npm
yarn config set registry http://localhost:8081/registry/npm
```

---

## 五、配置详解

### 完整配置示例

```yaml
# fast_proxy 配置文件
server:
  host: "0.0.0.0"
  port: 8081
  upstream_proxy: ""          # 上游代理，默认空表示直连
  public_host: "127.0.0.1:8081"  # 对外访问地址
  max_concurrent_downloads: 100  # 全局最大并发下载数

cache:
  dir: "/data/fast_proxy/cache"
  max_size_gb: 100
  lru_enabled: true

rules:
  - name: docker-blob
    pattern: "/v2/.*/blobs/sha256:[a-f0-9]+"
    upstream: "https://registry-1.docker.io"
    strategy: parallel
    min_size: 1
    concurrency: 20
    chunk_size: 1048576  # 1MB
  
  - name: docker-registry
    pattern: "/v2/.*"
    upstream: "https://registry-1.docker.io"
    strategy: proxy
    handler: handlers.docker
  
  - name: pip-packages
    pattern: "/packages/.+\\.(whl|tar\\.gz|zip)$"
    upstream: "https://pypi.org"
    strategy: parallel
    min_size: 1
    concurrency: 20
    chunk_size: 5242880  # 5MB
  
  - name: huggingface-files
    pattern: '/.*/(blob|resolve)/[^/]+/.+'
    upstream: "https://huggingface.co"
    strategy: parallel
    min_size: 102400  # 100K
    concurrency: 20
    chunk_size: 10485760  # 10MB
    cache_key_source: original
    path_rewrite:
      - search: "/blob/"
        replace: "/resolve/"
    head_meta_headers:
      - "x-repo-commit"
      - "x-linked-etag"
      - "x-linked-size"
      - "etag"
  
  - name: default
    pattern: ".*"
    upstream: "https://pypi.org"
    strategy: proxy
    content_rewrite:
      content_types:
        - "text/html"
        - "application/json"
        - "application/vnd.pypi.simple"
      targets:
        - "https://files.pythonhosted.org"

logging:
  level: "INFO"
  file: "/data/fast_proxy/fast_proxy.log"
```

### 配置字段说明

#### server配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `server.host` | string | `"0.0.0.0"` | 服务监听地址 |
| `server.port` | int | `8081` | 服务监听端口 |
| `server.upstream_proxy` | string | `""` | 上游代理地址，空表示直连 |
| `server.public_host` | string | `"127.0.0.1:8081"` | 对外访问地址，用于URL改写 |
| `server.max_concurrent_downloads` | int | `100` | 全局最大并发下载数 |

#### cache配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cache.dir` | string | `"./cache"` | 缓存目录路径 |
| `cache.max_size_gb` | float | `100` | 缓存最大容量（GB） |
| `cache.lru_enabled` | bool | `true` | 是否启用LRU淘汰 |

#### rules配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `rules[].name` | string | 规则名称 |
| `rules[].pattern` | string | URL匹配正则表达式 |
| `rules[].upstream` | string | 上游源base URL |
| `rules[].strategy` | string | 下载策略：`proxy` / `parallel` |
| `rules[].min_size` | int | 最小文件大小（字节），小于此值使用代理 |
| `rules[].concurrency` | int | 并行下载线程数 |
| `rules[].chunk_size` | int | 分片大小（字节），`≤0`表示自动计算 |
| `rules[].cache_key_source` | string | 缓存key来源：`original` / `final` |
| `rules[].path_rewrite` | array | 路径重写规则 |
| `rules[].content_rewrite` | dict | 响应内容改写配置 |
| `rules[].handler` | string | 特殊处理模块路径 |
| `rules[].head_meta_headers` | array | HEAD请求时额外保留的响应头 |

#### logging配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `logging.level` | string | `"INFO"` | 日志级别 |
| `logging.file` | string | `"/tmp/fast_proxy.log"` | 日志文件路径 |

---

## 六、扩展Handler

### 创建自定义Handler

```python
# handlers/custom.py

async def exec_path(request: Request, full_path: str, config: dict, http_client) -> tuple:
    """
    自定义请求处理器
    
    Args:
        request: FastAPI Request对象
        full_path: 请求路径
        config: 全局配置字典
        http_client: httpx.AsyncClient实例
    
    Returns:
        (handled, response): 
        - handled: bool，是否已处理
        - response: 如果handled=True，返回Response对象
    """
    if full_path.startswith('/custom/'):
        # 处理自定义逻辑
        return True, Response(content="Custom response")
    
    # 未处理，继续后续流程
    return False, None
```

### 配置Handler

```yaml
rules:
  - name: custom-handler
    pattern: "/custom/.*"
    upstream: "https://example.com"
    strategy: proxy
    handler: handlers.custom
```

---

## 七、常见问题

### Q1: 如何查看正在下载的文件？

```bash
curl http://localhost:8081/health
```

查看 `downloads` 字段。

### Q2: 如何查看缓存使用情况？

```bash
curl http://localhost:8081/stats | jq
```

### Q3: 缓存文件存储在哪里？

缓存文件默认存储在 `/data/fast_proxy/cache` 目录，文件名为URL的SHA256哈希值。

### Q4: 如何添加新的源加速？

在 `config.yaml` 的 `rules` 中添加新规则：

```yaml
rules:
  - name: github-releases
    pattern: '/.*/releases/download/.+'
    upstream: "https://github.com"
    strategy: parallel
    min_size: 1048576  # 1MB以上启用并行
    concurrency: 16
    chunk_size: 10485760  # 10MB分片
```

---

## 八、相关笔记

- [[README]]：项目概览和快速开始
- [[架构分析]]：架构设计和模块关系
- [[运行逻辑]]：请求处理流程和状态管理
- [[源码解析]]：核心代码逐行解析
- [[核心算法分析]]：算法原理和优化思路

---

**更新日期**：2026-03-12