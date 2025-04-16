# PyReminder - Web版时间提醒助手

PyReminder是一个基于Flask和HTML的Web版时间提醒助手，可以帮助用户管理各种任务和提醒。用户可以添加任务、设置提醒时间，系统会在指定时间自动发送通知提醒。支持Redis持久化存储和多通知账号配置。

## 功能特性

- **添加提醒任务**：设置任务标题、内容、日期和时间
- **HTTP通知**：到达设定时间时自动发送通知（通过息知API）
- **实时提醒**：在Web界面显示任务到期提醒
- **任务管理**：查看、删除和跟踪任务状态
- **通知账号管理**：可通过Web界面配置、添加和删除息知API令牌
- **响应式设计**：适配各种设备屏幕大小
- **持久化存储**：使用Redis存储任务，防止服务重启数据丢失
- **多通知账号**：支持配置多个息知API账号，可在添加任务时选择

## 技术栈

- **后端**：Flask (Python)
- **前端**：HTML, CSS, JavaScript, Bootstrap 5
- **通知**：息知API (HTTP请求)
- **存储**：Redis (带内存存储降级方案)
- **配置**：YAML

## 本地安装与使用

### 依赖

- Python 3.6+
- Flask
- python-dotenv
- requests
- werkzeug==2.2.3
- redis
- PyYAML
- Redis服务器（可选，无Redis时会降级为内存存储）

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/PyReminder.git
cd PyReminder
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置：
   - 复制 `.env.example` 为 `.env` 并配置环境变量
   - 通知账号可通过Web界面管理（访问`/manage`路径）

4. 运行应用：
```bash
python app.py
```
或者使用启动脚本（推荐）：
```bash
python start.py
```

5. 访问应用：
在浏览器中访问 `http://127.0.0.1:5000`

## Render部署指南

### 1. 准备工作

- 创建[Render](https://render.com)账号
- 创建[Upstash](https://upstash.com)账号并创建Redis数据库
- Fork或克隆此仓库到您的GitHub账号

### 2. 配置Upstash Redis

1. 登录[Upstash](https://upstash.com)控制台
2. 创建新的Redis数据库
3. 获取连接详情：
   - 终端地址（如：`amused-bream-11167.upstash.io`）
   - 端口（通常为`6379`）
   - 密码

### 3. 在Render上部署

#### 方法一：使用部署按钮

点击下面的按钮一键部署到Render：

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

#### 方法二：手动配置

1. 登录Render控制台
2. 点击"New +"按钮，选择"Web Service"
3. 连接您的GitHub仓库
4. 填写以下信息：
   - **Name**: `pyreminder`（或您喜欢的名称）
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. 点击"Advanced"，添加环境变量：
   - `FLASK_SECRET_KEY`: 生成一个随机字符串
   - `NOTIFICATION_TOKEN`: 您的息知API令牌
   - `REDIS_DB`: `0`（**注意：Upstash只支持0号数据库**）
   - `REDIS_HOST`: 您的Upstash终端地址（如：`amused-bream-11167.upstash.io`）
   - `REDIS_PORT`: `6379`
   - `REDIS_PASSWORD`: 您的Upstash密码
   - `REDIS_SSL`: `True`

6. 点击"Create Web Service"

### 4. 完成部署

- 部署完成后，点击生成的URL访问您的应用
- 第一次访问可能需要等待几分钟应用启动
- 通过应用日志确认是否成功连接到Upstash Redis

## Docker部署指南

### 1. 准备工作

- 确保服务器已安装Docker和Docker Compose
- 配置好`.env`文件（参考`.env.example`）

### 2. 使用Docker Compose部署（推荐）

1. 配置环境变量：
   - 复制`.env.example`为`.env`并修改配置
   - Docker Compose配置中已包含Redis服务，您不需要额外的Redis服务器
   - 默认Redis密码为`redispassword`，您应该在生产环境中修改它

2. 构建并启动容器：
```bash
docker-compose up -d
```

3. 查看容器状态：
```bash
docker-compose ps
```

4. 查看日志：
```bash
docker-compose logs -f
```

5. 停止服务：
```bash
docker-compose down
```

### 3. 直接使用Docker部署

如果您选择不使用Docker Compose，需要先创建一个Redis容器，然后再创建应用容器：

1. 创建Docker网络：
```bash
docker network create pyreminder-network
```

2. 启动Redis容器：
```bash
docker run -d \
  --name pyreminder-redis \
  --network pyreminder-network \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:6-alpine \
  redis-server --requirepass redispassword
```

3. 构建应用镜像：
```bash
docker build -t pyreminder .
```

4. 运行应用容器：
```bash
docker run -d \
  -p 8000:8000 \
  --name pyreminder \
  --network pyreminder-network \
  -e REDIS_HOST=pyreminder-redis \
  -e REDIS_PORT=6379 \
  -e REDIS_DB=0 \
  -e REDIS_PASSWORD=redispassword \
  -e REDIS_SSL=False \
  --env-file .env \
  pyreminder
```

5. 查看容器状态：
```bash
docker ps
```

6. 查看日志：
```bash
docker logs -f pyreminder
```

7. 停止服务：
```bash
docker stop pyreminder pyreminder-redis
docker rm pyreminder pyreminder-redis
```

### 4. 数据持久化说明

- Redis数据存储在名为`redis-data`的Docker卷中
- 即使容器被删除，数据仍会保留
- 如需备份数据，可以使用以下命令：
```bash
docker run --rm -v redis-data:/data -v $(pwd):/backup alpine tar -czf /backup/redis-backup.tar.gz /data
```

## 配置选项

### Redis配置（.env文件）

```
# Redis设置 (Upstash)
REDIS_HOST=amused-bream-11167.upstash.io
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=你的Upstash密码
REDIS_SSL=True
```

### 通知账号配置

通知账号可以通过Web界面进行管理，访问应用的`/manage`路径或点击主页底部的"管理通知账号"按钮。

你可以在此页面：
- 添加新的通知账号（账号名称和息知令牌）
- 查看已配置的所有通知账号
- 删除不需要的通知账号（默认账号不可删除）

## 使用说明

1. **添加任务**：
   - 填写任务标题
   - 输入任务详细内容
   - 选择日期和时间
   - 选择接收通知的账号
   - 点击"添加提醒任务"按钮

2. **查看任务**：
   - 所有任务会显示在任务列表中
   - 可以查看任务标题、提醒时间、通知账号和状态

3. **删除任务**：
   - 点击任务旁边的"删除"按钮即可删除任务

4. **接收提醒**：
   - 当任务时间到时，会在网页上显示提醒通知
   - 同时，系统会通过息知API发送通知提醒

5. **管理通知账号**：
   - 点击主页底部的"管理通知账号"按钮
   - 或直接访问`/manage`路径
   - 添加、查看和删除通知账号

## 关于通知功能

本应用使用[息知](https://xz.qqoq.net/)提供的API服务发送通知。您可以通过Web界面管理多个息知账号，每个任务可以选择使用哪个账号发送通知。

## 存储方式

应用支持两种存储方式：

1. **Redis存储**（推荐）：
   - 使用Upstash Redis提供云端存储
   - 任务数据持久化保存
   - 重启后数据不会丢失
   - 可用于分布式部署

2. **内存存储**（降级模式）：
   - 当Redis不可用时自动使用
   - 简单无依赖
   - 但服务重启后数据会丢失

## 未来改进计划

- 实现用户账户系统
- 添加重复提醒功能（每日/每周/每月）
- 支持更多提醒方式（短信、微信等）
- 任务分类和标签功能
- 任务优先级设置

## 许可

本项目采用MIT许可证。
