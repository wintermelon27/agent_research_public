#!/usr/bin/env python3
"""检查 INTC 20260618 $60 Call 是否触及 $2.45，写入标记文件供心跳读取
使用 IB Gateway API 获取实时期权价格（OPRA 订阅）"""
import ib_insync
import time
import os

TARGET_PRICE = 2.45
FLAG_FILE = "/tmp/intc_alert_flag.txt"
LOG_FILE = "/tmp/intc_alert.log"

def is_market_hours():
    """美股夏令时（北京时间 21:30 - 次日 04:00）"""
    now = time.localtime()
    hour = now.tm_hour
    wday = now.tm_wday  # 0=周一
    if wday < 5:
        if hour >= 21 or hour < 4:
            return True
    return False

def get_option_price():
    """通过 IB Gateway 获取期权实时报价"""
    ib = ib_insync.IB()
    ib.connect('127.0.0.1', 4003, clientId=10, timeout=15)

    contract = ib_insync.Option(
        symbol='INTC',
        lastTradeDateOrContractMonth='20260618',
        strike=60.0,
        right='C',
        multiplier='100',
        exchange='CBOE',
        currency='USD'
    )

    qualified = ib.qualifyContracts(contract)
    if not qualified:
        raise Exception("合约确认失败")

    ticker = ib.reqMktData(qualified[0], snapshot=True)
    ib.sleep(1.5)  # 等待实时数据返回

    bid = ticker.bid
    ask = ticker.ask
    last = ticker.last

    ib.disconnect()

    # 优先用 last，其次 bid/ask 均值
    if last and last > 0:
        return last
    elif bid and ask and bid > 0 and ask > 0:
        return (bid + ask) / 2
    else:
        raise Exception(f"无法获取有效报价 (last={last}, bid={bid}, ask={ask})")

def main():
    with open(LOG_FILE, 'a') as f:
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        if not is_market_hours():
            msg = f"[{ts}] 非交易时段，跳过"
            f.write(msg + '\n')
            print(msg)
            return

        try:
            price = get_option_price()
            msg = f"[{ts}] INTC 20260618 $60 Call 现价: ${price:.2f} | 目标: ${TARGET_PRICE}"
            f.write(msg + '\n')
            print(msg)

            if abs(price - TARGET_PRICE) <= 0.03:
                with open(FLAG_FILE, 'w') as flag:
                    flag.write(f"TRIGGERED|{ts}|${price:.2f}\n")
                f.write(f"[{ts}] ✅ 触发提醒已写入 FLAG FILE\n")
                print(f"[{ts}] ✅ 价格触及目标！")

        except Exception as e:
            err = f"[{ts}] 错误: {e}\n"
            f.write(err)
            print(err)

if __name__ == '__main__':
    main()
