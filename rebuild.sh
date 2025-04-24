#!/bin/bash

echo "=== 开始重建PyReminder容器 ==="

# 停止所有容器
echo "停止容器..."
docker-compose down

# 删除相关容器、网络、卷和镜像
echo "清理旧资源..."
docker-compose rm -f -s -v

# 清理Docker构建缓存
echo "清理Docker缓存..."
docker builder prune -f

# 重新构建并启动容器
echo "重新构建容器..."
docker-compose build --no-cache

echo "启动容器..."
docker-compose up -d

echo "=== 容器重建完成 ==="
echo "查看容器状态:"
docker-compose ps
echo "查看日志请运行: docker-compose logs -f" 