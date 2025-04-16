#!/bin/bash

# 设置颜色常量
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 输出带颜色的消息
echo_color() {
  echo -e "${2}${1}${NC}"
}

echo_color "开始部署 PyReminder 应用..." "${GREEN}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
  echo_color "错误: Docker未安装，请先安装Docker" "${RED}"
  exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
  echo_color "错误: Docker Compose未安装，请先安装Docker Compose" "${RED}"
  exit 1
fi

# 创建必要的目录
echo_color "创建必要的目录结构..." "${YELLOW}"
mkdir -p config/nginx logs/nginx logs/app

# 停止并移除旧容器（如果存在）
echo_color "停止并移除旧容器..." "${YELLOW}"
docker-compose down 2>/dev/null || true

# 检查并创建配置文件
if [ ! -f "config/nginx/nginx.conf" ]; then
  echo_color "创建Nginx配置文件..." "${YELLOW}"
  
  cat > config/nginx/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
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
        alias /app/static/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
    
    # 健康检查端点
    location /health {
        proxy_pass http://web:8000/health;
        access_log off;
    }
}
EOF
fi

# 确保环境变量文件存在
if [ ! -f "config/.env" ]; then
  echo_color "创建环境变量文件..." "${YELLOW}"
  
  if [ -f ".env.example" ]; then
    cp .env.example config/.env
    echo_color "已从.env.example创建环境变量文件，请检查配置" "${YELLOW}"
  else
    cat > config/.env << 'EOF'
# 通知服务配置
NOTIFICATION_TOKEN=XZ77c1d923959433459ec3a08556a6a5b6

# Flask设置
FLASK_SECRET_KEY=dawdawfaasfaav23134
FLASK_DEBUG=False

# 时区设置
TIMEZONE=Asia/Shanghai

# Redis设置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=5201314
REDIS_SSL=False
EOF
    echo_color "已创建默认环境变量文件，请检查并修改配置" "${YELLOW}"
  fi
fi

# 构建并启动服务
echo_color "构建并启动服务..." "${GREEN}"
docker-compose build
docker-compose up -d

# 等待服务启动
echo_color "等待服务启动..." "${YELLOW}"
sleep 5

# 检查服务状态
echo_color "检查服务状态..." "${YELLOW}"
docker-compose ps

# 检查应用是否可访问
echo_color "检查应用是否可访问..." "${YELLOW}"
if curl -s http://localhost/health &> /dev/null; then
  echo_color "✓ 应用已成功启动并可以访问!" "${GREEN}"
  
  # 获取服务器IP
  SERVER_IP=$(hostname -I | awk '{print $1}')
  
  echo_color "\n您可以通过以下地址访问应用:" "${GREEN}"
  echo_color "  http://localhost" "${GREEN}"
  echo_color "  http://$SERVER_IP" "${GREEN}"
else
  echo_color "✗ 应用启动失败或无法访问" "${RED}"
  echo_color "请检查docker日志了解详情:" "${YELLOW}"
  echo_color "  docker-compose logs" "${YELLOW}"
fi

# 显示日志查看命令
echo_color "\n如需查看应用日志，请运行:" "${YELLOW}"
echo_color "  docker-compose logs -f" "${YELLOW}" 