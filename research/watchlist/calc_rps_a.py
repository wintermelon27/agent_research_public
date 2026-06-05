#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股 RPS 排名计算脚本
- 输入: /root/.hermes/data/wintermelon_watchlist.json
- 计算 RPS-50 / RPS-120 / RPS-250
- 基准: A 股全市场 (akshare 实时拉)
- 输出: research/watchlist/RPS_自选股A股_20260605.md
"""
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import akshare as ak
import pandas as pd

WATCHLIST_PATH = Path("/root/.hermes/data/wintermelon_watchlist.json")
OUTPUT_DIR = Path("/root/.openclaw/workspace/research/watchlist")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 周期
PERIODS = [50, 120, 250]
# 至少需要的历史天数（多取 30 天缓冲）
HIST_DAYS = max(PERIODS) + 30
# RPS 阈值
RPS_THRESHOLD = 80


def load_watchlist():
    """加载自选股"""
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_a_shares(watchlist):
    """筛选 A 股 + A 股指数"""
    a_list = []
    for item in watchlist:
        market = item.get("market", "")
        # A 股: sh, sz, index (指数限定: 000xxx / 600xxx / 300xxx / 932xxx)
        if market in ("sh", "sz"):
            a_list.append(item)
        elif market == "index":
            # A 股指数限定: 000xxx (上证系列/深证系列) / 600xxx (很少,几乎不用) / 932xxx (中证)
            # 排除 H 系列港股指数 (H30184, H30269, HSTECH)
            code = item.get("code", "")
            if code.startswith(("000", "600", "932", "399")):
                a_list.append(item)
    return a_list


def get_a_share_universe():
    """获取 A 股全市场代码列表（用于全市场 RPS 基准）"""
    print("📡 拉取 A 股全市场代码列表...")
    df = ak.stock_info_a_code_name()
    # 返回字段: code, name, ...
    return df["code"].astype(str).str.zfill(6).tolist()


def fetch_kline(code, name, market, end_date, days):
    """拉取单只股票/指数 K 线（前复权）"""
    start_date = (end_date - timedelta(days=days)).strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    try:
        if market == "index":
            # A 股指数用 stock_zh_index_daily
            symbol = f"sh{code}" if code.startswith(("000", "600")) else f"sz{code}"
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is None or df.empty:
                return None
            df = df.rename(columns={"date": "日期", "close": "收盘"})
            df["日期"] = pd.to_datetime(df["日期"])
        else:
            # 个股 - 前复权
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_str,
                adjust="qfq",
            )
            if df is None or df.empty:
                return None
            df["日期"] = pd.to_datetime(df["日期"])

        df = df.sort_values("日期").reset_index(drop=True)
        if len(df) < max(PERIODS):
            return None
        return df
    except Exception as e:
        print(f"  ⚠️ {code} {name}: {e}")
        return None


def calc_rps(df, period):
    """计算单只股票 RPS-N（用 N 日涨幅在全市场分位）"""
    if df is None or len(df) < period:
        return None
    # 收盘价
    close_col = "收盘" if "收盘" in df.columns else "close"
    if close_col not in df.columns:
        return None
    closes = df[close_col].values
    # N 日涨幅 = (最新 / N 天前) - 1
    pct = closes[-1] / closes[-period - 1] - 1
    return pct


def calc_rps_universe(universe_dict, end_date):
    """
    计算全市场 RPS-N 排名百分位
    返回: {code: {period: rps_value}}
    """
    print(f"📊 计算全市场 RPS 基准（共 {len(universe_dict)} 只）...")
    # 全市场要拉 ~5000 只, 比较耗时, 用批处理
    results = {}  # {code: {period: pct_change}}
    start_date = (end_date - timedelta(days=HIST_DAYS)).strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    total = len(universe_dict)
    success = 0
    fail = 0
    t0 = time.time()

    for i, (code, name) in enumerate(universe_dict.items(), 1):
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_str,
                adjust="qfq",
            )
            if df is None or df.empty or len(df) < max(PERIODS):
                fail += 1
                continue

            closes = df["收盘"].values
            results[code] = {}
            for p in PERIODS:
                pct = closes[-1] / closes[-p - 1] - 1
                results[code][p] = pct
            success += 1
        except Exception as e:
            fail += 1

        if i % 200 == 0:
            elapsed = time.time() - t0
            speed = i / elapsed
            eta = (total - i) / speed
            print(f"  进度: {i}/{total} ({i*100//total}%) | 成功 {success} | 失败 {fail} | 速度 {speed:.1f}/s | ETA {eta/60:.1f}min")

    print(f"✅ 全市场 RPS 拉取完成: 成功 {success}, 失败 {fail}, 耗时 {(time.time()-t0)/60:.1f}min")
    return results


def to_rps(pct_values):
    """将涨幅列表转为 RPS 百分位"""
    s = pd.Series(pct_values).dropna()
    n = len(s)
    if n == 0:
        return {}
    # 排名: 1 = 涨幅最高
    ranks = s.rank(ascending=False, method="min")
    rps = (1 - (ranks - 1) / n) * 100
    return rps.to_dict()


def main():
    print("=" * 60)
    print(f"📊 A 股 RPS 排名计算 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. 加载自选股
    watchlist = load_watchlist()
    a_list = filter_a_shares(watchlist)
    print(f"✅ A 股 + 指数标的: {len(a_list)} 只")

    # 2. 拉全市场代码
    universe_codes = get_a_share_universe()
    print(f"✅ A 股全市场: {len(universe_codes)} 只")

    # 3. 自选股 code -> name 映射
    watch_map = {item["code"]: item for item in a_list}

    # 4. 拉全市场 K 线, 计算 RPS
    end_date = datetime.now()
    universe_results = calc_rps_universe(
        {c: c for c in universe_codes}, end_date
    )

    # 5. 转 RPS 百分位
    print("📐 计算 RPS 百分位排名...")
    rps_table = {}  # {code: {period: rps}}
    for p in PERIODS:
        pct_dict = {c: v.get(p) for c, v in universe_results.items() if v.get(p) is not None}
        rps_dict = to_rps(pct_dict)
        for c, r in rps_dict.items():
            rps_table.setdefault(c, {})[p] = r

    # 6. 提取自选股 RPS
    watchlist_rps = []
    for code, item in watch_map.items():
        rps = rps_table.get(code, {})
        watchlist_rps.append({
            "code": code,
            "name": item.get("name", ""),
            "market": item.get("market", ""),
            "rps50": rps.get(50),
            "rps120": rps.get(120),
            "rps250": rps.get(250),
        })

    # 7. 保存中间数据
    raw_path = OUTPUT_DIR / "rps_raw_data.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "universe_size": len(universe_codes),
            "watchlist": watchlist_rps,
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 原始数据: {raw_path}")

    # 8. 生成 Markdown 报告
    md_path = OUTPUT_DIR / f"RPS_自选股A股_{datetime.now().strftime('%Y%m%d')}.md"
    generate_report(md_path, watchlist_rps, len(universe_codes), end_date)
    print(f"📄 报告: {md_path}")

    return watchlist_rps


def generate_report(md_path, watchlist_rps, universe_size, end_date):
    """生成 Markdown 报告"""
    df = pd.DataFrame(watchlist_rps)

    # 排序: 按 rps250 降序
    df_sorted = df.sort_values("rps250", ascending=False, na_position="last").reset_index(drop=True)

    # 三线均 >= 80
    df_strong = df[
        (df["rps50"].fillna(0) >= RPS_THRESHOLD)
        & (df["rps120"].fillna(0) >= RPS_THRESHOLD)
        & (df["rps250"].fillna(0) >= RPS_THRESHOLD)
    ].sort_values("rps250", ascending=False)

    # 任一线 >= 80
    df_any_strong = df[
        (df["rps50"].fillna(0) >= RPS_THRESHOLD)
        | (df["rps120"].fillna(0) >= RPS_THRESHOLD)
        | (df["rps250"].fillna(0) >= RPS_THRESHOLD)
    ].sort_values("rps250", ascending=False)

    # 弱势
    df_weak = df.sort_values("rps250", ascending=True, na_position="last").head(10)

    # 写入报告
    today = end_date.strftime("%Y-%m-%d")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 A 股自选股 RPS 排名 · {today}\n\n")
        f.write(f"> **生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **基准池：** A 股全市场 ({universe_size} 只)  \n")
        f.write(f"> **RPS 周期：** 50 / 120 / 250 日  \n")
        f.write(f"> **RPS 阈值：** 80  \n")
        f.write(f"> **数据源：** akshare 1.18.49（前复权）  \n")
        f.write(f"> **样本数：** {len(df)} 只  \n\n")

        f.write("---\n\n")
        f.write("## 📐 RPS 概念速览\n\n")
        f.write("- **RPS** = Relative Price Strength（相对价格强度）\n")
        f.write("- **RPS-N = 90** 表示该股过去 N 天的涨幅**跑赢了 90% 的全市场股票**\n")
        f.write("- **三线共振**（RPS-50/120/250 均 ≥ 80）= 长期趋势最强信号\n")
        f.write("- **仅 250 日 ≥ 80** = 长线牛股\n")
        f.write("- **50/120 高，250 低** = 短期爆发但长期未确立\n\n")

        f.write("---\n\n")
        f.write(f"## 🏆 三线共振（RPS-50/120/250 均 ≥ 80）：{len(df_strong)} 只\n\n")
        if len(df_strong) == 0:
            f.write("> ⚠️ 当前无三线共振标的\n\n")
        else:
            f.write("| 代码 | 名称 | 市场 | RPS-50 | RPS-120 | RPS-250 |\n")
            f.write("|---|---|---|---:|---:|---:|\n")
            for _, row in df_strong.iterrows():
                f.write(
                    f"| {row['code']} | {row['name']} | {row['market']} | "
                    f"{row['rps50']:.1f} | {row['rps120']:.1f} | {row['rps250']:.1f} |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write(f"## 💪 任意一周期 ≥ 80：{len(df_any_strong)} 只\n\n")
        f.write("| 排名 | 代码 | 名称 | 市场 | RPS-50 | RPS-120 | RPS-250 |\n")
        f.write("|---:|---|---|---|---:|---:|---:|\n")
        for i, (_, row) in enumerate(df_any_strong.iterrows(), 1):
            r50 = f"{row['rps50']:.1f}" if pd.notna(row['rps50']) else "-"
            r120 = f"{row['rps120']:.1f}" if pd.notna(row['rps120']) else "-"
            r250 = f"{row['rps250']:.1f}" if pd.notna(row['rps250']) else "-"
            f.write(
                f"| {i} | {row['code']} | {row['name']} | {row['market']} | "
                f"{r50} | {r120} | {r250} |\n"
            )
        f.write("\n")

        f.write("---\n\n")
        f.write("## 📉 RPS 排名后 10（弱势标的）\n\n")
        f.write("| 排名 | 代码 | 名称 | 市场 | RPS-50 | RPS-120 | RPS-250 |\n")
        f.write("|---:|---|---|---|---:|---:|---:|\n")
        for i, (_, row) in enumerate(df_weak.iterrows(), 1):
            r50 = f"{row['rps50']:.1f}" if pd.notna(row['rps50']) else "-"
            r120 = f"{row['rps120']:.1f}" if pd.notna(row['rps120']) else "-"
            r250 = f"{row['rps250']:.1f}" if pd.notna(row['rps250']) else "-"
            f.write(
                f"| {i} | {row['code']} | {row['name']} | {row['market']} | "
                f"{r50} | {r120} | {r250} |\n"
            )
        f.write("\n")

        # 完整排名
        f.write("---\n\n")
        f.write("## 📋 完整 RPS 排名（按 RPS-250 降序）\n\n")
        f.write("| 排名 | 代码 | 名称 | 市场 | RPS-50 | RPS-120 | RPS-250 |\n")
        f.write("|---:|---|---|---|---:|---:|---:|\n")
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            r50 = f"{row['rps50']:.1f}" if pd.notna(row['rps50']) else "-"
            r120 = f"{row['rps120']:.1f}" if pd.notna(row['rps120']) else "-"
            r250 = f"{row['rps250']:.1f}" if pd.notna(row['rps250']) else "-"
            f.write(
                f"| {i} | {row['code']} | {row['name']} | {row['market']} | "
                f"{r50} | {r120} | {r250} |\n"
            )
        f.write("\n")

        f.write("---\n\n")
        f.write("## 🔧 工具与数据源\n\n")
        f.write("- **数据：** akshare 1.18.49（前复权日 K）\n")
        f.write("- **基准池：** A 股全市场\n")
        f.write("- **计算脚本：** `research/watchlist/calc_rps_a.py`\n")
        f.write("- **原始数据：** `research/watchlist/rps_raw_data.json`\n")
        f.write(f"\n---\n\n*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")


if __name__ == "__main__":
    main()
