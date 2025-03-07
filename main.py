import json
import tkinter as tk
from tkinter import messagebox, ttk
import time
from datetime import datetime, timedelta
import threading
import sys
import os
from pystray import Icon, Menu, MenuItem
import PIL.Image
from tkcalendar import DateEntry


class ReminderApp:

    def save_reminders(self):
        with open("reminders.json", "w") as f:
            json.dump([{"content": r["content"], "time": r["time"].isoformat(), 'repeat': r['repeat']} for r in
                       self.reminders], f)

    def load_reminders(self):
        try:
            with open("reminders.json", "r") as f:
                self.reminders = [{"content": r["content"], "time": r["time"].isoformat(), 'repeat': r['repeat']} for r
                                  in
                                  json.load(f)]
            self.update_listbox()
        except Exception as e:
            pass

    def __init__(self, root, autostart=False):
        self.root = root
        self.root.title("提醒小助手")
        self.root.geometry("400x600")
        self.reminders = []
        self.autostart = autostart

        if autostart:
            self.root.withdraw()

        # 顶部提示
        self.label = tk.Label(root, text="请输入提醒内容和时间", font=("Arial", 12))
        self.label.pack(pady=10)

        # 提醒内容
        self.content_label = tk.Label(root, text="提醒内容:")
        self.content_label.pack()
        self.content_entry = tk.Entry(root, width=40)
        self.content_entry.pack(pady=5)

        # 时间选择（放入Frame以优化布局）
        self.time_label = tk.Label(root, text="提醒时间:")
        self.time_label.pack()
        time_frame = tk.Frame(root)
        time_frame.pack(pady=5)

        self.date_entry = DateEntry(time_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, year=2025)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        hour_menu = ttk.Combobox(time_frame, textvariable=self.hour_var,
                                 values=[f"{i:02d}" for i in range(24)], width=5)
        hour_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

        minute_menu = ttk.Combobox(time_frame, textvariable=self.minute_var,
                                   values=[f"{i:02d}" for i in range(60)], width=5)
        minute_menu.pack(side=tk.LEFT, padx=5)

        # 是否每天重复
        self.repeat_var = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text="重复每天", variable=self.repeat_var).pack(pady=5)

        # 添加按钮
        self.add_button = tk.Button(root, text="添加提醒", command=self.add_reminder)
        self.add_button.pack(pady=10)

        # 提醒列表
        self.listbox = tk.Listbox(root, height=15, width=50)
        self.listbox.pack(pady=10)

        # 删除按钮
        self.delete_button = tk.Button(root, text="删除选中提醒", command=self.delete_reminder)
        self.delete_button.pack(pady=5)

        # 线程和托盘
        self.running = True
        self.check_thread = threading.Thread(target=self.check_reminders)
        self.check_thread.daemon = True
        self.check_thread.start()

        if autostart:
            self.create_tray_icon()

        # 导入之前的数据
        self.load_reminders()

    # 创建系统托盘
    def create_tray_icon(self):
        try:

            image = PIL.Image.new('RGB', (64, 64), color=(0, 128, 255))
            menu = Menu(
                MenuItem('显示', self.show_window),
                MenuItem('退出', self.on_closing)
            )
            self.tray_icon = Icon("Reminder", image, "提醒小助手", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except ImportError:
            print("需要安装 pystray 和 PIL 库来启用系统托盘功能")

    def show_window(self):
        self.root.deiconify()

    def add_reminder(self):
        content = self.content_entry.get()
        date_str = self.date_entry.get()  # 例如 "03/06/25"
        hour = self.hour_var.get()
        minute = self.minute_var.get()

        # 将 "03/06/25" 转换为 "2025-03-06"
        month, day, year = date_str.split('/')
        year = f"20{year}"  # 假设都是 20XX 年
        time_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour}:{minute}"  # "2025-03-06 14:30"

        try:
            reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            if reminder_time < datetime.now():
                messagebox.showwarning("警告", "不能添加过去的时间！")
                return
            reminder = {"content": content, "time": reminder_time, "repeat": self.repeat_var.get()}
            self.reminders.append(reminder)
            self.update_listbox()
            self.content_entry.delete(0, tk.END)
            self.date_entry.set_date(datetime.now())
            self.hour_var.set("00")
            self.minute_var.set("00")
            self.repeat_var.set(False)  # 重置为未选中
        except ValueError:
            messagebox.showerror("错误", "时间格式错误！")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for reminder in self.reminders:
            time_str = reminder["time"].strftime("%Y-%m-%d %H:%M")
            self.listbox.insert(tk.END,
                                f"{time_str} - {reminder['content']} - {'每天重复' if reminder['repeat'] == True else '单次'} ")

    def delete_reminder(self):
        try:
            selected_idx = self.listbox.curselection()[0]
            del self.reminders[selected_idx]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("警告", "请先选择一个提醒！")

    def check_reminders(self):
        while self.running:
            current_time = datetime.now()
            for i, reminder in enumerate(self.reminders[:]):
                if current_time >= reminder["time"]:
                    self.root.after(0, lambda: messagebox.showinfo("提醒", f"时间到！\n{reminder['content']}"))
                    if reminder["repeat"]:
                        reminder["time"] += timedelta(days=1)  # 推迟一天
                    else:
                        self.reminders.pop(i)
                    self.root.after(0, self.update_listbox)
            time.sleep(60)

    def on_closing(self):
        self.save_reminders()
        if self.autostart:
            self.root.withdraw()  # 后台模式隐藏
        else:
            self.running = False
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
            self.root.destroy()


def main():
    autostart = "--autostart" in sys.argv
    root = tk.Tk()
    app = ReminderApp(root, autostart)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
