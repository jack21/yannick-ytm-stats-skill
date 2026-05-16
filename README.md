# 亞尼克 YTM 庫存查詢 SKILL

一個 Agent Skill — 一鍵彙整亞尼克 YTM 蛋糕販賣機全台據點的即時庫存，依商品聚合並產出 Markdown 統計報告

聊到「哪一站的 YTM 還有**三顆布丁生乳捲**？」、「BUBU 切片組剩幾個？」、「巴斯克生起司哪裡可以買到？」、「全站庫存統計」這類話題時，AI 會自動觸發本 skill，跑完全部站點把整理好的資料端到你面前；近期最爆紅的是**三顆布丁生乳捲**，幾乎每站都會被秒空，本 skill 就是為了快速比對「現在還剩哪幾站有貨」而生

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

> 註：**三顆布丁生乳捲**是近期爆紅商品，補貨後通常數小時內就被掃空，總庫存看起來不高是因為一直在被搶，想吃的話建議用本 skill 即時掃一次再出門

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

下面依工具字母序列出安裝步驟

<details>
<summary><b>Aider</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
aider --read ~/yannick-ytm-stats-skill/AGENTS.md
```

或把它寫進 `~/.aider.conf.yml` 永久生效：

```yaml
read:
  - ~/yannick-ytm-stats-skill/AGENTS.md
```

</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/.claude/skills/yannick-ytm-stats
```

開新對話、提到「亞尼克 YTM」就會自動觸發

</details>

<details>
<summary><b>Claude Desktop</b></summary>

