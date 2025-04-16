#!/bin/bash

# 停止并删除所有容器
echo "正在停止并删除所有容器..."
docker-compose down
docker rm -f $(docker ps -a | grep certbot | awk '{print $1}') 2>/dev/null || true

# 删除certbot相关目录
echo "正在删除证书相关目录..."
rm -rf ./certbot

# 清理nginx.conf文件
echo "重写nginx.conf文件..."
cat > nginx.conf << 'EOT'
server {
    listen 80;
    server_name pyreminder.top www.pyreminder.top;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时设置
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    # 静态文件缓存设置
    location /static/ {
        proxy_pass http://web:8000/static/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
    
    # 健康检查
    location /nginx-health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOT

# 重写docker-compose.yml文件
echo "重写docker-compose.yml文件..."
cat > docker-compose.yml << 'EOT'
version: '3.8'

services:
  web:
    build: .
    expose:
      - "8000"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - TIMEZONE=Asia/Shanghai
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - REDIS_PASSWORD=5201314
      - REDIS_SSL=False
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - .:/app
    networks:
      - app-network
    depends_on:
      - redis

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass 5201314
    expose:
      - "6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./app/static:/app/static
    depends_on:
      - web
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  redis-data:
    driver: local
EOT

# 重新启动服务
echo "重新启动服务..."
docker-compose up -d

# 查看容器状态
echo "服务状态:"
docker-compose ps

echo "部署完成！"
echo "现在可以通过 http://pyreminder.top 访问您的网站" 