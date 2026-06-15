import unittest

from src.analysis import xhs_fukui_analysis


def note(note_id="", title="福井攻略", note_url="", author="author"):
    return {
        "note_id": note_id,
        "title": title,
        "note_url": note_url,
        "author": author,
        "author_url": "",
    }


class XhsFukuiAnalysisTests(unittest.TestCase):
    def test_dedupe_uses_note_id_as_primary_key(self):
        rows, duplicate_count = xhs_fukui_analysis.dedupe_notes(
            [
                note(note_id="abc", title="old title"),
                note(note_id="abc", title="new title"),
                note(note_id="def", title="other title"),
            ]
        )

        self.assertEqual(duplicate_count, 1)
        self.assertEqual([row["note_id"] for row in rows], ["abc", "def"])
        self.assertEqual(rows[0]["title"], "new title")

    def test_dedupe_extracts_note_id_from_tokenized_urls(self):
        rows, duplicate_count = xhs_fukui_analysis.dedupe_notes(
            [
                note(note_url="https://www.rednote.com/search_result/abc?xsec_token=one"),
                note(note_url="https://www.rednote.com/search_result/abc?xsec_token=two"),
            ]
        )

        self.assertEqual(duplicate_count, 1)
        self.assertEqual(len(rows), 1)

    def test_dedupe_falls_back_to_title_and_author_without_ids_or_urls(self):
        rows, duplicate_count = xhs_fukui_analysis.dedupe_notes(
            [
                note(title=" 福井   攻略 ", author="Author"),
                note(title="福井 攻略", author="author"),
            ]
        )

        self.assertEqual(duplicate_count, 1)
        self.assertEqual(len(rows), 1)

    def test_analysis_counts_deduped_notes_once(self):
        rows, duplicate_count = xhs_fukui_analysis.dedupe_notes(
            [
                note(note_id="abc", title="福井攻略"),
                note(note_id="abc", title="福井攻略"),
            ]
        )
        report = xhs_fukui_analysis.analyze_notes(rows)

        self.assertEqual(duplicate_count, 1)
        self.assertEqual(report["total_notes"], 1)


if __name__ == "__main__":
    unittest.main()
