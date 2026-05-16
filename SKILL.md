---
name: yannick-ytm-stats
description: 彙整亞尼克 YTM 蛋糕販賣機全台據點的即時庫存，依商品聚合並產出 Markdown 統計報告（含商品排行、出現站點、價格、總數量）。當使用者提到「亞尼克」、「YTM」、「蛋糕販賣機」、「生乳捲庫存」、「三顆布丁生乳捲」、「BUBU 切片組」、「巴斯克生起司」、「景安站」/「南港站」等任一捷運站想查庫存、想看哪些站還有貨、整理全站存貨清單、做進貨/補貨參考時，務必啟用本 skill — 即使使用者沒有講「庫存」二字，只要話題跟亞尼克 YTM 哪裡有/沒有什麼商品（包含近期熱門的三顆布丁生乳捲）有關，就應該主動跑這個 skill 給出數據
---

# 亞尼克 YTM 全站庫存統計

## 這個 skill 在做什麼

亞尼克在台北捷運、高雄捷運、各地門市共設有多個 YTM（蛋糕販賣機）據點，官方查詢頁
`https://www.yannick.com.tw/ytm/service2` 一次只能看一站，本 skill 把全部站點的查詢結果並行整合、依商品聚合，產出可讀的 Markdown 統計報告 —— 哪個商品在哪些站有貨、共幾個、單價多少、哪些站查詢失敗都一目了然

## 怎麼用（最小流程）

直接執行 `scripts/scan.py`，它會：

1. 取得最新站點清單（即時取得失敗時自動退回讀 `scripts/stations.tsv` 快照）
2. 並行查詢各站庫存
3. 聚合並把 Markdown 報告印到 **stdout**

```bash
python3 scripts/scan.py
```

執行時間：**約 25–60 秒**（視站點數、預設併發 6、視網路情況），輸出包含：

- 📊 整體摘要：站點數、有庫存站、商品種類、總庫存
- 🗺️ 各據點分類（台北/高雄/門市）小計
- 🍰 商品排行表
- 📍 每個商品「出現在哪些站 + 各站剩幾個」
- ⚠️ 查詢失敗站點清單（若有）

直接把 stdout 內容呈現給使用者即可，已是 Markdown 格式

## 系統需求

腳本只需要：

- **Python 3.8+**（macOS 預設、所有主流 Linux 預設、Windows 從 [python.org](https://python.org) 一鍵安裝）

不用 `pip install` 任何套件；不需要 curl、jq、Node.js、任何雲端服務或 API key
全部使用 Python 標準函式庫（`urllib`、`json`、`csv`、`concurrent.futures`、`datetime`、`collections`），幾乎所有能跑 Claude Code 的電腦都直接能執行

## 環境變數（可選）

| 變數 | 預設 | 說明 |
|------|------|------|
| `CONCURRENCY` | 6 | 同時併發查詢的站點數，網路差或想更保守可設 3–4；想快可設 10 |
| `YANNICK_USE_LOCAL_STATIONS` | (空) | 設 `1` 時跳過動態取得，直接讀 `scripts/stations.tsv` 快照 |
| `YANNICK_OFFLINE_CACHE` | (空) | 指向 mock JSON 目錄；設定後跳過所有 HTTP，從目錄讀，給開發/測試用，使用者一般不需要設 |

```bash
CONCURRENCY=10 python3 scripts/scan.py   # 較快
CONCURRENCY=3  python3 scripts/scan.py   # 較保守
```

## 注意事項

1. **節制使用原則**：每次執行每站只送一次請求，預設併發 6 已是兼顧速度與不造成伺服器負擔的設定，請勿任意調高
2. **站點清單預設即時取得**：腳本會自動跟上官方變更，不再依賴 `stations.tsv`；TSV 只在動態取得失敗時作為 fallback
3. **失敗站點不會中斷整個流程**：腳本內每站逾時 15 秒、自動重試 2 次（指數退避），仍失敗就記錄在報告底部，不影響其他站

## 不要做的事

- **不要把並行改成 sequential**：使用者會覺得慢，預設併發 6 是合理設定
- **不要任意調高 `CONCURRENCY`**：避免對官方服務造成負擔
- **不要透過第三方代理服務轉發請求**：本機 CLI 環境直接呼叫即可
- **不要對輸出做太多後處理**：腳本已產出格式良好的 Markdown，直接呈現給使用者就好，若使用者要 JSON 等其他格式，再另外處理
- **不要把本工具用於商業用途或大量自動化請求**：僅供個人便利查詢

## 免責聲明

本工具僅供個人非商業用途的便利查詢，所有資料著作權與商標皆屬亞尼克所有；庫存資料可能有延遲或誤差，請以實際到店為準，若亞尼克官方表示反對此類用途，請立即停止使用本工具

## 參考檔案

- `scripts/stations.tsv` — 站點 master data 快照（fallback 用），含 TID / 據點分類 / 路線 / 站名
- `scripts/scan.sh` — 向後相容的 bash wrapper（內部呼叫 `python3 scan.py`），一般情況下直接用 `python3 scan.py` 即可
