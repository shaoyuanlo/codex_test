# Shao-Yuan Lo · 學術個人網站

以英文為主、簡潔專業、手機閱讀良好，並方便長期自行手動更新的學術網站。採用 Eleventy、Markdown、Nunjucks 與原生 CSS；沒有 CMS、資料庫、前端框架或客戶端 JavaScript。

目前開發與代理預覽位於 `shaoyuanlo/codex_test`。正式網站為 https://shaoyuanlo.github.io/ ，對應另一個儲存庫 `shaoyuanlo/shaoyuanlo.github.io`；本專案尚未取代原網站。

本文件是日常使用指南；Codex 的共用工作規則見 [AGENTS.md](AGENTS.md)。設計值以 [style.css](src/assets/style.css) 為準，以下表格是目前設定的說明，修改樣式時需同步核對。

- [日常更新](#日常更新)：內容、首頁資料、News 與論文。
- [設計設定](#設計設定)：色彩、字型、字級、行高、間距與版面。
- [預覽與發布](#預覽與發布)：固定預覽、版本預覽、快取及正式遷移。
- [開發與驗證](#開發與驗證)：建置、檢查與工作流程。
- [Codex 協作](#codex-協作)：網頁版、GitHub 雲端任務與自由聊天。

## 日常更新

在 GitHub 開啟來源檔 → 按鉛筆編輯 → Commit 到 `main`，GitHub Actions 會自動建置。日常編輯不需要在自己的電腦安裝軟體。

| 分頁 | 來源檔 | 網址 | 版型 |
| --- | --- | --- | --- |
| Home | [src/home.md](src/home.md) | `/` | `layouts/home.njk` |
| Lab | [src/lab.md](src/lab.md) | `/lab/` | `layouts/page.njk` |
| Publications | [src/publications.md](src/publications.md) | `/publications/` | `layouts/page.njk` |
| Activities | [src/activities.md](src/activities.md) | `/activities/` | `layouts/page.njk` |
| Teaching | [src/teaching.md](src/teaching.md) | `/teaching/` | `layouts/page.njk` |
| Blog | [src/blog.md](src/blog.md) | `/blog/` | `layouts/page.njk` |

六個選單連至獨立頁面，順序為 Home、Lab、Publications、Activities、Teaching、Blog；Home 就是根網址。Blog 與其他一般分頁相同，直接編輯 Markdown，沒有文章集合、自動列表、日期排序、草稿旗標或獨立文章版型。

| 要更新的項目 | 編輯位置 |
| --- | --- |
| 姓名、職稱、所屬單位、聯絡／社群連結、導覽 | `src/home.md` 上方的 `website:` |
| 首頁簡介、News、Honors & Awards、Media Coverage | `src/home.md` 正文 |
| 各分頁標題與簡介 | 該 `.md` 的 `title`、可選的 `intro` |
| 頭像原檔 | [files/portrait.jpg](files/portrait.jpg) |
| 頭像路徑、圖片尺寸資訊與首頁結構 | [layouts/home.njk](src/_includes/layouts/home.njk) |
| 頁尾文字、網頁 metadata、校徽路徑與共用導覽結構 | [layouts/base.njk](src/_includes/layouts/base.njk) |
| 校徽原檔 | [files/ntu-emblem.png](files/ntu-emblem.png) |
| CV | [files/SYLo_CV.pdf](files/SYLo_CV.pdf) |
| 配色、字體、間距、容器與元件外觀 | [src/assets/style.css](src/assets/style.css) |
| 資料讀取、Markdown 顯示轉換與資源複製 | [eleventy.config.js](eleventy.config.js) |

`files/` 專門放置網站內容檔案：CV、照片、校徽，以及 `papers/`、`talks/` 子目錄中的論文與投影片。CSS 與字型保留在 `src/assets/`，建置腳本留在 `scripts/`，查核與來源紀錄留在 `docs/`，不混入 `files/`。

### Markdown 與頁面設定

檔案開頭兩條 `---` 之間是 YAML front matter。先列運作設定，再列可編輯內容：

```yaml
---
layout: layouts/page.njk
section: lab
permalink: /lab/index.html
title: Lab
intro: A short introduction.
---
```

`layout` 決定版型，`section` 對應導覽識別與頁面 CSS 類別，`permalink` 決定網址；一般編輯保留這些欄位，主要修改 `title`、`intro` 與下方正文。`intro` 可省略；標題或文字含冒號時，可加雙引號。首頁使用 `permalink: /index.html`，來源檔名不會產生 `/home/` 頁面。404 頁另有 `eleventyExcludeFromCollections` 運作設定。

```md
## Section heading

Normal text, **bold text**, and *italic text*.

### A subsection

- A list item
- Another item

---
```

正文從 `##` 開始，頁面主標題由版型產生。標題與頁尾不自帶分隔線；需要額外區塊留白時在正文另起一段寫 `---`，目前不顯示線條。目前沒有 `eyebrow`、`description` 或首頁標語欄位。

站內連結使用 `url` filter，支援正式根網址、GitHub Pages 子路徑與代理預覽：

```njk
[Lab]({{ '/lab/' | url }})
[CV]({{ '/files/SYLo_CV.pdf' | url }})
```

不要把當次 `revisions/<版本>/` 預覽網址寫進內容，避免下一次發布後連結失效。

### 首頁資料與職稱

全站共用資料集中在 `src/home.md` 的 `website:`。建置設定會讀取它，提供版型使用的 `site` 資料；沒有獨立 `site.json`。以下為部分欄位範例，編輯時保留原有其他項目。

```yaml
website:
  name: Shao-Yuan Lo
  nameChinese: 羅紹元
  roles:
  - role: Assistant Professor
    affiliations:
    - Department of Computer Science and Information Engineering
    - AI Center of Research Excellence
    - National Taiwan University
  social:
  - label: Email
    url: mailto:sylo@csie.ntu.edu.tw
  - label: CV
    url: /files/SYLo_CV.pdf
```

保留 YAML 縮排及清單前的 `-`。每組職稱由 `role` 與一到多個 `affiliations` 組成；複製整組即可增加職稱。職稱及每個所屬單位各自成行。

Email、CV、Google Scholar 等都由 `social` 清單控制，依清單順序顯示。`label` 是文字，`url` 是網址；內部檔案寫 `/files/...`，版型會自動處理路徑。其他頁面的聯絡信箱取自第一個 `mailto:` 連結，因此修改信箱只需改這一處，並保留此連結供聯絡文字使用。

`navigation` 中的 `label` 是選單文字；`url`、`key` 分別對應頁面路徑與 `section`，更改頁面識別時需一起核對。

### News

News 仍以普通 Markdown 清單編輯：

```md
- **Oct 2025** — Message text with **bold text** or [a link](https://example.com).
```

月份直接寫三個英文字母，不另設月份轉換選項。共用版型透過 `datedLists` filter 將日期與內容分組，再由 CSS 排成兩欄；長文字換行留在右欄，連結、粗體與斜體仍可使用。

`<details class="news-more">` 外面的消息一直顯示，裡面的消息可展開收起。**顯示數量由消息放置的位置決定，沒有自動截斷的數量參數。** 新增消息時放在清單頂端，再視需要將較舊的項目移入展開區。

點選 **Show more ↓** 會展開並變為 **Show less ↑**，再次點選收起。這是原生 `details`／`summary` 功能，不需要 JavaScript；文字與箭頭在 `home.md` 的 `summary` 中，外觀沿用 Email 的 `.button`。編輯時保留 `summary` 與結尾 `</details>`。

News、Media Coverage 與 Invited Talks 共用 `.dated-list` 日期清單樣式，集中在 `Dated lists` 註解區塊；其後緊接共用 bullet／編號清單設定，再與其餘共用樣式保留三個空白行。目前列間距為 8px、日期欄至少 6em，並依日期內容自動加寬、欄間距為桌機 16px／手機 12px。

### Honors & Awards、Media Coverage 與 Activities

首頁 `News` 後依序為 `Honors & Awards`、`Media Coverage`。獎項使用一般 Markdown bullet 清單，保留獎項名稱、單位、年份及來源連結；媒體報導使用完整日期，例如 `- **Apr 25, 2026** — Message text.`，沿用共用兩欄清單。

`src/activities.md` 使用預設 `layouts/page.njk`，導覽位於 Publications 與 Teaching 之間；受邀演講在 `## Invited Talks` 下方編輯，使用完整日期（例如 `Mar 03, 2026`），並沿用共用日期欄與間距，沒有 Activities 專用設計值。演講保留題目、場合、主持人及原連結；本地投影片放在 `files/talks/`，使用 `url` filter 連結。

News 的日期維持三字母月份與年份；Media Coverage 與 Invited Talks 則直接在 Markdown 寫成 `Mon DD, YYYY` 完整日期，日數補足兩位。原網頁前兩場演講誤列為 2025，匯入時依投影片標題頁確認為 Mar 2026，註記保留在 `activities.md`。

### Publications

在 `src/publications.md` 對應年份下新增：

```md
### Paper title

First Author, **Shao-Yuan Lo**, Last Author

*Conference or Journal (**ABC**)*, Year · **Oral**

[Paper](https://arxiv.org/pdf/0000.00000) / [arXiv](https://arxiv.org/abs/0000.00000) / [Code](https://github.com/example/project)
```

- 年份由新到舊排列；同年份論文之間只留 Markdown 空行，在該年份最後一篇下方才加 `---`，最後一個年份亦同。Preprints 亦以區塊處理。
- 標題使用 H3。會議／期刊名稱斜體，括號內簡稱粗體，年份在斜體之外。
- 標記寫成 `· **Oral**`、`· **Spotlight**` 等；建置時只有粗體標記文字套用 `--highlight`，前方的 `·` 維持一般文字顏色。
- 連結用 ` / ` 分隔，順序為 `Paper`、`arXiv`，再接 Code、Poster 等。`Paper` 優先使用正式出版 PDF，找不到時用該篇 arXiv PDF；`arXiv` 保留原有論文頁面網址，既有出版社頁面也可能使用此標籤。
- 沒有網址時寫純文字 `Paper / arXiv`，不建立空連結。不加入 BibTeX 欄位、連結或 `.bib` 檔案。
- 新增或更換來源時核對標題、作者、年份與實際 PDF；不要把投影片當作論文 PDF。

`publications.md` 最後的 `## Dissertations` 收錄學位論文，使用共用 H3、作者、學位／學校與年份，資源連結標為 `Thesis`；不加入 BibTeX 或額外圖卡樣式。

[publication-pdf-check.json](docs/publication-pdf-check.json) 是首次匯入時的 PDF 來源與查核紀錄，包含公開 PDF、機構權限及瀏覽器驗證等結果，不能代表後續新增內容已查核。[publication-link-check.json](docs/publication-link-check.json) 是資源連結檢查報告；可在 Actions 手動執行 **Check publication resource links** 更新。此流程也會在相關檢查腳本／workflow 變更時觸發，並可能由 bot 回寫報告到 `main`；單改論文內容不會自動觸發它。

## 設計設定

原則是**變數與選項盡量精簡、統一管理，優先共用及繼承**。內容放 Markdown、結構放版型、外觀放 CSS。新增元件先用既有選項，不為每個數字新增變數，也不為每個分頁複製樣式。

用 CSS 的英文分類註解定位設定；行號會隨編輯移動。順序為色彩／字級、行高／間距與手機覆寫、共用圓角、標題與分隔線、共用容器、導覽列（桌機與手機）、首頁、文字式按鈕、共用日期清單與 News 展開控制、共用 bullet／編號清單，以及其餘共用樣式。

### 色彩

| 變數 | 色碼 | 用途 |
| --- | --- | --- |
| `--white` | `#FFFFFF` | 頁面背景、導覽白字 |
| `--black` | `#000000` | 一般文字、標題、文字式按鈕 |
| `--accent` | `#002D72` | 連結、導覽背景、職稱、日期清單的日期、少量強調與互動 |
| `--accent-light` | `#EAF0F8` | 提示框、程式碼背景與邊框 |
| `--selection-bg` | `#AFC7E8` | 文字選取背景 |
| `--highlight` | `#900C26` | 論文的 Oral、Highlight、Spotlight 等標記 |

共六個色彩變數。一般文字用黑色、主藍背景上的導覽用白字，少部分文字用主藍；不設主要／次要灰階。頁面底色全白，提示框與程式碼區塊共用淺藍。網站不設定 `theme-color`，手機瀏覽器工具列顏色由瀏覽器決定。照片與校徽保留圖片自身色彩。

### 字型與字級

全站字型為 `Inter`、`Noto Sans TC`、`system-ui`、`sans-serif`。英文優先 Inter，中文使用 Noto Sans TC，備援為系統字型。字型檔與授權位於 [src/assets/fonts/](src/assets/fonts/)，透過本地檔案載入並使用 `font-display: swap`。

字重只有 **400** 與 **600**；一般文字 400，Markdown 粗體、H3、文字式按鈕與目前選取的導覽項目為 600。字距與單字間距沿用 `normal`，沒有額外選項。

| 變數 | 桌機 >767px | 手機 ≤767px | 使用位置 |
| --- | --- | --- | --- |
| `--font-size-sm` | 14px | 12px | 頁尾 |
| `--font-size-base` | 16px | 15px | 內文、導覽選單及未另指定的項目 |
| `--font-size-lg` | 18px | 16px | 桌機導覽列姓名、H3／論文標題 |
| `--font-size-xl` | 28px | 24px | 正文 H2、中文姓名 |
| `--font-size-2xl` | 36px | 32px | 首頁英文姓名、分頁主標題 |

### 行高與間距

全站只有 **767px** 一個螢幕寬度斷點。手機在共用變數區集中覆寫，不為各元件另加一套數字。

| 變數 | 桌機 | 手機 | 用途 |
| --- | --- | --- | --- |
| `--line-height-compact` | 1.3 | 1.2 | 標題、職稱與所屬單位、論文相關資訊、導覽 |
| `--line-height-body` | 1.7 | 1.5 | 一般內文、日期清單、Blog、提示框 |
| `--space-xs` | 4px | 4px | 論文標題與相關資訊的下外距 |
| `--space-sm` | 8px | 8px | 職稱組間距、日期清單列間距、部分標題下外距 |
| `--space-md` | 16px | 12px | 段落、欄間距、一般標題下方 |
| `--space-lg` | 24px | 16px | 標題上方、分隔線、手機容器留白 |
| `--space-xl` | 32px | 24px | 共用大間距 |
| `--space-2xl` | 40px | 32px | 桌機容器左右內距、手機正文下內距 |

`margin`、`padding`、`gap` 共用上述間距；`0` 表示不留白，`auto` 用於置中。必要的大尺寸可由既有變數計算，例如桌機正文下內距為 `calc(var(--space-xl) * 2)`。容器寬度、照片寬度、導覽高度等功能尺寸依用途直接設定。

### 標題與分隔線

所有標題使用 compact 行高，上外距均為 `--space-lg`。首頁姓名沿用共用 H1 的內外距，不另設間距例外。

| 元素 | 字級變數 | 字重 | 下外距 |
| --- | --- | --- | --- |
| 首頁姓名／分頁主標題 H1 | `--font-size-2xl` | 400 | `--space-md` |
| 正文 H2 | `--font-size-xl` | 400 | `--space-md` |
| H3 | `--font-size-lg` | 600 | `--space-sm` |
| 論文 H3 | 沿用 H3 | 600 | `--space-xs` |
| H4～H6 | `--font-size-base` | 400 | `--space-sm` |

正文若另寫 H1，預設為 base 字級；一般內容請從 H2 開始，以保持每頁只有一個主標題。論文標題只獨立覆寫下外距，其他設定沿用 H3；作者、會議與資源連結段落使用 compact 行高及 `--space-xs` 下外距。

`.page-heading` 與首頁 `.hero` 共用：上內距 `--space-lg`、左右 0、下內距 `--space-md`；上／左右外距 0、下外距 `--space-md`。列印時共用移除上內距。

Markdown 分隔線 `.prose hr` 使用透明的 1px 線框，不顯示線條，保留原本的上下外距 `--space-lg`（桌機 24px／手機 16px）控制區塊留白；透明線框維持原有留白結構，避免改成零高度後外距合併。相鄰區塊的垂直外距可能合併，實際距離不一定相加。

### 容器與首頁元件

| 項目 | 桌機 | 手機 |
| --- | --- | --- |
| 共用容器最大外寬 | 980px，含左右內距 | 相同上限 |
| 容器左右內距 | 各 40px | 各 16px |
| 正文下內距 | 64px | 32px |
| 頁尾上下內距 | 各 32px | 各 16px |
| 導覽列容器上下內距 | 0 | 0 |
| 每個選單項目最低高度 | 48px | 48px |
| 頭像顯示寬度 | 200px | 100px |

`.header-inner`、`.site-main`、`.footer-inner` 共用容器；各分頁正文使用完整寬度。頁面採垂直 Flex，短頁面頁尾自然位於視窗底部。導覽列容器不設最低高度、上下內距為 0，由 48px 高的選單項目與原生捲動區自然決定高度。導覽列使用 sticky；桌機顯示姓名與選單，姓名不額外加句點；手機（≤767px）隱藏導覽列姓名，選單維持單列，空間不足時可左右滑動，項目不縮小或拆行；支援 Tab 移至選單項目及方向鍵水平捲動，焦點框收在項目內避免被裁切。選取與滑入均使用連結底線，選取項目另用粗體。

首頁桌機版為文字與照片兩欄；手機維持兩欄：左欄依序為姓名、職稱與所屬單位，右欄照片跨越這兩列；聯絡連結放在下方並占滿整列。照片頂端與姓名標題頂端對齊，維持 5:6 比例、`object-fit: cover`，不套用飽和度濾鏡。修改頭像檔名時需核對首頁圖片與共用 metadata 的路徑。

職稱組內段落外距為 0、使用 compact 自然行距；組間距為 `--space-sm`。中文姓名使用 xl 字級；桌機同行，左外距 `--space-md`；手機固定另起一行，左外距為 0，與英文姓名靠左對齊。

`.button` 是共用文字式連結外觀：黑色、600 字重，滑入時主藍加底線；沒有底色、邊框、內距或最低高度。Email、CV 與所有社群連結共用此樣式。News 控制也沿用它，另提供上下箭頭。聯絡連結可自動換行，水平間距 `--space-md`、換行間距 `--space-sm`。

`Shared rectangular corners` 規則緊接間距設定，目前圓角 6px；連結底線距離 4px、粗細 1px。頁尾只有置中的 `© 2026 Shao-Yuan Lo（羅紹元）`；姓名取自首頁資料，年份文字在 `base.njk` 手動維護。

## 預覽與發布

### 固定與快速預覽

**固定入口，持續更新，可加入書籤：**

https://raw.githack.com/shaoyuanlo/codex_test/site-preview/index.html

**當次版本入口：**

```text
https://raw.githack.com/shaoyuanlo/codex_test/site-preview/revisions/<提交版本>/index.html
```

從 [`site-preview/preview.json`](https://github.com/shaoyuanlo/codex_test/blob/site-preview/preview.json) 取得 `stableUrl`、`url`、`sourceCommit`。快速路徑使用來源提交的前 12 碼，不要自行猜測當次網址或把它當作永久入口。

修改 `main` 後，[Update interactive website preview](https://github.com/shaoyuanlo/codex_test/actions/workflows/preview.yml) 會建置、檢查、發布檔案，再檢查公共代理。這是提交後的可操作網站預覽，不是逐字即時更新，也不以圖片代替網站。

| 項目 | 職責 |
| --- | --- |
| `main` | 人工維護的原始碼 |
| `site-preview` | Actions 產生的網站；不手改、不合併回 `main` |
| `_site/` | 一般建置輸出 |
| `_preview/` | 代理預覽建置輸出 |

兩個分支的提交歷史會自然不同，不需為了 ahead／behind 狀態互相合併。固定版導覽指向固定路徑。快速版的頁面、導覽與圖片指向當次版本；每次發布只保留最新版本目錄，舊路徑移除後仍可能因第三方快取暫時可讀取。舊程式碼仍可留在 Git 歷史中。

代理預覽內嵌網站與字型 CSS，字型檔共用固定路徑，以減少請求及版本更新時的重複下載；一般／正式建置使用外部 CSS。預覽加入 `noindex, nofollow`，但這不限制公開存取。儲存庫及其中的公開資源仍可被其他人讀取。

### 快取與線上檢查

發布後會透過 raw.githack 官方 `/purge` 介面清除六個固定分頁的快取。若固定首頁仍讀到舊版，流程會等待後再次清除、重試；遇到 429 或暫時性伺服器錯誤時也會間隔重試並參考 `Retry-After`。

結果見 [`preview-health.json`](https://github.com/shaoyuanlo/codex_test/blob/site-preview/preview-health.json)：

| 欄位 | 意義 |
| --- | --- |
| `sourceCommit` | 本次檢查對應的來源提交，需與 `preview.json` 相符 |
| `checks` | 固定首頁、快速版六個分頁、兩個字型檔及舊路徑的個別結果 |
| 固定首頁的 `currentVersion` | 是否已讀到該次來源版本；200 仍可能是舊快取 |
| `purges` | 固定分頁清除快取的請求結果 |
| `passed` | 所有檢查通過，且固定首頁確實為本次版本 |

清除快取成功不代表每個瀏覽器已刷新；檔案已發布也不代表全部代理檢查通過。重試後仍可能限流或讀到舊版，應查看個別結果。若固定入口尚未更新，可先用已驗證的快速入口；若快速入口限流而固定首頁已驗證為新版，則使用固定入口。

暫時預覽需要儲存庫公開及 Actions 的 `contents: write` 權限，使用工作流程內建權杖，不需另填個人存取權杖。歷史圖片保留在 [docs/preview/](docs/preview/)，不在 README 嵌入或連結圖片作為目前預覽。

### 正式遷移與結束暫時預覽

正式發布需另行在 `shaoyuanlo/shaoyuanlo.github.io` 執行：

1. 保留原網站 Git 歷史、既有內容檔案及 `CNAME`；本專案將論文與投影片集中於 `files/papers/`、`files/talks/`，遷移時同步調整相關連結。將本專案的來源、設定、腳本、依賴鎖檔及 Pages workflow 合併到正式儲存庫，避免覆寫既有資源或重複部署流程。
2. 核對所有舊連結、資源目錄、主分支名稱與自訂網域；建置設定只會複製已列出的資源目錄及存在的 `CNAME`。
3. 在正式儲存庫 **Settings → Pages → Source** 選擇 **GitHub Actions**，確認 **Deploy website to GitHub Pages** 成功。

Pages workflow 會為個人網站儲存庫使用 `/`，其他專案儲存庫使用 `/儲存庫名稱/`。預設分支不是 `main` 時，需一併修改 workflow 觸發分支。正式遷移以該儲存庫實際部署結果為準；保留原網址並不需要保留 `codex_test` 預覽。

結束暫時預覽時，可停用預覽 workflow，再刪除產物分支 `site-preview`；若另有啟用本測試儲存庫的 GitHub Pages，也需取消發布。第三方快取與 Git 歷史不會因此立即消失。本段為操作說明，不代表已執行遷移或移除。

## 開發與驗證

需要 Node.js 22 以上；一般使用者可直接在 GitHub 編輯，以下供開發與雲端任務使用：

```sh
npm ci
npm run dev
```

開發伺服器會顯示本機網址；修改 Markdown、版型或 CSS 後自動重建，Ctrl+C 結束。

```sh
npm run build
npm run check
npm run build:preview
node scripts/check-site.mjs _preview
```

一般建置會先清除 `_site/`，避免刪除的頁面殘留。`check-site.mjs` 檢查 HTML、每頁單一 H1、導覽選取狀態及本地連結／資源，不查核外部網站。代理檢查另由 Actions 中的 `check-proxy-preview.mjs` 執行。

`PATH_PREFIX` 可測試子路徑，`SITE_URL` 控制 canonical／社群 metadata 的網址來源；一般建置預設為 `/` 與 `https://shaoyuanlo.github.io`。例如：

```sh
PATH_PREFIX=/codex_test/ npm run build
npm run check
npm run build
```

最後一個指令恢復根路徑的一般建置。`build:preview` 另產生 `_preview/`、明確的 `index.html` 連結及預覽 metadata，不覆寫 `_site/`。`node_modules/`、`_site/`、`_preview/`、`artifacts/` 是依賴或產物，不編輯、不提交。

| 工作流程 | 位置與用途 |
| --- | --- |
| Deploy website to GitHub Pages | [pages.yml](.github/workflows/pages.yml)：推送 `main` 建置並部署；PR 執行建置與檢查 |
| Update interactive website preview | [preview.yml](.github/workflows/preview.yml)：發布公開代理預覽與線上檢查結果 |
| Check publication resource links | [publication-links.yml](.github/workflows/publication-links.yml)：論文資源網址查核與報告回寫 |
| Refresh official NTU favicon | [ntu-favicon.yml](.github/workflows/ntu-favicon.yml)：需要更新校徽時，從官方來源取得圖片 |

校徽工作流程也會在自身腳本／workflow 修改時觸發，可能由 bot 更新圖片。無關修改保留現有校徽；圖片顏色不受 CSS 色盤控制。

## Codex 協作

使用 **Codex 網頁版 + GitHub 雲端任務 + 同一份 AGENTS.md + 自由開啟的聊天視窗**。不需要預先建立功能固定的 Threads、額外介面 Project、安裝電腦 App 或在使用者電腦 clone。

每次在 Codex 選擇本儲存庫與環境，以 `main` 為基準；可用以下文字開始：

```text
請先讀取根目錄 AGENTS.md、README 與 main 最新內容，再幫我……
```

新聊天不假設能讀到其他聊天或前次未提交的檔案。使用者可能直接在 GitHub 編輯內容與 CSS，因此每次以遠端最新程式碼、文件及 Git 紀錄核對；避免並行工作覆蓋彼此的修改。

溝通、README 與 AGENTS.md 使用繁體中文；網站內容以英文為主，程式碼註解使用簡短英文。每次修改交付時顯示代表性 diff、完整提交或比較連結，以及實際驗證結果。純文件整理不需等待無關的網站部署檢查。

## 來源與歷史紀錄

原網站提供簡介、照片、CV、論文、News 與相關本地資源；後續內容持續由使用者手動更新，實際筆數與內容以來源檔為準。PDF／連結查核 JSON 與 `docs/preview/` 圖片是當時的紀錄，不能當作目前網站已完整驗證的證明。

最初參考包含 [Shih-Hsin Wang](https://shihhsinwang0214.github.io/personal_website/)、[Yaoyao Liu](https://yaoyaoliu.web.illinois.edu/)、[Maria Antoniak](https://maria-antoniak.github.io/) 的學術網站；目前外觀依使用者後續決定的色彩、字型、留白與共用設計規則維護。

後續參考的網站：

- <https://viterbi-web.usc.edu/~yzhao010/index.html>
- <https://limanling.github.io/>
- <https://yulunalexliu.github.io/>
- <https://shaohua0116.github.io/>
- <https://www.csie.ntu.edu.tw/~yvchen/>
- <https://learner.csie.ntu.edu.tw/>
