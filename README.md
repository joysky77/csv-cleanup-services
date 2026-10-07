# Small CSV cleanup — checked output and a reusable script

Have a CSV export with stray spaces, duplicate records or broken Chinese characters? A small, fixed-scope cleanup can include the cleaned file, a reproducible Python script and a before/after report.

**US$25 proposed fixed price:** one CSV, up to 20,000 rows and 20 columns, UTF-8 or GB18030 input, surrounding whitespace cleanup and an agreed duplicate rule. One correction within the agreed scope is included. File-specific scope and turnaround are confirmed before accepting an order.

The demonstration uses fictional records. It preserves leading-zero identifiers, quoted commas, Chinese text and separate orders belonging to the same customer. Spreadsheet formula-like cells become inert text. It refuses to overwrite source or output files.

The included demonstration implements exact duplicates across all columns. A different duplicate key needs an agreed specification and verification; it is not automatically implemented by this sample.

## Request a quote

Open an issue with the approximate row/column counts, input encoding if known, desired transformation, duplicate rule and deadline. Use fictional examples only in public issues. Do not upload private customer files, credentials or payment details. Private sample exchange and data handling must be agreed separately.

No payment is requested before scope and acceptance criteria are agreed. Direct orders may use PayPal after acceptance; orders originating on a marketplace follow that marketplace's payment rules. A proposal or demo is not an order or proof of earnings.

Delivery uses AI-assisted development and reproducible checks. There are no claims of previous client work or independent human technical review.

## Run the demonstration

Python 3.13 was used for the local verification. No third-party package or network request is needed.

```text
python csv_cleanup_v1.py demo_input.csv cleaned_new.csv
```

Use a new output name. The command creates the CSV and its `.report.json` audit report. For GB18030 input, add `--encoding gb18030`. Keep a copy of the original input. Do not run this sample on confidential records until data handling is agreed.

Local verification passed for BOM/Chinese text, quoted commas, duplicate counts, separate orders, inert formulas, malformed-row rejection and refusal to overwrite existing files. This is a prepared demonstration, not a production certification.

---

## 中文服务说明

拟报价25美元：整理一份CSV导出表，最多2万行、20列；按事先确认的规则去空格、检查重复，保留编号前导零和中文，交付结果、运行脚本和变更报告，包含一次约定范围内的修正。

现有演示只删除全字段完全一致的重复行。按订单号等业务字段判重，需要先确认规则，不能直接按姓名删除记录。金额保留原文本，不猜测日期或金额含义。

公开询价请只提供行列数量、问题说明、输出要求和虚构样例。不要上传客户资料或收款信息。需求、验收条件和交付时间确认后才接受订单；当前没有已成交客户。
