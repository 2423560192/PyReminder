#!/bin/bash

# 设置颜色常量
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 检查Docker是否运行
echo -e "${BLUE}[检查] ${NC}检查Docker服务状态..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] ${NC}Docker未安装！"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}[错误] ${NC}Docker服务未运行，请先启动Docker！"
    exit 1
fi

echo -e "${GREEN}[成功] ${NC}Docker服务运行正常"

# 检查容器是否存在并运行
echo -e "\n${BLUE}[检查] ${NC}检查PyReminder服务状态..."

containers=("pyreminder-web" "pyreminder-nginx" "pyreminder-redis")
all_running=true

for container in "${containers[@]}"; do
    status=$(docker ps -a --filter "name=$container" --format "{{.Status}}" 2>/dev/null)
    
    if [ -z "$status" ]; then
        echo -e "${RED}[错误] ${NC}容器 $container 不存在！"
        all_running=false
    elif [[ "$status" != Up* ]]; then
        echo -e "${YELLOW}[警告] ${NC}容器 $container 存在但未运行。状态: $status"
        all_running=false
    else
        echo -e "${GREEN}[成功] ${NC}容器 $container 运行正常"
    fi
done

# 检查健康状态
echo -e "\n${BLUE}[检查] ${NC}检查服务健康状态..."

for container in "${containers[@]}"; do
    if docker ps -q --filter "name=$container" &> /dev/null; then
        health=$(docker inspect --format="{{.State.Health.Status}}" $container 2>/dev/null)
        
        if [ -z "$health" ] || [ "$health" == "<nil>" ]; then
            echo -e "${YELLOW}[警告] ${NC}容器 $container 没有健康检查配置"
        elif [ "$health" == "healthy" ]; then
            echo -e "${GREEN}[成功] ${NC}容器 $container 健康状态: $health"
        else
            echo -e "${YELLOW}[警告] ${NC}容器 $container 健康状态: $health"
            all_running=false
        fi
    fi
done

# 检查应用可访问性
echo -e "\n${BLUE}[检查] ${NC}检查应用可访问性..."
if curl -sf http://localhost/health &> /dev/null; then
    echo -e "${GREEN}[成功] ${NC}应用健康检查接口可访问"
else
    echo -e "${YELLOW}[警告] ${NC}无法访问应用健康检查接口"
    all_running=false
fi

# 检查日志路径
echo -e "\n${BLUE}[检查] ${NC}检查日志目录..."
log_dirs=("logs/app" "logs/nginx")

for dir in "${log_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}[成功] ${NC}日志目录 $dir 存在"
    else
        echo -e "${YELLOW}[警告] ${NC}日志目录 $dir 不存在"
    fi
done

# 打印总结
echo -e "\n${BLUE}========== 状态总结 ==========${NC}"
if $all_running; then
    echo -e "${GREEN}[✓] ${NC}所有PyReminder服务运行正常！"
    
    # 获取应用URL
    ip=$(hostname -I | awk '{print $1}')
    echo -e "\n${BLUE}[信息] ${NC}您可以通过以下地址访问应用："
    echo -e "  - 本地访问: ${GREEN}http://localhost${NC}"
    echo -e "  - 局域网访问: ${GREEN}http://$ip${NC}"
else
    echo -e "${YELLOW}[!] ${NC}部分PyReminder服务有问题，请查看上面的详细信息"
    echo -e "\n使用以下命令查看详细日志："
    echo -e "  ${BLUE}docker-compose logs -f${NC}"
fi 