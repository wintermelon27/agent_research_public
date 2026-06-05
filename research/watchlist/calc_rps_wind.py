#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股 RPS 排名 - 方案 D
- 标的: Hermes 自选股 A 股
- 基准: 6 大宽基指数
- 算法: 个股 vs 指数的相对收益百分位
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

WATCHLIST_PATH = Path("/root/.hermes/data/wintermelon_watchlist.json")
OUTPUT_DIR = Path("/root/.openclaw/workspace/research/watchlist")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 6 大宽基指数
BENCHMARKS = [
    {"name": "沪深300", "windcode": "000300.SH"},
    {"name": "中证500", "windcode": "000905.SH"},
    {"name": "中证1000", "windcode": "000852.SH"},
    {"name": "科创50", "windcode": "000688.SH"},
    {"name": "创业板指", "windcode": "399006.SZ"},
    {"name": "红利低波", "windcode": "H30269.SH"},
]

PERIODS = [50, 120, 250]
HIST_DAYS = 450
RPS_THRESHOLD = 80

WIND_SKILL_DIR = "/root/.agents/skills/wind-mcp-skill"


def call_wind(server_type, tool, params, max_retry=3):
    """调用 Wind MCP"""
    cmd = [
        "node", f"{WIND_SKILL_DIR}/scripts/cli.mjs", "call",
        server_type, tool, json.dumps(params),
    ]
    for attempt in range(max_retry):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                err = result.stdout[:200]
                print(f"  ⚠️ {server_type}/{tool} {params.get('windcode','')} 失败: {err}")
                time.sleep(2)
                continue
            data = json.loads(result.stdout)
            # 实际响应: {"content": [{"type": "text", "text": "..."}], "isError": false}
            text = data["content"][0]["text"]
            inner = json.loads(text)
            if inner.get("error"):
                print(f"  ⚠️ {server_type}/{tool} 错误: {inner['error']}")
                return None
            return inner.get("data", {})
        except Exception as e:
            print(f"  ⚠️ {server_type}/{tool} 异常 {attempt+1}: {e}")
            time.sleep(2)
    return None


def call_stock_kline(windcode, begin, end):
    return call_wind("stock_data", "get_stock_kline", {
        "windcode": windcode, "begin_date": begin, "end_date": end, "count": -HIST_DAYS
    })


def call_index_kline(windcode, begin, end):
    return call_wind("index_data", "get_index_kline", {
        "windcode": windcode, "begin_date": begin, "end_date": end, "count": -HIST_DAYS
    })


def calc_pct_change(rows, period, close_col="MATCH"):
    """从 rows 计算 period 日涨幅 (%)"""
    if not rows or len(rows) < period + 1:
        return None
    # rows 是 list of list, 需要先找列名对应的索引
    # 通过 columns 解析
    if isinstance(rows[-1], list):
        # list of list 模式, 不知道列名. 默认 MATCH 是第 2 列 (idx=2)
        # TIME=0, OPEN=1, MATCH=2, HIGH=3, LOW=4
        close_idx = 2
    else:
        # list of dict
        return None
    latest = float(rows[-1][close_idx])
    past = float(rows[-period - 1][close_idx])
    if past == 0:
        return None
    return (latest - past) / past * 100


def load_watchlist():
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_a_shares(watchlist):
    a_list = []
    for item in watchlist:
        market = item.get("market", "")
        code = item.get("code", "")
        if market in ("sh", "sz"):
            a_list.append(item)
        elif market == "index" and code.startswith(("000", "600", "932", "399")):
            a_list.append(item)
    return a_list


def to_windcode(code, market):
    if market == "sh":
        return f"{code}.SH"
    elif market == "sz":
        return f"{code}.SZ"
    elif market == "index":
        if code.startswith(("000", "600")):
            return f"{code}.SH"
        elif code.startswith(("399", "932", "300")):
            return f"{code}.SZ"
    return None


