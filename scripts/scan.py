#!/usr/bin/env python3
"""
Yannick YTM 全站庫存掃描器（純 Python）

流程：
1. GET 官方頁面 service2，從內嵌的 `Machines` JSON 取得最新站點清單（即時 master data）
   - 取得失敗時自動退回讀內建 stations.tsv 快照
2. 用 concurrent.futures.ThreadPoolExecutor 並行 POST 官方 API 抓各站庫存
3. 聚合並把 Markdown 報告印到 stdout

依賴：
    Python ≥ 3.8 — 僅使用標準函式庫 (urllib / json / csv / re / concurrent.futures)。
    不需 pip install。不需 curl 或其他工具。

用法：
    python3 scan.py

可選環境變數：
    CONCURRENCY              同時併發站數，預設 6
    YANNICK_USE_LOCAL_STATIONS  =1 時跳過動態取得，直接讀 stations.tsv
    YANNICK_OFFLINE_CACHE    指向 mock JSON 目錄；設定後跳過 HTTP，直接從目錄讀
                             (本機沒網路時的測試 / 開發用；同時也會跳過動態站點取得)

免責聲明：
    本工具僅供個人便利查詢使用，所有資料產權皆屬原網站所有。
    請勿用於商業用途或高頻率惡意查詢，以免造成對方伺服器負擔。
"""

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

API_URL = "https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx"
STATIONS_PAGE_URL = "https://www.yannick.com.tw/ytm/service2"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIONS_TSV = os.path.join(SCRIPT_DIR, "stations.tsv")
CONCURRENCY = int(os.environ.get("CONCURRENCY", "6"))
TIMEOUT_SEC = 15
RETRY_COUNT = 2
OFFLINE_CACHE = os.environ.get("YANNICK_OFFLINE_CACHE")
USE_LOCAL_STATIONS = os.environ.get("YANNICK_USE_LOCAL_STATIONS")
MACHINES_RE = re.compile(r"(?:var|let|const)\s+Machines\s*=\s*(\[.*?\]);", re.S)


def fetch_station(tid: str):
    """抓取單一站點。回 (tid, data_dict_or_None, error_str_or_None)。"""
    # Offline / mock 模式：從本機目錄讀
    if OFFLINE_CACHE:
        json_path = os.path.join(OFFLINE_CACHE, f"{tid}.json")
        status_path = os.path.join(OFFLINE_CACHE, f"{tid}.status")
        if os.path.exists(status_path):
            with open(status_path, encoding="utf-8") as f:
                status = f.read().strip()
            if not status.startswith("OK"):
                return tid, None, f"mock 狀態：{status}"
        if not os.path.exists(json_path):
            return tid, None, "mock JSON 不存在"
        try:
            with open(json_path, encoding="utf-8") as f:
                return tid, json.load(f), None
        except Exception as exc:
            return tid, None, f"mock JSON 解析失敗：{exc}"

    # 線上模式：POST 官方 API + 重試
    body = urllib.parse.urlencode({"TID": tid}).encode("utf-8")
    last_err = None
    for attempt in range(RETRY_COUNT + 1):
        try:
            req = urllib.request.Request(
                API_URL,
                data=body,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "yannick-ytm-stats-skill/1.0 (python urllib)",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                raw = resp.read().decode("utf-8")
                return tid, json.loads(raw), None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code} {e.reason}"
        except urllib.error.URLError as e:
            last_err = f"網路錯誤：{e.reason}"
        except json.JSONDecodeError as e:
            last_err = f"JSON 解析失敗：{e}"
        except Exception as e:  # noqa: BLE001
            last_err = f"未預期錯誤：{e}"
            break
        if attempt < RETRY_COUNT:
            time.sleep(0.5 * (attempt + 1))  # 指數退避 0.5s / 1.0s
    return tid, None, last_err


