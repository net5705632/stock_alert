import os
import requests
import json
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# 配置参数
PUSHDEER_PUSHKEY = os.environ.get('PUSHDEER_PUSHKEY')
TENCENT_STOCK_API = 'http://qt.gtimg.cn/q=sh000001'
TRIGGER_PERCENT = 1.5
STATE_FILE = 'push_state.json'

def get_shanghai_index():
    """从腾讯接口获取上证指数数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(TENCENT_STOCK_API, headers=headers, timeout=10)
        response.raise_for_status()
        
        if '="' not in response.text:
            raise ValueError("无效的API响应格式")
            
        raw_data = response.text.split('="')[1].strip('"')
        parts = raw_data.split('~')
        
        if len(parts) < 5:
            raise ValueError("数据字段不足")
            
        return {
            'current_price': float(parts[3]),
            'change_percent': round((float(parts[3]) - float(parts[4])) / float(parts[4]) * 100, 2)
        }
    except Exception as e:
        print(f"[{datetime.now()}] 获取数据失败: {str(e)}")
        return None

def send_notification(stock_data):
    """发送推送通知"""
    try:
        percent = stock_data['change_percent']
        current_price = stock_data['current_price']
        
        direction = "涨" if percent > 0 else "跌"
        message = (
            f"⚠️ 上证指数{direction}幅警报！\n"
            f"当前点位：{current_price}\n"
            f"涨跌幅：{percent}%"
        )
        encoded_msg = quote_plus(message)
        url = f"https://api2.pushdeer.com/message/push?pushkey={PUSHDEER_PUSHKEY}&text={encoded_msg}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"[{datetime.now()}] 通知发送成功")
    except Exception as e:
        print(f"[{datetime.now()}] 推送失败: {str(e)}")

def load_push_state():
    """加载推送状态"""
    try:
        if not os.path.exists(STATE_FILE):
            return {'last_push': None, 'push_count': 0}
            
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            state['last_push'] = datetime.fromisoformat(state['last_push']) if state['last_push'] else None
            return state
    except Exception as e:
        print(f"[{datetime.now()}] 状态加载失败: {str(e)}")
        return {'last_push': None, 'push_count': 0}

def save_push_state(state):
    """保存推送状态"""
    try:
        state_to_save = {
            'last_push': state['last_push'].isoformat() if state['last_push'] else None,
            'push_count': state['push_count']
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state_to_save, f)
    except Exception as e:
        print(f"[{datetime.now()}] 状态保存失败: {str(e)}")

def should_send(current_time, state):
    """判断是否需要发送通知"""
    # 当天首次触发
    if state['push_count'] == 0:
        return True
    
    # 检查时间间隔
    if state['last_push']:
        time_diff = current_time - state['last_push']
        return time_diff >= timedelta(hours=1)
    return True

if __name__ == "__main__":
    current_time = datetime.now()
    print(f"[{current_time}] 开始执行监控任务")
    
    stock_data = get_shanghai_index()
    if stock_data is None:
        print(f"[{current_time}] 获取数据失败")
        exit()

    change_percent = stock_data['change_percent']
    current_price = stock_data['current_price']
    print(f"[{current_time}] 当前点位：{current_price}，涨跌幅：{change_percent}%")

    if abs(change_percent) < TRIGGER_PERCENT:
        print(f"[{current_time}] 涨跌幅未达阈值")
        exit()

    state = load_push_state()
    if should_send(current_time, state):
        print(f"[{current_time}] 触发通知条件")
        send_notification(stock_data)
        new_state = {
            'last_push': current_time,
            'push_count': state['push_count'] + 1
        }
        save_push_state(new_state)
    else:
        next_push = state['last_push'] + timedelta(hours=1)
        print(f"[{current_time}] 已达今日推送上限，下次可推送时间：{next_push}")
