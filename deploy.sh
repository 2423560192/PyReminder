#!/bin/bash

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 输出带颜色的文本
echo_color() {
    echo -e "${2}${1}${NC}"
}

echo_color "开始部署 PyReminder 应用..." "${GREEN}"

# 检查Docker和Docker Compose是否安装
if ! command -v docker &> /dev/null; then
    echo_color "错误: Docker 未安装." "${RED}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo_color "错误: Docker Compose 未安装." "${RED}"
    exit 1
fi

# 创建必要的目录
echo_color "创建必要的目录结构..." "${YELLOW}"
mkdir -p config/nginx logs/nginx logs/app

# 清理旧容器（如果存在）
echo_color "停止并移除旧容器..." "${YELLOW}"
docker-compose down 2>/dev/null || true
docker rm -f $(docker ps -a | grep "pyreminder-" | awk '{print $1}') 2>/dev/null || true

# 确保所有配置文件都存在
if [ ! -f "config/.env" ]; then
    echo_color "环境配置文件不存在，从模板创建..." "${YELLOW}"
    cp .env.example config/.env
    echo_color "请编辑 config/.env 文件进行配置." "${YELLOW}"
fi

if [ ! -f "config/nginx/nginx.conf" ]; then
    echo_color "Nginx配置文件不存在，从模板创建..." "${YELLOW}"
    mkdir -p config/nginx
    cat > config/nginx/nginx.conf << 'EOF'
server {
    listen 80;
    server_name pyreminder.top www.pyreminder.top;
    
    # 日志配置
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # 应用主路径
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    # 静态文件处理
    location /static/ {
        proxy_pass http://web:8000/static/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
    
    # 健康检查端点
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # 错误页面配置
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF
fi

# 构建并启动服务
echo_color "构建并启动服务..." "${GREEN}"
docker-compose build
docker-compose up -d

# 检查服务状态
echo_color "检查服务状态..." "${YELLOW}"
docker-compose ps

# 输出访问信息
echo_color "\n部署完成!" "${GREEN}"
echo_color "您可以通过以下地址访问您的应用:" "${GREEN}"
echo_color "  http://pyreminder.top" "${GREEN}"
echo_color "\n如需查看日志，请运行:" "${YELLOW}"
echo_color "  docker-compose logs -f" "${YELLOW}"
echo_color "如需重启服务，请运行:" "${YELLOW}"
echo_color "  docker-compose restart" "${YELLOW}" 