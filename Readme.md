# PyReminder - Web版时间提醒助手

PyReminder是一个基于Flask和HTML的Web版时间提醒助手，可以帮助用户管理各种任务和提醒。用户可以添加任务、设置提醒时间，系统会在指定时间自动发送通知提醒。支持Redis持久化存储和多通知账号配置。

## 目录结构

项目采用模块化结构，各组件职责清晰：

```
PyReminder/
├── app/                   # 应用主目录
│   ├── static/            # 静态文件
│   ├── templates/         # 模板文件
├── config/                # 配置目录
│   ├── nginx/             # Nginx配置
│   │   └── default.conf   # Nginx默认配置文件
├── logs/                  # 日志目录
│   ├── app/               # 应用日志
│   └── nginx/             # Nginx日志
├── docker-compose.yml     # Docker Compose配置
├── Dockerfile             # Docker构建文件
├── gunicorn.conf.py       # Gunicorn配置
├── requirements.txt       # Python依赖
├── app.py                 # 应用入口
├── deploy.sh              # 部署脚本
├── .env.example           # 环境变量示例
├── .env                   # 环境变量（本地开发）
└── README.md              # 项目文档
```

## 主要功能

- **添加提醒任务**：设置任务标题、内容、日期和时间
- **HTTP通知**：到达设定时间时自动发送通知（通过息知API）
- **实时提醒**：在Web界面显示任务到期提醒
- **任务管理**：查看、删除和跟踪任务状态
- **通知账号管理**：可通过Web界面配置、添加和删除息知API令牌
- **响应式设计**：适配各种设备屏幕大小
- **持久化存储**：使用Redis存储任务，防止服务重启数据丢失
- **多通知账号**：支持配置多个息知API账号，可在添加任务时选择

## 技术栈

- **后端**：Flask (Python 3.9)
- **前端**：HTML, CSS, JavaScript, Bootstrap 5
- **通知**：息知API (HTTP请求)
- **存储**：Redis (带内存存储降级方案)
- **部署**：Docker, Docker Compose, Nginx
- **配置**：环境变量, YAML

## 部署方法

### 在CentOS 7.6上使用Docker部署

1. **克隆代码**：
   ```bash
   git clone https://your-git-repo/PyReminder.git
   cd PyReminder
   ```

2. **使用部署脚本**：
   ```bash
   # 给脚本执行权限
   chmod +x deploy.sh
   
   # 运行部署脚本
   ./deploy.sh
   ```
   
   此脚本将自动检查Docker安装、创建必要的目录、配置文件，并启动所有服务。

3. **配置环境变量**：
   ```bash
   # 编辑环境变量文件
   nano .env
   ```
   
   确保设置以下变量：
   - `FLASK_SECRET_KEY`：设置为随机字符串
   - `REDIS_PASSWORD`：设置Redis密码
   - `NOTIFICATION_TOKEN`：息知API令牌（可选，也可在Web界面设置）

4. **访问应用**：
   - 应用将在 `http://服务器IP` 上可用
   - 管理通知账号：`http://服务器IP/manage`

### 手动部署步骤

如果不想使用部署脚本，可以按以下步骤手动部署：

1. **准备目录结构**：
   ```bash
   mkdir -p config/nginx logs/nginx logs/app
   ```

2. **创建配置文件**：
   - 将 `.env.example` 复制到 `.env` 并自定义
   - 确保 `config/nginx/default.conf` 包含正确配置

3. **构建和启动容器**：
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **查看服务状态**：
   ```bash
   docker-compose ps
   ```

## 日常维护

### 查看日志

```bash
# 查看所有容器日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f redis
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web
```

### 备份数据

```bash
# 备份Redis数据
docker-compose exec redis redis-cli -a your_password SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup-$(date +%Y%m%d).rdb
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建和部署
docker-compose up -d --build
```

## 常见问题解决

### 无法访问应用

1. 检查容器状态：
   ```bash
   docker-compose ps
   ```

2. 查看日志：
   ```bash
   docker-compose logs nginx
   docker-compose logs web
   ```

3. 检查防火墙：
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   
   # CentOS
   sudo firewall-cmd --list-all
   ```

4. Nginx容器重启问题：
   如果Nginx容器不断重启，可能是SSL配置问题。使用`deploy-simple.sh`脚本进行HTTP-only部署。

### Redis连接问题

1. 检查Redis容器状态：
   ```bash
   docker-compose logs redis
   ```

2. 测试Redis连接：
   ```bash
   docker-compose exec redis redis-cli -a your_password ping
   ```

### Redis数据持久化与备份

为确保数据安全，系统配置了以下Redis持久化机制：

1. **AOF持久化**：
   - 启用了 AOF 持久化，系统会将每个写命令追加到 appendonly.aof 文件
   - 配置了 `appendfsync everysec` 模式，每秒执行一次 fsync 操作

2. **RDB快照**：
   - 配置了自动保存规则：
     - 900秒（15分钟）内至少1个键被修改时
     - 300秒（5分钟）内至少10个键被修改时
     - 60秒内至少10000个键被修改时

3. **手动备份**：
   系统提供了备份脚本，可以手动执行或设置定时任务：
   ```bash
   # 执行备份
   ./backup_redis.sh
   
   # 查看备份文件
   ls -l backups/
   ```

4. **数据恢复**：
   如需从备份恢复数据，可使用恢复脚本：
   ```bash
   # 从备份文件恢复
   ./restore_redis.sh backups/redis_backup_20230601_120000.rdb
   ```

5. **定时备份设置**（推荐）：
   建议设置crontab定时任务实现自动备份：
   ```bash
   # 编辑crontab
   crontab -e
   
   # 添加以下行（每天凌晨2点执行备份）
   0 2 * * * cd /path/to/project && ./backup_redis.sh >> backups/backup.log 2>&1
   ```

**注意**：在服务器迁移或重新部署时，请确保备份Redis数据。

## 关于通知功能

本应用使用[息知](https://xz.qqoq.net/)提供的API服务发送通知。您可以通过Web界面管理多个息知账号，每个任务可以选择使用哪个账号发送通知。

## 许可

本项目采用MIT许可证。

## 配置HTTPS（可选）

如果您需要启用HTTPS，请修改Nginx配置：

1. 获取SSL证书（使用certbot或其他方式）

2. 将证书复制到`config/nginx/certs/`目录

3. 更新Nginx配置（`config/nginx/default.conf`）

4. 重启容器：
   ```bash
   docker-compose restart nginx
   ```
