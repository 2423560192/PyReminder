# Gunicorn配置文件

# 绑定IP和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = 2

# 每个工作进程的线程数
threads = 2

# 工作模式
worker_class = 'sync'

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 超时设置
timeout = 30
graceful_timeout = 30
keepalive = 2

# 日志设置
accesslog = "/app/logs/app/access.log"
errorlog = "/app/logs/app/error.log"
loglevel = "info"

# 守护进程设置
daemon = False

# 进程名称
proc_name = "pyreminder"

# 清理环境
preload_app = True 