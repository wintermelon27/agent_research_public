#!/usr/bin/env python3
"""
股票异动监控脚本 v2
监控标的：赣锋锂业(A股)、泡泡玛特(港股)

异动条件：
  - 赣锋锂业：当日跌幅超3%
  - 泡泡玛特：价格跌破120港币

说明：
  - 使用日线数据（收盘价），适合非交易时段或收盘后巡检
  - 有异动时完整输出警报，常规状态输出简洁一行
"""

import akshare as ak
import json
import os
import sys
import time
from datetime import datetime, date

# ========== 配置区 ==========
WATCH_LIST = {
    "赣锋锂业": {
        "code": "002460",
        "market": "A股",
        "alert_drop_pct": 3.0,      # 跌幅超此值则警报
    },
    "泡泡玛特": {
        "code": "09992",
        "market": "港股",
        "alert_price_hkd": 120.0,   # 跌破此价格则警报
    },
}
STATE_FILE = "/root/.openclaw/workspace/stock_monitor_state.json"
# ============================


def get_ah_price(code: str, retries: int = 3) -> dict:
    """获取A股（沪深）单股最新日线数据，带重试"""
    prefix = "sh" if code.startswith("6") else "sz"
    symbol = prefix + code
    for attempt in range(retries):
        try:
            df = ak.stock_zh_a_daily(symbol=symbol, adjust="qfq")
            if df is None or df.empty:
                return None
            # 取最后2行，计算涨跌幅
            row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) >= 2 else None
            prev_close = float(prev_row["close"]) if prev_row is not None else None
            chg_pct = None
            if prev_close and prev_close != 0:
                chg_pct = (float(row["close"]) - prev_close) / prev_close * 100
            return {
                "code": code,
                "date": str(row["date"]),
                "close": float(row["close"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "chg_pct": chg_pct,
                "prev_close": prev_close,
                "amount": float(row.get("amount", 0)),
            }
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise e


def get_hk_price(code: str) -> dict:
    """获取港股单股最新日线数据"""
    df = ak.stock_hk_daily(symbol=code, adjust="qfq")
    if df is None or df.empty:
        return None
    row = df.iloc[-1]
    # 前一行算昨日
    prev_row = df.iloc[-2] if len(df) >= 2 else None
    prev_close = float(prev_row["close"]) if prev_row is not None else None
    chg_pct = None
    if prev_close:
        chg_pct = (float(row["close"]) - prev_close) / prev_close * 100
    return {
        "code": code,
        "date": str(row["date"]),
        "close": float(row["close"]),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "chg_pct": chg_pct,
        "prev_close": prev_close,
    }


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_alerts():
    """主检查逻辑"""
    results = []
    state = load_state()
    new_state = {}

    # ── 赣锋锂业 A股 ──
    try:
        data = get_ah_price("002460")
        if data:
            new_state["赣锋锂业"] = {
                "date": data["date"],
                "close": data["close"],
                "chg_pct": data["chg_pct"],
            }
            alert = data["chg_pct"] <= -WATCH_LIST["赣锋锂业"]["alert_drop_pct"]
            results.append({
                "name": "赣锋锂业",
                "market": "A股",
                "data": data,
                "alert": alert,
            })
    except Exception as e:
        results.append({"name": "赣锋锂业", "error": str(e)})

    # ── 泡泡玛特 港股 ──
    try:
        data = get_hk_price("09992")
        if data:
            new_state["泡泡玛特"] = {
                "date": data["date"],
                "close": data["close"],
                "chg_pct": data["chg_pct"],
            }
            alert = data["close"] <= WATCH_LIST["泡泡玛特"]["alert_price_hkd"]
            results.append({
                "name": "泡泡玛特",
                "market": "港股",
                "data": data,
                "alert": alert,
            })
    except Exception as e:
        results.append({"name": "泡泡玛特", "error": str(e)})

    save_state(new_state)
    return results


def format_output(results):
    """格式化输出：有异动时发完整警报，常规时发一行状态"""
    now = datetime.now().strftime("%m-%d %H:%M")
    alerts = []
    normals = []

    for r in results:
        name = r["name"]
        if r.get("error"):
            normals.append(f"❌ {name} 获取失败: {r['error']}")
            continue

        data = r["data"]
        chg = data.get("chg_pct", 0)
        chg_str = f"{'+' if chg >= 0 else ''}{chg:.2f}%"

        if name == "赣锋锂业":
            close = data["close"]
            threshold = WATCH_LIST["赣锋锂业"]["alert_drop_pct"]
            if data["chg_pct"] <= -threshold:
                alerts.append(
                    f"🚨 [{now}] 【赣锋锂业】跌幅 {chg_str}，现价 ¥{close}，已跌破 {-threshold}% 阈值"
                )
            else:
                normals.append(f"✅ {name} ¥{close} {chg_str}")

        elif name == "泡泡玛特":
            close = data["close"]
            threshold = WATCH_LIST["泡泡玛特"]["alert_price_hkd"]
            if data["close"] <= threshold:
                alerts.append(
                    f"🚨 [{now}] 【泡泡玛特】现价 HK${close}，已跌破 {threshold} HK$ 目标价"
                )
            else:
                normals.append(f"✅ {name} HK${close} {chg_str}")

    # 优先输出警报
    if alerts:
        output = "\n".join(alerts)
        if normals:
            output += "\n" + " | ".join(normals)
    elif normals:
        output = f"[{now}] " + " | ".join(normals)
    else:
        output = f"[{now}] ⚠️ 未能获取到任何行情数据"

    return output


if __name__ == "__main__":
    results = check_alerts()
    output = format_output(results)
    print(output)

    # 输出JSON原始数据（供调试或后续解析）
    print("\n---RAW---")
    print(json.dumps(results, ensure_ascii=False, indent=2))
