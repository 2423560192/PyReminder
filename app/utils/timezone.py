import datetime
import os
import pytz

# 配置时区
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')  # 默认使用中国时区

try:
    TZ = pytz.timezone(TIMEZONE)
    print(f"使用时区: {TIMEZONE}")
except Exception as e:
    print(f"时区设置错误，将使用UTC: {str(e)}")
    TZ = pytz.UTC


# 获取当前时间（带时区）
def get_now():
    return datetime.datetime.now(TZ)


# 格式化日期时间
def format_datetime(dt):
    """自定义格式化日期时间"""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt 