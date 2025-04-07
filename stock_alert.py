import os
import requests
from urllib.parse import quote_plus
from datetime import datetime

# 配置参数
PUSHDEER_PUSHKEY = os.environ.get('PUSHDEER_PUSHKEY')  # 从环境变量获取
TENCENT_STOCK_API = 'http://qt.gtimg.cn/q=sh000001'
TRIGGER_PERCENT = 1.5

def get_shanghai_index():
    """从腾讯接口获取上证指数并计算涨跌幅"""
    try:
        response = requests.get(TENCENT_STOCK_API, timeout=10)
        response.raise_for_status()
        
        # 解析返回数据
        raw_data = response.text.split('="')[1].strip('"')
        parts = raw_data.split('~')
        print(f"[{datetime.now()}] 调试信息 - 原始字段:", parts)

        # 核心字段索引
        current_price = float(parts[3])  # 当前价
        prev_close = float(parts[4])    # 昨收价
        
        # 计算涨跌幅百分比
        change_percent = (current_price - prev_close) / prev_close * 100
        return round(change_percent, 2)
    except (IndexError, ValueError) as e:
        print(f"[{datetime.now()}] 数据解析失败: {str(e)}")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] 获取数据失败: {str(e)}")
        return None

def send_notification(percent):
    """通过PushDeer发送通知"""
    try:
        direction = "涨" if percent > 0 else "跌"
        message = f"⚠️ 上证指数{direction}幅警报！当前：{percent}%"
        encoded_msg = quote_plus(message)
        url = f"https://api2.pushdeer.com/message/push?pushkey={PUSHDEER_PUSHKEY}&text={encoded_msg}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"[{datetime.now()}] 通知发送成功")
    except Exception as e:
        print(f"[{datetime.now()}] 推送失败: {str(e)}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始执行监控任务")
    change_percent = get_shanghai_index()
    
    if change_percent is not None and abs(change_percent) >= TRIGGER_PERCENT:
        print(f"[{datetime.now()}] 当前涨跌幅：{change_percent}%，触发通知")
        send_notification(change_percent)
    else:
        print(f"[{datetime.now()}] 当前涨跌幅：{change_percent or '未知'}%，未达阈值")
