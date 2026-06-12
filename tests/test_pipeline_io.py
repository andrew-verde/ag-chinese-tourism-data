import csv
import tempfile
import unittest
from pathlib import Path

from src.pipeline_io import UnsafeWriteError, read_csv_rows, safe_write_csv


FIELDNAMES = ["note_id", "title", "note_url"]


class SafeWriteCsvTests(unittest.TestCase):
    def test_refuses_empty_write_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "reviews.csv"

            with self.assertRaises(UnsafeWriteError):
                safe_write_csv([], output, FIELDNAMES)

            self.assertFalse(output.exists())

    def test_merges_new_rows_with_existing_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "reviews.csv"

            safe_write_csv(
                [{"note_id": "1", "title": "old", "note_url": "https://example.com/1"}],
                output,
                FIELDNAMES,
                key_fields=["note_id", "note_url"],
            )
            total_rows, backup_path = safe_write_csv(
                [
                    {"note_id": "1", "title": "updated", "note_url": "https://example.com/1"},
                    {"note_id": "2", "title": "new", "note_url": "https://example.com/2"},
                ],
                output,
                FIELDNAMES,
                key_fields=["note_id", "note_url"],
            )

            rows = read_csv_rows(output)
            self.assertEqual(total_rows, 2)
            self.assertEqual([row["note_id"] for row in rows], ["1", "2"])
            self.assertEqual(rows[0]["title"], "updated")
            self.assertIsNotNone(backup_path)
            self.assertTrue(backup_path.exists())

    def test_refuses_shrinking_replace_without_explicit_permission(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "reviews.csv"
            with output.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(
                    [
                        {"note_id": "1", "title": "one", "note_url": "https://example.com/1"},
                        {"note_id": "2", "title": "two", "note_url": "https://example.com/2"},
                    ]
                )

            with self.assertRaises(UnsafeWriteError):
                safe_write_csv(
                    [{"note_id": "1", "title": "one", "note_url": "https://example.com/1"}],
                    output,
                    FIELDNAMES,
                    merge_existing=False,
                )

            self.assertEqual(len(read_csv_rows(output)), 2)


if __name__ == "__main__":
    unittest.main()
