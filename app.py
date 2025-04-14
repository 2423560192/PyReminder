from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import threading
import time
import datetime
import os
import requests
import json
import yaml
import redis
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Redis连接配置
# 优先使用REDIS_URL（Render提供的环境变量）
redis_url = os.getenv('REDIS_URL')
if redis_url:
    # 解析REDIS_URL
    parsed_url = urllib.parse.urlparse(redis_url)
    redis_host = parsed_url.hostname
    redis_port = parsed_url.port or 6379
    redis_password = parsed_url.password
    redis_db = int(os.getenv('REDIS_DB', 2))  # 使用DB 2
    print(f"使用REDIS_URL环境变量连接Redis")
else:
    # 使用单独的环境变量
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 2))  # 默认使用DB 2
    redis_password = os.getenv('REDIS_PASSWORD')

# 初始化Redis客户端
try:
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=True  # 自动将字节解码为字符串
    )
    r.ping()  # 测试连接
    print(f"已连接到Redis服务器 (数据库: {redis_db})")
except Exception as e:
    print(f"警告: 无法连接到Redis服务器: {str(e)}，将使用内存存储")
    r = None

# 任务ID计数器键名
TASK_ID_KEY = "task:id_counter"
# 任务列表键名
TASKS_KEY = "tasks"

