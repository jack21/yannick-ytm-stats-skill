# 貢獻指南

歡迎 PR / Issue，本 repo 故意保持極小、好維護，請先看完以下原則再動工

## 設計原則（硬性約束）

- **不引入第三方套件**：一切只用 Python 標準函式庫，使用者不需要 `pip install` 就能跑
- **不加 framework / build step / lint config**：skill 越小越好維護
- **保持 Markdown 輸出版面穩定**：`build_report()` 的章節順序、emoji、表頭被使用者習慣依賴，改版面前請先在 issue 討論
- **保持並行查詢**：sequential 太慢；預設併發 6 約 25 秒
- **不要任意調高 `CONCURRENCY` 預設值**：避免對官方服務造成負擔
- **不要把工具設計成商業用途或大量自動化請求**：僅供個人便利查詢

## 開發環境

只需要 Python 3.8+，沒有其他依賴

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

`stations.tsv` 只是 fallback 快照，一般不需要手動更新（`scan.py` 預設會即時取得最新站點清單）；若想完全離線使用，可自行整理一份新的 TSV，更新後重新打包 `.skill`：

```bash
./scripts/package.sh
```

## 發 release

1. 更新 `CHANGELOG.md`
2. `git tag v0.x.y && git push --tags`
3. `.github/workflows/release.yml` 會自動打包並建立 GitHub Release，把 `.skill` 檔附上去

## 免責

本工具僅供個人非商業用途的便利查詢，所有資料著作權與商標皆屬亞尼克所有，請勿用於商業用途或高頻率自動化請求，以免造成對方伺服器負擔，若亞尼克官方表示反對此類用途，請立即停止使用
