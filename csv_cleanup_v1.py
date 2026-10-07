"""CSV cleanup service sample v1.0.0. Python standard library only."""
import argparse
import csv
import io
import json
from pathlib import Path

VERSION = "1.0.0"


def prepare(source: Path, encoding: str):
    text = source.read_text(encoding=encoding)
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    header = next(reader, None)
    if header is None:
        raise ValueError("Input is empty")
    header = [value.strip() for value in header]
    if any(not value for value in header) or len(set(header)) != len(header):
        raise ValueError("Column names must be nonempty and unique after trimming")
    unique = []
    seen = set()
    duplicates = []
    input_rows = 0
    trimmed_cells = 0
    for row in reader:
        if len(row) != len(header):
            raise ValueError(f"CSV line {reader.line_num}: expected {len(header)} columns, got {len(row)}")
        input_rows += 1
        if input_rows > 100000:
            raise ValueError("Sample limit is 100000 rows")
        normalized = tuple(cell.strip() for cell in row)
        trimmed_cells += sum(old != new for old, new in zip(row, normalized))
        if normalized in seen:
            duplicates.append({"record": input_rows, "ending_csv_line": reader.line_num})
        else:
            seen.add(normalized)
            unique.append(normalized)
    report = {
        "tool_version": VERSION,
        "input_encoding": encoding,
        "input_records": input_rows,
        "output_records": len(unique),
        "duplicate_records_removed": len(duplicates),
        "duplicate_locations": duplicates,
        "trimmed_cells": trimmed_cells,
        "deduplication_rule": "All columns equal after trimming surrounding whitespace",
        "financial_values": "Preserved as text; no amounts inferred, summed, or merged",
        "spreadsheet_protection": "Leading = + - @ and control-character cells receive an apostrophe in the output CSV",
    }
    return header, unique, report


def spreadsheet_safe(value):
    return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--encoding", default="utf-8-sig", help="e.g. utf-8-sig or gb18030")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args()
    report_path = args.output.with_suffix(args.output.suffix + ".report.json")
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files")
        if args.output.exists() or report_path.exists():
            raise ValueError("Output or report already exists; choose a new filename")
        header, rows, report = prepare(args.input, args.encoding)
        protected = sum(spreadsheet_safe(cell) != cell for row in [header, *rows] for cell in row)
        report["spreadsheet_cells_protected"] = protected
        # Exclusive creation prevents overwriting an existing file after validation.
        with args.output.open("x", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow([spreadsheet_safe(cell) for cell in header])
            writer.writerows([[spreadsheet_safe(cell) for cell in row] for row in rows])
        with report_path.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        print(json.dumps(report, ensure_ascii=False))
    except (ValueError, UnicodeError, csv.Error, OSError) as error:
        parser.exit(2, f"Cleanup failed: {error}\n")


if __name__ == "__main__":
    main()
