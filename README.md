# Shao-Yuan Lo · Academic website

A small, English-first academic website with five separate pages, a sticky navigation bar, and a mobile layout. Content is plain **Markdown**. There is no CMS, database, or client-side JavaScript; pages and navigation also work with JavaScript disabled.

Built with [Eleventy](https://www.11ty.dev/) and deployed as static HTML to GitHub Pages. No paid service, API key, or custom domain is required.

## 網站預覽

目前使用 raw.githack 提供可操作的多頁網站預覽，可點擊導覽、閱讀文章、開啟 CV，並以手機瀏覽。預覽來自公開的 `codex_test` 儲存庫，不會取代正式網站 `https://shaoyuanlo.github.io/`。

**固定預覽網址（持續更新，可加入書籤）：**

https://raw.githack.com/shaoyuanlo/codex_test/site-preview/index.html

每次發布都會更新固定網址的頁面及資源；導覽使用固定路徑，不依賴可能被移除的版本目錄。代理與瀏覽器快取可能使更新延後出現；若要立即確認當次修改，請使用以下快速版本預覽。

**快速版本預覽（每次發布產生新網址）：**

```text
https://raw.githack.com/shaoyuanlo/codex_test/site-preview/revisions/<提交版本>/index.html
```

開啟 [`site-preview` 分支的 `preview.json`](https://github.com/shaoyuanlo/codex_test/blob/site-preview/preview.json)，複製 `url` 即可取得最新快速預覽；`stableUrl` 則是固定入口。也可在 [Update interactive website preview 工作流程](https://github.com/shaoyuanlo/codex_test/actions/workflows/preview.yml) 的建置輸出中找到 `Fixed preview:` 與 `Interactive preview:` 兩個網址。

快速預覽的頁面、導覽與資源都指向同一版本目錄，以避開舊快取。發布目錄只保留當次版本；舊版本目錄會在下次發布時移除，舊網址可能暫時因快取仍可讀取，快取到期後通常回傳 404，不會自動切換到新版。固定網址持續保留及更新。舊版本仍可留存在 Git 提交歷史中。

更新流程：修改 **`main` 分支**並提交 → 等待上述工作流程成功 → 開啟固定網址，或從 `preview.json` 取得最新快速預覽。這是提交後的自動建置預覽，不是逐字即時更新。`main` 是手動維護的原始碼，`site-preview` 是自動產生的網站，請勿手動編輯或將其合併回 `main`。

工作流程會檢查固定入口可讀取、快速預覽來源版本、導覽連結、樣式與字型，並確認舊的 `/publication/` 路徑回傳 404；結果保存在 [`preview-health.json`](https://github.com/shaoyuanlo/codex_test/blob/site-preview/preview-health.json)。固定入口的 `currentVersion` 可辨識是否仍命中舊快取。代理預覽需要儲存庫維持公開，且 GitHub Actions 具有 `contents: write` 權限，不需要另外設定個人存取權杖。

歷史預覽圖片原檔保留在 `docs/preview/`，作為歷史紀錄，不代表目前網站樣式；此處不再嵌入或連結圖片。

## 日常更新：只需修改文字

不需要修改版型，也不需要在電腦安裝軟體。網站部署完成後，在 GitHub 開啟以下檔案 → 按鉛筆編輯 → Commit 到 `main`，GitHub Actions 就會自動重新發布。建置失敗時不會覆蓋上一次成功發布的網站。

| 要更新的內容 | 修改的檔案 |
| --- | --- |
| Home 簡介、研究方向、最新消息 | [`src/index.md`](src/index.md) |
| Lab 介紹、成員、招生資訊 | [`src/lab.md`](src/lab.md) |
| 論文清單 | [`src/publications.md`](src/publications.md) |
| 課程與教材 | [`src/teaching.md`](src/teaching.md) |
| 新增文章 | 在 [`src/posts/`](src/posts/) 新增 `.md` 檔案 |
| 姓名、職稱、學校、Email、社群連結、首頁標語 | [`src/_data/site.json`](src/_data/site.json) |
| 首頁按鈕文字 | [`src/_includes/layouts/home.njk`](src/_includes/layouts/home.njk) |
| 各頁標題下方的簡介 | 各頁頂端 `intro:` 欄位 |
| 個人照片 | 替換 `src/assets/portrait.jpg`（建議 5:6 比例） |
| 瀏覽器分頁圖示／台大校徽 | [`src/assets/ntu-emblem.png`](src/assets/ntu-emblem.png) |
| CV | 替換 `files/SYLo_CV.pdf`，檔名保留即可 |
| 配色、字體、間距 | [`src/assets/style.css`](src/assets/style.css) 開頭的變數 |

導覽列尺寸也在 `src/assets/style.css`：`.header-inner` 的 `min-height` 設定最低高度（桌機 `50px`、手機 `80px`）。選單使用一般內文字級（桌機 `16px`、手機 `15px`），左側姓名使用大一級文字（桌機 `18px`、手機 `16px`）；窄螢幕時選單可自動換行，實際高度也會受內距及內容影響。

字級選項集中在 CSS 上方 `:root` 的顏色設定之後，緊接著的手機 `:root` 在螢幕寬度不超過 `767px` 時覆寫同一組變數。各元素透過 `var(...)` 使用，避免另寫零散字級：

| 字級變數 | 桌機 | 手機（≤767px） | 使用位置 |
| --- | --- | --- | --- |
| `--font-size-sm` | `14px` | `12px` | 頁尾資訊 |
| `--font-size-base` | `16px` | `15px` | 一般內文、導覽選單，以及未特別指定的項目 |
| `--font-size-lg` | `18px` | `16px` | 導覽列左側姓名、論文標題 |
| `--font-size-xl` | `28px` | `24px` | 區塊標題（內容中的 `h2`） |
| `--font-size-2xl` | `36px` | `32px` | 首頁英文姓名、各分頁及 Blog 文章主標題 |

行高與共用間距變數集中在字級與內容容器設定之間，桌機、手機共用：

| 變數 | 數值 | 用途 |
| --- | --- | --- |
| `--line-height-heading` | `1.3` | 一般標題（H1、H2、H3 等） |
| `--line-height-compact` | `1.5` | 論文標題及相關資訊（作者、會議、連結）、導覽列 |
| `--line-height-body` | `1.7` | 一般內文、Blog、提示框 |
| `--space-sm` | `8px` | 標題緊接內容、相關資訊、清單項目 |
| `--space-md` | `16px` | 段落之間、一般標題下方 |
| `--space-lg` | `24px` | 手機容器左右內距、頁尾上下內距 |
| `--space-xl` | `32px` | 區塊之間、標題上方、桌機頁尾上下內距 |
| `--space-2xl` | `40px` | 桌機容器左右內距、手機正文下方內距 |

所有非零固定 `margin` 均使用上述間距變數；`0` 保留給不需留白的元素，`auto` 用於容器置中。手機不再個別覆寫外距與行高。`padding`（內距）與 `gap`（排列間隔）也共用這五個變數，大區塊可用 `calc(var(--space-xl) * 2)` 取得 64px。容器左右內距也引用對應的間距變數；照片寬度、導覽列高度等具有明確用途的尺寸另行保留。

其他共用樣式：矩形元件圓角統一 `3px`（狀態圓點保留圓形），連結底線距離統一 `4px`、粗細 `1px`，箭頭尺寸統一 `1em` 並隨字級縮放。這些共用規則直接集中設定，不另外增加變數。全站字距及單字間距使用預設 `normal`。

整頁使用垂直 Flex 排版，`body` 最低高度 `100vh`，正文 `.site-main` 使用 `flex: 1` 撐滿剩餘空間，短頁面的頁尾自然位於視窗底部，不再用固定數字扣除導覽與頁尾高度。手機只保留字級、容器左右內距、導覽排列及照片欄位等必要調整。

字重只使用 **400（一般）**與 **600（粗體）**，預設 400。Markdown 的 `**粗體文字**`、HTML 的 `strong`／`b`、目前導覽頁面的強調狀態等使用 600。正文、提示框、程式碼、中文姓名、社群連結等未指定項目皆使用一般內文字級（桌機 16px／手機 15px）；頁尾繼承小字級（桌機 14px／手機 12px）。

各分頁（含首頁與 Blog 文章）共用置中的 `.site-main` 內容容器，與導覽列、頁尾統一最大外寬 `980px`（含左右內距）；正文、標題簡介與段落不再另設較窄的最大寬度，文字可使用完整的容器寬度。桌機左右內距各 `40px`；≤767px 時左右內距統一各 `24px`。正文下方內距為桌機 `64px`、手機 `40px`；頁尾上下內距為桌機各 `32px`、手機各 `24px`。容器設定集中在 CSS 上方、字級設定之後。只有 `767px` 一個螢幕寬度斷點，原有 `800px` 規則已移除。首頁照片旁的文字仍依原有欄位排列。

全站字型統一由 `style.css` 的 `--font: "Inter", "Noto Sans TC", system-ui, sans-serif` 設定：英文優先使用 Inter，中文使用 Noto Sans TC，載入失敗或缺字時使用系統預設字型。標題、內文、導覽、中文姓名與程式碼都沿用這一組字型；字級限用上述五項，字重限用 400／600。原本的 `--serif`、`--sans` 已移除。字型檔存於 `src/assets/fonts/`，以分段 WOFF2 按需載入，採 `font-display: swap`，不依賴外部字型 CDN；來源版本及授權分別保存在 `sources.json` 與各字型目錄的 `LICENSE.txt`。

配色維持白色頁面背景、黑色一般文字、主藍互動與少量強調文字。導覽橫幅使用主藍底、白字，深藍按鈕也使用白字；首頁職稱、提示框標籤及消息日期沿用主藍。提示框與程式碼區塊恢復淺藍背景，分隔線與邊框共用這個淺藍色。文字反白使用較深的藍底，搭配黑字。介面文字僅使用黑、白、主藍三色。

介面配色集中在 `style.css` 開頭的 `:root`：

| 設定 | 色碼 | 用途 |
| --- | --- | --- |
| `--white` | `#FFFFFF` | 頁面背景、導覽與按鈕白字、導覽選取底線及鍵盤焦點標示 |
| `--black` | `#000000` | 大多數一般文字、標題、日期、圖片說明、反白文字 |
| `--accent` | `#002D72` | 連結、導覽背景、按鈕底色、少量強調文字及頁面鍵盤焦點標示 |
| `--accent-hover` | `#00245B` | 按鈕滑過時的底色 |
| `--accent-light` | `#EAF0F8` | 提示框與程式碼區塊背景、分隔線與邊框 |
| `--selection-bg` | `#AFC7E8` | 滑鼠或觸控選取文字時的反白底色 |

共 **6 個色彩變數、6 種實際顏色**；邊框與提示背景共用色碼，文字不設主要／次要灰階。網站不設定 `theme-color`，讓手機瀏覽器自行決定工具列顏色；網站內的導覽列仍為主藍色。列印背景沿用 `--white`。照片與校徽的顏色來自圖片檔本身，不由這些 CSS 變數控制。

這份版本帶入原網站的簡介、照片、CV、Publications 區塊的全部 29 篇論文（2018–2026 年）與部分消息。Lab 成員、課程內容保留待填；Blog 目前有一篇明確標示 Example 的示範文章，正式上線前可替換或刪除。沒有虛構學生、課程或研究成果。原網站論文使用的 49 個本地資源檔（BibTeX、海報與投影片）也已帶入 `papers/`、`talks/`，不依賴舊網站的檔案路徑。

### Markdown 基本格式

```md
## Section heading
### Paper or course title

Normal text, **bold text**, and *italic text*.

[Link label](https://example.com)

- A list item
- Another item
```

頁面頂端兩條 `---` 之間是設定欄位（front matter）。請保留 `layout`、`section` 和 `permalink`；主要文字直接寫在第二條 `---` 下面。標題或簡介含冒號時請加雙引號，例如 `title: "Research: new directions"`。JSON 檔案請保留雙引號與逗號格式。

站內連結請使用下列格式，讓主網址與測試子路徑皆可運作：

```njk
[Lab]({{ '/lab/' | url }})
[A PDF]({{ '/files/filename.pdf' | url }})
```

### 新增論文

在 `src/publications.md` 相應年份下方複製這個區塊，不需要修改 HTML。論文標題後的作者、會議與連結段落統一使用 `1.5` 行高、`8px` 下方外距；第一篇論文標題之前的頁面說明維持一般內文設定。同年份的論文只以 Markdown 空行分開，只有該年份最後一篇的連結下方才加 `---`（最後一個年份也一樣）。資源連結用 ` / ` 分隔：

```md
### Paper title

First Author, **Shao-Yuan Lo**, Last Author

*Conference or Journal, Year*

[Paper](https://example.com/paper) / [Code](https://github.com/example/project)
```

若這篇是該年份最後一篇，在其後另起一段加入 `---`。

### 新增 Blog 文章

在 `src/posts/` 新增 `your-article-title.md`：

```md
---
title: Your article title
date: 2026-10-23
description: A short summary shown in the Blog list.
category: Research notes
published: true
---

Your article starts here.

## A section

More text.
```

文章會自動出現在 Blog，按日期由新到舊排列，網址為 `/blog/your-article-title/`。將 `published` 改為 `false` 可保留草稿：不產生文章頁，也不顯示於清單。日期請換成實際發布日期；未來日期不會自動排程，而是依 `published` 決定是否發布。沒有文章時，Blog 會自動顯示簡短空白狀態。

`src/posts/research-notes.md` 是現成範例。正式使用時請刪除 `example: true` 並替換內容。已發布文章的檔名決定網址，請盡量不要變更，以免既有連結失效。

## Local development

Requires Node.js 22 or newer. Use the existing checkout; a Git worktree is unnecessary.

```sh
npm ci
npm run dev
```

The development server reports its local address. Editing Markdown, templates, or CSS rebuilds the site automatically. Stop with Ctrl+C.

```sh
npm run build
npm run check
```

`_site/` contains the generated website; do not edit it. The check validates all generated pages, the main navigation, and local links/assets. It does not check external services. Production uses the same pinned dependencies through `package-lock.json`.

To test a project-site subpath:

```sh
PATH_PREFIX=/codex_test/ npm run build
npm run check
npm run build
```

The final command restores the root-path build. `SITE_URL` optionally overrides the canonical/social URL origin; its default is `https://shaoyuanlo.github.io`.

Build and check the raw-file proxy preview separately:

```sh
npm run build:preview
node scripts/check-site.mjs _preview
```

`_preview/` is generated output. Preview links use explicit `index.html` filenames and the proxy path, so all pages work without a directory-index server. `_site/` and the production URL configuration are not modified by this preview build.

## 保留 https://shaoyuanlo.github.io/

**這次的實作位於 `codex_test` 儲存庫，尚未修改或發布目前的正式網站。** 正式網址對應的是 `shaoyuanlo/shaoyuanlo.github.io`；僅發布到 `codex_test` 不會取代原網址，而會是 `/codex_test/` 的測試網站。

確認版面後，在原本的 **`shaoyuanlo.github.io` 儲存庫**使用這份框架：

1. 先保留原網站的 Git 歷史或建立備份分支。把這份專案的 `src/`、`files/SYLo_CV.pdf`、`scripts/`、`eleventy.config.js`、`package.json`、`package-lock.json`、`.gitignore`、`.github/workflows/pages.yml` 和這份說明加入正式儲存庫。**不要複製 `.git`、`node_modules` 或 `_site`。** 若正式儲存庫已有相同檔案或部署 workflow，先合併並確認只有一個發布流程。
2. **保留原本的 `papers/`、`talks/` 和 `files/` 檔案**，避免舊的論文、投影片、照片與 CV 連結失效。這份測試專案只包含一份 CV，沒有搬入所有舊檔案。確認同名 CV 的版本再替換。
3. 建置會自動將存在的 `files/`、`papers/`、`talks/` 與 `CNAME` 複製至 `_site`。若原網站另有其他公開資源目錄，請在 `eleventy.config.js` 的 `addPassthroughCopy` 中加入，再確認舊連結仍可開啟。
4. 到正式儲存庫 **Settings → Pages → Build and deployment → Source** 選擇 **GitHub Actions**。
5. 把變更合併至 `main`（若預設分支不同，先修改 workflow 的兩個分支設定），查看 Actions 中的 **Deploy website to GitHub Pages** 是否成功。

Workflow 會自動辨識個人網站並使用 `/` 作為根路徑，因此 **Home 就是原本主網址**。其他頁面是 `/lab/`、`/publications/`、`/teaching/`、`/blog/`，不是首頁錨點。正式網址不需更換。若正式網站有既有 `CNAME`，請保留並設定對應的 `SITE_URL`，不要意外換掉自訂網域。

程式碼與預覽圖片保存在此儲存庫。這與正式網站的發布是兩件事；`shaoyuanlo.github.io` 的原網站尚未被這份框架取代。GitHub Actions 工作流程需在目標儲存庫上實際執行成功後，才算完成正式發布。

## Design & accessibility

- Pure white backgrounds, black text, navy links and buttons, and one shared Inter / Noto Sans TC font stack with system fallbacks. Fonts are self-hosted; no external font CDN is required.
- All five navigation links remain visible on mobile, in a sticky two-row header.
- Semantic headings, a keyboard skip link, visible focus indicators, and active-page announcements.
- Responsive images, print styles, canonical URLs, social metadata, and a custom 404 page.
- Shared layouts keep changes consistent across all pages; content remains in Markdown.

The profile photo, CV, biography, links, news, and all 29 publication entries and their linked local resources were sourced from the existing `shaoyuanlo.github.io` repository. The design takes cues from the restrained academic presentation and warm palette in the accessible Shih-Hsin Wang reference source. The other two reference sites were inaccessible from this environment; their layouts were not verified.

The favicon is the original NTU emblem image from [National Taiwan University's official website](https://www.ntu.edu.tw/images/favicon/apple-touch-icon.png), copied without modification. Its source is recorded in `src/assets/ntu-emblem-source.json`. The **Refresh official NTU favicon** workflow can refresh the source asset; the university emblem is independent of the site's CSS accent color.
