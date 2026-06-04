# DiligenceBinder

AI-powered evidence binder automation for IBD workpapers.

面向投行 IBD 底稿整理场景的 AI 证据材料结构化工具。

`DiligenceBinder` turns non-standard scanned supporting documents, such as
accounting vouchers, invoices, bank receipts, and mixed PDF attachments, into
reviewable structured data for investment banking due diligence and workpaper
preparation.

`DiligenceBinder` 可以将非标准化扫描底稿材料，例如记账凭证、发票、银行水单、
审批附件和混合 PDF，转换成可复核、可修改、可导出的结构化底稿数据。

The name reflects the product idea: a digital binder that organizes scattered
transaction evidence into a structured, reviewable workpaper package.

项目名里的 `Binder` 指的是“底稿证据册”：把分散、非标准、顺序不固定的交易证据
整理成一个可复核的结构化底稿包。

## Why This Project / 项目背景

In IBD projects, supporting documents are often collected as photos or scanned
PDFs. They are usually non-standard, page order varies, and a single PDF may mix
vouchers, invoices, bank receipts, approvals, and attachments.

在 IBD 项目中，底稿支持文件经常来自拍照件或扫描 PDF。材料格式不统一、页面顺序不
固定，同一个 PDF 里可能混有记账凭证、发票、银行水单、审批单和其他附件。

Manual work usually means opening each PDF, reading every page, copying voucher
numbers, invoice numbers, dates, counterparties, and amounts into Excel, then
checking whether voucher, invoice, and payment evidence match.

传统处理方式通常需要人工逐页打开 PDF，识别并复制凭证号、发票号、日期、交易对手、
金额等字段，再在 Excel 中核对凭证、发票、水单之间是否匹配。

This project automates the repetitive part while keeping a human review step in
the loop.

本项目自动化处理其中重复、机械、耗时的部分，同时保留人工复核和修改环节，适合对
准确性和可追溯性要求较高的底稿整理流程。

## Core Capabilities / 核心能力

- Convert scanned PDF pages into Markdown through an AI document parsing API.
- Extract structured fields page by page with an LLM.
- Support mixed document types in the same PDF.
- Generate an editable browser review page.
- Allow reviewers to correct, delete, or create document records manually.
- Export reviewed CSV data.
- Match vouchers, invoices, and bank receipts into an Excel workbook.
- Provide a Tkinter launcher for non-technical users.

- 通过 AI 文档解析接口将扫描 PDF 页面转换为 Markdown。
- 使用大模型逐页归纳、识别并提取结构化字段。
- 支持一个 PDF 中混合出现多类材料。
- 生成可编辑的浏览器审核页面。
- 支持人工修改、删除、新增单据条目。
- 导出审核后的 CSV。
- 根据规则将记账凭证、发票、银行水单匹配并输出 Excel。
- 提供 Tkinter 图形界面，方便非技术用户使用。

Supported document types include:

支持的主要材料类型包括：

| English | 中文 |
| --- | --- |
| Accounting vouchers | 记账凭证 |
| Invoices | 发票 |
| Bank receipts | 银行水单 / 银行回单 |
| Approval pages and attachments | 审批页及其他附件 |

## Pipeline / 处理流程

```text
Scanned PDFs / 扫描 PDF
  |
  |-- split PDF into pages / 拆分页面
  |-- document parsing: PDF page -> Markdown / 页面转 Markdown
  |-- LLM extraction: Markdown -> structured JSON / 大模型提取字段
  |-- consolidation: page records -> document-level records / 汇总单据记录
  |-- human review: editable HTML page / 人工复核页面
  |-- export: reviewed CSV / 导出审核结果
  |-- matching rules: voucher + invoice + bank receipt / 匹配凭证、发票、水单
  |
Matched Excel workbook / 匹配后的 Excel 底稿表
```

The current implementation uses:

当前实现主要使用：

- TextIn `pdf_to_markdown` for document-to-Markdown conversion.
- DeepSeek chat completions for page-level summarization and field extraction.
- PyMuPDF for PDF page processing and review image rendering.
- OpenPyXL for Excel output.

- TextIn `pdf_to_markdown`：将扫描件解析为 Markdown。
- DeepSeek chat completions：逐页归纳并提取结构化字段。
- PyMuPDF：处理 PDF 页面和审核页图片渲染。
- OpenPyXL：生成 Excel 输出。

