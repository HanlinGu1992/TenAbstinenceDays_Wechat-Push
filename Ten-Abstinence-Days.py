# 安装依赖 pip install os datetime lunarcalendar requests json
import os
import datetime
from lunarcalendar import Converter, Solar
import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号，见上文
userId = os.environ.get("USER_ID")

# 十斋日模板ID
template_id = os.environ.get("TEMPLATE_ID")

# 十斋日列表
ten_zhai_days = {1, 8, 14, 15, 18, 23, 24, 28, 29, 30}


def is_ten_zhai_day(date):
    """判断给定日期是否为十斋日"""
    # 将公历日期转换为阴历
    solar = Solar(date.year, date.month, date.day)
    lunar = Converter.Solar2Lunar(solar)
    
    # 判断是否为十斋日
    return lunar.day in ten_zhai_days


def message_today_info(date):
    """发送推送通知"""
    # 判断明天是否为十斋日
    if is_ten_zhai_day(date):
        solar = Solar(date.year, date.month, date.day)
        lunar = Converter.Solar2Lunar(solar)
        
        # 判断是否为闰月
        leap_month_info = "闰" if lunar.isleap else ""
        
        message = f"今日{solar.year}年阴历{leap_month_info}{lunar.month}月初{lunar.day}为十斋日，可诵读地藏经。"
        # message = f"{solar.year}年阴历{leap_month_info}{lunar.month}月初{lunar.day}(阳历{solar.month}月{solar.day}日)为十斋日，可诵读地藏经。"
        return message
    else:
        return None
    
    
def get_access_token():
    """获取access token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}"
    try:
        response = requests.get(url).json()
        access_token = response.get("access_token")
        if access_token:
            return access_token
        else:
            print("Failed to get access token:", response)
            return None
    except Exception as e:
        print("Error occurred while getting access token:", e)
        return None


def send_message(access_token):
    """发送消息"""
    if not access_token:
        print("Access token is missing.")
        return

    # 获取当前日期
    # today = datetime.date.today()
    today = datetime.datetime(2025, 7, 25) # 闰6月初1
    
    message_today = message_today_info(today)
    
    if message_today:
        body = {
            "touser": userId.strip(),
            "template_id": template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "message": {
                    "value": message_today
                }
            }
        }
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        try:
            response = requests.post(url, json.dumps(body)).json()
            if response.get("errcode") == 0:
                print("Message sent successfully.")
            else:
                print("Failed to send message:", response)
        except Exception as e:
            print("Error occurred while sending message:", e)
    else:
        print("今天不是十斋日，不发送消息。")


if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        send_message(access_token)
        
        # schedule.every().day.at("08:00").do(send_message, access_token)
        
        # while True:
        # schedule.run_pending()
        # time.sleep(1)
