# DiligenceBinder

**AI-powered evidence binder automation for IBD workpapers.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Domain](https://img.shields.io/badge/Domain-IBD%20Workpapers-1f6feb)](#overview)
[![Review](https://img.shields.io/badge/Review-Human--in--the--loop-orange)](#review-and-export)

## Language / 语言

- [English](#english)
- [中文](#中文)

---

## English

## Overview

DiligenceBinder converts non-standard scanned evidence materials, such as
accounting vouchers, invoices, bank receipts, approval pages, and mixed PDF
attachments, into structured, reviewable workpaper records.

It is designed for investment banking due diligence workflows where source
documents are messy, page order is inconsistent, and manual Excel entry consumes
large amounts of analyst time.

The product idea is simple: turn scattered transaction evidence into a clean
digital binder that analysts can inspect, correct, and export.

## What It Does

| Capability | Description |
| --- | --- |
| Document parsing | Converts scanned PDF pages into Markdown through an AI document parsing API. |
| Page intelligence | Uses an LLM to summarize each page and extract structured fields. |
| Mixed evidence support | Handles vouchers, invoices, bank receipts, approval pages, and attachments in the same PDF. |
| Review workflow | Generates an editable browser review page for human correction. |
| Excel output | Matches voucher, invoice, and payment evidence into an Excel workbook. |
| Configurable rules | Keeps prompts and matching rules editable for different project formats. |

## Why It Matters

IBD workpaper preparation often starts with unstructured evidence: phone photos,
scanned PDFs, inconsistent voucher layouts, invoice attachments, bank receipts,
and approval pages. Analysts need to read every page, identify document types,
copy key fields, and check whether accounting, invoice, and payment evidence
align.

DiligenceBinder automates the repetitive extraction and matching layer while
keeping the final review under human control. The goal is not to remove
judgment, but to turn scattered evidence into a clean review package faster.

## Workflow

```text
Scanned evidence PDFs
        |
        v
Split pages and render previews
        |
        v
AI parsing: PDF page -> Markdown
        |
        v
LLM extraction: Markdown -> structured JSON
        |
        v
Record consolidation
        |
        v
Editable review page
        |
        v
Reviewed CSV
        |
        v
Voucher + invoice + bank receipt matching
        |
        v
Matched Excel workbook
```

## Extracted Fields

| Document type | Fields |
| --- | --- |
| Accounting voucher | voucher number, accounting date, company name, summary, amount |
| Invoice | invoice number, invoice date, seller name, total amount |
| Bank receipt | receipt number, transaction date, transaction amount |

## Architecture

| Layer | Implementation |
| --- | --- |
| PDF processing | PyMuPDF for page splitting and review preview rendering |
| Document parsing | TextIn `pdf_to_markdown` API |
| Field extraction | DeepSeek chat completions for page-level summarization and JSON extraction |
| Review interface | Static editable HTML generated from intermediate records |
| Matching and export | OpenPyXL workbook generation |
| Desktop entry point | Tkinter launcher for non-technical users |

## Review and Export

The review page is intentionally part of the pipeline. It allows reviewers to
inspect page images, correct extracted fields, delete false records, and add
missing records before exporting the final CSV.

The matching script then applies document-level rules to produce an Excel
workbook for downstream workpaper preparation.

## Installation

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

## API Keys

Copy `.env.example` to `.env` and fill in your own credentials:

```bash
cp .env.example .env
```

```env
TEXTIN_APP_ID=your_textin_app_id
TEXTIN_SECRET_CODE=your_textin_secret_code
DEEPSEEK_API_KEY=your_deepseek_api_key
```

`.env` is ignored by git and should never be committed.

## Usage

### 1. Extract Records

```bash
python pipeline_items.py --dirs /path/to/pdf_folder --output output_items
```

Output:

```text
output_items/
├── 单据明细.xlsx
├── {pdf_name}/
│   ├── intermediate.json
│   └── pages/
│       ├── p1_markdown.md
│       └── p1_deepseek.json
```

### 2. Generate Review Page

```bash
python build_review_html.py
```

Open `output_items/审核页面.html`, review and edit the extracted records, then
export `审核结果.csv` from the page.

### 3. Match Evidence and Export Excel

```bash
python match_and_export.py /path/to/审核结果.csv
```

This writes `匹配结果.xlsx` next to the CSV file.

### 4. Desktop Launcher

```bash
python launcher.py
```

## Customization

The extraction prompts and matching rules are kept in code so teams can adapt
the workflow to different voucher layouts, naming conventions, and workpaper
templates.

The default filename-based category rule labels filenames containing `销`, `研`,
or `管` as sales, R&D, or management expense. Adjust `match_and_export.py` if
your project uses a different convention.

## Repository Scope

This open-source version contains reusable pipeline code only. It does not
include real financial documents, parsed Markdown/JSON outputs, review CSV
files, Excel workpapers, screenshots, API keys, or private business data.

## Privacy Notice

Do not commit real financial documents, extracted outputs, screenshots, review
CSV files, Excel workbooks, or `.env` files. These files may contain company
names, bank accounts, invoice numbers, approver names, and transaction details.

## License

MIT

---

## 中文

## 项目概览

DiligenceBinder 是一套面向投行 IBD 底稿整理场景的 AI 证据材料结构化工具。

它可以将非标准化扫描底稿材料，例如记账凭证、发票、银行水单、审批页和混合 PDF
附件，转换为可复核、可修改、可导出的结构化底稿记录。

它适用于尽调和底稿整理中常见的复杂材料场景：原始文件格式不统一、页面顺序不固定、
同一 PDF 内混合多类证据、人工逐页录入 Excel 成本高且容易出错。

这个项目的核心产品思路是：把分散的交易证据整理成一份清晰、可复核、可导出的数字化
底稿证据册。

## 项目能力

| 能力 | 说明 |
| --- | --- |
| 文档解析 | 通过 AI 文档解析接口将扫描 PDF 页面转换为 Markdown。 |
| 页面理解 | 使用大模型逐页归纳页面内容并提取结构化字段。 |
| 混合材料支持 | 支持同一 PDF 内混合出现记账凭证、发票、银行水单、审批页及附件。 |
| 人工复核流程 | 生成可编辑浏览器审核页，保留人工修正和补录环节。 |
| Excel 导出 | 将凭证、发票、水单匹配后导出 Excel 底稿表。 |
| 规则可配置 | 提示词和匹配规则可调整，适配不同项目底稿口径。 |

## 项目价值

IBD 底稿整理经常从非结构化证据开始：拍照件、扫描 PDF、格式不统一的记账凭证、发票
附件、银行回单和审批页。分析师需要逐页识别材料类型、复制关键字段，并核对记账、
开票、付款证据是否匹配。

DiligenceBinder 自动化处理重复性的识别、提取和匹配步骤，同时保留人工最终复核。它的
目标不是替代判断，而是更快地把分散证据整理成清晰、可追溯的底稿包。

## 处理流程

```text
扫描底稿材料 PDF
        |
        v
拆分页面并生成预览
        |
        v
AI 解析：页面转 Markdown
        |
        v
大模型提取：Markdown 转结构化 JSON
        |
        v
单据级记录汇总
        |
        v
可编辑审核页面
        |
        v
人工复核后的 CSV
        |
        v
凭证、发票、水单匹配
        |
        v
匹配后的 Excel 底稿表
```

## 提取字段

| 材料类型 | 字段 |
| --- | --- |
| 记账凭证 | 凭证编号、记账日期、公司名称、摘要、金额 |
| 发票 | 发票号码、开票日期、销售方名称、价税合计 |
| 银行水单 / 回单 | 回单编号、交易日期、交易金额 |

## 技术架构

| 层级 | 实现 |
| --- | --- |
| PDF 处理 | PyMuPDF 拆分页面并渲染审核预览图 |
| 文档解析 | TextIn `pdf_to_markdown` 接口 |
| 字段提取 | DeepSeek chat completions 逐页总结并输出 JSON |
| 人工复核 | 基于中间结果生成可编辑静态 HTML |
| 匹配导出 | OpenPyXL 生成 Excel 结果表 |
| 桌面入口 | Tkinter 图形界面，降低非技术用户使用门槛 |

## 人工复核与导出

审核页是流程中的关键环节。复核人员可以查看页面图片、修正提取字段、删除误识别记录、
补录缺失单据，再导出最终 CSV。

匹配脚本会基于复核后的单据记录执行匹配规则，并生成后续底稿整理可用的 Excel 表。

## 安装

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

## API Key 配置

复制 `.env.example` 为 `.env`，并填入你自己的 API Key：

```bash
cp .env.example .env
```

```env
TEXTIN_APP_ID=your_textin_app_id
TEXTIN_SECRET_CODE=your_textin_secret_code
DEEPSEEK_API_KEY=your_deepseek_api_key
```

`.env` 已被 `.gitignore` 忽略，不应提交到仓库。

## 使用方式

### 1. 提取单据记录

```bash
python pipeline_items.py --dirs /path/to/pdf_folder --output output_items
```

输出：

```text
output_items/
├── 单据明细.xlsx
├── {pdf_name}/
│   ├── intermediate.json
│   └── pages/
│       ├── p1_markdown.md
│       └── p1_deepseek.json
```

### 2. 生成审核页面

```bash
python build_review_html.py
```

打开 `output_items/审核页面.html`，复核并修改提取结果，然后从页面导出
`审核结果.csv`。

### 3. 匹配证据并导出 Excel

```bash
python match_and_export.py /path/to/审核结果.csv
```

程序会在 CSV 同目录下生成 `匹配结果.xlsx`。

### 4. 图形界面

```bash
python launcher.py
```

## 自定义

提示词和匹配规则保留为可调整形式，方便根据不同企业凭证格式、文件命名规则和底稿模板
进行定制。

默认文件名分类规则会将包含 `销`、`研`、`管` 的文件分别标记为销售费用、研发费用、
管理费用。如果项目底稿命名口径不同，可在 `match_and_export.py` 中调整。

## 仓库范围

当前开源版本只包含可复用的程序代码，不包含真实财务材料、解析生成的 Markdown/JSON、
审核 CSV、Excel 底稿、截图、API Key 或任何私有业务数据。

## 隐私提示

请勿提交真实财务文件、解析输出、截图、审核 CSV、Excel 工作簿或 `.env` 文件。这些文件
可能包含公司名称、银行账号、发票号码、审批人姓名和交易明细。

## 开源协议

MIT
