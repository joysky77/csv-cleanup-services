#!/usr/bin/env python3
"""Reconcile two CSV files by one exact, unique key column."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path, encoding: str, key: str, max_rows: int = 20_000, max_columns: int = 50):
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if not fields or any(not name for name in fields):
            raise ValueError(f"{path.name}: column names must be nonempty")
        if len(fields) > max_columns:
            raise ValueError(f"{path.name}: more than {max_columns} columns")
        if key not in fields:
            raise ValueError(f"{path.name}: key column {key!r} is missing")
        rows: dict[str, dict[str, str]] = {}
        for index, row in enumerate(reader, 1):
            if index > max_rows:
                raise ValueError(f"{path.name}: more than {max_rows} data rows")
            if None in row:
                raise ValueError(f"{path.name}: row {index} has too many columns")
            value = row[key]
            if value == "":
                raise ValueError(f"{path.name}: row {index} has an empty key")
            if value in rows:
                raise ValueError(f"{path.name}: duplicate key {value!r}")
            rows[value] = row
    return fields, rows


def reconcile(left_fields, left_rows, right_fields, right_rows, key):
    common = [name for name in left_fields if name != key and name in right_fields]
    left_keys, right_keys = set(left_rows), set(right_rows)
    matched = sorted(left_keys & right_keys)
    changes = []
    for item_key in matched:
        changed = []
        for column in common:
            before, after = left_rows[item_key][column], right_rows[item_key][column]
            if before != after:
                changed.append({"column": column, "left": before, "right": after})
        if changed:
            changes.append({"key": item_key, "changes": changed})
    return {
        "key_column": key,
        "left_records": len(left_rows),
        "right_records": len(right_rows),
        "matched_records": len(matched),
        "changed_records": len(changes),
        "left_only_keys": sorted(left_keys - right_keys),
        "right_only_keys": sorted(right_keys - left_keys),
        "common_compared_columns": common,
        "changes": changes,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_outputs(report, left_rows, right_rows, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    report = dict(report)
    report_path = output_dir / "reconciliation-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "left-only.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([report["key_column"]])
        writer.writerows([[value] for value in report["left_only_keys"]])
    with (output_dir / "right-only.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([report["key_column"]])
        writer.writerows([[value] for value in report["right_only_keys"]])
    with (output_dir / "changed-cells.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([report["key_column"], "column", "left_value", "right_value"])
        for record in report["changes"]:
            for change in record["changes"]:
                writer.writerow([record["key"], change["column"], change["left"], change["right"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--key", required=True)
    parser.add_argument("--left-encoding", default="utf-8-sig", choices=("utf-8-sig", "gb18030"))
    parser.add_argument("--right-encoding", default="utf-8-sig", choices=("utf-8-sig", "gb18030"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    left_fields, left_rows = read_csv(args.left, args.left_encoding, args.key)
    right_fields, right_rows = read_csv(args.right, args.right_encoding, args.key)
    report = reconcile(left_fields, left_rows, right_fields, right_rows, args.key)
    report["left_sha256"] = sha256(args.left)
    report["right_sha256"] = sha256(args.right)
    write_outputs(report, left_rows, right_rows, args.output_dir)
    print(json.dumps({k: report[k] for k in ("matched_records", "changed_records", "left_only_keys", "right_only_keys")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
