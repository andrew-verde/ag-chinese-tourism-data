"""Tests for the data-loading integrity gate.

These tests are the executable form of the project's data-integrity rules
(docs/adr/0001, docs/adr/0002): synthetic data cannot be loaded for
analysis, and empty datasets are refused.
"""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_loading import (
    FIXTURES_DIR,
    EmptyDataError,
    MissingDataError,
    SyntheticDataError,
    load_research_data,
)


class LoadResearchDataTests(unittest.TestCase):
    def test_refuses_paths_under_tests_fixtures(self):
        fixture = FIXTURES_DIR / "some_fixture.csv"
        with self.assertRaises(SyntheticDataError):
            load_research_data(fixture)

    def test_refuses_simulated_filenames_anywhere(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fukui_china_time_series_simulated.csv"
            pd.DataFrame({"a": [1]}).to_csv(path, index=False)
            with self.assertRaises(SyntheticDataError):
                load_research_data(path)

    def test_refuses_mock_filenames_anywhere(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kanazawa_mock_reviews.csv"
            pd.DataFrame({"a": [1]}).to_csv(path, index=False)
            with self.assertRaises(SyntheticDataError):
                load_research_data(path)

    def test_refuses_header_only_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reviews.csv"
            path.write_text("note_id,title,note_url\n", encoding="utf-8")
            with self.assertRaises(EmptyDataError):
                load_research_data(path)

    def test_refuses_missing_file_with_collection_hint(self):
        with self.assertRaises(MissingDataError):
            load_research_data("data/raw/social/does_not_exist.csv")

    def test_loads_real_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reviews.csv"
            pd.DataFrame({"note_id": ["n1"], "title": ["福井旅游"]}).to_csv(path, index=False)
            df = load_research_data(path)
            self.assertEqual(len(df), 1)


if __name__ == "__main__":
    unittest.main()
