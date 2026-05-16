# tests/

本資料夾是給開發 / CI 用的離線測試素材，不會被打包進 `.skill`（見 `scripts/package.sh` 的排除清單）

## 怎麼跑

```bash
YANNICK_OFFLINE_CACHE=tests/fixtures python3 scripts/scan.py
```

`scan.py` 看到 `YANNICK_OFFLINE_CACHE` 就會跳過 HTTP，改從目錄讀 `<tid>.json`

## fixtures 結構

```
tests/fixtures/
  A0001.json       # 對應 stations.tsv 裡 tid=A0001 的站
  A0002.json
  ...
  B0099.status     # 可選：寫 "FAIL: reason" 模擬失敗站
```

如果某站沒有對應 JSON，scan.py 會把它記成失敗站，正好可以驗證錯誤分支

## 為什麼沒提供完整 fixtures

商品庫存隨時在變，提供快照只會誤導測試；若要建立離線測試素材，請自行用線上跑一次後手動整理需要的 station JSON 放入 `tests/fixtures/`，或從 stderr / 報告複製需要的欄位另寫測試樣本
