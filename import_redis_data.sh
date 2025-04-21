#!/bin/bash

# Redis数据导入脚本
echo "开始导入Redis数据..."

# 创建临时Redis命令文件
cat > redis_import.commands << EOF
# 清除所有现有数据
FLUSHALL

# 添加pending_tasks (ZSET类型)
ZADD pending_tasks 1744679760.0 "17"

# 添加sync_queue:tasks (LIST类型)
LPUSH sync_queue:tasks '{"key": 17, "data": {"id": 17, "title": "\\u5c31\\u8fd9", "content": "111", "datetime": "2025-04-15T09:16:00+08:00", "token_name": "\\u9ed8\\u8ba4", "owner": "diaomao", "triggered": false, "created_at": "2025-04-15T09:15:54.798710+08:00", "updated_at": 1744679754.7986917}, "operation": "create", "timestamp": 1744679755.1878881}'

# 添加sync_queue:users (LIST类型)
LPUSH sync_queue:users '{"key": "diaomao", "data": {"username": "diaomao", "password_hash": "c04d6e34aab689c5c0e68eb51753c843e032efa7c16427f8642ee07ab946e981", "is_admin": false, "created_at": "2025-04-15T09:12:23.920143+08:00"}, "operation": "create", "timestamp": 1744679544.596104}'

# 设置task:id_counter (STRING类型)
SET task:id_counter "29"

# 添加tasks (HASH类型)
HSET tasks "19" '{"id": 19, "title": "\\u52a0\\u52d2\\u6bd4\\u6d77", "content": "\\u62a2\\u6d3b\\u52a8", "datetime": "2025-04-15T15:50:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "23" '{"id": 23, "title": "\\u4e2d\\u5348\\u966a\\u54e5\\u5403\\u996d", "content": "1. \\u7b54\\u5e94 \\u3002 2. \\u7b54\\u5e94 \\u3002 3. \\u8fd8tm\\u662f\\u7b54\\u5e94", "datetime": "2025-04-15T11:20:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": true}'
HSET tasks "18" '{"id": 18, "title": "\\u52a0\\u52d2\\u6bd4\\u6d77", "content": "\\u62a2\\u6d3b\\u52a8", "datetime": "2025-04-15T15:50:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": true}'
HSET tasks "29" '{"id": 29, "title": "\\u79fb\\u901a\\u676f", "content": "", "datetime": "2025-04-16T14:00:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "15" '{"id": 15, "title": "\\u5e26\\u889c\\u5b50", "content": "\\u4e0d\\u5e26200\\u5b57", "datetime": "2025-04-15T08:32:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "13" '{"id": 13, "title": "\\u6625\\u6ee1\\u7da6\\u6cb3", "content": "\\u53c2\\u52a0\\u6d3b\\u52a8", "datetime": "2025-04-16T15:29:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": true}'
HSET tasks "24" '{"id": 24, "title": "\\u52a0\\u52d2\\u6bd4", "content": "\\u52a0\\u52d2\\u6bd4\\u6d3b\\u52a8", "datetime": "2025-04-16T15:30:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "25" '{"id": 25, "title": "\\u52a0\\u52d2\\u6bd4", "content": "\\u6d3b\\u52a8", "datetime": "2025-04-16T15:30:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": true}'
HSET tasks "11" '{"id": 11, "title": "\\u4e2d\\u533b\\u6587\\u5316", "content": "", "datetime": "2025-04-14T17:55:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "26" '{"id": 26, "title": "\\u543e\\u7231\\u543e\\u732b", "content": "", "datetime": "2025-04-15T16:50:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'
HSET tasks "10" '{"id": 10, "title": "\\u4e2d\\u533b\\u6587\\u5316\\u4f53\\u9a8c\\u65e5", "content": "\\u4f53\\u9a8c", "datetime": "2025-04-14T17:55:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": true}'
HSET tasks "12" '{"id": 12, "title": "\\u4e2d\\u533b\\u6587\\u5316", "content": "\\u53c2\\u52a0\\u6d3b\\u52a8", "datetime": "2025-04-25T13:00:00+08:00", "token_name": "\\u6db5\\u6db5", "triggered": false}'
HSET tasks "27" '{"id": 27, "title": "\\u543e\\u7231\\u543e\\u732b", "content": "", "datetime": "2025-04-23T15:30:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": false}'
HSET tasks "28" '{"id": 28, "title": "\\u4fa6\\u63a2", "content": "", "datetime": "2025-04-16T17:00:00+08:00", "token_name": "\\u9ed8\\u8ba4", "triggered": true}'

# 添加tasks_hash (HASH类型)
HSET tasks_hash "17" '{"id": 17, "title": "\\u5c31\\u8fd9", "content": "111", "datetime": "2025-04-15T09:16:00+08:00", "token_name": "\\u9ed8\\u8ba4", "owner": "diaomao", "triggered": false, "created_at": "2025-04-15T09:15:54.798710+08:00", "updated_at": 1744679754.7986917}'

# 添加tokens (HASH类型)
HSET tokens "涵涵" "XZ404844bef6878f73ec30b68e68af2491"
HSET tokens "默认" "XZ77c1d923959433459ec3a08556a6a5b6"
HSET tokens "测试" "XZ86376cfff05ba749dd400b662e05f15b"

# 添加user_diaomao_tasks (SET类型)
SADD user_diaomao_tasks "17"

# 添加users (HASH类型)
HSET users "diaomao" '{"username": "diaomao", "password_hash": "c04d6e34aab689c5c0e68eb51753c843e032efa7c16427f8642ee07ab946e981", "is_admin": false, "created_at": "2025-04-15T09:12:23.920143+08:00"}'

# 保存数据
SAVE
EOF

# 检查docker-compose是否已启动
if [ ! "$(docker-compose ps -q redis)" ]; then
  echo "Redis容器未运行，请先启动Docker环境"
  echo "运行: docker-compose up -d"
  exit 1
fi

# 将命令文件传入Redis容器
echo "正在导入数据到Redis..."
cat redis_import.commands | docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD:-5201314}"

# 删除临时文件
rm redis_import.commands

echo "Redis数据导入完成!"
echo "你可以通过以下命令验证数据："
echo "docker-compose exec redis redis-cli -a 5201314 keys '*'" 