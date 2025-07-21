import os
import requests

class Notifier:
    def __init__(self):
        self.mode = os.getenv("NOTIFY_MODE", "ntfy")  # gotify/dingtalk/ntfy/...

    def send(self, content, title=None, priority=None):
        if self.mode == "gotify":
            return self._send_gotify(content, title, priority)
        elif self.mode == "dingtalk":
            return self._send_dingtalk(content, title)
        elif self.mode == "ntfy":
            return self._send_ntfy(content, title, priority)
        else:
            print("Unknown notify mode:", self.mode)
            return False

    def _send_gotify(self, content, title=None, priority=None):
        url = os.getenv("GOTIFY_URL")
        token = os.getenv("GOTIFY_TOKEN")
        if not url or not token:
            print("GOTIFY_URL or GOTIFY_TOKEN not set")
            return False
        api_url = url.rstrip('/') + f"/message?token={token}"
        payload = {
            "title": title or os.getenv("GOTIFY_TITLE", "通知"),
            "message": content,
            "priority": int(priority or os.getenv("GOTIFY_PRIORITY", "3"))
        }
        try:
            resp = requests.post(api_url, json=payload, timeout=10)
            if resp.status_code == 200:
                print("✅ Gotify 推送成功")
                return True
            else:
                print(f"❌ Gotify 推送失败: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print("Gotify推送异常:", e)
            return False

    def _send_dingtalk(self, content, title=None):
        webhook = os.getenv("DINGTALK_WEBHOOK")
        if not webhook:
            print("DINGTALK_WEBHOOK not set")
            return False
        data = {
            "msgtype": "text",
            "text": {"content": (title + '\n' if title else '') + content}
        }
        try:
            resp = requests.post(webhook, json=data, timeout=10)
            if resp.status_code == 200:
                print("✅ 钉钉推送成功")
                return True
            else:
                print(f"❌ 钉钉推送失败: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print("钉钉推送异常:", e)
            return False

    def _send_ntfy(self, content, title=None, priority=None):
        url = os.getenv("NTFY_URL")  # 例如 https://ntfy.sh
        topic = os.getenv("NTFY_TOPIC")
        token = os.getenv("NTFY_TOKEN")  # 可选
        if not url or not topic:
            print("NTFY_URL or NTFY_TOPIC not set")
            return False
        api_url = url.rstrip('/') + f"/{topic}"

        # 只允许ASCII标题，否则拼到内容前面
        def safe_ascii(s):
            try:
                s.encode('ascii')
                return s
            except Exception:
                return None

        ascii_title = safe_ascii(title) if title else None
        headers = {
            "Content-Type": "text/plain; charset=utf-8"
        }
        if ascii_title:
            headers["Title"] = ascii_title
        if priority:
            headers["Priority"] = str(priority)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 如果title不能做header，就拼到内容前面
        if not ascii_title and title:
            content = f"{title}\n{content}"

        try:
            resp = requests.post(api_url, data=content.encode('utf-8'), headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                print("✅ ntfy 推送成功")
                return True
            else:
                print(f"❌ ntfy 推送失败: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print("ntfy推送异常:", e)
            return False 
