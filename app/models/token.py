from datetime import datetime
from app.config.database import db
from sqlalchemy import func

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    def __init__(self, name, value, id=None):
        if id is not None:
            self.id = id
        self.name = name
        self.value = value
    
    @classmethod
    def from_dict(cls, token_dict):
        """从字典创建Token对象列表"""
        tokens = []
        for name, value in token_dict.items():
            tokens.append(cls(name, value))
        return tokens
    
    def to_dict(self):
        """转换为字典"""
        return {self.name: self.value}
    
    @staticmethod
    def dict_from_list(token_list):
        """从Token对象列表创建字典"""
        result = {}
        for token in token_list:
            result[token.name] = token.value
        return result 