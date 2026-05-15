# tests/

本資料夾是給開發 / CI 用的離線測試素材，不會被打包進 `.skill`（見 `scripts/package.sh` 的排除清單）。

## 怎麼跑

```bash
YANNICK_OFFLINE_CACHE=tests/fixtures python3 scripts/scan.py
```

`scan.py` 看到 `YANNICK_OFFLINE_CACHE` 就會跳過 HTTP，改從目錄讀 `<tid>.json`。

## fixtures 結構

```
tests/fixtures/
  A0001.json       # 對應 stations.tsv 裡 tid=A0001 的站
  A0002.json
  ...
  B0099.status     # 可選：寫 "FAIL: reason" 模擬失敗站
```

JSON 內容請對照 [`../references/api.md`](../references/api.md) 的回傳格式。
如果某站沒有對應 JSON，scan.py 會把它記成失敗站，正好可以驗證錯誤分支。

## 為什麼沒提供完整 fixtures

86 站的 JSON 隨時在變，提供快照只會誤導測試。若要建一份：

```bash
mkdir -p tests/fixtures
for tid in $(awk -F'\t' 'NR>1 {print $1}' scripts/stations.tsv); do
  curl -s -X POST https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx \
    --data-urlencode "TID=$tid" > "tests/fixtures/$tid.json"
done
```
