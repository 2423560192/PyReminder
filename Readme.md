
# PyReminder

PyReminder 是一个基于 Python 的桌面提醒工具，支持开机自启和系统托盘运行。用户可以添加多个提醒任务，设置具体时间，到期后自动弹出提示窗口，帮助你高效管理日程。

## 功能特性
- **添加提醒**：支持自定义提醒内容和时间（格式：`YYYY-MM-DD HH:MM`）。
- **任务管理**：查看所有提醒任务，支持删除已添加的提醒。
- **自动提醒**：到达设定时间时弹出提示窗口。
- **开机自启**：支持 Windows 系统开机自动运行，启动后隐藏至系统托盘。
- **系统托盘**：后台运行时可通过托盘图标显示主界面或退出程序。
- **轻量简洁**：基于 `tkinter` 实现，界面直观易用。

## 安装
### 依赖
- Python 3.x
- 必要库：
  ```bash
  pip install pystray Pillow
  ```
  （`tkinter` 通常随 Python 自带，无需额外安装）

### 下载
克隆仓库：
```bash
git clone https://github.com/[你的用户名]/PyReminder.git
```
进入项目目录：
```bash
cd PyReminder
```

## 使用方法
### 普通运行
运行主程序：
```bash
python pyreminder.py
```
- 输入提醒内容和时间，点击“添加提醒”。
- 在列表中查看所有任务，支持选中删除。
- 到时自动弹出提醒窗口。

### 开机自启
运行带 `--autostart` 参数：
```bash
python pyreminder.py --autostart
```
- 程序将启动并隐藏至系统托盘。
- 通过托盘图标点击“显示”打开主界面，或“退出”关闭程序。

### Windows 开机自启设置
1. 使用 PyInstaller 打包为可执行文件：
   ```bash
   pip install pyinstaller
   pyinstaller -F pyreminder.py
   ```
2. 创建快捷方式，目标添加 `--autostart` 参数，例如：
   ```text
   "C:\path\to\pyreminder.exe" --autostart
   ```
3. 将快捷方式放入启动文件夹（`Win + R` 输入 `shell:startup`）。

## 截图
（建议上传界面截图到仓库，例如 `screenshots/` 文件夹，然后在此处添加链接）

- **主界面**：
- **提醒弹窗**：

## 未来改进
- 添加声音提醒
- 支持提醒任务保存到本地文件
- 优化界面样式
- 添加重复提醒功能（每日/每周）

## 贡献
欢迎提交 Issues 或 Pull Requests！如果有任何建议或问题，请随时联系。

## 许可
本项目采用 MIT 许可证。
