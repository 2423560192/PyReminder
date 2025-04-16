import redis
import json

# Redis连接配置
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'password': '5201314',
    'db': 0
}

# 要导入的数据
data = {
    "pending_tasks": {
        "type": "zset",
        "value": [
            ["17", 1744679760.0]
        ]
    },
    "sync_queue:tasks": {
        "type": "list",
        "value": [
            "{\"key\": 17, \"data\": {\"id\": 17, \"title\": \"\\u5c31\\u8fd9\", \"content\": \"111\", \"datetime\": \"2025-04-15T09:16:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"owner\": \"diaomao\", \"triggered\": false, \"created_at\": \"2025-04-15T09:15:54.798710+08:00\", \"updated_at\": 1744679754.7986917}, \"operation\": \"create\", \"timestamp\": 1744679755.1878881}"
        ]
    },
    "sync_queue:users": {
        "type": "list",
        "value": [
            "{\"key\": \"diaomao\", \"data\": {\"username\": \"diaomao\", \"password_hash\": \"c04d6e34aab689c5c0e68eb51753c843e032efa7c16427f8642ee07ab946e981\", \"is_admin\": false, \"created_at\": \"2025-04-15T09:12:23.920143+08:00\"}, \"operation\": \"create\", \"timestamp\": 1744679544.596104}"
        ]
    },
    "task:id_counter": {
        "type": "string",
        "value": "29"
    },
    "tasks": {
        "type": "hash",
        "value": {
            "18": "{\"id\": 18, \"title\": \"\\u52a0\\u52d2\\u6bd4\\u6d77\", \"content\": \"\\u62a2\\u6d3b\\u52a8\", \"datetime\": \"2025-04-15T15:50:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": true}",
            "28": "{\"id\": 28, \"title\": \"\\u4fa6\\u63a2\", \"content\": \"\", \"datetime\": \"2025-04-16T17:00:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": false}",
            "13": "{\"id\": 13, \"title\": \"\\u6625\\u6ee1\\u7da6\\u6cb3\", \"content\": \"\\u53c2\\u52a0\\u6d3b\\u52a8\", \"datetime\": \"2025-04-16T15:29:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": true}",
            "25": "{\"id\": 25, \"title\": \"\\u52a0\\u52d2\\u6bd4\", \"content\": \"\\u6d3b\\u52a8\", \"datetime\": \"2025-04-16T15:30:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": true}",
            "10": "{\"id\": 10, \"title\": \"\\u4e2d\\u533b\\u6587\\u5316\\u4f53\\u9a8c\\u65e5\", \"content\": \"\\u4f53\\u9a8c\", \"datetime\": \"2025-04-14T17:55:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": true}",
            "19": "{\"id\": 19, \"title\": \"\\u52a0\\u52d2\\u6bd4\\u6d77\", \"content\": \"\\u62a2\\u6d3b\\u52a8\", \"datetime\": \"2025-04-15T15:50:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}",
            "26": "{\"id\": 26, \"title\": \"\\u543e\\u7231\\u543e\\u732b\", \"content\": \"\", \"datetime\": \"2025-04-15T16:50:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}",
            "27": "{\"id\": 27, \"title\": \"\\u543e\\u7231\\u543e\\u732b\", \"content\": \"\", \"datetime\": \"2025-04-23T15:30:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": false}",
            "11": "{\"id\": 11, \"title\": \"\\u4e2d\\u533b\\u6587\\u5316\", \"content\": \"\", \"datetime\": \"2025-04-14T17:55:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}",
            "12": "{\"id\": 12, \"title\": \"\\u4e2d\\u533b\\u6587\\u5316\", \"content\": \"\\u53c2\\u52a0\\u6d3b\\u52a8\", \"datetime\": \"2025-04-25T13:00:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": false}",
            "23": "{\"id\": 23, \"title\": \"\\u4e2d\\u5348\\u966a\\u54e5\\u5403\\u996d\", \"content\": \"1. \\u7b54\\u5e94 \\u3002 2. \\u7b54\\u5e94 \\u3002 3. \\u8fd8tm\\u662f\\u7b54\\u5e94\", \"datetime\": \"2025-04-15T11:20:00+08:00\", \"token_name\": \"\\u6db5\\u6db5\", \"triggered\": true}",
            "29": "{\"id\": 29, \"title\": \"\\u79fb\\u901a\\u676f\", \"content\": \"\", \"datetime\": \"2025-04-16T14:00:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}",
            "15": "{\"id\": 15, \"title\": \"\\u5e26\\u889c\\u5b50\", \"content\": \"\\u4e0d\\u5e26200\\u5b57\", \"datetime\": \"2025-04-15T08:32:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}",
            "24": "{\"id\": 24, \"title\": \"\\u52a0\\u52d2\\u6bd4\", \"content\": \"\\u52a0\\u52d2\\u6bd4\\u6d3b\\u52a8\", \"datetime\": \"2025-04-16T15:30:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"triggered\": true}"
        }
    },
    "tasks_hash": {
        "type": "hash",
        "value": {
            "17": "{\"id\": 17, \"title\": \"\\u5c31\\u8fd9\", \"content\": \"111\", \"datetime\": \"2025-04-15T09:16:00+08:00\", \"token_name\": \"\\u9ed8\\u8ba4\", \"owner\": \"diaomao\", \"triggered\": false, \"created_at\": \"2025-04-15T09:15:54.798710+08:00\", \"updated_at\": 1744679754.7986917}"
        }
    },
    "tokens": {
        "type": "hash",
        "value": {
            "测试": "XZ86376cfff05ba749dd400b662e05f15b",
            "涵涵": "XZ404844bef6878f73ec30b68e68af2491",
            "默认": "XZ77c1d923959433459ec3a08556a6a5b6"
        }
    },
    "user_diaomao_tasks": {
        "type": "set",
        "value": ["17"]
    },
    "users": {
        "type": "hash",
        "value": {
            "diaomao": "{\"username\": \"diaomao\", \"password_hash\": \"c04d6e34aab689c5c0e68eb51753c843e032efa7c16427f8642ee07ab946e981\", \"is_admin\": false, \"created_at\": \"2025-04-15T09:12:23.920143+08:00\"}"
        }
    }
}

def import_data():
    # 连接Redis
    r = redis.Redis(**REDIS_CONFIG)
    
    # 清空现有数据
    r.flushdb()
    
    # 导入数据
    for key, value in data.items():
        if value["type"] == "string":
            r.set(key, value["value"])
        elif value["type"] == "hash":
            r.hmset(key, value["value"])
        elif value["type"] == "list":
            for item in value["value"]:
                r.rpush(key, item)
        elif value["type"] == "set":
            for item in value["value"]:
                r.sadd(key, item)
        elif value["type"] == "zset":
            for item, score in value["value"]:
                r.zadd(key, {item: score})
    
    print("数据导入完成！")

if __name__ == "__main__":
    import_data() 