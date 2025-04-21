#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis数据导入脚本生成器
将JSON格式的Redis数据导出转换为Redis命令脚本
"""

import json
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='将JSON格式的Redis数据转换为Redis命令脚本')
    parser.add_argument('input', help='输入的JSON文件路径')
    parser.add_argument('-o', '--output', help='输出的Redis命令文件路径（默认为stdout）')
    parser.add_argument('-p', '--password', default='5201314', help='Redis密码（默认为5201314）')
    args = parser.parse_args()
    
    # 读取JSON文件
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}", file=sys.stderr)
        return 1
    
    # 生成Redis命令
    commands = ["# 清除所有现有数据", "FLUSHALL", ""]
    
    for key, item in data.items():
        item_type = item.get('type')
        value = item.get('value')
        
        if item_type == 'string':
            commands.append(f"# 设置字符串: {key}")
            commands.append(f"SET {key} {json.dumps(value)}")
            commands.append("")
        
        elif item_type == 'hash':
            commands.append(f"# 添加哈希表: {key}")
            for field, val in value.items():
                commands.append(f"HSET {key} {json.dumps(field)} {json.dumps(val)}")
            commands.append("")
        
        elif item_type == 'list':
            commands.append(f"# 添加列表: {key}")
            for val in value:
                commands.append(f"LPUSH {key} {json.dumps(val)}")
            commands.append("")
        
        elif item_type == 'set':
            commands.append(f"# 添加集合: {key}")
            for val in value:
                commands.append(f"SADD {key} {json.dumps(val)}")
            commands.append("")
        
        elif item_type == 'zset':
            commands.append(f"# 添加有序集合: {key}")
            for member, score in value:
                commands.append(f"ZADD {key} {score} {json.dumps(member)}")
            commands.append("")
    
    commands.append("# 保存数据")
    commands.append("SAVE")
    
    # 输出命令
    script_content = "\n".join(commands)
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"Redis命令已保存到: {args.output}")
            
            # 创建执行脚本
            shell_script = f"""#!/bin/bash

# Redis数据导入脚本
echo "开始导入Redis数据..."

# 检查docker-compose是否已启动
if [ ! "$(docker-compose ps -q redis)" ]; then
  echo "Redis容器未运行，请先启动Docker环境"
  echo "运行: docker-compose up -d"
  exit 1
fi

# 将命令文件传入Redis容器
echo "正在导入数据到Redis..."
cat {args.output} | docker-compose exec -T redis redis-cli -a "{args.password}"

echo "Redis数据导入完成!"
echo "你可以通过以下命令验证数据："
echo "docker-compose exec redis redis-cli -a {args.password} keys '*'"
"""
            
            shell_script_path = 'import_redis_data.sh'
            with open(shell_script_path, 'w', encoding='utf-8') as f:
                f.write(shell_script)
            
            # 设置执行权限
            os.chmod(shell_script_path, 0o755)
            print(f"导入脚本已创建: {shell_script_path}")
            
        except Exception as e:
            print(f"写入输出文件失败: {e}", file=sys.stderr)
            return 1
    else:
        print(script_content)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 