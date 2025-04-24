from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
import datetime
from app.models.task import Task
from app.services.task_service import add_task as add_task_service, get_all_tasks, delete_task_by_id
from app.services.token_service import get_tokens, refresh_tokens
from app.utils.timezone import TZ
from app.services.database import get_db_status

# 创建blueprint
task_bp = Blueprint('task', __name__)

@task_bp.route('/')
def index():
    """主页视图"""
    # 刷新tokens
    refresh_tokens()
    
    # 获取所有任务和tokens
    tasks = get_all_tasks()
    tokens = get_tokens()
    
    # 获取数据库状态
    db_status = get_db_status()
    
    return render_template('index.html', tasks=tasks, tokens=tokens, db_connected=db_status["connected"])


@task_bp.route('/add_task', methods=['POST'])
def add_task():
    # 添加任务前先刷新tokens，确保使用最新的通知账号列表
    refresh_tokens()
    tokens = get_tokens()

    title = request.form.get('title', '未命名任务')
    content = request.form.get('content', '')
    reminder_date = request.form.get('date', '')
    reminder_time = request.form.get('time', '')
    token_name = request.form.get('token_name', '默认')
    recurrence = request.form.get('recurrence', '')  # 获取重复选项

    if not reminder_date or not reminder_time:
        flash("日期和时间不能为空", "danger")
        return redirect(url_for('task.index'))

    # 验证token名称是否存在
    if token_name not in tokens:
        flash(f"通知账号 '{token_name}' 不存在", "danger")
        return redirect(url_for('task.index'))

    # 解析日期和时间
    try:
        # 创建无时区的datetime对象
        naive_datetime = datetime.datetime.strptime(
            f"{reminder_date} {reminder_time}", "%Y-%m-%d %H:%M"
        )

        # 添加时区信息
        reminder_datetime = TZ.localize(naive_datetime)
        print(f"新任务时间设置为: {reminder_datetime} (带时区)")

        # 添加任务
        task = add_task_service(
            title=title,
            content=content,
            reminder_datetime=reminder_datetime,
            token_name=token_name,
            recurrence=recurrence
        )

        flash("任务添加成功！", "success")
        return redirect(url_for('task.index'))
    except ValueError as e:
        print(f"日期解析错误: {str(e)}")
        flash("日期格式错误，请使用YYYY-MM-DD HH:MM格式", "danger")
        return redirect(url_for('task.index'))


@task_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """删除任务"""
    if delete_task_by_id(task_id):
        flash("任务已删除", "success")
    else:
        flash("删除任务失败", "danger")
    
    return redirect(url_for('task.index'))


@task_bp.route('/get_tasks')
def get_tasks():
    # 同步Redis中的tokens数据
    refresh_tokens()

    # 获取所有任务并序列化
    all_tasks = get_all_tasks()
    serializable_tasks = []

    for task in all_tasks:
        serializable_tasks.append(task.to_serializable_dict())

    return jsonify(serializable_tasks) 