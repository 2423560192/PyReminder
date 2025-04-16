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
import secrets
import pytz

# 加载环境变量
load_dotenv()

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# 记录程序启动时间
STARTUP_TIME = datetime.datetime.now()

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

# Redis连接配置
# 优先使用REDIS_URL（Render提供的环境变量）
redis_url = os.getenv('REDIS_URL')
if redis_url:
    # 解析REDIS_URL
    parsed_url = urllib.parse.urlparse(redis_url)
    redis_host = parsed_url.hostname
    redis_port = parsed_url.port or 6379
    redis_password = parsed_url.password
    redis_db = 0  # Upstash只支持0号数据库
    redis_ssl = True  # Render Redis通常需要SSL
    print(f"使用REDIS_URL环境变量连接Redis")
else:
    # 使用单独的环境变量
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = 0  # Upstash只支持0号数据库
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_ssl = os.getenv('REDIS_SSL', 'False').lower() in ['true', '1', 'yes']

# 初始化Redis客户端
try:
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        ssl=redis_ssl,  # 启用SSL支持Upstash
        decode_responses=True  # 自动将字节解码为字符串
    )
    r.ping()  # 测试连接
    print(f"已连接到Redis服务器 (数据库: {redis_db}, SSL: {redis_ssl})")
except Exception as e:
    print(f"警告: 无法连接到Redis服务器: {str(e)}，将使用内存存储")
    r = None

# 任务ID计数器键名
TASK_ID_KEY = "task:id_counter"
# 任务列表键名
TASKS_KEY = "tasks"
# token配置键名
TOKENS_KEY = "tokens"
# 本地文件路径（仅作为备用）
TOKENS_FILE = 'tokens.yaml'

# 加载息知token配置
def load_tokens():
    tokens_dict = {}
    default_token = os.getenv('NOTIFICATION_TOKEN', 'XZ77c1d923959433459ec3a08556a6a5b6')
    
    try:
        # 首先尝试从Redis加载
        if r:
            redis_tokens = r.hgetall(TOKENS_KEY)
            if redis_tokens:
                print(f"从Redis加载了{len(redis_tokens)}个通知账号")
                return redis_tokens
        
        # 如果Redis中没有数据，尝试从文件加载
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                tokens_dict = config.get('tokens', {})
                
                # 如果从文件加载成功，保存到Redis
                if r and tokens_dict:
                    for name, token in tokens_dict.items():
                        r.hset(TOKENS_KEY, name, token)
                    print(f"已将{len(tokens_dict)}个通知账号从文件同步到Redis")
                    
                return tokens_dict
    except Exception as e:
        print(f"加载token配置失败: {str(e)}")
    
    # 默认token
    tokens_dict = {"默认": default_token}
    
    # 保存默认token到Redis
    if r:
        r.hset(TOKENS_KEY, "默认", default_token)
        
    return tokens_dict

