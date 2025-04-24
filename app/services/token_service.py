import os
import flask
from app.models.token import Token
from app.config.database import db

# Flask应用实例的引用
_app = None

def init_app(app):
    """初始化服务，保存对应用程序实例的引用"""
    global _app
    _app = app

# 加载息知token配置
def load_tokens():
    """加载并返回所有可用tokens"""
    default_token = os.getenv('NOTIFICATION_TOKEN', 'XZ77c1d923959433459ec3a08556a6a5b6')

    try:
        # 确保在应用上下文中执行
        if _app is None:
            # 如果没有应用实例，返回默认token
            print("警告: 无法加载tokens，应用程序上下文未初始化")
            return {"默认": default_token}
            
        with _app.app_context():
            # 从数据库加载tokens
            tokens = Token.query.all()
            
            # 如果没有tokens，创建默认token
            if not tokens:
                default = Token(name="默认", value=default_token)
                db.session.add(default)
                db.session.commit()
                print("已创建默认通知账号")
                tokens = [default]
            
            # 转换为字典格式返回
            token_dict = Token.dict_from_list(tokens)
            print(f"从数据库加载了{len(token_dict)}个通知账号")
            return token_dict
        
    except Exception as e:
        print(f"加载token配置失败: {str(e)}")
        # 返回默认token
        return {"默认": default_token}

# 获取当前所有tokens
def get_tokens():
    """返回当前所有可用tokens"""
    try:
        if _app is None:
            print("警告: 无法获取tokens，应用程序上下文未初始化")
            return {}
            
        with _app.app_context():
            tokens = Token.query.all()
            token_dict = Token.dict_from_list(tokens)
            return token_dict
    except Exception as e:
        print(f"获取tokens失败: {str(e)}")
        # 出错时返回空字典
        return {}

# 刷新tokens
def refresh_tokens():
    """从数据库重新加载tokens"""
    return get_tokens()

# 添加或更新token
def add_token(name, value):
    """添加或更新token"""
    try:
        if _app is None:
            print("警告: 无法添加token，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            # 查找是否已存在
            token = Token.query.filter_by(name=name).first()
            
            if token:
                # 更新现有token
                token.value = value
            else:
                # 添加新token
                token = Token(name=name, value=value)
                db.session.add(token)
            
            # 提交更改
            db.session.commit()
            print(f"已保存通知账号：{name}")
            return True
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"保存token失败: {str(e)}")
        return False

# 删除token
def delete_token(name):
    """删除token"""
    if name == '默认':
        return False  # 不允许删除默认token
    
    try:
        if _app is None:
            print("警告: 无法删除token，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            # 查找并删除
            token = Token.query.filter_by(name=name).first()
            if token:
                db.session.delete(token)
                db.session.commit()
                print(f"已删除通知账号：{name}")
                return True
            return False
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"删除token失败: {str(e)}")
        return False 