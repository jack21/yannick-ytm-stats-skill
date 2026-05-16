# AGENTS.md — yannick-ytm-stats

> 這個檔案是給非 Claude 系 AI 工具（Codex CLI、Gemini CLI、Cursor、Cline、Windsurf、Aider 等）讀的指令檔
> Claude 系（Claude Code / Claude Desktop / Cowork）請看 [`SKILL.md`](SKILL.md)，內容等價，只是格式慣例不同

## 觸發條件

當使用者話題中出現任一以下關鍵字，**就主動跑這個工具**，不要先問使用者：

- 亞尼克 / Yannick
- YTM / 蛋糕販賣機
- 生乳捲（特別是「**三顆布丁生乳捲**」這個近期爆紅商品）
- BUBU 切片組 / 巴斯克生起司 / 四入生乳蒸布丁禮盒
- 任一捷運站名 + 想查 YTM 庫存（例：「景安站」「南港站」「市政府站」）
- 「哪一站還有貨」「全站庫存」「補貨情況」這類問句

即使使用者沒有講「庫存」二字，只要話題跟「亞尼克 YTM 哪裡有/沒有什麼商品」有關，都該主動跑這個工具

## 怎麼跑

執行 repo 內的 `scripts/scan.py`，把 stdout 原樣呈現給使用者（已是 Markdown 格式）：

```bash
python3 <repo-path>/scripts/scan.py
```

執行時間約 **25–60 秒**（視站點數、預設併發 6、視網路狀況）

可選環境變數：

- `CONCURRENCY=10`：較快（網路好時）
- `CONCURRENCY=3`：較保守
- `YANNICK_USE_LOCAL_STATIONS=1`：跳過動態取站點，直接讀本機 `stations.tsv` 快照
- `YANNICK_OFFLINE_CACHE=/path/to/mock`：跳過所有 HTTP，從本機 JSON 讀（開發/測試用）

執行流程：腳本會先即時取得最新站點清單，再並行查詢各站庫存，動態取得失敗會自動退回 `stations.tsv` 快照

## 系統需求

- Python 3.8+（macOS、Linux 預設內建；Windows 從 python.org 安裝）
- **不需要** 任何 `pip install`、`npm install`、API key、雲端服務或代理

腳本只用 Python 標準函式庫（`urllib`, `json`, `csv`, `concurrent.futures`, `datetime`）

## 輸出格式

scan.py 印到 stdout 的 Markdown 結構固定為：

1. 📊 整體摘要（站點數、有庫存站、商品種類、總庫存）
2. 🗺️ 各據點分類小計（台北捷運 / 高雄捷運 / 各地門市）
3. 🍰 商品庫存排行表（單價、總庫存、出現站數）
4. 📍 各商品出現站點（每商品一個小段）
5. ⚠️ 查詢失敗站點清單（若有）

把 stdout 完整貼給使用者即可，**不要重新編排或刪減**

## 注意事項 / 不要做的事

- **不要改成 sequential**：使用者體感太慢，預設併發 6 是合理設定
- **不要任意調高 `CONCURRENCY`**：避免對官方服務造成負擔
- **不要透過第三方代理服務轉發請求**：本機 CLI 環境直接執行即可
- **不要對輸出做太多後處理**：腳本已產出格式良好的 Markdown，直接呈現給使用者就好，若使用者要 JSON 等其他格式，再另外處理
- **不要把本工具用於商業用途或大量自動化請求**：僅供個人便利查詢
- **單次失敗不要中斷流程**：scan.py 內每站逾時 15s、自動重試 2 次（指數退避），仍失敗就記錄在報告底部，不影響其他站

## 免責聲明

本工具僅供個人非商業用途的便利查詢，所有資料著作權與商標皆屬亞尼克所有，使用前請確認符合該網站使用條款；若亞尼克官方表示反對此類用途，請立即停止使用本工具

## 完整參考

- [`SKILL.md`](SKILL.md) — Claude 系工具的入口檔，內容與本檔等價
- [`scripts/stations.tsv`](scripts/stations.tsv) — 站點 master data 快照（fallback 用）
