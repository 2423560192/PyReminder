import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
class DatabaseConfig:
    # MySQL数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '5201314')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'zhunshi')
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() in ['true', '1', 'yes']

# 数据库实例
db = SQLAlchemy()

def init_db(app):
    """初始化数据库连接"""
    try:
        # 配置SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_ECHO'] = DatabaseConfig.SQLALCHEMY_ECHO
        
        # 初始化数据库
        db.init_app(app)
        
        # 在应用上下文中创建所有表
        with app.app_context():
            db.create_all()
            
        print(f"已连接到MySQL数据库 (数据库: {DatabaseConfig.MYSQL_DATABASE})")
        return True
    except Exception as e:
        print(f"警告: 无法连接到MySQL数据库: {str(e)}")
        return False 