# yannick-ytm-stats-skill

一個 [Claude Code](https://claude.com/claude-code) / [Cowork](https://claude.ai/) skill — 一鍵抓取亞尼克 YTM 蛋糕販賣機全台 86 個據點的即時庫存，依商品聚合並產出 Markdown 統計報告。

聊到「哪一站的 YTM 還有**三顆布丁生乳捲**？」、「BUBU 切片組剩幾個？」、「巴斯克生起司哪裡可以買到？」、「全站庫存統計」這類話題時，Claude 會自動觸發本 skill，跑完 86 站把整理好的資料端到你面前。近期最爆紅的是**三顆布丁生乳捲**，幾乎每站都會被秒空，本 skill 就是為了快速比對「現在還剩哪幾站有貨」而生。

## 範例輸出

完整輸出見 [`examples/sample-output.md`](examples/sample-output.md)，這裡是其中一個片段（實際輸出會包含當下所有上架商品，例如近期爆紅的**三顆布丁生乳捲**、原味生乳捲、BUBU 切片組、巴斯克生起司、四入生乳蒸布丁禮盒等）：

```markdown
## 🍰 商品庫存排行

| 排名 | 商品 | 單價 | 總庫存 | 出現站數 |
| ---: | --- | ---: | ---: | ---: |
| 1 | 三顆布丁生乳捲 (`31Z02XXXX`) | NT$ 399 | **48** 個 | 22 站 |
| 2 | 原味生乳捲 (`31Z021079`) | NT$ 353 | **136** 個 | 64 站 |
| 3 | BUBU切片組-常態 (`31Z011082`) | NT$ 329 | **100** 個 | 43 站 |
| 4 | 四入生乳蒸布丁禮盒 (`31Z014127`) | NT$ 223 | **63** 個 | 30 站 |
| 5 | 巴斯克生起司 (`31Z064078`) | NT$ 378 | **30** 個 | 12 站 |

> 註：**三顆布丁生乳捲**是近期爆紅商品，補貨後通常數小時內就被掃空，總庫存看起來不高是因為一直在被搶。想吃的話建議用本 skill 即時掃一次再出門。

## 📍 各商品出現的站點

### 三顆布丁生乳捲 — 共 48 個 / 22 站

| 站點 | 分類 | 數量 |
| --- | --- | ---: |
| 淡水信義線-台北 101/世貿站 | 台北捷運據點 | 4 |
| 板南線-市政府站 | 台北捷運據點 | 3 |
| 文湖線-南港展覽館站 | 台北捷運據點 | 3 |
| ... |

### 巴斯克生起司 — 共 30 個 / 12 站

| 站點 | 分類 | 數量 |
| --- | --- | ---: |
| 中和新蘆線-行天宮站 | 台北捷運據點 | 5 |
| 板南線-市政府站 | 台北捷運據點 | 4 |
| ... |
```

## 安裝

只有兩個東西要記：

- **Claude 系（Claude Code / Desktop / Web）** → 把這個 repo 當作 skill 安裝
- **其他工具（Codex / Gemini / Cursor / …）** → 引入本 repo 的 `AGENTS.md`

挑你用的工具，照著做就好。

### Claude Code

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/.claude/skills/yannick-ytm-stats-skill
```

開新對話、提到「亞尼克 YTM」就會自動觸發。

### Claude Desktop（Mac / Windows）

1. 下載 [`dist/yannick-ytm-stats-skill.skill`](dist/yannick-ytm-stats-skill.skill)
2. **Settings → Capabilities → Skills → Upload skill** 選那個檔

### Claude.ai / Cowork（網頁）

同 Desktop：下載 `.skill` 後在 **Settings → Capabilities → Skills** 上傳。

### Codex CLI

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
mkdir -p ~/.codex && echo "@$HOME/yannick-ytm-stats-skill/AGENTS.md" >> ~/.codex/AGENTS.md
```

### Gemini CLI

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
mkdir -p ~/.gemini && echo "@$HOME/yannick-ytm-stats-skill/AGENTS.md" >> ~/.gemini/GEMINI.md
```

### Cursor

clone repo 後，把 `AGENTS.md` 的內容貼到 **Settings → Rules → User Rules**。

### Windsurf

clone repo 後，把 `AGENTS.md` 的內容貼到 **Settings → Cascade → Memories / Rules**。

### Aider

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
aider --read ~/yannick-ytm-stats-skill/AGENTS.md
```

或把它寫進 `~/.aider.conf.yml`：

```yaml
read:
  - ~/yannick-ytm-stats-skill/AGENTS.md
```

### Cline / Roo Code（VS Code）

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
ln -sf ~/yannick-ytm-stats-skill/AGENTS.md ~/.clinerules
```

### 其他工具 / 純命令列

任何能跑 shell 的 AI 工具：clone repo，把 `AGENTS.md` 內容貼進 system prompt 即可。

不用任何 AI 工具，自己跑也行：

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git
python3 yannick-ytm-stats-skill/scripts/scan.py
```

---

<details>
<summary>自行打包成 <code>.skill</code>（給開發者）</summary>

修改內容後想重新打包：

```bash
./scripts/package.sh   # 產出 dist/yannick-ytm-stats-skill.skill
```

該 script 內就是一行 `zip`，刻意排除 `dist/`、`examples/`、`.github/`、`tests/`、`README.md` 等非 runtime 檔案。

Release：推 `v*` tag 後，`.github/workflows/release.yml` 會自動打包並上傳 `.skill` 到 GitHub Release。
</details>

## 使用

安裝後直接跟 Claude 對話即可，例如：

- 「幫我看一下亞尼克 YTM 蛋糕販賣機現在全部站點各有什麼商品。」
- 「**三顆布丁生乳捲**現在哪幾個 YTM 還有貨？最近超紅都搶不到。」
- 「我想吃巴斯克生起司，哪幾個 YTM 還有貨？」
- 「亞尼克整體補貨狀況怎樣？哪些商品最缺貨？三顆布丁生乳捲還剩多少？」

Claude 看到這類請求會自動跑 `scripts/scan.py`，抓完聚合後把 Markdown 報告整理給你。

也可以直接從命令列跑：

```bash
python3 scripts/scan.py
```

執行時間：**約 25–60 秒**（86 站、預設併發 6、視網路狀況）。

### 可選環境變數

| 變數 | 預設 | 說明 |
|------|------|------|
| `CONCURRENCY` | `6` | 同時併發抓取的站點數。網路差或想保守可設 3–4；想快可設 10。 |
| `YANNICK_USE_LOCAL_STATIONS` | (空) | 設 `1` 時跳過動態取站點，直接讀 `scripts/stations.tsv` 快照。 |
| `YANNICK_OFFLINE_CACHE` | (空) | 指向 mock JSON 目錄。設定後跳過所有 HTTP，從目錄讀。給開發/測試用。 |

```bash
CONCURRENCY=10 python3 scripts/scan.py    # 較快
CONCURRENCY=3  python3 scripts/scan.py    # 較保守
```

## 系統需求

只需要 **Python 3.8+**：

- macOS 預設內建
- 大部分 Linux 預設內建
- Windows 從 [python.org](https://python.org) 一鍵安裝

完全不需要 `pip install` 任何套件、不需 curl / jq / Node.js / 任何雲端服務。  
全部用 Python 標準函式庫（`urllib`, `json`, `csv`, `concurrent.futures`, `datetime`）。

## 它是怎麼運作的

亞尼克的官方查詢頁 `https://www.yannick.com.tw/ytm/service2` 用的是 ASP.NET WebForms + Vue.js，每次只能查一個站。底層 ajax endpoint 已反向工程過：

```
POST https://www.yannick.com.tw/_zh-cht/ajaxTYTMStock.ashx
Content-Type: application/x-www-form-urlencoded
Body: TID=<站點 ID>
```

`scan.py` 做的事很單純：

1. **動態取得最新站點清單**：GET 官方 `service2` 頁面，從內嵌 JS 的 `Machines` 變數抽出 86 站 JSON（即時抓，不依賴本機快照）。動態取得失敗時自動退回讀 `scripts/stations.tsv`。
2. `concurrent.futures.ThreadPoolExecutor` 並行 POST 上述 stock endpoint
3. 收集每站的 `StockList`、依商品代碼聚合
4. 輸出整理好的 Markdown 表格

詳細 API 規格、回傳欄位、踩過的雷區見 [`references/api.md`](references/api.md)。

## 專案結構

```
yannick-ytm-stats-skill/
├── SKILL.md              # Claude skill 入口（含 frontmatter 觸發描述）
├── README.md             # 本檔
├── CLAUDE.md             # 給 Claude Code 接手此 repo 的指南
├── CONTRIBUTING.md       # 貢獻指南
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── .github/
│   ├── workflows/
│   │   ├── ci.yml             # PR / push 時跑語法檢查與離線 smoke test
│   │   └── release.yml        # 推 v* tag 時自動打包 .skill 並上傳 Release
│   ├── ISSUE_TEMPLATE/        # Bug / 站點更新範本
│   └── PULL_REQUEST_TEMPLATE.md
├── references/
│   └── api.md            # 亞尼克 API 完整規格、踩雷紀錄
├── scripts/
│   ├── scan.py           # 主腳本（純 Python 標準函式庫）
│   ├── scan.sh           # 向後相容 wrapper（呼叫 scan.py）
│   ├── package.sh        # 打包成 .skill 的 script
│   └── stations.tsv      # 86 站 master data
├── tests/
│   └── README.md         # 離線 fixtures 怎麼建（fixtures 本身不進 git）
├── examples/
│   └── sample-output.md  # 完整範例輸出
└── dist/
    └── yannick-ytm-stats-skill.skill   # 預打包好的 skill 安裝檔
```

## 站點清單更新

`stations.tsv` 是 2026-05 抓的快照。若亞尼克官方新增了據點或站名變更，可從官方頁面 `service2` 第二個 `<select>` 撈最新清單來更新：

```js
// 在瀏覽器 DevTools console 跑（先選定 BranchCode）
const sels = document.querySelectorAll('select');
sels[0].value = '001';   // 改 '002' / '003' 切換據點分類
sels[0].dispatchEvent(new Event('change', { bubbles: true }));
// 等 1 秒
Array.from(sels[1].options)
  .filter(o => o.value)
  .map(o => `${o.value}\t${o.textContent.trim()}`)
  .join('\n');
```

把輸出整理進 `scripts/stations.tsv`，重新打包即可。

## 貢獻

PR / Issue 歡迎。本 repo 故意保持極小，所以：

- **不引入第三方套件**（標準函式庫已足夠）。
- **不加 framework / build step**（純 Python script + Markdown）。
- **盡量保持 Markdown 輸出格式穩定**，使用者已習慣現有版面。

## 授權

[MIT License](LICENSE)

## 致謝

- 亞尼克 YTM 蛋糕販賣機提供了這個 API。本 skill 只是讓查詢更便利，不對亞尼克官網造成異常負載（單次掃描 86 個 POST 而已）。
- Claude Code / Cowork [skill-creator](https://github.com/anthropics) 提供 skill 框架。

## 免責聲明

本工具透過公開 API 抓取公開資訊。庫存資料由亞尼克官方提供，可能有延遲或誤差。請以實際到店為準。
