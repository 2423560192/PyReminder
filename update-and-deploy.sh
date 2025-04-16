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

echo_color "开始更新和部署 PyReminder 应用..." "${GREEN}"

# 1. 停止现有容器
echo_color "停止现有容器..." "${YELLOW}"
docker-compose down

# 2. 备份当前的修改（如果有）
echo_color "备份当前的本地修改..." "${YELLOW}"
git stash

# 3. 拉取最新代码
echo_color "拉取最新代码..." "${GREEN}"
if git pull; then
  echo_color "代码更新成功！" "${GREEN}"
else
  echo_color "代码拉取过程中发现冲突，将使用远程版本..." "${YELLOW}"
  
  # 放弃本地修改，使用远程版本
  git reset --hard origin/master
  git pull
fi

# 4. 确保目录和权限设置正确
echo_color "创建必要的目录结构..." "${YELLOW}"
mkdir -p config/nginx logs/nginx logs/app

echo_color "设置日志目录权限..." "${YELLOW}"
chmod -R 777 logs/app
chmod -R 777 logs/nginx

# 5. 运行部署脚本
echo_color "开始部署应用..." "${GREEN}"
./deploy.sh

# 6. 显示部署后的状态
echo_color "部署完成，显示容器状态:" "${GREEN}"
docker-compose ps

echo_color "\n查看应用健康状态:" "${GREEN}"
curl -s http://localhost/health || echo -e "${RED}应用健康检查失败，请检查日志${NC}"

echo_color "\n如需查看详细日志，请运行:" "${YELLOW}"
echo_color "  docker-compose logs -f" "${YELLOW}" 