1. 下載最新 [`yannick-ytm-stats.skill`](https://github.com/jack21/yannick-ytm-stats-skill/releases/download/latest/yannick-ytm-stats.skill)（或從 [Releases](https://github.com/jack21/yannick-ytm-stats-skill/releases) 挑版本）
2. 打開 Claude Desktop → **Settings → Capabilities → Skills → Upload skill**
3. 選剛下載的 `.skill` 檔，確認啟用

</details>

<details>
<summary><b>Claude.ai / Cowork</b></summary>

1. 下載最新 [`yannick-ytm-stats.skill`](https://github.com/jack21/yannick-ytm-stats-skill/releases/download/latest/yannick-ytm-stats.skill)（或從 [Releases](https://github.com/jack21/yannick-ytm-stats-skill/releases) 挑版本）
2. 登入 claude.ai → **Settings → Capabilities → Skills → Upload skill**
3. 選剛下載的 `.skill` 檔，確認啟用

</details>

<details>
<summary><b>Cline / Roo Code</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
ln -sf ~/yannick-ytm-stats-skill/AGENTS.md ~/.clinerules
```

工具會自動讀 `~/.clinerules` 作為全域 rules

</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
mkdir -p ~/.codex && echo "@$HOME/yannick-ytm-stats-skill/AGENTS.md" >> ~/.codex/AGENTS.md
```

工具會自動讀 `~/.codex/AGENTS.md`，把 AGENTS.md 用 `@` 語法 import 進去即可

</details>

<details>
<summary><b>Continue.dev</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
```

把 `~/yannick-ytm-stats-skill/AGENTS.md` 的內容貼進 `~/.continue/config.json` 的 `systemMessage` 欄位

</details>

<details>
<summary><b>Cursor</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
```

打開 Cursor → **Settings → Rules → User Rules**，把 `~/yannick-ytm-stats-skill/AGENTS.md` 的內容貼進去

</details>

<details>
<summary><b>Gemini CLI</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
mkdir -p ~/.gemini && echo "@$HOME/yannick-ytm-stats-skill/AGENTS.md" >> ~/.gemini/GEMINI.md
```

工具會自動讀 `~/.gemini/GEMINI.md`，把 AGENTS.md 用 `@` 語法 import 進去即可

</details>

<details>
<summary><b>Windsurf</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
```

打開 Windsurf → **Settings → Cascade → Memories / Rules**，把 `~/yannick-ytm-stats-skill/AGENTS.md` 的內容貼進去

</details>

<details>
<summary><b>Zed</b></summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
```

把 `~/yannick-ytm-stats-skill/AGENTS.md` 的內容貼進 `~/.config/zed/settings.json` 的 `assistant.default_model.system_prompt` 欄位

</details>

<details>
<summary><b>其他工具</b>（ChatGPT custom GPT、自製 MCP / LangChain agent…）</summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git ~/yannick-ytm-stats-skill
```

把 `~/yannick-ytm-stats-skill/AGENTS.md` 的內容貼進該工具的 system prompt，確保工具有能力呼叫 shell 跑 `python3 ~/yannick-ytm-stats-skill/scripts/scan.py`

</details>

<details>
<summary><b>純命令列</b>（不透過任何 AI 工具）</summary>

```bash
git clone https://github.com/jack21/yannick-ytm-stats-skill.git
python3 yannick-ytm-stats-skill/scripts/scan.py
```

只需 Python 3.8+，不用任何 `pip install`

</details>

<details>
<summary><b>自行打包成 <code>.skill</code></b>（給開發者）</summary>

修改內容後想重新打包：

```bash
./scripts/package.sh   # 產出 dist/yannick-ytm-stats.skill
```

該 script 內就是一行 `zip`，刻意排除 `dist/`、`examples/`、`.github/`、`tests/`、`README.md` 等非 runtime 檔案

Release：推 `v*` tag 後，`.github/workflows/release.yml` 會自動打包並上傳 `.skill` 到 GitHub Release

</details>

## 使用方式

### 1. 直接呼叫 skill

```
/yannick-ytm-stats
```

### 2. 自然語言觸發

直接跟 AI 對話即可，例如：

- 「幫我看一下亞尼克 YTM 蛋糕販賣機現在全部站點各有什麼商品」
- 「**三顆布丁生乳捲**現在哪幾個 YTM 還有貨？最近超紅都搶不到」
- 「我想吃巴斯克生起司，哪幾個 YTM 還有貨？」
- 「亞尼克整體補貨狀況怎樣？哪些商品最缺貨？三顆布丁生乳捲還剩多少？」

執行時間約 **25–60 秒**

## 它是怎麼運作的

本 skill 透過亞尼克官網 YTM 查詢頁的同一個查詢介面，把各站結果並行取得、依商品聚合後以 Markdown 呈現，僅供使用者個人即時查詢使用

為避免對官方服務造成負擔，設計上以節制為原則：

- 每次執行，每站僅發送一次請求
- 預設併發連線數保守（6），可由 `CONCURRENCY` 環境變數調整
- 不對取得的資料做修改、儲存或再散布

## 專案結構

```
yannick-ytm-stats-skill/
├── SKILL.md              # Agent skill 入口（含 frontmatter 觸發描述）
├── README.md             # 本檔
├── AGENTS.md             # AGENTS.md 規則檔（給非 Anthropic 系工具讀）
├── CLAUDE.md             # 開發者接手此 repo 的指南
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
│   └── api.md            # 開發者參考（資料格式、注意事項）
├── scripts/
│   ├── scan.py           # 主腳本（純 Python 標準函式庫）
│   ├── scan.sh           # 向後相容 wrapper（呼叫 scan.py）
│   ├── package.sh        # 打包成 .skill 的 script
│   └── stations.tsv      # 站點 master data 快照（fallback 用）
├── tests/
│   └── README.md         # 離線 fixtures 怎麼建（fixtures 本身不進 git）
├── examples/
│   └── sample-output.md  # 完整範例輸出
└── dist/
    └── yannick-ytm-stats.skill   # 預打包好的 skill 安裝檔
```

## 貢獻

PR / Issue 歡迎本 repo 故意保持極小，所以：

- **不引入第三方套件**（標準函式庫已足夠）
- **不加 framework / build step**（純 Python script + Markdown）
- **盡量保持 Markdown 輸出格式穩定**，使用者已習慣現有版面

## 授權

[MIT License](LICENSE)

## 致謝

- 亞尼克 YTM 蛋糕販賣機提供了公開的庫存查詢頁，本 skill 只是讓查詢更便利
- [Anthropic Agent Skills 規格](https://docs.anthropic.com/en/docs/build-with-claude/skills) 提供 `.skill` 套件格式
- [agents.md](https://agents.md) 開放標準提供 `AGENTS.md` 規則檔慣例（由 OpenAI、Cursor、Sourcegraph 等共同推動）

## 免責聲明

- 本工具僅供個人非商業用途的便利查詢，不得用於商業營利、轉售或大量自動化請求
- 所查詢的資訊均來自亞尼克官方公開頁面，所有資料著作權與商標皆屬亞尼克所有
- 庫存資料由亞尼克官方提供，可能有延遲或誤差，請以實際到店為準
- 若亞尼克官方明示反對此類用途、或修改服務條款，請立即停止使用本工具
- 使用者應自行遵守當地法律與該網站的使用條款，本專案作者不對使用本工具所造成的任何後果負責
