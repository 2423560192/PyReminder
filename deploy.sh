#!/bin/bash

# 部署脚本 - PyReminder项目

echo "=== 开始部署PyReminder ==="

# 检查是否安装了Docker和Docker Compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "错误: 需要安装Docker和Docker Compose"
    echo "可以使用以下命令安装Docker:"
    echo "curl -fsSL https://get.docker.com | bash"
    echo "可以使用以下命令安装Docker Compose:"
    echo "curl -L \"https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p config/nginx logs/nginx logs/app

# 如果.env文件不存在，从.env.example复制
if [ ! -f .env ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑.env文件设置你的环境变量"
fi

# 构建并启动容器
echo "构建并启动Docker容器..."
docker-compose up -d --build

# 检查启动状态
echo "检查容器状态..."
docker-compose ps

echo "=== PyReminder部署完成 ==="
echo "你可以通过服务器IP或域名访问应用"
echo "如需查看日志，请运行: docker-compose logs -f" 