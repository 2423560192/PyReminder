#!/bin/bash

# 域名和邮箱设置
domains=(pyreminder.top www.pyreminder.top)
email="2480419172@qq.com"  # 替换为您的邮箱

# 创建证书存放目录
mkdir -p ./certbot/conf/live/pyreminder.top
mkdir -p ./certbot/www

# 允许目录权限
chmod -R 755 ./certbot

# 只有首次运行时生成证书
if [ ! -e "./certbot/conf/live/pyreminder.top/fullchain.pem" ]; then
  echo "### 获取初始证书 ###"
  
  # 启动Nginx以处理ACME挑战
  docker-compose up --force-recreate -d nginx
  
  # 等待Nginx启动
  echo "等待Nginx启动..."
  sleep 5
  
  # 获取证书
  docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
    ${domains[@]/#/-d } \
    --email $email \
    --agree-tos \
    --no-eff-email
  
  # 重启Nginx以加载证书
  docker-compose exec nginx nginx -s reload
else
  echo "### 证书已存在，跳过获取步骤 ###"
fi

echo "### 初始化完成! ###" 