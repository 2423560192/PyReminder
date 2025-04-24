import os
import flask
from app.config.database import db
from sqlalchemy import text

# Flask应用实例的引用
_app = None

def init_app(app):
    """初始化服务，保存对应用程序实例的引用"""
    global _app
    _app = app

# 获取数据库连接信息
def get_db_status():
    """获取数据库连接状态信息"""
    try:
        if _app is None:
            return {
                "connected": False,
                "type": "MySQL",
                "message": "应用程序上下文未初始化"
            }
            
        with _app.app_context():
            # 执行一个简单查询来测试连接
            result = db.session.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                return {
                    "connected": True,
                    "type": "MySQL",
                    "message": "MySQL数据库连接正常"
                }
            else:
                return {
                    "connected": False,
                    "type": "MySQL",
                    "message": "MySQL数据库连接异常"
                }
    except Exception as e:
        return {
            "connected": False,
            "type": "MySQL",
            "message": f"MySQL数据库连接失败: {str(e)}"
        } 