# 加载息知token配置
def load_tokens():
    try:
        # 检查tokens.yaml文件是否存在
        if os.path.exists('tokens.yaml'):
            with open('tokens.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config.get('tokens', {})
        else:
            # 在生产环境中，可能没有tokens.yaml文件
            # 尝试从环境变量加载
            token = os.getenv('NOTIFICATION_TOKEN')
            if token:
                return {"默认": token}
            else:
                return {"默认": "XZ77c1d923959433459ec3a08556a6a5b6"}
    except Exception as e:
        print(f"加载token配置失败: {str(e)}")
        return {"默认": os.getenv('NOTIFICATION_TOKEN', 'XZ77c1d923959433459ec3a08556a6a5b6')}

# 获取所有配置的通知令牌
tokens = load_tokens()

# 获取下一个任务ID
def get_next_task_id():
    if r:
        # 使用Redis的INCR命令自动递增
        return r.incr(TASK_ID_KEY)
    else:
        # 从任务列表中找出最大ID
        max_id = 0
        for task in get_all_tasks():
            if task["id"] > max_id:
                max_id = task["id"]
        return max_id + 1

# 保存任务到Redis
def save_task(task):
    if r:
        # 将datetime对象转换为ISO格式字符串存储
        task_copy = task.copy()
        task_copy["datetime"] = task["datetime"].isoformat()
        # 添加到Redis列表
        r.hset(TASKS_KEY, str(task["id"]), json.dumps(task_copy))
        return True
    else:
        # 内存存储方式不需要额外保存
        return False

# 从Redis加载所有任务
def get_all_tasks():
    tasks = []
    
    if r:
        # 从Redis加载所有任务
        all_tasks = r.hgetall(TASKS_KEY)
        for task_id, task_json in all_tasks.items():
            try:
                task = json.loads(task_json)
                # 将ISO格式字符串转回datetime对象
                task["datetime"] = datetime.datetime.fromisoformat(task["datetime"])
                tasks.append(task)
            except Exception as e:
                print(f"任务解析错误: {str(e)}")
    
    # 按时间排序
    return sorted(tasks, key=lambda x: x["datetime"])

# 删除任务
def delete_task_by_id(task_id):
    if r:
        r.hdel(TASKS_KEY, str(task_id))
        return True
    else:
        # 内存存储模式在全局tasks列表已处理
        return False

# 更新任务状态
def update_task_status(task_id, triggered=True):
    if r:
        task_json = r.hget(TASKS_KEY, str(task_id))
        if task_json:
            task = json.loads(task_json)
            task["triggered"] = triggered
            # 保存回Redis
            r.hset(TASKS_KEY, str(task_id), json.dumps(task))
            return True
    return False

# 内存存储模式的任务列表（仅当Redis不可用时使用）
tasks = []

# 发送通知
def send_notification(task_title, task_content, task_time, token_name="默认"):
    try:
        # 获取指定名称的token
        token = tokens.get(token_name, tokens.get("默认"))
        
        params = {
            'title': '任务提醒通知',
            'content': f"""任务名称: {task_title}\n
任务内容: {task_content}\n
提醒时间: {task_time}\n

您设置的任务时间已到！请及时处理。
"""
        }
        
        response = requests.get(f'https://xizhi.qqoq.net/{token}.send', params=params, verify=False)
        
        if response.status_code == 200:
            print(f"已发送任务提醒通知：{task_title}，使用token: {token_name}")
            return True
        else:
            print(f"发送通知失败，状态码：{response.status_code}")
            return False
            
    except Exception as e:
        print(f"发送通知失败: {str(e)}")
        return False

# 检查任务线程
def check_tasks():
    while True:
        now = datetime.datetime.now()
        triggered_tasks = []
        
        # 获取所有任务
        current_tasks = get_all_tasks() if r else tasks
        
        # 检查是否有到期任务
        for task in current_tasks:
            if not task.get("triggered", False) and now >= task["datetime"]:
                print(f"任务触发: {task['title']}")
                
                # 更新任务状态
                if r:
                    update_task_status(task["id"], True)
                else:
                    task["triggered"] = True
                
                triggered_tasks.append(task)
        
        # 处理触发的任务
        for task in triggered_tasks:
            task_time = task["datetime"].strftime("%Y-%m-%d %H:%M")
            print('发送提醒')
            send_notification(
                task_title=task["title"],
                task_content=task.get("content", "无内容"),
                task_time=task_time,
                token_name=task.get("token_name", "默认")
            )
        
        # 每秒检查一次
        time.sleep(1)

# 启动检查线程
check_thread = threading.Thread(target=check_tasks, daemon=True)
check_thread.start()

@app.route('/')
def index():
    # 获取所有任务
    all_tasks = get_all_tasks() if r else tasks
    return render_template('index.html', tasks=all_tasks, tokens=tokens)

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title', '未命名任务')
    content = request.form.get('content', '')
    reminder_date = request.form.get('date', '')
    reminder_time = request.form.get('time', '')
    token_name = request.form.get('token_name', '默认')
    
    if not reminder_date or not reminder_time:
        flash("日期和时间不能为空", "danger")
        return redirect(url_for('index'))
    
    # 验证token名称是否存在
    if token_name not in tokens:
        flash(f"通知账号 '{token_name}' 不存在", "danger")
        return redirect(url_for('index'))
    
    # 解析日期和时间
    try:
        reminder_datetime = datetime.datetime.strptime(
            f"{reminder_date} {reminder_time}", "%Y-%m-%d %H:%M"
        )
        
        # 创建新任务
        task_id = get_next_task_id()
        task = {
            "id": task_id,
            "title": title,
            "content": content,
            "datetime": reminder_datetime,
            "token_name": token_name,
            "triggered": False
        }
        
        # 存储任务
        if r:
            save_task(task)
        else:
            tasks.append(task)
        
        flash("任务添加成功！", "success")
        return redirect(url_for('index'))
    except ValueError:
        flash("日期格式错误，请使用YYYY-MM-DD HH:MM格式", "danger")
        return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if r:
        delete_task_by_id(task_id)
    else:
        global tasks
        tasks = [task for task in tasks if task["id"] != task_id]
    
    flash("任务已删除", "success")
    return redirect(url_for('index'))

@app.route('/get_tasks')
def get_tasks():
    # 获取所有任务并序列化
    all_tasks = get_all_tasks() if r else tasks
    serializable_tasks = []
    
    for task in all_tasks:
        serializable_task = task.copy()
        serializable_task["datetime"] = task["datetime"].strftime("%Y-%m-%d %H:%M")
        serializable_tasks.append(serializable_task)
    
    return jsonify(serializable_tasks)

@app.template_filter('format_datetime')
def format_datetime(dt):
    """自定义过滤器：格式化日期时间"""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt

if __name__ == '__main__':
    print("时间提醒助手启动...")
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode, host='0.0.0.0', port=5000) 