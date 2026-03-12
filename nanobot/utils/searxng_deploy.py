"""SearXNG auto-deployment utility."""

import subprocess
import time
from pathlib import Path

from loguru import logger


class SearXNGDeployer:
    """SearXNG 自动部署器"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.container_name = "nanobot-searxng"

    def check_docker(self) -> bool:
        """检查 Docker 是否安装"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def is_running(self) -> bool:
        """检查 SearXNG 是否已运行"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return self.container_name in result.stdout
        except Exception:
            return False

    def deploy(self) -> bool:
        """部署 SearXNG"""
        if not self.check_docker():
            logger.error("Docker 未安装，请先安装 Docker")
            return False

        if self.is_running():
            logger.info(f"SearXNG 已运行在端口 {self.port}")
            return True

        logger.info("正在部署 SearXNG...")

        try:
            # 拉取镜像
            logger.info("拉取 SearXNG 镜像...")
            subprocess.run(
                ["docker", "pull", "searxng/searxng"],
                check=True,
                timeout=120
            )

            # 启动容器
            logger.info("启动 SearXNG 容器...")
            subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", self.container_name,
                    "--restart", "unless-stopped",
                    "-p", f"{self.port}:8080",
                    "-v", f"{self._get_config_dir()}:/etc/searxng",
                    "searxng/searxng"
                ],
                check=True,
                timeout=30
            )

            # 等待服务就绪
            logger.info("等待 SearXNG 启动...")
            time.sleep(5)

            if self.is_running():
                logger.info(f"SearXNG 部署成功: http://localhost:{self.port}")
                return True
            else:
                logger.error("SearXNG 启动失败")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"部署失败: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("部署超时")
            return False

    def stop(self) -> bool:
        """停止 SearXNG"""
        try:
            subprocess.run(
                ["docker", "stop", self.container_name],
                check=True,
                timeout=10
            )
            logger.info("SearXNG 已停止")
            return True
        except Exception as e:
            logger.error(f"停止失败: {e}")
            return False

    def remove(self) -> bool:
        """移除 SearXNG 容器"""
        try:
            # 先停止
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                timeout=10
            )
            # 再移除
            subprocess.run(
                ["docker", "rm", self.container_name],
                check=True,
                timeout=10
            )
            logger.info("SearXNG 容器已移除")
            return True
        except Exception as e:
            logger.error(f"移除失败: {e}")
            return False

    def _get_config_dir(self) -> str:
        """获取配置目录"""
        config_dir = Path.home() / ".nanobot" / "searxng"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir)


def ensure_searxng(port: int = 8080) -> str | None:
    """确保 SearXNG 可用，返回 URL"""
    deployer = SearXNGDeployer(port)

    if deployer.deploy():
        return f"http://localhost:{port}"
    return None


def get_searxng_status() -> dict:
    """获取 SearXNG 状态"""
    deployer = SearXNGDeployer()

    return {
        "docker_installed": deployer.check_docker(),
        "running": deployer.is_running(),
        "url": "http://localhost:8080" if deployer.is_running() else None
    }


if __name__ == "__main__":
    # 测试部署
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = get_searxng_status()
        print(f"Docker 安装: {'是' if status['docker_installed'] else '否'}")
        print(f"运行状态: {'运行中' if status['running'] else '未运行'}")
        if status['url']:
            print(f"访问地址: {status['url']}")
    else:
        url = ensure_searxng()
        if url:
            print(f"SearXNG 已就绪: {url}")
        else:
            print("SearXNG 部署失败")
            sys.exit(1)
