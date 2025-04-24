import os
import datetime
import secrets
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))
    TEMPLATES_FOLDER = 'app/templates'
    STATIC_FOLDER = 'app/static'
    
    # 应用程序配置
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5000))
    
    # 记录程序启动时间
    STARTUP_TIME = datetime.datetime.now()
    
    # 默认通知Token
    DEFAULT_TOKEN = os.getenv('NOTIFICATION_TOKEN', 'XZ77c1d923959433459ec3a08556a6a5b6') 