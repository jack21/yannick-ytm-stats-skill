# 貢獻指南

歡迎 PR / Issue。本 repo 故意保持極小、好維護，請先看完以下原則再動工。

## 設計原則（硬性約束）

- **不引入第三方套件**。一切只用 Python 標準函式庫，使用者不需要 `pip install` 就能跑。
- **不加 framework / build step / lint config**。skill 越小越好維護。
- **保持 Markdown 輸出版面穩定**。`build_report()` 的章節順序、emoji、表頭被使用者習慣依賴；改版面前請先在 issue 討論。
- **保持並行抓取**。86 站 sequential 要兩分多鐘；預設併發 6 約 25 秒。

## 開發環境

只需要 Python 3.8+，沒有其他依賴。

```bash
# 線上跑
python3 scripts/scan.py

# 離線跑（需先準備 mock JSON 目錄，每站一個 <tid>.json）
YANNICK_OFFLINE_CACHE=tests/fixtures python3 scripts/scan.py
```

## 提交前自我檢查

- [ ] `python3 -m py_compile scripts/scan.py` 通過
- [ ] 改過 `scan.py`：實際跑一次（線上或離線模式）確認輸出正常
- [ ] 改過 `SKILL.md` frontmatter：確認觸發描述仍涵蓋常見問法
- [ ] `CHANGELOG.md` 補上對應條目
- [ ] 沒有引入新的第三方依賴

## 更新 stations.tsv

官方新增/停用站點時更新。撈法見 [`README.md`](README.md) 「站點清單更新」段。
更新後不需重新 build 程式碼，但要重新打包 `.skill` 給使用者：

```bash
./scripts/package.sh
```

## 發 release

1. 更新 `CHANGELOG.md`
2. `git tag v0.x.y && git push --tags`
3. `.github/workflows/release.yml` 會自動打包並建立 GitHub Release，把 `.skill` 檔附上去

## API 行為異常時

先讀 [`references/api.md`](references/api.md)，那邊有完整的官方 API 規格與踩雷紀錄。

## 免責

本工具僅供個人便利查詢使用，所有資料產權皆屬原網站所有。請勿用於商業用途或高頻率惡意查詢，以免造成對方伺服器負擔。
