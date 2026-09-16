#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股强势股抓取工具 v1.0
基于东方财富免费数据接口，多维度量化评分筛选强势股。
作者：user_7400cfba
版本：1.0.0

数据源：东方财富（国内免费接口，无需 API Key）
依赖：纯 Python 标准库，零 pip 依赖
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
import ssl
from datetime import datetime


# ──────────────────────────────────────────────
# 网络层：强制直连，不走代理
# ──────────────────────────────────────────────

def _build_opener():
    """构建强制直连 opener，绕过代理。"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    handler = urllib.request.HTTPSHandler(context=ctx)
    proxy_handler = urllib.request.ProxyHandler({})
    return urllib.request.build_opener(handler, proxy_handler)


_opener = _build_opener()


def _get_json(url, params=None):
    """GET 请求并解析 JSON，失败返回 None。"""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/",
        })
        resp = _opener.open(req, timeout=15)
        raw = resp.read().decode("utf-8")
        return json.loads(raw)
    except Exception as e:
        print("[WARN] 请求失败: {}".format(e), file=sys.stderr)
        return None


def _safe_float(val, default=0.0):
    """安全转换浮点数。"""
    if val is None or val == "-" or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


EASTMONEY_FIELDS = "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f62,f184"

MARKET_MAP = {
    "sh": "m:1+t:2,m:1+t:23",
    "sz": "m:0+t:6,m:0+t:80",
    "gem": "m:0+t:80",
    "kcb": "m:1+t:23",
    "all": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81",
}


def fetch_stock_list(market="all", no_st=False, no_kcb=False, no_bse=False):
    """从东方财富获取全市场实时行情快照。"""
    fs = MARKET_MAP.get(market, MARKET_MAP["all"])
    if no_kcb and market == "all":
        fs = "m:0+t:6,m:0+t:80,m:1+t:2,m:0+t:81"
    if no_bse and market == "all":
        fs = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
    params = {
        "pn": 1, "pz": 5000, "po": 1, "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2, "invt": 2, "fid": "f3",
        "fs": fs, "fields": EASTMONEY_FIELDS,
    }
    data = _get_json("https://push2.eastmoney.com/api/qt/clist/get", params)
    if not data or "data" not in data or data["data"] is None:
        print("[ERROR] 获取行情数据失败，请检查网络连接（需国内直连）", file=sys.stderr)
        return []
    stocks = []
    for item in data["data"].get("diff", []):
        code = str(item.get("f12", ""))
        name = str(item.get("f14", ""))
        if no_st and ("ST" in name or "st" in name):
            continue
        price = item.get("f2")
        change_pct = item.get("f3")
        if price is None or change_pct is None:
            continue
        if price == "-" or change_pct == "-":
            continue
        stocks.append({
            "code": code, "name": name,
            "price": float(price) if price != 0 else 0,
            "change_pct": float(change_pct) if change_pct != "-" else 0,
            "volume_ratio": _safe_float(item.get("f10")),
            "turnover_rate": _safe_float(item.get("f8")),
            "amplitude": _safe_float(item.get("f7")),
            "volume": _safe_float(item.get("f5")),
            "amount": _safe_float(item.get("f6")),
            "high": _safe_float(item.get("f15")),
            "low": _safe_float(item.get("f16")),
            "open": _safe_float(item.get("f17")),
            "prev_close": _safe_float(item.get("f18")),
            "main_net_inflow": _safe_float(item.get("f62")),
            "main_net_pct": _safe_float(item.get("f184")),
            "pe_ratio": _safe_float(item.get("f9")),
            "market_cap": _safe_float(item.get("f20")),
        })
    return stocks


def fetch_sector_ranking(sector_type="industry"):
    """获取板块排行。"""
    if sector_type == "concept":
        fs = "m:90+t:3"
        title = "概念板块"
    else:
        fs = "m:90+t:2"
        title = "行业板块"
    params = {
        "pn": 1, "pz": 100, "po": 1, "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2, "invt": 2, "fid": "f3",
        "fs": fs, "fields": "f2,f3,f4,f8,f12,f14,f20,f62,f184,f104,f105",
    }
    data = _get_json("https://push2.eastmoney.com/api/qt/clist/get", params)
    if not data or "data" not in data or data["data"] is None:
        print("[ERROR] 获取{}数据失败".format(title), file=sys.stderr)
        return []
    sectors = []
    for item in data["data"].get("diff", []):
        name = str(item.get("f14", ""))
        change_pct = item.get("f3")
        if change_pct is None or change_pct == "-":
            continue
        sectors.append({
            "code": str(item.get("f12", "")),
            "name": name,
            "change_pct": float(change_pct),
            "turnover_rate": _safe_float(item.get("f8")),
            "main_net_inflow": _safe_float(item.get("f62")),
            "main_net_pct": _safe_float(item.get("f184")),
            "up_count": item.get("f104", 0),
            "down_count": item.get("f105", 0),
        })
    return sectors


def _score_momentum(change_pct):
    if change_pct >= 9.5: return 18
    elif change_pct >= 7: return 16
    elif change_pct >= 5: return 13
    elif change_pct >= 3: return 10
    elif change_pct >= 1: return 6
    elif change_pct >= 0: return 3
    else: return max(0, 3 + change_pct)


def _score_volume(volume_ratio):
    if volume_ratio <= 0: return 5
    elif 1.5 <= volume_ratio <= 3.0: return 20
    elif 3.0 < volume_ratio <= 5.0: return 15
    elif 5.0 < volume_ratio <= 8.0: return 10
    elif volume_ratio > 8.0: return 5
    elif 1.0 <= volume_ratio < 1.5: return 12
    else: return 5


def _score_turnover(turnover_pct):
    if turnover_pct <= 0: return 5
    elif 3 <= turnover_pct <= 8: return 20
    elif 8 < turnover_pct <= 15: return 16
    elif 15 < turnover_pct <= 20: return 10
    elif turnover_pct > 20: return 5
    elif 1 <= turnover_pct < 3: return 12
    else: return 5


def _score_technical(change_pct, prev_close, high, low):
    if prev_close <= 0 or high <= 0 or low <= 0: return 10
    intraday_range = high - low
    if intraday_range <= 0: return 10
    close = change_pct / 100 * prev_close + prev_close
    price_pos = max(0, min(1, (close - low) / intraday_range))
    if price_pos >= 0.9: return 20
    elif price_pos >= 0.7: return 16
    elif price_pos >= 0.5: return 12
    elif price_pos >= 0.3: return 8
    else: return 4


def _score_capital_flow(main_net_pct):
    if main_net_pct >= 15: return 20
    elif main_net_pct >= 10: return 17
    elif main_net_pct >= 5: return 14
    elif main_net_pct >= 2: return 10
    elif main_net_pct >= 0: return 6
    elif main_net_pct >= -5: return 3
    else: return 0


def calculate_strength_score(stock):
    s1 = _score_momentum(stock["change_pct"])
    s2 = _score_volume(stock["volume_ratio"])
    s3 = _score_turnover(stock["turnover_rate"])
    s4 = _score_technical(stock["change_pct"], stock["prev_close"], stock["high"], stock["low"])
    s5 = _score_capital_flow(stock["main_net_pct"])
    total = s1 + s2 + s3 + s4 + s5
    stock["score"] = round(total, 1)
    stock["score_detail"] = {"momentum": s1, "volume": s2, "turnover": s3, "technical": s4, "capital": s5}
    return stock


def grade_score(score):
    if score >= 80: return "A(极强)"
    elif score >= 60: return "B(较强)"
    elif score >= 40: return "C(一般)"
    else: return "D(偏弱)"


def format_table(stocks, title="强势股排名"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sep = "=" * 85
    lines = ["", sep, "  {}  |  数据时间: {}".format(title, now), sep,
        "{:>4} | {:<8} | {:<10} | {:>7} | {:>5} | {:>6} | {:>7} | {:>5} | {}".format(
            "排名", "代码", "名称", "涨幅%", "量比", "换手%", "主力净%", "评分", "等级"),
        "{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}".format(
            "-"*4, "-"*8, "-"*10, "-"*7, "-"*5, "-"*6, "-"*7, "-"*5, "-"*8)]
    for i, s in enumerate(stocks, 1):
        grade = grade_score(s["score"])
        lines.append("{:>4} | {:<8} | {:<10} | {:>+7.2f} | {:>5.2f} | {:>6.2f} | {:>+7.2f} | {:>5.1f} | {}".format(
            i, s["code"], s["name"], s["change_pct"], s["volume_ratio"], s["turnover_rate"], s["main_net_pct"], s["score"], grade))
    lines.append(sep)
    lines.append("  免责声明：以上数据仅供参考，不构成投资建议。股市有风险，投资需谨慎。")
    lines.append("")
    return "\n".join(lines)


def format_sector_table(sectors, title="板块强势排名"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sep = "=" * 75
    lines = ["", sep, "  {}  |  {}".format(title, now), sep,
        "{:>4} | {:<12} | {:>7} | {:>6} | {:>4} | {:>4} | {:>7}".format(
            "排名", "板块名称", "涨幅%", "换手%", "上涨", "下跌", "主力净%"),
        "{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}".format("-"*4, "-"*12, "-"*7, "-"*6, "-"*4, "-"*4, "-"*7)]
    for i, s in enumerate(sectors, 1):
        lines.append("{:>4} | {:<12} | {:>+7.2f} | {:>6.2f} | {:>4} | {:>4} | {:>+7.2f}".format(
            i, s["name"], s["change_pct"], s["turnover_rate"], s["up_count"], s["down_count"], s["main_net_pct"]))
    lines.append(sep)
    lines.append("  免责声明：数据仅供参考，不构成投资建议。")
    lines.append("")
    return "\n".join(lines)


def run_screener(args):
    # 板块模式（独立接口）
    if args.sector:
        sector_type = args.sector_type if args.sector_type else "industry"
        title = "概念板块强势排名" if sector_type == "concept" else "行业板块强势排名"
        print("正在获取{}...".format(title), file=sys.stderr)
        sectors = fetch_sector_ranking(sector_type)
        if not sectors:
            print("[ERROR] 板块数据获取失败，请检查网络连接（需国内直连）", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(sectors[:args.top], ensure_ascii=False, indent=2))
        else:
            print(format_sector_table(sectors[:args.top], title))
        return
    # 个股筛选模式
    print("正在获取A股行情数据...", file=sys.stderr)
    stocks = fetch_stock_list(market=args.market, no_st=args.no_st, no_kcb=args.no_kcb, no_bse=args.no_bse)
    if not stocks:
        print("[ERROR] 未获取到数据，请检查网络连接（需国内直连，关闭代理）", file=sys.stderr)
        sys.exit(1)
    print("共获取 {} 只股票数据".format(len(stocks)), file=sys.stderr)
    if args.custom:
        if args.min_change is not None:
            stocks = [s for s in stocks if s["change_pct"] >= args.min_change]
        if args.min_volume_ratio is not None:
            stocks = [s for s in stocks if s["volume_ratio"] >= args.min_volume_ratio]
        if args.min_turnover is not None:
            stocks = [s for s in stocks if s["turnover_rate"] >= args.min_turnover]
        print("自定义筛选后剩余 {} 只".format(len(stocks)), file=sys.stderr)
    for s in stocks:
        calculate_strength_score(s)
    stocks.sort(key=lambda x: x["score"], reverse=True)
    top_stocks = stocks[:args.top]
    if args.json:
        output = [{"code": s["code"], "name": s["name"], "change_pct": s["change_pct"],
            "volume_ratio": s["volume_ratio"], "turnover_rate": s["turnover_rate"],
            "main_net_pct": s["main_net_pct"], "score": s["score"],
            "grade": grade_score(s["score"]), "score_detail": s["score_detail"]} for s in top_stocks]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_table(top_stocks, "A股强势股排名 Top {}".format(args.top)))


def main():
    parser = argparse.ArgumentParser(
        description="A股强势股抓取工具 v1.0 - 多维度量化评分筛选强势股",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n  python strong_stock_screener.py                    # 全市场扫描 Top 30\n  python strong_stock_screener.py --top 50 --json    # Top 50 JSON输出\n  python strong_stock_screener.py --sector           # 行业板块排名\n  python strong_stock_screener.py --custom --min-change 3 --min-volume-ratio 2\n")
    parser.add_argument("--top", type=int, default=30, help="输出数量（默认30）")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--market", default="all", choices=["all", "sh", "sz", "gem", "kcb"],
        help="市场筛选：all=全市场, sh=沪市, sz=深市, gem=创业板, kcb=科创板")
    parser.add_argument("--no-st", action="store_true", help="排除ST股票")
    parser.add_argument("--no-kcb", action="store_true", help="排除科创板")
    parser.add_argument("--no-bse", action="store_true", help="排除北交所")
    parser.add_argument("--sector", action="store_true", help="板块强势排名模式")
    parser.add_argument("--sector-type", default="industry", choices=["industry", "concept"],
        help="板块类型：industry=行业, concept=概念")
    parser.add_argument("--custom", action="store_true", help="自定义筛选模式")
    parser.add_argument("--min-change", type=float, default=None, help="最低涨幅%%")
    parser.add_argument("--min-volume-ratio", type=float, default=None, help="最低量比")
    parser.add_argument("--min-turnover", type=float, default=None, help="最低换手率%%")
    parser.add_argument("--new-high", action="store_true", help="N日新高模式（开发中）")
    parser.add_argument("--days", type=int, default=20, help="新高天数（默认20）")
    args = parser.parse_args()
    if args.new_high:
        print("[INFO] --new-high 功能将在 v1.1 版本实现，当前先按综合评分排序输出", file=sys.stderr)
    run_screener(args)


if __name__ == "__main__":
    main()
