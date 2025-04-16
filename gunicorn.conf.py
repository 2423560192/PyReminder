import multiprocessing
import os

# 工作进程配置
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2

# 绑定地址
bind = "0.0.0.0:8000"

# 日志配置
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# 性能配置
timeout = 120
graceful_timeout = 30
keepalive = 5

# 工作进程设置
max_requests = 1000
max_requests_jitter = 50

# 其他配置
daemon = False
preload_app = True

# 健康检查端点
def on_starting(server):
    print("Gunicorn starting...")

def on_exit(server):
    print("Gunicorn shutting down...") 