def fetch_stations_live():
    """GET 官方 service2 頁面，從內嵌 JS 的 `Machines` 變數取出最新站點清單。

    回 list of dict，欄位與 load_stations() 對齊：
        tid / branch_code / branch_name / line / station_name
    取得失敗會 raise 例外，由呼叫端決定是否退回 TSV。
    """
    req = urllib.request.Request(
        STATIONS_PAGE_URL,
        headers={
            "User-Agent": "yannick-ytm-stats-skill/1.0 (python urllib)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    m = MACHINES_RE.search(html)
    if not m:
        raise RuntimeError("頁面結構變更，找不到 Machines 變數")
    try:
        machines = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Machines JSON 解析失敗：{e}")

    if not isinstance(machines, list) or not machines:
        raise RuntimeError(f"Machines 不是非空陣列（type={type(machines).__name__}）")

    stations = []
    for it in machines:
        tname = (it.get("TName") or "").strip()
        # TName 格式為「路線-站名」（捷運站）或純店名（門市據點，無 dash）
        if "-" in tname:
            line, station_name = tname.split("-", 1)
        else:
            line, station_name = "門市", tname
        stations.append(
            {
                "tid": (it.get("TID") or "").strip(),
                "branch_code": (it.get("RID") or "").strip(),
                "branch_name": (it.get("RName") or "").strip(),
                "line": line.strip(),
                "station_name": station_name.strip(),
            }
        )
    return stations


def load_stations(path: str):
    """從本機 TSV 快照讀站點清單（fallback 用）。"""
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)
    return rows


def get_stations():
    """取得站點清單。優先動態抓官方頁面；失敗或被環境變數關閉時退回 TSV。

    回 (stations, source_label) — source_label 用來印給使用者看是哪個來源。
    """
    if OFFLINE_CACHE:
        stations = load_stations(STATIONS_TSV)
        return stations, f"本機 TSV 快照 (offline mode, {len(stations)} 站)"

    if USE_LOCAL_STATIONS:
        stations = load_stations(STATIONS_TSV)
        return stations, f"本機 TSV 快照 (YANNICK_USE_LOCAL_STATIONS=1, {len(stations)} 站)"

    try:
        stations = fetch_stations_live()
        return stations, f"官方頁面即時取得 ({len(stations)} 站)"
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  動態取得站點失敗：{e}", file=sys.stderr)
        print("   退回使用內建 stations.tsv 快照…", file=sys.stderr)
        stations = load_stations(STATIONS_TSV)
        return stations, f"本機 TSV 快照 (fallback, {len(stations)} 站)"


def scan_all(stations):
    """並行抓取所有站點，回 {tid: (data, error)}."""
    results = {}
    if OFFLINE_CACHE:
        # mock 模式不需要 thread pool；快得很
        for s in stations:
            tid, data, err = fetch_station(s["tid"])
            results[tid] = (data, err)
        return results

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(fetch_station, s["tid"]) for s in stations]
        for fut in as_completed(futures):
            tid, data, err = fut.result()
            results[tid] = (data, err)
    return results


