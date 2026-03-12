#!/bin/bash
# super_nanobot Docker 部署脚本

set -e

echo "🚀 开始部署 super_nanobot..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建配置目录
mkdir -p ~/.nanobot

# 检查配置文件是否存在
if [ ! -f ~/.nanobot/config.json ]; then
    echo "⚠️  配置文件不存在，创建默认配置..."
    cat > ~/.nanobot/config.json << 'EOF'
{
  "providers": {
    "ollama": {
      "apiKey": "dummy",
      "apiBase": "http://host.docker.internal:11434",
      "defaultModel": "qwen3.5:4b",
      "smallModelMode": true,
      "smallModelConfig": {
        "temperature": 0.7,
        "topP": 0.9,
        "topK": 40,
        "repeatPenalty": 1.1,
        "numCtx": 8192,
        "maxTokens": 2048
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen3.5:4b",
      "provider": "ollama",
      "skills": ["enhanced_search", "graphrag"]
    }
  },
  "tools": {
    "enhanced_search": {
      "searxngUrl": "http://localhost:8080"
    }
  }
}
EOF
    echo "✅ 默认配置已创建: ~/.nanobot/config.json"
    echo "⚠️  请修改配置文件，添加你的 API 密钥和模型设置"
fi

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker build -t super_nanobot:latest .

# 运行容器
echo "🚀 启动 super_nanobot..."
docker run -d \
    --name super_nanobot \
    --restart unless-stopped \
    -p 18790:18790 \
    -v ~/.nanobot:/root/.nanobot \
    -e NANOBOT_CONFIG_DIR=/root/.nanobot \
    super_nanobot:latest gateway

echo "✅ super_nanobot 已启动！"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker logs -f super_nanobot"
echo "  停止服务: docker stop super_nanobot"
echo "  启动服务: docker start super_nanobot"
echo "  重启服务: docker restart super_nanobot"
echo "  进入容器: docker exec -it super_nanobot bash"
echo ""
echo "🌐 网关地址: http://localhost:18790"
