import unittest
from unittest.mock import patch

from src.scrapers import xhs_fukui_reviews


class FakePage:
    def __init__(self):
        self.scrolls = 0

    def evaluate(self, script):
        if "scrollBy" in script:
            self.scrolls += 1


def note(note_id):
    return {
        "note_id": note_id,
        "title": f"title {note_id}",
        "note_url": f"https://www.rednote.com/search_result/{note_id}",
        "author": "",
        "author_url": "",
    }


class XhsFukuiReviewsTests(unittest.TestCase):
    def test_scroll_waits_through_temporary_no_growth(self):
        page = FakePage()
        snapshots = [
            [note("1")],
            [note("1")],
            [note("1")],
            [note("1"), note("2")],
        ]

        def collect(_page):
            index = min(page.scrolls, len(snapshots) - 1)
            return snapshots[index]

        with patch.object(xhs_fukui_reviews, "collect_notes", side_effect=collect), patch.object(
            xhs_fukui_reviews.time, "sleep"
        ):
            rows = xhs_fukui_reviews.scroll_to_load(page, iterations=4, delay=0, no_growth_limit=3)

        self.assertEqual([row["note_id"] for row in rows], ["1", "2"])

    def test_scroll_accumulates_notes_that_disappear_from_visible_dom(self):
        page = FakePage()
        snapshots = [
            [note("1")],
            [note("2")],
            [note("3")],
        ]

        def collect(_page):
            index = min(page.scrolls, len(snapshots) - 1)
            return snapshots[index]

        with patch.object(xhs_fukui_reviews, "collect_notes", side_effect=collect), patch.object(
            xhs_fukui_reviews.time, "sleep"
        ):
            rows = xhs_fukui_reviews.scroll_to_load(page, iterations=2, delay=0, no_growth_limit=2)

        self.assertEqual([row["note_id"] for row in rows], ["1", "2", "3"])

    def test_parse_keywords_accepts_repeated_and_comma_separated_values(self):
        keywords = xhs_fukui_reviews.parse_keywords(["福井, 福井旅游", "福井", "永平寺"])

        self.assertEqual(keywords, ["福井", "福井旅游", "永平寺"])


if __name__ == "__main__":
    unittest.main()
