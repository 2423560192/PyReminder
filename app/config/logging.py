import os
import logging
from logging.handlers import RotatingFileHandler

# 日志配置
def configure_logging(app):
    """配置应用的日志系统"""
    # 确保日志目录存在
    log_dir = os.path.join(app.root_path, '..', 'logs', 'app')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置错误日志
    error_log = os.path.join(log_dir, 'error.log')
    error_file_handler = RotatingFileHandler(
        error_log, 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # 设置访问日志
    access_log = os.path.join(log_dir, 'access.log')
    access_file_handler = RotatingFileHandler(
        access_log, 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s: %(message)s'
    ))
    
    # 设置应用级别的日志处理
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(access_file_handler)
    
    # 设置Werkzeug（Flask的WSGI工具库）的日志处理
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.addHandler(access_file_handler)
    
    # 记录应用启动信息
    app.logger.info('准时宝应用启动') 