def main():
    print("=" * 60)
    print(f"📊 A 股 RPS 排名（万得数据）- {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    watchlist = load_watchlist()
    a_list = filter_a_shares(watchlist)
    print(f"✅ A 股自选股: {len(a_list)} 只")

    end_date = datetime.now()
    end_str = end_date.strftime("%Y%m%d")
    begin_str = (end_date - timedelta(days=int(HIST_DAYS * 1.5))).strftime("%Y%m%d")

    # 1. 拉 6 大基准指数
    print(f"\n📡 拉取 6 大基准指数 K 线 ({begin_str} ~ {end_str})...")
    benchmark_pct = {}
    for b in BENCHMARKS:
        data = call_index_kline(b["windcode"], begin_str, end_str)
        if not data or not data.get("rows"):
            print(f"  ❌ {b['name']} 拉取失败")
            continue
        pcts = {}
        for p in PERIODS:
            pct = calc_pct_change(data["rows"], p)
            pcts[p] = pct
        benchmark_pct[b["name"]] = pcts
        p50 = pcts.get(50)
        p120 = pcts.get(120)
        p250 = pcts.get(250)
        print(f"  ✅ {b['name']}: 50d={p50:+.2f}%  120d={p120:+.2f}%  250d={p250:+.2f}%" if all(v is not None for v in [p50,p120,p250]) else f"  ⚠️ {b['name']} 部分缺失")

    time.sleep(1)

    # 2. 拉自选股
    print(f"\n📡 拉取自选股 K 线 ({len(a_list)} 只)...")
    watch_pct = {}
    watch_meta = {}
    success = 0
    fail = 0
    t0 = time.time()

    for i, item in enumerate(a_list, 1):
        code = item["code"]
        name = item.get("name", "")
        market = item.get("market", "")
        windcode = to_windcode(code, market)
        if not windcode:
            fail += 1
            continue

        data = call_stock_kline(windcode, begin_str, end_str)
        if not data or not data.get("rows") or len(data["rows"]) < max(PERIODS) + 1:
            fail += 1
            if i % 20 == 0:
                elapsed = time.time() - t0
                speed = max(i / elapsed, 0.1)
                eta = (len(a_list) - i) / speed
                print(f"  进度: {i}/{len(a_list)} | 成功 {success} | 失败 {fail} | ETA {eta/60:.1f}min")
            time.sleep(0.3)
            continue

        watch_pct[windcode] = {}
        for p in PERIODS:
            pct = calc_pct_change(data["rows"], p)
            if pct is not None:
                watch_pct[windcode][p] = pct
        watch_meta[windcode] = {"code": code, "name": name, "market": market}
        success += 1

        if i % 10 == 0 or i == len(a_list):
            elapsed = time.time() - t0
            speed = i / elapsed
            eta = (len(a_list) - i) / speed
            print(f"  进度: {i}/{len(a_list)} ({i*100//len(a_list)}%) | 成功 {success} | 失败 {fail} | 速度 {speed:.1f}/s | ETA {eta/60:.1f}min")

        time.sleep(0.3)

    print(f"\n✅ 拉取完成: 成功 {success}, 失败 {fail}, 耗时 {(time.time()-t0)/60:.1f}min")

    # 3. 计算 RPS
    print("\n📐 计算 RPS 百分位（vs 6 大指数）...")
    rps_results = []
    for windcode, pcts in watch_pct.items():
        meta = watch_meta[windcode]
        rps_data = {"code": meta["code"], "name": meta["name"], "market": meta["market"]}
        for p in PERIODS:
            stock_pct = pcts.get(p)
            bench_pcts = [benchmark_pct[b["name"]][p] for b in BENCHMARKS
                          if benchmark_pct.get(b["name"], {}).get(p) is not None]
            if stock_pct is None or not bench_pcts:
                rps_data[f"rps{p}"] = None
                rps_data[f"chg{p}"] = None
                continue
            all_pcts = [stock_pct] + bench_pcts
            sorted_pcts = sorted(all_pcts, reverse=True)
            rank = sorted_pcts.index(stock_pct) + 1
            rps = (1 - (rank - 1) / len(sorted_pcts)) * 100
            rps_data[f"rps{p}"] = rps
            rps_data[f"chg{p}"] = stock_pct
        rps_results.append(rps_data)

    rps_results.sort(key=lambda x: x.get("rps250") or -1, reverse=True)

    # 4. 缓存
    raw_path = OUTPUT_DIR / "rps_wind_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "benchmarks": benchmark_pct,
            "watchlist": rps_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 原始数据: {raw_path}")

    # 5. 生成报告
    md_path = OUTPUT_DIR / f"RPS_自选股A股_{datetime.now().strftime('%Y%m%d')}_wind.md"
    generate_report(md_path, rps_results, benchmark_pct, end_date)
    print(f"📄 报告: {md_path}")


def generate_report(md_path, results, bench_pct, end_date):
    today = end_date.strftime("%Y-%m-%d")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 📊 A 股自选股 RPS 排名 · {today}\n\n")
        f.write(f"> **生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"> **数据源：** 万得 Wind 金融数据服务  \n")
        f.write(f"> **基准池：** 6 大宽基指数（沪深300/中证500/中证1000/科创50/创业板指/红利低波）  \n")
        f.write(f"> **RPS 周期：** 50 / 120 / 250 日  \n")
        f.write(f"> **RPS 算法：** 个股 vs 6 大指数相对涨幅百分位（Rank 1-7）  \n")
        f.write(f"> **样本数：** {len(results)} 只  \n\n")

        f.write("---\n\n")
        f.write("## 📐 RPS 概念速览\n\n")
        f.write("- **RPS** = Relative Price Strength（相对价格强度）\n")
        f.write("- **RPS-N = 100** 表示该股过去 N 天涨幅**跑赢所有 6 大宽基指数**\n")
        f.write("- **RPS-N = 50** 表示与指数中位数持平\n")
        f.write("- **RPS-N = 0** 表示弱于所有 6 大指数\n")
        f.write("- **三线共振**（RPS-50/120/250 均 ≥ 80）= 长期趋势最强信号\n\n")

        f.write("---\n\n")
        f.write("## 🏛️ 6 大基准指数涨幅\n\n")
        f.write("| 指数 | 50 日 | 120 日 | 250 日 |\n")
        f.write("|---|---:|---:|---:|\n")
        for b in BENCHMARKS:
            name = b["name"]
            r50 = bench_pct.get(name, {}).get(50)
            r120 = bench_pct.get(name, {}).get(120)
            r250 = bench_pct.get(name, {}).get(250)
            f.write(f"| {name} | {r50:+.2f}% | {r120:+.2f}% | {r250:+.2f}% |\n"
                    if all(v is not None for v in [r50, r120, r250])
                    else f"| {name} | {'-' if r50 is None else f'{r50:+.2f}%'} | {'-' if r120 is None else f'{r120:+.2f}%'} | {'-' if r250 is None else f'{r250:+.2f}%'} |\n")
        f.write("\n")

        # 三线共振
        strong = [r for r in results if r.get("rps50", 0) >= RPS_THRESHOLD
                  and r.get("rps120", 0) >= RPS_THRESHOLD
                  and r.get("rps250", 0) >= RPS_THRESHOLD]
        f.write("---\n\n")
        f.write(f"## 🏆 三线共振（RPS-50/120/250 均 ≥ 80）：{len(strong)} 只\n\n")
        if not strong:
            f.write("> ⚠️ 当前无三线共振标的\n\n")
        else:
            f.write("| 代码 | 名称 | 市场 | RPS-50 | RPS-120 | RPS-250 |\n")
            f.write("|---|---|---|---:|---:|---:|\n")
            for r in strong:
                f.write(f"| {r['code']} | {r['name']} | {r['market']} | {r['rps50']:.1f} | {r['rps120']:.1f} | {r['rps250']:.1f} |\n")
            f.write("\n")

        # 完整排名
        f.write("---\n\n")
        f.write("## 📋 完整 RPS 排名（按 RPS-250 降序）\n\n")
        f.write("| 排名 | 代码 | 名称 | 市场 | 50日涨幅 | RPS-50 | 120日涨幅 | RPS-120 | 250日涨幅 | RPS-250 |\n")
        f.write("|---:|---|---|---|---:|---:|---:|---:|---:|---:|\n")
        for i, r in enumerate(results, 1):
            r50 = f"{r['rps50']:.1f}" if r.get('rps50') is not None else "-"
            r120 = f"{r['rps120']:.1f}" if r.get('rps120') is not None else "-"
            r250 = f"{r['rps250']:.1f}" if r.get('rps250') is not None else "-"
            c50 = f"{r['chg50']:+.1f}%" if r.get('chg50') is not None else "-"
            c120 = f"{r['chg120']:+.1f}%" if r.get('chg120') is not None else "-"
            c250 = f"{r['chg250']:+.1f}%" if r.get('chg250') is not None else "-"
            f.write(f"| {i} | {r['code']} | {r['name']} | {r['market']} | {c50} | {r50} | {c120} | {r120} | {c250} | {r250} |\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("## 🔧 工具与数据源\n\n")
        f.write("- **数据：** 万得 Wind 金融数据服务（@wind-mcp-skill）\n")
        f.write("- **基准池：** 6 大宽基指数\n")
        f.write("- **计算脚本：** `research/watchlist/calc_rps_wind.py`\n")
        f.write("- **原始数据：** `research/watchlist/rps_wind_raw.json`\n")
        f.write("\n---\n")
        f.write("\n*数据来源于万得 Wind 金融数据服务*\n")
        f.write(f"\n*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")


if __name__ == "__main__":
    main()
