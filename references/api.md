# 亞尼克 YTM 庫存 API — 詳細規格

底層 API 是 `scan.sh` 在打的東西。一般使用 skill 時不需要看；遇到 API 行為異常、想新增功能、或要更新站點清單時再讀。

## Endpoint

```
POST https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx
Content-Type: application/x-www-form-urlencoded
Body: TID=<站點 ID>
```

最簡 Python 範例（不需任何第三方套件）：

```python
import json
import urllib.parse
import urllib.request

body = urllib.parse.urlencode({"TID": "F638C56F0B2313"}).encode("utf-8")
req = urllib.request.Request(
    "https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx",
    data=body,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))
print(json.dumps(data, ensure_ascii=False, indent=2))
```

## 回傳格式

```json
{
  "Result": {
    "StockList": [
      {
        "SaleID": "31Z011082",
        "ProductName": "(YTM)生乳捲BUBU切片組",
        "ColorID": "f",
        "SizeID": "f",
        "Price": 329,
        "commodityID": 2016657,
        "commodityName": "BUBU切片組-常態",
        "commodityCode": "31Z011082",
        "quantity": 1
      }
    ]
  },
  "Status": { "code": "00", "info": "" },
  "Alert": null
}
```

- `Status.code === "00"` 才是成功。其他 code 視為失敗。
- 常見錯誤：`code=05` + `info="TID 欄位是必要項。"` → 表示沒帶 body（或 body 被某些 CORS proxy 丟掉）。
- `StockList` 為空陣列 = 該站目前沒上架任何商品。
- 單一站點 stock list 通常 0–5 項；同一商品不會在同站重複。

## 重要欄位

| 欄位 | 來自 | 說明 |
|------|------|------|
| `commodityCode` | API | 商品代碼，聚合用 key (如 `31Z011082`) |
| `commodityName` | API | 商品名稱 (如 `BUBU切片組-常態`) |
| `ProductName` | API | 顯示用全名 (如 `(YTM)生乳捲BUBU切片組`)；含通路前綴 |
| `Price` | API | 售價 (整數，TWD) |
| `quantity` | API | 該站剩餘數量 |
| `SaleID` | API | 銷售用 ID；通常等於 `commodityCode` |

## 據點分類

| BranchCode | 名稱 | 站數 (2026-05) |
|------------|------|---------------|
| 001 | 台北捷運據點 | 71 |
| 002 | 高雄捷運據點 | 10 |
| 003 | 門市據點 | 5 |

合計 86 個 YTM 服務點。台北的 71 站涵蓋 6 條路線：環狀線、松山新店線、中和新蘆線、文湖線、板南線、淡水信義線。

## 已知產品（2026-05）

實測整網路只看過這 4 種商品；可能會增加（近期已新增**三顆布丁生乳捲**爆紅品項，commodityCode 尚需從 API 回傳實測確認後補上）。

- 原味生乳捲、BUBU 切片組、巴斯克生起司、四入生乳蒸布丁禮盒、**三顆布丁生乳捲**是目前最常被查詢的商品名稱。
- 「三顆布丁生乳捲」自上架以來幾乎站站秒空，搜尋查庫存的需求最高。

商品代碼對照（以下為已穩定觀測到的）：

- `31Z021079` — 原味生乳捲（NT$ 353）
- `31Z011082` — BUBU切片組-常態（NT$ 329）
- `31Z014127` — 四入生乳蒸布丁禮盒（NT$ 223）
- `31Z064078` — 巴斯克生起司（NT$ 378）
- *待補* — 三顆布丁生乳捲（單價依官方公告為準）

## 取得最新站點清單

官方頁面 `https://www.yannick.com.tw/ytm/service2` 是 ASP.NET WebForms + Vue.js render。
**本 skill 的 `scan.py` 已內建動態取得邏輯**：每次執行都會 GET 該頁面，用正則抓出內嵌的 `Machines = [...]` JSON 變數，解析成 86 站清單（含 TID / RName / TName / TAddr / PHOTO_URL）。

`Machines` 是一個 inline JS 陣列，每筆結構：

```json
{
  "TID": "F638C63801AA82",
  "TName": "環狀線-新北產業園區站",
  "TAddr": "新北市新莊區五工路35號",
  "RID": "001",
  "RName": "台北捷運據點",
  "PHOTO_URL": "https://photo.yannick.com.tw/...",
  "Sort": 70
}
```

只要這個變數結構不變，`scan.py` 就會自動跟上官方新增/停用的站點，**不需要更新 `stations.tsv`**。TSV 只在以下情況才會被讀：

- `YANNICK_USE_LOCAL_STATIONS=1`
- `YANNICK_OFFLINE_CACHE` 有設
- 動態取得失敗（網路問題、官方頁面 HTML 結構變更導致正則對不上）

若要手動更新 TSV 快照（離線情境用），仍可從同一頁面的第二個 `<select>` 撈：

1. 在瀏覽器開該頁，DevTools console 跑：

   ```js
   const sels = document.querySelectorAll('select');
   sels[0].value = '001';   // 改 '002' / '003' 切換據點分類
   sels[0].dispatchEvent(new Event('change', { bubbles: true }));
   // 等 1 秒
   Array.from(sels[1].options)
     .filter(o => o.value)
     .map(o => `${o.value}\t${o.textContent.trim()}`)
     .join('\n');
   ```

2. 輸出格式：`TID<TAB>路線-站名`，把它整理進 `stations.tsv`。

## 踩過的雷區

### 1. CORS proxy 不可靠

亞尼克 API 無 CORS header。瀏覽器版要透過代理才能打，但實測：

- `cors.eu.org` 支援 POST body 轉發，但短時間 100+ 請求會被限流封鎖 30 分鐘+
- `api.allorigins.win` / `api.codetabs.com` 把 POST body 丟掉
- `corsproxy.io` 要 API key
- 其他 (`cors.lol` / `proxy.cors.sh` / `crossorigin.me` …) 都掛了

**本 skill 跑在 CLI 環境（沒有 CORS 概念），直接打官方 API，徹底繞開這個問題。**

### 2. 直接 GET 不可用

```python
import urllib.request
resp = urllib.request.urlopen(
    "https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx?TID=F638C56F0B2313"
).read().decode()
# → {"Result":null,"Status":{"code":"05","info":"TID 欄位是必要項。"},...}
```

API 強制要 POST + form body。

### 3. ASP.NET WebForms 識別

如果想反向工程其他類似站，看到 `__VIEWSTATE`、`__EVENTTARGET` 等 hidden field 就是 WebForms。
form 通常 POST 回自己只更新 viewstate；真正資料常在另一個 `.ashx` endpoint。

### 4. 試營運站

有些站名後面會帶「(試營運中，5/15 正式開幕)」之類後綴。`stations.tsv` 已清理為純站名，
正式開幕後通常不會再改 TID，所以這份清單應可長期使用。

## 系統需求

- 只需 **Python 3.8+**。macOS / Linux 預設內建；Windows 從 python.org 一鍵安裝。
- 全部使用 Python 標準函式庫：`urllib`（HTTP）、`json`、`csv`、`concurrent.futures`（並行）、`collections`、`datetime`。
- **不需 pip install 任何套件、不需 curl、不需 jq。**

## 效能特性

實測 (台北住宅 100Mbps):

- 86 站、併發 6、每站 retry 0–2 次：約 **25–35 秒**
- 86 站、併發 3：約 **45–60 秒**
- 86 站、併發 12：約 **18–25 秒**（再高邊際效益遞減，主要受官方伺服器吞吐量限制）

`CONCURRENCY=6` 是兼顧速度與被限流風險的甜蜜點。