def build_report(stations, fetch_results, elapsed_sec, station_source=""):
    """整理 + 聚合 + 產出 Markdown 字串。"""
    station_results = []
    for s in stations:
        data, err = fetch_results.get(s["tid"], (None, "未抓取"))
        stocks = []
        if not err and data is not None:
            api_status = (data.get("Status") or {}).get("code", "")
            if api_status != "00":
                info = (data.get("Status") or {}).get("info", "")
                err = f"API 回 code={api_status} {info}".strip()
            else:
                stocks = (data.get("Result") or {}).get("StockList") or []
        station_results.append({"station": s, "stocks": stocks, "error": err})

    products = defaultdict(
        lambda: {"commodity_name": "", "price": 0, "total_qty": 0, "stations": []}
    )
    total_qty = 0
    with_stock = 0
    err_count = 0
    for r in station_results:
        if r["error"]:
            err_count += 1
        if r["stocks"]:
            with_stock += 1
        for it in r["stocks"]:
            code = (
                it.get("commodityCode")
                or it.get("SaleID")
                or it.get("ProductName")
                or "?"
            )
            qty = int(it.get("quantity") or 0)
            total_qty += qty
            p = products[code]
            p["commodity_name"] = (
                it.get("commodityName") or it.get("ProductName") or "-"
            )
            p["price"] = int(it.get("Price") or 0)
            p["total_qty"] += qty
            p["stations"].append(
                {
                    "full_name": f"{r['station']['line']}-{r['station']['station_name']}",
                    "branch_name": r["station"]["branch_name"],
                    "qty": qty,
                }
            )

    products_sorted = sorted(
        [{"code": c, **v} for c, v in products.items()],
        key=lambda p: (-p["total_qty"], p["commodity_name"]),
    )

    branch_stats = defaultdict(
        lambda: {"total": 0, "with_stock": 0, "items": 0, "err": 0}
    )
    for r in station_results:
        b = r["station"]["branch_name"]
        branch_stats[b]["total"] += 1
        if r["stocks"]:
            branch_stats[b]["with_stock"] += 1
        if r["error"]:
            branch_stats[b]["err"] += 1
        branch_stats[b]["items"] += sum(int(it.get("quantity") or 0) for it in r["stocks"])

    tz = timezone(timedelta(hours=8))
    now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    out = []
    out.append("# 亞尼克 YTM 全站庫存統計")
    out.append("")
    out.append(f"- **掃描時間：** {now_str} (台北時區)")
    out.append(f"- **耗時：** {elapsed_sec} 秒")
    out.append(f"- **資料來源：** {API_URL} (官方 API)")
    if station_source:
        out.append(f"- **站點清單：** {station_source}")
    out.append("")

    out.append("## 📊 整體摘要")
    out.append("")
    out.append("| 指標 | 數值 |")
    out.append("| --- | --- |")
    out.append(f"| 查詢站點 | {len(station_results)} |")
    out.append(f"| 有庫存站點 | {with_stock} |")
    out.append(f"| 商品種類 | {len(products_sorted)} |")
    out.append(f"| 總庫存量 | {total_qty} 個 |")
    if err_count:
        out.append(f"| ⚠️ 失敗站點 | {err_count} |")
    out.append("")

    out.append("## 🗺️ 各據點分類")
    out.append("")
    out.append("| 分類 | 站數 | 有庫存 | 總庫存 | 失敗 |")
    out.append("| --- | ---: | ---: | ---: | ---: |")
    for b in ["台北捷運據點", "高雄捷運據點", "門市據點"]:
        if b in branch_stats:
            s = branch_stats[b]
            out.append(
                f"| {b} | {s['total']} | {s['with_stock']} | {s['items']} | {s['err']} |"
            )
    out.append("")

    out.append("## 🍰 商品庫存排行")
    out.append("")
    if products_sorted:
        out.append("| 排名 | 商品 | 單價 | 總庫存 | 出現站數 |")
        out.append("| ---: | --- | ---: | ---: | ---: |")
        for i, p in enumerate(products_sorted, 1):
            out.append(
                f"| {i} | {p['commodity_name']} (`{p['code']}`) | "
                f"NT$ {p['price']} | **{p['total_qty']}** 個 | {len(p['stations'])} 站 |"
            )
        out.append("")

        out.append("## 📍 各商品出現的站點")
        out.append("")
        for p in products_sorted:
            out.append(
                f"### {p['commodity_name']} — 共 {p['total_qty']} 個 / "
                f"{len(p['stations'])} 站"
            )
            out.append("")
            stns = sorted(p["stations"], key=lambda s: (-s["qty"], s["full_name"]))
            out.append("| 站點 | 分類 | 數量 |")
            out.append("| --- | --- | ---: |")
            for s in stns:
                out.append(f"| {s['full_name']} | {s['branch_name']} | {s['qty']} |")
            out.append("")
    else:
        out.append("_目前所有站點都沒有商品上架。_")
        out.append("")

    if err_count:
        out.append("## ⚠️ 查詢失敗站點")
        out.append("")
        out.append("| 站點 | 分類 | 錯誤訊息 |")
        out.append("| --- | --- | --- |")
        for r in station_results:
            if r["error"]:
                s = r["station"]
                out.append(
                    f"| {s['line']}-{s['station_name']} | {s['branch_name']} | "
                    f"{r['error']} |"
                )
        out.append("")

    return "\n".join(out)


def main():
    print("🍰 Yannick YTM 全站庫存掃描", file=sys.stderr)
    print(f"   開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
    print("🔎 取得站點清單…", file=sys.stderr)

    try:
        stations, station_source = get_stations()
    except FileNotFoundError:
        print(f"ERROR: 動態取得失敗且 stations.tsv 不存在於 {STATIONS_TSV}", file=sys.stderr)
        return 1

    if not stations:
        print("ERROR: 取得到的站點清單是空的", file=sys.stderr)
        return 1

    print(f"   站點來源：{station_source}", file=sys.stderr)
    print(f"   API：{API_URL}", file=sys.stderr)
    if OFFLINE_CACHE:
        print(f"   🔌 OFFLINE MODE：{OFFLINE_CACHE}", file=sys.stderr)
    else:
        print(f"   併發：{CONCURRENCY}", file=sys.stderr)
    print("", file=sys.stderr)

    start = time.time()
    fetch_results = scan_all(stations)
    elapsed = int(time.time() - start)

    print(f"✅ 抓取完成，耗時 {elapsed} 秒。聚合中…", file=sys.stderr)
    print("", file=sys.stderr)

    report = build_report(stations, fetch_results, elapsed, station_source)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
