import os
import json
import requests
from datetime import datetime

# ==================== 配置区域 ====================
API_URL = "https://lecture.tongji.edu.cn/api/gj/studentwx/lecturehallapi/GetLectureHallList?page=1&pageSize=10&status=0&time=0&classLevel=0"

# 从环境变量中读取敏感配置（安全且方便修改）
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY")
SESSION_ID = os.getenv("SESSION_ID")
WEIXIN_CODE_ID = os.getenv("WEIXIN_CODE_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541d41) XWEB/25560 Flue",
    "Authorization": "Basic cTN4YXRwbTV0eHc0MmtoejVjYzg1YWY0OmI1dTRteWVrZDVkYno0cGUxcTFoY3dnb3h4eXR0bTM3",
    "Cookie": f"PG.ASP.Session.ID={SESSION_ID}; PG.ASP.WeiXinCode.ID={WEIXIN_CODE_ID}",
    "Referer": "https://lecture.tongji.edu.cn/index",
    "Accept": "application/json, text/plain, */*"
}

HISTORY_FILE = "known_lectures.json"
# ==================================================

def send_wechat_notice(title, content):
    if not SERVERCHAN_KEY:
        print("未设置 SERVERCHAN_KEY，跳过发送推送")
        return
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {"title": title, "desp": content}
    try:
        requests.post(url, data=data, timeout=5)
        print("微信推送发送成功")
    except Exception as e:
        print(f"推送异常: {e}")

def load_known_ids():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_known_ids(known_ids):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(known_ids), f, ensure_ascii=False, indent=2)

def run_check():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查讲座更新...")
    known_ids = load_known_ids()
    
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"请求接口失败，HTTP 状态码: {response.status_code}")
            if response.status_code in [401, 403]:
                send_wechat_notice("高等讲堂监控提醒", "Cookie 已失效，请在 GitHub Secrets 中更新凭证！")
            return
        
        res_json = response.json()
        lectures = res_json.get("data", {}).get("row", [])
        
        new_lectures_count = 0
        for lec in lectures:
            lec_id = lec.get("DataId")
            if not lec_id:
                continue
                
            if lec_id not in known_ids:
                known_ids.add(lec_id)
                new_lectures_count += 1
                
                # 如果历史记录不为空，说明是真正的新讲座；如果是第一次运行（生成历史文件），不发送消息
                if len(known_ids) > len(lectures):
                    title = lec.get("Cathedra", "未命名讲座")
                    venue = lec.get("Venue", "未知地点")
                    start_time = lec.get("LectureTimeStart", "未知时间")
                    signup_time = lec.get("TimeSigningUp", "未知抢票时间")
                    
                    msg = f"**讲座题目**：{title}\n\n**地点**：{venue}\n\n**讲座时间**：{start_time}\n\n**抢票时间**：{signup_time}"
                    print(f"发现新讲座：{title}")
                    send_wechat_notice("高等讲堂·新讲座上线通知", msg)

        save_known_ids(known_ids)
        print(f"检查完成，本次新增 {new_lectures_count} 条记录。")

    except Exception as e:
        print(f"运行发生异常: {e}")

if __name__ == "__main__":
    run_check()