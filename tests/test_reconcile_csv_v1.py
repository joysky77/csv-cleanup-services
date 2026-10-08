import csv
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reconcile_csv import read_csv, reconcile, write_outputs


class ReconcileTests(unittest.TestCase):
    def write(self, root, name, rows):
        path = root / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        return path

    def test_reports_changes_and_unmatched_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            left = self.write(root, "left.csv", [["id", "amount", "name"], ["001", "10", "Ada"], ["002", "20", "Lin"], ["003", "30", "Mo"]])
            right = self.write(root, "right.csv", [["id", "amount", "name"], ["001", "10", "Ada"], ["002", "25", "Lin"], ["004", "40", "Yu"]])
            lf, lr = read_csv(left, "utf-8-sig", "id")
            rf, rr = read_csv(right, "utf-8-sig", "id")
            report = reconcile(lf, lr, rf, rr, "id")
            self.assertEqual(report["matched_records"], 2)
            self.assertEqual(report["changed_records"], 1)
            self.assertEqual(report["left_only_keys"], ["003"])
            self.assertEqual(report["right_only_keys"], ["004"])
            self.assertEqual(report["changes"][0]["changes"][0], {"column": "amount", "left": "20", "right": "25"})
            out = root / "out"
            write_outputs(report, lr, rr, out)
            self.assertTrue((out / "changed-cells.csv").read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertEqual(json.loads((out / "reconciliation-report.json").read_text(encoding="utf-8"))["changed_records"], 1)

    def test_rejects_duplicate_and_empty_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            duplicate = self.write(root, "duplicate.csv", [["id", "v"], ["1", "a"], ["1", "b"]])
            empty = self.write(root, "empty.csv", [["id", "v"], ["", "a"]])
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                read_csv(duplicate, "utf-8-sig", "id")
            with self.assertRaisesRegex(ValueError, "empty key"):
                read_csv(empty, "utf-8-sig", "id")

    def test_compares_only_shared_columns_and_preserves_leading_zero_keys(self):
        left_fields = ["id", "left_only", "shared"]
        right_fields = ["id", "right_only", "shared"]
        left = {"001": {"id": "001", "left_only": "x", "shared": "a"}}
        right = {"001": {"id": "001", "right_only": "y", "shared": "b"}}
        report = reconcile(left_fields, left, right_fields, right, "id")
        self.assertEqual(report["common_compared_columns"], ["shared"])
        self.assertEqual(report["changes"][0]["key"], "001")


if __name__ == "__main__":
    unittest.main()
