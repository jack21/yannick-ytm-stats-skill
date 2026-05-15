# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這個 repo 是什麼

這不是一個應用程式 repo，而是一個 **Claude Code / Cowork skill**：`yannick-ytm-stats-skill`。打包後的成品就是 `dist/yannick-ytm-stats-skill.skill`，使用者安裝後 Claude 會在聊到「亞尼克 / YTM / 蛋糕販賣機 / 某站庫存」時自動觸發 `scripts/scan.py`，把亞尼克全台 86 個 YTM 據點的即時庫存抓回來、聚合、輸出 Markdown 報告。

Skill 的觸發描述、注意事項、用法寫在 `SKILL.md` 的 frontmatter；那是 skill runtime 真正讀的入口檔。修改觸發行為時改 `SKILL.md`，不是改 `README.md`。

## 常用指令

執行全站掃描（一般用法，輸出 Markdown 到 stdout）：

```bash
python3 scripts/scan.py
```

調整併發 / 離線模式：

```bash
CONCURRENCY=10 python3 scripts/scan.py                  # 較快
CONCURRENCY=3  python3 scripts/scan.py                  # 較保守
YANNICK_OFFLINE_CACHE=/path/to/mock python3 scripts/scan.py  # 跳過 HTTP、從本機 mock JSON 讀
```

重新打包 `.skill`（zip 即可、刻意排除非 runtime 的檔案）：

```bash
cd /Users/jack/Workspace/yannick-ytm-skill
zip -r dist/yannick-ytm-stats-skill.skill . \
  -x "dist/*" "examples/*" ".github/*" "README.md" "LICENSE" ".gitignore" "CLAUDE.md"
```

沒有 build / lint / test pipeline。沒有 `package.json`、沒有 `requirements.txt`。只需 Python 3.8+ 標準函式庫。

## 架構

整個 skill 由三個檔案撐起來，理解這三個就夠了：

- **`SKILL.md`** — Claude skill 的入口檔，frontmatter 的 `description` 決定 skill 何時被觸發，body 是給 Claude 看的「怎麼用這個 skill」說明。改觸發行為時編這裡。
- **`scripts/scan.py`** — 唯一的可執行腳本，純標準函式庫。流程：
  1. `get_stations()` 先呼叫 `fetch_stations_live()` GET 官方頁面 `service2`，用正則抓出內嵌的 `Machines = [...]` JSON，解析成 86 站 master data（tid / branch_name / line / station_name）。**這是 primary path，每次跑都會抓最新站點清單。** 取得失敗（網路問題或官方頁面結構大改）會自動退回 `load_stations()` 讀 `stations.tsv` 快照，並在 stderr 印警告。
  2. `scan_all()` 用 `ThreadPoolExecutor` 並行對每個 tid `POST` 一次官方 stock ajax endpoint，預設併發 6、單站 15s timeout、失敗指數退避重試 2 次。
  3. `build_report()` 把每站的 `Result.StockList[]` 依商品代碼（`commodityCode`）聚合成商品 → 出現站點清單，輸出固定版面的 Markdown：整體摘要 → 各據點分類 → 商品庫存排行 → 各商品出現站點 → 失敗站點。
- **`scripts/stations.tsv`** — 86 站 master data 快照（2026-05 抓的），**現在只作為 fallback**，動態取得失敗時才會被讀。一般情況下不需要手動更新；但若想完全離線跑 / 官方頁面長期掛掉，可以更新它。更新方法見 `README.md` 「站點清單更新」段。

底層 API 的完整規格、`Status.code` 對照、踩過的雷區（強制 POST、無 CORS header、必須 form body）寫在 `references/api.md`。**遇到 API 行為異常時先讀這個，再改 `scan.py`。**

## 設計上刻意的取捨

修改本 repo 時請保留這些約束（PR 也會以此為準）：

- **不引入第三方套件**。一切只用 Python 標準函式庫，使用者不用 `pip install` 就能跑。新增依賴前請先確認真的標準庫做不到。
- **不加 framework / build step / lint config**。skill 越小越好維護，使用者下載 `.skill` 拖入就能用。
- **保持 Markdown 輸出版面穩定**。`build_report()` 輸出的章節順序、emoji、表頭都被使用者習慣依賴；要動版面前想清楚。
- **不要把並行改成 sequential**。86 × ~1.5s = 兩分鐘，使用者體感太慢。預設併發 6 約 25 秒完成。
- **不要改成 GET `?TID=xxx`**。官方 API 強制 POST + form body，GET 會回 `Status.code=05`。
- **不要走公開 CORS proxy（如 cors.eu.org）**。CLI 環境沒有 CORS 限制，直接打官方 API 最穩；proxy 反而會被限流。

## 修改 stations.tsv 後

`stations.tsv` 改動後不需要重新 build 程式碼，但要重新打包 `.skill` 給使用者；`scan.py` 是在執行時讀 TSV 的。
