# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 這個 repo 是什麼

這不是一個應用程式 repo，而是一個 **Agent Skill**，命名規則：

- **Repo 名**：`yannick-ytm-stats-skill`（GitHub repo / clone 後的本機資料夾）
- **Skill 名**：`yannick-ytm-stats`（`SKILL.md` frontmatter 的 `name:`、打包後的 `dist/yannick-ytm-stats.skill`、AI 載入時識別用的名字）

使用者安裝後 AI 會在聊到「亞尼克 / YTM / 蛋糕販賣機 / 某站庫存」時自動觸發 `scripts/scan.py`，把亞尼克全台 YTM 據點的即時庫存彙整、聚合、輸出 Markdown 報告

Skill 的觸發描述、注意事項、用法寫在 `SKILL.md` 的 frontmatter，那是 skill runtime 真正讀的入口檔，修改觸發行為時改 `SKILL.md`，不是改 `README.md`

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

重新打包 `.skill`：

```bash
./scripts/package.sh                                    # 產出 dist/yannick-ytm-stats.skill
```

沒有 build / lint / test pipeline，沒有 `package.json`、沒有 `requirements.txt`，只需 Python 3.8+ 標準函式庫

## 架構

整個 skill 由三個檔案撐起來，理解這三個就夠了：

- **`SKILL.md`** — Agent skill 的入口檔，frontmatter 的 `description` 決定 skill 何時被觸發，body 是給 AI 看的「怎麼用這個 skill」說明，改觸發行為時編這裡
- **`scripts/scan.py`** — 唯一的可執行腳本，純標準函式庫，流程：
  1. `get_stations()` 先呼叫 `fetch_stations_live()` 即時取得站點清單，**這是 primary path**，取得失敗（網路問題或頁面結構變更）會自動退回 `load_stations()` 讀 `stations.tsv` 快照，並在 stderr 印警告
  2. `scan_all()` 用 `ThreadPoolExecutor` 並行查詢各站，預設併發 6、單站 15s timeout、失敗指數退避重試 2 次
  3. `build_report()` 把每站結果依商品代碼（`commodityCode`）聚合成商品 → 出現站點清單，輸出固定版面的 Markdown：整體摘要 → 各據點分類 → 商品庫存排行 → 各商品出現站點 → 失敗站點
- **`scripts/stations.tsv`** — 站點 master data 快照（2026-05），**現在只作為 fallback**，動態取得失敗時才會被讀，一般情況下不需要手動更新

## 設計上刻意的取捨

修改本 repo 時請保留這些約束（PR 也會以此為準）：

- **不引入第三方套件**，一切只用 Python 標準函式庫，使用者不用 `pip install` 就能跑，新增依賴前請先確認真的標準庫做不到
- **不加 framework / build step / lint config**，skill 越小越好維護，使用者下載 `.skill` 拖入就能用
- **保持 Markdown 輸出版面穩定**，`build_report()` 輸出的章節順序、emoji、表頭都被使用者習慣依賴，要動版面前想清楚
- **不要把並行改成 sequential**，使用者體感太慢，預設併發 6 約 25 秒完成
- **不要任意調高 `CONCURRENCY`**，避免對官方服務造成負擔
- **不要透過第三方代理服務轉發請求**，CLI 環境直接執行即可
- **不要把工具設計成商業用途或大量自動化請求**，僅供個人便利查詢

## 合規與免責

本工具僅供個人非商業用途的便利查詢，所有資料著作權與商標皆屬亞尼克所有；使用前請確認符合該網站使用條款，若亞尼克官方表示反對此類用途，請立即停止使用

## 修改 stations.tsv 後

`stations.tsv` 改動後不需要重新 build 程式碼，但要重新打包 `.skill` 給使用者，`scan.py` 是在執行時讀 TSV 的
