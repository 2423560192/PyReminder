#!/bin/bash

# Redis数据恢复脚本

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 <备份文件路径>"
    echo "例如: $0 ./backups/redis_backup_20230601_120000.rdb"
    exit 1
fi

BACKUP_FILE=$1

# 检查文件是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件 '$BACKUP_FILE' 不存在"
    exit 1
fi

echo "准备从文件恢复Redis数据: $BACKUP_FILE"
echo "警告: 这将覆盖Redis中的所有现有数据!"
read -p "确定要继续吗? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "操作已取消"
    exit 0
fi

# 检查Redis容器是否运行
REDIS_CONTAINER=$(docker-compose ps -q redis)
if [ -z "$REDIS_CONTAINER" ]; then
    echo "错误: Redis容器未运行"
    echo "请先启动服务: docker-compose up -d"
    exit 1
fi

# 停止Redis服务
echo "停止Web应用服务..."
docker-compose stop web

echo "停止Redis服务..."
docker-compose stop redis

# 复制备份文件到Redis数据目录
echo "复制备份文件到Redis数据卷..."
TEMP_DIR=$(mktemp -d)
cp "$BACKUP_FILE" "$TEMP_DIR/dump.rdb"

# 启动临时容器来复制文件
docker run --rm -v redis_data:/data -v $TEMP_DIR:/backup alpine sh -c "cp /backup/dump.rdb /data/ && chown 999:999 /data/dump.rdb"

# 清理临时目录
rm -rf "$TEMP_DIR"

# 重启服务
echo "重启Redis和Web服务..."
docker-compose up -d

echo "数据恢复完成!"
echo "提示: 查看应用日志确认连接正常: docker-compose logs -f web" 