import multiprocessing

# 工作进程数量
workers = multiprocessing.cpu_count() * 2 + 1
# 每个进程的线程数
threads = 2
# 绑定地址
bind = "0.0.0.0:8000"
# 超时时间
timeout = 120
# 日志级别
loglevel = "info"
# 最大请求数
max_requests = 1000
# 最大请求随机抖动
max_requests_jitter = 50
# 预加载应用
preload_app = True
# 守护进程模式
daemon = False
# 工作模式
worker_class = "sync"
# 优雅重启时间
graceful_timeout = 30
# 保持连接时间
keepalive = 5 