# 保存息知token配置
def save_tokens(tokens_dict):
    try:
        # 确保包含默认令牌
        if '默认' not in tokens_dict:
            tokens_dict['默认'] = os.getenv('NOTIFICATION_TOKEN', 'XZ77c1d923959433459ec3a08556a6a5b6')
        
        # 优先保存到Redis
        if r:
            # 先清除旧数据
            r.delete(TOKENS_KEY)
            # 添加新数据
            for name, token in tokens_dict.items():
                r.hset(TOKENS_KEY, name, token)
            print(f"已成功保存{len(tokens_dict)}个通知账号到Redis")
            return True
        
        # 如果Redis不可用，尝试保存到文件（可能在Render上失败）
        try:
            config = {'tokens': tokens_dict}
            with open(TOKENS_FILE, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, allow_unicode=True)
            print(f"已保存{len(tokens_dict)}个token到{TOKENS_FILE}")
            return True
        except Exception as e:
            print(f"保存token到文件失败（在Render上这是正常现象）: {str(e)}")
            return False if not r else True  # 如果Redis正常工作，仍然返回成功
            
    except Exception as e:
        print(f"保存token配置失败: {str(e)}")
        return False

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
        # 确保datetime有时区信息
        dt = task["datetime"]
        if dt.tzinfo is None:
            dt = TZ.localize(dt)
        task_copy["datetime"] = dt.isoformat()
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
                # 将ISO格式字符串转回datetime对象（带时区）
                task["datetime"] = datetime.datetime.fromisoformat(task["datetime"])
                # 确保时区正确
                if task["datetime"].tzinfo is None:
                    task["datetime"] = TZ.localize(task["datetime"])
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
        # 首先刷新tokens以确保使用最新的数据
        global tokens
        if r:
            refreshed_tokens = r.hgetall(TOKENS_KEY)
            if refreshed_tokens:
                tokens = refreshed_tokens
        
        # 获取指定名称的token
        token = tokens.get(token_name)
        if not token:
            print(f"警告: 通知账号'{token_name}'不存在，将使用默认通知账号")
            token = tokens.get("默认")
            
        # 如果默认账号也不存在，这是一个严重错误
        if not token:
            print("错误: 无法找到有效的通知账号，无法发送通知")
            return False
        
        params = {
            'title': task_title,
            'content': f"""任务名称: {task_title}\n
任务内容: {task_content}\n
提醒时间: {task_time}\n

您设置的任务时间已到！请及时处理。
"""
        }
        
        print(f"正在发送通知: {token[:8]}*** URL={f'https://xizhi.qqoq.net/{token}.send'}")
        
        try:
            # 设置较长的超时时间和重试次数
            response = requests.get(
                f'https://xizhi.qqoq.net/{token}.send', 
                params=params, 
                verify=False,
                timeout=30  # 增加请求超时时间
            )
            
            print(f"通知请求状态码: {response.status_code}")
            if response.status_code == 200:
                response_text = response.text[:100] if len(response.text) > 100 else response.text
                print(f"息知API响应: {response_text}")
                print(f"已成功发送任务提醒通知：{task_title}，使用token: {token_name}")
                return True
            else:
                print(f"发送通知失败，状态码：{response.status_code}，响应内容：{response.text[:200]}")
                return False
        except requests.exceptions.Timeout:
            print(f"发送通知超时，可能是网络跨境问题，任务标题: {task_title}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"发送通知连接错误，可能是网络限制问题，任务标题: {task_title}")
            return False
            
    except Exception as e:
        print(f"发送通知失败，详细错误: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细堆栈信息
        return False

# 检查任务线程
def check_tasks():
    while True:
        now = get_now()
        triggered_tasks = []
        
        # 获取所有任务
        current_tasks = get_all_tasks() if r else tasks
        
        # 检查是否有到期任务
        for task in current_tasks:
            # 确保任务时间有时区信息
            task_datetime = task["datetime"]
            if task_datetime.tzinfo is None:
                # 为无时区任务添加时区
                task_datetime = TZ.localize(task_datetime)
            
            if not task.get("triggered", False) and now >= task_datetime:
                print(f"任务触发: {task['title']} (计划时间: {task_datetime}, 当前时间: {now})")
                
                # 更新任务状态
                if r:
                    update_task_status(task["id"], True)
                else:
                    task["triggered"] = True
                
                triggered_tasks.append(task)
        
        # 处理触发的任务
        for task in triggered_tasks:
            task_time = task["datetime"].strftime("%Y-%m-%d %H:%M")
            print(f'发送提醒: {task["title"]} - {task_time}')
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

@app.route('/system_info')
def system_info():
    """系统信息页面，显示时区和数据库连接状态"""
    now = get_now()
    
    # 同步Redis中的tokens数据
    global tokens
    if r:
        tokens = r.hgetall(TOKENS_KEY) or tokens
    
    # 计算系统运行时间
    uptime = datetime.datetime.now() - STARTUP_TIME
    hours, remainder = divmod(uptime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
    
    # 获取内存任务数量
    memory_tasks_count = len(tasks) if not r else 0
    
    system_data = {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "startup_time": STARTUP_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": uptime_str,
        "timezone": TIMEZONE,
        "redis_connected": r is not None,
        "redis_host": redis_host if r else "未连接",
        "redis_port": redis_port if r else "未连接",
        "redis_ssl": "已启用" if redis_ssl else "未启用",
        "total_tasks": len(get_all_tasks() if r else tasks),
        "memory_tasks": memory_tasks_count,
        "total_tokens": len(tokens),
        "python_version": os.popen('python --version').read().strip(),
    }
    return render_template('system_info.html', system_data=system_data)

@app.route('/')
def index():
    # 重新从数据源加载tokens，确保与最新添加的账号同步
    global tokens
    if r:
        # 从Redis重新获取最新数据
        tokens = r.hgetall(TOKENS_KEY) or tokens
    
    # 获取所有任务
    all_tasks = get_all_tasks() if r else tasks
    return render_template('index.html', tasks=all_tasks, tokens=tokens, redis_connected=r is not None)

@app.route('/add_task', methods=['POST'])
def add_task():
    # 添加任务前先刷新tokens，确保使用最新的通知账号列表
    global tokens
    if r:
        tokens = r.hgetall(TOKENS_KEY) or tokens
    
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
        # 创建无时区的datetime对象
        naive_datetime = datetime.datetime.strptime(
            f"{reminder_date} {reminder_time}", "%Y-%m-%d %H:%M"
        )
        
        # 添加时区信息
        reminder_datetime = TZ.localize(naive_datetime)
        print(f"新任务时间设置为: {reminder_datetime} (带时区)")
        
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
    except ValueError as e:
        print(f"日期解析错误: {str(e)}")
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
    # 同步Redis中的tokens数据
    global tokens
    if r:
        tokens = r.hgetall(TOKENS_KEY) or tokens
    
    # 获取所有任务并序列化
    all_tasks = get_all_tasks() if r else tasks
    serializable_tasks = []
    
    for task in all_tasks:
        serializable_task = task.copy()
        serializable_task["datetime"] = task["datetime"].strftime("%Y-%m-%d %H:%M")
        serializable_tasks.append(serializable_task)
    
    return jsonify(serializable_tasks)

@app.route('/manage')
def manage_tokens():
    """息知API令牌管理页面"""
    # 重新从数据源加载最新tokens
    global tokens
    if r:
        # 从Redis重新获取最新数据
        tokens = r.hgetall(TOKENS_KEY) or tokens
    
    return render_template('manage_tokens.html', tokens=tokens, redis_connected=r is not None)

@app.route('/add_token', methods=['POST'])
def add_token():
    """添加或更新息知API令牌"""
    token_name = request.form.get('token_name', '').strip()
    token_value = request.form.get('token_value', '').strip()
    
    # 验证输入
    if not token_name:
        flash("账号名称不能为空", "danger")
        return redirect(url_for('manage_tokens'))
    
    if not token_value or not token_value.startswith('XZ'):
        flash("息知令牌格式不正确，应以XZ开头", "danger")
        return redirect(url_for('manage_tokens'))
    
    # 更新全局tokens字典
    global tokens
    
    # 检查是否已存在同名账号
    is_new = token_name not in tokens
    tokens[token_name] = token_value
    
    # 直接保存到Redis（如果可用）
    if r:
        # 直接设置，无需经过save_tokens函数
        r.hset(TOKENS_KEY, token_name, token_value)
        if is_new:
            flash(f"已添加新通知账号「{token_name}」", "success")
        else:
            flash(f"已更新通知账号「{token_name}」的令牌", "success")
        return redirect(url_for('manage_tokens'))
    
    # 如果Redis不可用，尝试通过save_tokens保存
    if save_tokens(tokens):
        if is_new:
            flash(f"已添加新通知账号「{token_name}」", "success")
        else:
            flash(f"已更新通知账号「{token_name}」的令牌", "success")
    else:
        flash(f"保存账号失败，请检查数据库连接", "danger")
    
    return redirect(url_for('manage_tokens'))

@app.route('/delete_token/<token_name>', methods=['POST'])
def delete_token(token_name):
    """删除息知API令牌"""
    global tokens
    
    # 不允许删除"默认"账号
    if token_name == '默认':
        flash("不能删除默认通知账号", "danger")
        return redirect(url_for('manage_tokens'))
    
    # 从字典中删除
    if token_name in tokens:
        del tokens[token_name]
        
        # 如果Redis可用，直接从Redis删除
        if r:
            r.hdel(TOKENS_KEY, token_name)
            # 重新从Redis加载tokens确保同步
            tokens = r.hgetall(TOKENS_KEY) or tokens
            flash(f"已删除通知账号「{token_name}」", "success")
            return redirect(url_for('manage_tokens'))
        
        # 否则尝试通过save_tokens保存
        if save_tokens(tokens):
            flash(f"已删除通知账号「{token_name}」", "success")
        else:
            flash(f"删除账号失败，请检查数据库连接", "danger")
    else:
        flash(f"通知账号「{token_name}」不存在", "warning")
    
    return redirect(url_for('manage_tokens'))

@app.template_filter('format_datetime')
def format_datetime(dt):
    """自定义过滤器：格式化日期时间"""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt

# 健康检查端点
@app.route('/health')
def health_check():
    """健康检查端点，用于Docker健康检查"""
    try:
        # 检查Redis连接
        if r:
            r.ping()
        
        return jsonify({
            'status': 'healthy',
            'redis': 'connected' if r else 'disconnected',
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

if __name__ == '__main__':
    print("时间提醒助手启动...")
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
