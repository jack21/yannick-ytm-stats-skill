---
name: yannick-ytm-stats-skill
description: 抓取亞尼克 YTM 蛋糕販賣機全部 86 個據點的即時庫存，依商品聚合並產出 Markdown 統計報告（含商品排行、出現站點、價格、總數量）。當使用者提到「亞尼克」、「YTM」、「蛋糕販賣機」、「生乳捲庫存」、「三顆布丁生乳捲」、「BUBU 切片組」、「巴斯克生起司」、「景安站」/「南港站」等任一捷運站想查庫存、想看哪些站還有貨、整理全站存貨清單、做進貨/補貨參考時，務必啟用本 skill — 即使使用者沒有講「庫存」二字，只要話題跟亞尼克 YTM 哪裡有/沒有什麼商品（包含近期熱門的三顆布丁生乳捲）有關，就應該主動跑這個 skill 給出數據。
---

# 亞尼克 YTM 全站庫存統計

## 這個 skill 在做什麼

亞尼克在台北捷運、高雄捷運、各地門市共 86 個據點放了 YTM（蛋糕販賣機）。官方查詢頁
`https://www.yannick.com.tw/ytm/service2` 一次只能看一站。本 skill 一鍵把全部 86 站抓回來、
依商品聚合，產出可讀的 Markdown 統計報告 —— 哪個商品在哪些站有貨、共幾個、單價多少、
哪些站查詢失敗都一目了然。

底層 API 已反向工程過：

- `POST https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx`
- Body: `TID=<站點 ID>` (`application/x-www-form-urlencoded`)
- 回 JSON，含 `Result.StockList[]`

詳細的 API 規格、回傳欄位、踩過的雷區見 [`references/api.md`](references/api.md)。

## 怎麼用（最小流程）

直接執行 `scripts/scan.py`，它會：

1. **GET 官方頁面 `service2`，從內嵌 JS 的 `Machines` 變數取得最新站點清單**（即時 master data，不靠本機快照）
   - 取得失敗會自動退回讀 `scripts/stations.tsv` 快照，不會整個失敗
2. 用 `concurrent.futures.ThreadPoolExecutor` 並行 POST 官方 stock API
3. 聚合並把 Markdown 報告印到 **stdout**

```bash
python3 scripts/scan.py
```

執行時間：**約 25–60 秒**（86 站、併發 6、視網路情況）。輸出包含：

- 📊 整體摘要：站點數、有庫存站、商品種類、總庫存
- 🗺️ 各據點分類（台北/高雄/門市）小計
- 🍰 商品排行表
- 📍 每個商品「出現在哪些站 + 各站剩幾個」
- ⚠️ 查詢失敗站點清單（若有）

直接把 stdout 內容呈現給使用者即可，已是 Markdown 格式。

## 系統需求

腳本只需要：

- **Python 3.8+**（macOS 預設、所有主流 Linux 預設、Windows 從 [python.org](https://python.org) 一鍵安裝）

不用 `pip install` 任何套件；不需要 curl、jq、Node.js、任何雲端服務或 API key。
全部使用 Python 標準函式庫（`urllib`、`json`、`csv`、`concurrent.futures`、`datetime`、`collections`）。

幾乎所有能跑 Claude Code 的電腦都直接能執行。

## 環境變數（可選）

| 變數 | 預設 | 說明 |
|------|------|------|
| `CONCURRENCY` | 6 | 同時併發抓取的站點數。網路差或想更保守可設 3–4；想快可設 10。 |
| `YANNICK_USE_LOCAL_STATIONS` | (空) | 設 `1` 時跳過動態取得，直接讀 `scripts/stations.tsv` 快照。網路差時可加速。 |
| `YANNICK_OFFLINE_CACHE` | (空) | 指向 mock JSON 目錄；設定後跳過所有 HTTP（含站點清單），從目錄讀。給開發/測試用，使用者一般不需要設。 |

```bash
CONCURRENCY=10 python3 scripts/scan.py   # 較快
CONCURRENCY=3  python3 scripts/scan.py   # 較保守
```

## 注意事項

1. **官方 API 強制 POST + form body**。直接 `GET ?TID=xxx` 會回 `Status.code=05` 「TID 欄位是必要項」。腳本已正確處理。
2. **API 無 CORS header**。本 skill 是在本機直接打 API（CLI 環境沒有 CORS 概念），所以**不需任何代理服務**。這跟瀏覽器版前端不同。
3. **站點清單預設會即時從官方頁面取得**，不再依賴 `stations.tsv`。TSV 只作為動態取得失敗（網路問題、官方頁面結構變更）時的 fallback 快照。若官方頁面 HTML 結構大改導致 `Machines` 變數正則對不上，會自動退回 TSV，並在 stderr 印出警告。
4. **失敗站點不會中斷整個流程**。`scan.py` 內每站 POST 超時 15 秒、自動重試 2 次（指數退避），仍失敗就記錄在報告底部的「查詢失敗站點」段落，不影響其他站。

## 不要做的事

- **不要試著用 `?TID=xxx` GET**：API 強制要 POST + body。
- **不要把並行改成 sequential**：86 × 1.5s = 2 分鐘以上，使用者會覺得慢。預設併發 6 跑完約 25 秒。
- **不要透過 `cors.eu.org` 等公開 CORS proxy 抓**：那些代理短時間多次請求會被限流；本機 CLI 沒這個問題，直接打官方 API 最穩。
- **不要對輸出做太多後處理**：腳本已產出格式良好的 Markdown，直接呈現給使用者就好。若使用者要 JSON 等其他格式，再另外處理。

## 免責聲明

本工具僅供個人便利查詢使用，所有資料產權皆屬原網站所有。請勿用於商業用途或高頻率惡意查詢，以免造成對方伺服器負擔。

## 參考檔案

- [`references/api.md`](references/api.md) — 官方 API 完整規格、回傳欄位、踩雷紀錄。**遇到 API 行為異常時讀這個。**
- `scripts/stations.tsv` — 86 站 master data（TID / 據點分類 / 路線 / 站名）。可直接 `awk -F'\t'` 或 Python `csv.DictReader` 查詢。
- `scripts/scan.sh` — 向後相容的 bash wrapper（內部呼叫 `python3 scan.py`）。一般情況下直接用 `python3 scan.py` 即可。
