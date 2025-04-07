import os
import requests
import json
from urllib.parse import quote_plus
from datetime import datetime, timedelta

# 配置参数
PUSHDEER_PUSHKEY = os.environ.get('PUSHDEER_PUSHKEY')
TENCENT_STOCK_API = 'http://qt.gtimg.cn/q=sh000001'
TRIGGER_PERCENT = 1.5
STATE_FILE = 'push_state.json'  # 状态存储文件

def get_shanghai_index():
    """从腾讯接口获取上证指数数据"""

def send_notification(stock_data):
    """发送推送通知"""

def load_push_state():
    """加载推送状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            # 转换字符串时间为datetime对象
            state['last_push'] = datetime.fromisoformat(state['last_push']) if state['last_push'] else None
            return state
    except (FileNotFoundError, json.JSONDecodeError):
        return {'last_push': None, 'push_count': 0}

def save_push_state(state):
    """保存推送状态"""
    # 转换datetime为字符串
    state_to_save = {
        'last_push': state['last_push'].isoformat() if state['last_push'] else None,
        'push_count': state['push_count']
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state_to_save, f)

def should_send(current_time):
    """判断是否需要发送通知"""
    state = load_push_state()
    
    # 当天首次触发
    if state['push_count'] == 0:
        return True
    
    # 后续触发检查时间间隔
    time_diff = current_time - state['last_push']
    return time_diff >= timedelta(hours=1)

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始执行监控任务")
    current_time = datetime.now()
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
    if should_send(current_time):
        print(f"[{current_time}] 触发通知条件")
        send_notification(stock_data)
        # 更新状态
        new_state = {
            'last_push': current_time,
            'push_count': state['push_count'] + 1
        }
        save_push_state(new_state)
    else:
        next_push = state['last_push'] + timedelta(hours=1)
        print(f"[{current_time}] 已达今日推送上限，下次可推送时间：{next_push}")
