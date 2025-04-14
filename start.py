#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import webbrowser
import time
import platform

def check_python_version():
    """检查Python版本是否满足要求"""
    print("检查Python版本...")
    if sys.version_info < (3, 6):
        print("错误：需要Python 3.6或更高版本！")
        return False
    return True

def check_dependencies():
    """检查依赖是否已安装"""
    print("检查项目依赖...")
    try:
        import flask
        import dotenv
        print("依赖检查通过！")
        return True
    except ImportError as e:
        print(f"错误：缺少必要的依赖：{e}")
        print("请运行：pip install -r requirements.txt")
        return False

def check_env_file():
    """检查.env文件是否存在，如果不存在则从示例文件创建"""
    print("检查环境配置文件...")
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("未找到.env文件，将从.env.example创建...")
        try:
            with open(".env.example", "r", encoding="utf-8") as example:
                with open(".env", "w", encoding="utf-8") as env_file:
                    env_file.write(example.read())
            print("已创建.env文件，请打开此文件并配置您的邮箱信息！")
            
            # 尝试打开.env文件供用户编辑
            if platform.system() == "Windows":
                os.system("notepad .env")
            elif platform.system() == "Darwin":  # macOS
                os.system("open .env")
            else:  # Linux and others
                editors = ["nano", "vim", "vi", "gedit"]
                for editor in editors:
                    try:
                        subprocess.call([editor, ".env"])
                        break
                    except FileNotFoundError:
                        continue
                        
        except Exception as e:
            print(f"创建.env文件时出错：{e}")
            return False
    
    return True

def start_app():
    """启动Flask应用"""
    print("\n启动时间提醒助手...")
    
    # 根据操作系统选择不同的启动方式
    if platform.system() == "Windows":
        flask_process = subprocess.Popen(["python", "app.py"], 
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        flask_process = subprocess.Popen(["python", "app.py"])
    
    # 等待服务器启动
    print("正在启动服务器，请稍候...")
    time.sleep(3)
    
    # 自动打开浏览器
    print("正在打开Web界面...")
    webbrowser.open("http://localhost:5000")
    
    print("\n==================================================")
    print("时间提醒助手已启动！访问：http://localhost:5000")
    print("按Ctrl+C关闭此窗口停止服务器")
    print("==================================================\n")
    
    try:
        # 保持脚本运行
        flask_process.wait()
    except KeyboardInterrupt:
        # 捕获Ctrl+C，结束进程
        print("\n正在关闭时间提醒助手...")
        flask_process.terminate()
        flask_process.wait()
        print("已关闭！")

if __name__ == "__main__":
    print("=" * 50)
    print("时间提醒助手启动程序")
    print("=" * 50)
    
    if (check_python_version() and 
        check_dependencies() and 
        check_env_file()):
        start_app()
    else:
        print("\n启动失败：请解决上述问题后重试！")
        input("按Enter键退出...") 