## Extracted Fields / 提取字段

| Document type | Fields |
| --- | --- |
| Accounting voucher | voucher number, accounting date, company name, summary, amount |
| Invoice | invoice number, invoice date, seller name, total amount |
| Bank receipt | receipt number, transaction date, transaction amount |

| 材料类型 | 字段 |
| --- | --- |
| 记账凭证 | 凭证编号、记账日期、公司名称、摘要、金额 |
| 发票 | 发票号码、开票日期、销售方名称、价税合计 |
| 银行水单 / 回单 | 回单编号、交易日期、交易金额 |

The prompts and matching rules are intentionally editable so teams can adapt the
pipeline to different workpaper formats and document naming conventions.

提示词和匹配规则保留为可编辑形式，方便根据不同项目、不同企业、不同底稿命名规则进行
调整。

## Install / 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure API Keys / 配置 API Key

Copy `.env.example` to `.env` and fill in your own keys:

复制 `.env.example` 为 `.env`，并填入你自己的 API Key：

```bash
cp .env.example .env
```

```env
TEXTIN_APP_ID=your_textin_app_id
TEXTIN_SECRET_CODE=your_textin_secret_code
DEEPSEEK_API_KEY=your_deepseek_api_key
```

`.env` is ignored by git.

`.env` 已被 `.gitignore` 忽略，不会进入 Git 仓库。

## Usage / 使用方式

### 1. Extract Fields / 提取字段

```bash
python pipeline_items.py --dirs /path/to/pdf_folder --output output_items
```

Output / 输出：

```text
output_items/
├── 单据明细.xlsx
├── {pdf_name}/
│   ├── intermediate.json
│   └── pages/
│       ├── p1_markdown.md
│       └── p1_deepseek.json
```

### 2. Generate Review Page / 生成审核页面

```bash
python build_review_html.py
```

Open `output_items/审核页面.html`, review the extracted fields, then export
`审核结果.csv` from the page.

打开 `output_items/审核页面.html`，人工复核字段后，从页面导出 `审核结果.csv`。

### 3. Match and Export Excel / 匹配并导出 Excel

```bash
python match_and_export.py /path/to/审核结果.csv
```

This writes `匹配结果.xlsx` next to the CSV file.

程序会在 CSV 同目录下生成 `匹配结果.xlsx`。

The matcher includes a default filename-based category rule: filenames
containing `销`, `研`, or `管` are labeled as sales, R&D, or management expense.
Adjust `match_and_export.py` if your voucher naming convention is different.

匹配脚本包含一个默认的文件名分类规则：文件名包含 `销`、`研`、`管` 时，会分别标记为
销售费用、研发费用、管理费用。如果你的底稿命名规则不同，可以在
`match_and_export.py` 中调整。

### GUI Launcher / 图形界面

```bash
python launcher.py
```

## Repository Scope / 仓库范围

This open-source version contains the reusable pipeline code only. It does not
include real financial documents, extracted Markdown/JSON outputs, workpaper
files, API keys, or private business data.

当前开源版本只包含可复用的程序代码，不包含真实财务材料、真实解析结果、底稿文件、
API Key 或任何私有业务数据。

## Resume Summary / 简历表述

Suggested resume wording:

英文简历可写：

> Built DiligenceBinder, an AI-powered IBD workpaper automation tool that turns
> non-standard scanned vouchers, invoices, and bank receipts into structured
> evidence records, performs page-level LLM extraction, supports
> human-in-the-loop review, and exports matched Excel tables for due diligence
> workflows.

中文简历可写：

> 开发 DiligenceBinder，一套面向 IBD 底稿整理的 AI 证据材料结构化工具，可将非标准化
> 扫描凭证、发票及银行水单转换为结构化证据记录，支持逐页大模型提取、人工复核修改、
> 凭证-发票-水单匹配及 Excel 底稿表导出。

## Important Privacy Notice / 隐私提示

Do not commit real financial documents, extracted JSON/Markdown, screenshots,
CSV review files, or Excel outputs. They may contain company names, bank
accounts, invoice numbers, approval names, and transaction details.

请勿提交真实财务文件、解析生成的 JSON/Markdown、截图、审核 CSV 或 Excel 输出。这些
文件可能包含公司名称、银行账号、发票号码、审批人姓名和交易明细。

## License / 开源协议

MIT
