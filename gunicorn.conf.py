# Gunicorn配置文件

import os
import multiprocessing

# 绑定IP和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 每个工作进程的线程数
threads = 2

# 工作模式
worker_class = "gevent"

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时设置
timeout = 60
graceful_timeout = 30
keepalive = 2

# 日志设置
logdir = "/app/logs"
os.makedirs(logdir, exist_ok=True)

accesslog = os.path.join(logdir, "access.log")
errorlog = os.path.join(logdir, "error.log")
loglevel = "info"

# 守护进程设置
daemon = False

# 进程名称
proc_name = "pyreminder"

# 清理环境
preload_app = True

# 保持环境变量
raw_env = [
    "FLASK_APP=wsgi:app",
] 