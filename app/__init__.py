from flask import Flask
from app.config.config import Config
from app.controllers.task_controller import task_bp
from app.controllers.token_controller import token_bp
from app.controllers.system_controller import system_bp
from app.config.database import init_db
from app.services.task_service import start_check_thread, init_app as init_task_service
from app.services.token_service import load_tokens, init_app as init_token_service
from app.services.database import init_app as init_db_service
from app.utils.filters import register_filters
import os


def create_app(config_class=Config):
    """应用程序工厂函数"""
    # 获取当前文件所在目录的上级目录（项目根目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 使用绝对路径来指定模板和静态文件夹
    templates_folder = os.path.join(base_dir, config_class.TEMPLATES_FOLDER)
    static_folder = os.path.join(base_dir, config_class.STATIC_FOLDER)

    app = Flask(__name__,
                template_folder=templates_folder,
                static_folder=static_folder)

    # 加载配置
    app.config.from_object(config_class)

    # 初始化MySQL数据库连接
    init_db(app)
    
    # 初始化服务
    init_db_service(app)
    init_task_service(app)
    init_token_service(app)
    
    # 在应用上下文中加载令牌配置
    with app.app_context():
        load_tokens()

    # 注册蓝图
    app.register_blueprint(task_bp, url_prefix='/')
    app.register_blueprint(token_bp, url_prefix='/token')
    app.register_blueprint(system_bp, url_prefix='/system')

    # 注册自定义过滤器
    register_filters(app)

    # 启动任务检查线程
    start_check_thread()

    print("准时宝启动...")

    return app
