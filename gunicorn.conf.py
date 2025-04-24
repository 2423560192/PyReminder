# Gunicorn configuration file

import os
import multiprocessing

# Bind IP and port
bind = "0.0.0.0:5000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Threads per worker
threads = 2

# Worker class
worker_class = "sync"

# Maximum requests
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 60
graceful_timeout = 30
keepalive = 2

# Log settings
logdir = "/app/logs"
os.makedirs(logdir, exist_ok=True)

accesslog = os.path.join(logdir, "access.log")
errorlog = os.path.join(logdir, "error.log")
loglevel = "info"

# Daemon settings
daemon = False

# Process name
proc_name = "pyreminder"

# Cleanup environment
preload_app = True

# Environment variables
raw_env = [
    "FLASK_APP=wsgi:app",
] 