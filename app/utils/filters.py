import datetime
from app.utils.timezone import format_datetime

# 自定义过滤器
def register_filters(app):
    """注册自定义模板过滤器"""
    
    @app.template_filter('format_datetime')
    def _format_datetime(dt):
        """自定义过滤器：格式化日期时间"""
        return format_datetime(dt) 