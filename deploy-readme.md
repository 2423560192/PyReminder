# PyReminder 部署指南

## 快速部署步骤

我已经准备了一个脚本，可以自动重置和部署您的应用。请按照以下步骤操作：

1. 设置脚本执行权限：
```bash
chmod +x reset-and-deploy.sh
```

2. 运行脚本：
```bash
./reset-and-deploy.sh
```

3. 验证部署：
   - 访问 `http://pyreminder.top`
   - 验证网站是否正常运行

## 手动部署步骤（如果脚本不生效）

如果自动脚本无法正常工作，您可以按照以下步骤手动部署：

1. 停止并删除所有容器：
```bash
docker-compose down
docker rm -f $(docker ps -a | grep certbot | awk '{print $1}') 2>/dev/null || true
```

2. 删除certbot相关目录：
```bash
rm -rf ./certbot
```

3. 修改nginx.conf文件：
```bash
# 编辑nginx.conf文件，删除所有SSL相关配置
nano nginx.conf
```

4. 修改docker-compose.yml文件：
```bash
# 编辑docker-compose.yml文件，删除certbot服务和所有SSL相关配置
nano docker-compose.yml
```

5. 重新启动服务：
```bash
docker-compose up -d
```

6. 检查容器状态：
```bash
docker-compose ps
```

## 故障排查

如果遇到问题，可以查看容器日志：

```bash
# 查看Nginx日志
docker-compose logs nginx

# 查看Web应用日志
docker-compose logs web

# 查看Redis日志
docker-compose logs redis
```

要完全重置部署，可以执行：

```bash
# 停止并删除所有容器和卷
docker-compose down -v

# 清理未使用的资源
docker system prune -f

# 从头开始部署
docker-compose up -d
```

## 维护

### 数据备份

备份Redis数据：
```bash
docker-compose exec redis redis-cli -a 5201314 SAVE
docker cp pyreminder-redis-1:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb
```

### 重启服务

```bash
docker-compose restart
```

### 更新应用

当有代码更新时：
```bash
git pull
docker-compose up -d --build
``` 