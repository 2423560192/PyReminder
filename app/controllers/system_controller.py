import subprocess

from flask import Blueprint, render_template, jsonify
import datetime
import os
from app.config.config import Config
from app.services.database import get_db_status
from app.services.task_service import get_all_tasks
from app.services.token_service import get_tokens, refresh_tokens
from app.utils.timezone import get_now, TIMEZONE

# 创建blueprint
system_bp = Blueprint('system', __name__)


@system_bp.route('/system_info')
def system_info():
    """系统信息页面，显示时区和数据库连接状态"""
    now = get_now()

    # 同步数据库中的tokens数据
    refresh_tokens()
    tokens = get_tokens()

    # 获取数据库连接状态
    db_status = get_db_status()

    # 计算系统运行时间
    uptime = datetime.datetime.now() - Config.STARTUP_TIME
    hours, remainder = divmod(uptime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"

    # 获取任务数量
    tasks_count = len(get_all_tasks())

    # 获取MySQL数据库信息
    system_data = {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "startup_time": Config.STARTUP_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": uptime_str,
        "timezone": TIMEZONE,
        "db_connected": db_status["connected"],
        "db_type": db_status["type"],
        "db_message": db_status["message"],
        "total_tasks": tasks_count,
        "total_tokens": len(tokens),
        'python_version': subprocess.getoutput('python --version')  # 直接返回字符串
    }
    return render_template('system_info.html', system_data=system_data)


@system_bp.route('/health')
def health_check():
    """健康检查端点，用于Docker健康检查"""
    try:
        # 检查数据库连接
        db_status = get_db_status()

        return jsonify({
            'status': 'healthy' if db_status["connected"] else 'degraded',
            'database': db_status["message"],
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200 if db_status["connected"] else 207
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500
