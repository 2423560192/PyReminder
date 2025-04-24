from datetime import datetime
import json
from app.utils.timezone import get_now, TZ
from app.config.database import db
from sqlalchemy import func

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    datetime = db.Column(db.DateTime, nullable=False)
    token_name = db.Column(db.String(50), nullable=False, default="默认")
    triggered = db.Column(db.Boolean, default=False)
    recurrence = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    
    def __init__(self, id=None, title=None, content=None, datetime_obj=None, token_name="默认", triggered=False, recurrence=None):
        if id is not None:
            self.id = id
        self.title = title
        self.content = content
        self.datetime = datetime_obj
        self.token_name = token_name
        self.triggered = triggered
        self.recurrence = recurrence
    
    @classmethod
    def from_dict(cls, task_dict):
        """从字典创建任务对象"""
        datetime_obj = task_dict["datetime"]
        # 如果是字符串格式，转换为datetime对象
        if isinstance(datetime_obj, str):
            datetime_obj = datetime.fromisoformat(datetime_obj)
            # 确保时区正确
            if datetime_obj.tzinfo is None:
                datetime_obj = TZ.localize(datetime_obj)
        
        return cls(
            id=task_dict.get("id"),
            title=task_dict["title"],
            content=task_dict["content"],
            datetime_obj=datetime_obj,
            token_name=task_dict.get("token_name", "默认"),
            triggered=task_dict.get("triggered", False),
            recurrence=task_dict.get("recurrence")
        )
    
    def to_dict(self):
        """转换为字典"""
        # 确保datetime有时区信息
        dt = self.datetime
        if dt.tzinfo is None:
            dt = TZ.localize(dt)
            
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "datetime": dt.isoformat() if isinstance(dt, datetime) else dt,
            "token_name": self.token_name,
            "triggered": self.triggered,
            "recurrence": self.recurrence
        }
    
    def to_json(self):
        """转换为JSON字符串"""
        return json.dumps(self.to_serializable_dict())
    
    def to_serializable_dict(self):
        """转换为可序列化的字典（用于JSON）"""
        result = self.to_dict()
        result["datetime"] = self.datetime.strftime("%Y-%m-%d %H:%M") if isinstance(self.datetime, datetime) else self.datetime
        return result 