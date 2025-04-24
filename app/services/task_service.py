from datetime import datetime, timedelta
import threading
import time
from app.models.task import Task
from app.utils.timezone import get_now, TZ
from app.config.database import db
from app.services.notification_service import send_notification

# Flask应用实例的引用
_app = None

def init_app(app):
    """初始化服务，保存对应用程序实例的引用"""
    global _app
    _app = app

# 保存任务到数据库
def save_task(task):
    try:
        if _app is None:
            print("警告: 无法保存任务，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            db.session.add(task)
            db.session.commit()
            return True
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"保存任务失败: {str(e)}")
        return False

# 获取所有任务
def get_all_tasks():
    try:
        if _app is None:
            print("警告: 无法获取任务列表，应用程序上下文未初始化")
            return []
            
        with _app.app_context():
            # 查询所有任务并按时间排序
            tasks = Task.query.order_by(Task.datetime).all()
            return tasks
    except Exception as e:
        print(f"获取任务列表失败: {str(e)}")
        return []

# 删除任务
def delete_task_by_id(task_id):
    try:
        if _app is None:
            print("警告: 无法删除任务，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            task = Task.query.get(task_id)
            if task:
                db.session.delete(task)
                db.session.commit()
                return True
            return False
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"删除任务失败: {str(e)}")
        return False

# 更新任务状态
def update_task_status(task_id, triggered=True):
    try:
        if _app is None:
            print("警告: 无法更新任务状态，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            task = Task.query.get(task_id)
            if task:
                task.triggered = triggered
                db.session.commit()
                return True
            return False
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"更新任务状态失败: {str(e)}")
        return False

# 重置周期性任务的状态并更新下次执行时间
def reset_recurring_task(task_id):
    try:
        if _app is None:
            print("警告: 无法重置周期任务，应用程序上下文未初始化")
            return False
            
        with _app.app_context():
            task = Task.query.get(task_id)
            
            # 只处理周期性任务
            if not task or not task.recurrence:
                return False

            now = get_now()
            
            # 计算下一次执行时间
            if task.recurrence == "daily":
                # 增加一天
                next_dt = task.datetime + timedelta(days=1)
                
                # 如果下次执行时间已经过去，设置为今天的相同时间
                if next_dt < now:
                    next_dt = datetime(
                        now.year, now.month, now.day,
                        task.datetime.hour, task.datetime.minute,
                        tzinfo=task.datetime.tzinfo
                    )
                    # 如果更新后的时间仍然小于当前时间，再加一天
                    if next_dt < now:
                        next_dt = next_dt + timedelta(days=1)

                # 更新任务
                task.datetime = next_dt
                task.triggered = False
                db.session.commit()
                
                print(f"已重置周期任务 ID:{task.id}，下次执行时间: {next_dt}")
                return True
            
            return False
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"重置周期任务错误: {str(e)}")
        return False

# 添加任务
def add_task(title, content, reminder_datetime, token_name="默认", recurrence=None):
    try:
        if _app is None:
            print("警告: 无法添加任务，应用程序上下文未初始化")
            return None
            
        with _app.app_context():
            task = Task(
                title=title,
                content=content,
                datetime_obj=reminder_datetime,
                token_name=token_name,
                triggered=False,
                recurrence=recurrence
            )
            
            # 存储到数据库
            db.session.add(task)
            db.session.commit()
            
            return task
    except Exception as e:
        if _app:
            with _app.app_context():
                db.session.rollback()
        print(f"添加任务失败: {str(e)}")
        return None

# 检查任务线程
def check_tasks_thread():
    """检查并触发到期任务的后台线程"""
    while True:
        try:
            if _app is None:
                print("警告: 无法检查任务，应用程序上下文未初始化")
                time.sleep(5)
                continue
                
            with _app.app_context():
                now = get_now()
                
                # 查询未触发且时间已到的任务
                pending_tasks = Task.query.filter(
                    Task.triggered == False,
                    Task.datetime <= now
                ).all()

                for task in pending_tasks:
                    print(f"触发任务提醒: {task.title} (ID: {task.id})")

                    # 获取token名称，默认使用"默认"
                    token_name = task.token_name if task.token_name else "默认"

                    # 发送息知通知
                    result = send_notification(
                        task.title,
                        task.content,
                        task.datetime.strftime("%Y-%m-%d %H:%M") if isinstance(task.datetime, datetime) else task.datetime,
                        token_name
                    )

                    # 更新任务状态
                    if result:
                        update_task_status(task.id)

                        # 如果是周期性任务，重置状态并设置下一次执行时间
                        if task.recurrence:
                            reset_recurring_task(task.id)

            # 每5秒检查一次
            time.sleep(5)

        except Exception as e:
            print(f"任务检查线程发生错误: {str(e)}")
            time.sleep(5)  # 发生错误后等待5秒再继续

# 启动任务检查线程
def start_check_thread():
    check_thread = threading.Thread(target=check_tasks_thread, daemon=True)
    check_thread.start()
    return check_thread 