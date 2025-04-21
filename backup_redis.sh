#!/bin/bash

# Redis数据备份脚本
# 建议通过crontab定期执行此脚本

# 设置备份目录
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# 备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"

echo "开始备份Redis数据..."

# 执行Redis SAVE命令
docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-redis_password}" SAVE

# 复制RDB文件到备份目录
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_FILE

# 删除老旧备份，只保留最近的7个备份
ls -t $BACKUP_DIR/redis_backup_*.rdb | tail -n +8 | xargs -r rm

echo "备份完成: $BACKUP_FILE"
echo "备份目录下文件数量: $(ls $BACKUP_DIR/redis_backup_*.rdb | wc -l)" 