#!/usr/bin/env python3
"""
监控 INTC 20260618 $60 Call 限价单触发
价格达到 $2.45 时发送微信通知
"""
import urllib.request
import json
import time
import os
import sys

# ==== 配置 ====
TARGET_PRICE = 2.45
SYMBOL = "INTC260618C00060000"
CHECK_INTERVAL = 60  # 每60秒检查一次
NOTIFY_THRESHOLD = 0.03  # 价格在 2.45 ± 0.03 范围内都通知
START_HOUR = 21  # 北京时间 21:30 开始监控
END_HOUR = 4     # 北京时间次日 04:00 停止（美股收盘后）

# ==== 价格获取 ====
def get_price():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval=1m&range=1d"
    req = urllib.request.urlopen(
        urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), 
        timeout=10
    )
    data = json.loads(req.read())
    result = data['chart']['result'][0]
    meta = result['meta']
    price = meta.get('regularMarketPrice')
    return price

# ==== 发微信通知 ====
def send_wechat_alert(price):
    message = (
        f"📢 INTC $60 Call (2026-06-18) 价格提醒\n\n"
        f"当前价格: ${price:.2f}\n"
        f"监控价: ${TARGET_PRICE:.2f}\n"
        f"状态: 已触及限价附近，请前往 IBKR 挂单买入！\n\n"
        f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    cmd = [
        'curl', '-s', '-X', 'POST',
        os.environ.get('OPENCLAW_WEBHOOK', 'http://localhost:3000/webhook'),
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'text': message})
    ]
    os.system(' '.join(cmd))
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ 已发送价格提醒: ${price:.2f}")

def is_market_open():
    """粗略判断美股是否在交易"""
    now = time.localtime()
    hour = now.tm_hour
    wday = now.tm_wday  # 0=周一
    # 美股夏令时 21:30 - 04:00（次日）= 北京时间
    if wday in (0, 1, 2, 3, 4):  # 周一到周五
        if hour >= START_HOUR or hour < END_HOUR:
            return True
    return False

def main():
    print(f"🟢 监控启动: {SYMBOL} 目标价 ${TARGET_PRICE}")
    print(f"⏰ 监控时段: 北京时间 {START_HOUR}:30 - 次日 {END_HOUR}:00")
    notified = False

    while True:
        try:
            if is_market_open():
                price = get_price()
                now_str = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{now_str}] 当前价格: ${price:.2f} | 目标: ${TARGET_PRICE}")

                if price and abs(price - TARGET_PRICE) <= NOTIFY_THRESHOLD:
                    if not notified:
                        send_wechat_alert(price)
                        notified = True
                        print(f"[{now_str}] ✅ 触发提醒，监控结束")
                        break
                else:
                    notified = False
            else:
                now_str = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{now_str}] ⏸ 非交易时段，跳过检查")

        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ 错误: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
