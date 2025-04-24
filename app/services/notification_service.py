import requests
import traceback
from app.services.token_service import get_tokens, refresh_tokens

# 发送通知
def send_notification(task_title, task_content, task_time, token_name="默认"):
    try:
        # 首先刷新tokens以确保使用最新的数据
        refresh_tokens()
        tokens = get_tokens()

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
        traceback.print_exc()  # 打印详细堆栈信息
        return False 