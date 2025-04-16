#!/bin/bash

# 域名和邮箱设置
domains=(pyreminder.top www.pyreminder.top)
email="2480419172@qq.com"  # 替换为您的邮箱

# 创建证书存放目录
mkdir -p ./certbot/conf
mkdir -p ./certbot/www

# 允许目录权限
chmod -R 755 ./certbot

echo "### 清理现有目录 ###"
rm -rf ./certbot/conf/live/pyreminder.top
rm -rf ./certbot/conf/archive/pyreminder.top
rm -rf ./certbot/conf/renewal/pyreminder.top.conf

echo "### 获取初始证书 ###"

# 启动Nginx以处理ACME挑战
docker-compose down
docker-compose up --force-recreate -d nginx

# 等待Nginx启动
echo "等待Nginx启动..."
sleep 10

# 获取证书 - 使用 --force-renewal 强制获取新证书
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
  ${domains[@]/#/-d } \
  --email $email \
  --force-renewal \
  --agree-tos \
  --no-eff-email

# 检查证书是否获取成功
if [ -e "./certbot/conf/live/pyreminder.top/fullchain.pem" ]; then
  echo "### 证书获取成功! ###"
else
  echo "### 证书获取失败! ###"
  echo "### 请检查域名是否正确解析到服务器IP，以及80端口是否开放 ###"
  exit 1
fi

# 重启所有服务
echo "### 重启所有服务 ###"
docker-compose down
docker-compose up -d

echo "### 初始化完成! ###"
echo "### 现在可以通过 https://pyreminder.top 访问您的网站 ###" 