import unittest
from unittest.mock import patch

from src.scrapers import douyin_kanazawa_reviews


class FakePage:
    def __init__(self):
        self.scrolls = 0

    def evaluate(self, script):
        if "scrollBy" in script:
            self.scrolls += 1


def video(video_id):
    return {
        "video_id": video_id,
        "title": f"title {video_id}",
        "video_url": f"https://www.douyin.com/video/{video_id}",
        "author": "",
    }


class DouyinReviewsTests(unittest.TestCase):
    def test_scroll_waits_through_temporary_no_growth(self):
        page = FakePage()
        snapshots = [
            [video("1")],
            [video("1")],
            [video("1")],
            [video("1"), video("2")],
        ]

        def collect(_page):
            index = min(page.scrolls, len(snapshots) - 1)
            return snapshots[index]

        with patch.object(douyin_kanazawa_reviews, "collect_videos", side_effect=collect), patch.object(
            douyin_kanazawa_reviews.time, "sleep"
        ):
            rows = douyin_kanazawa_reviews.scroll_to_load(page, iterations=4, delay=0, no_growth_limit=3)

        self.assertEqual([row["video_id"] for row in rows], ["1", "2"])

    def test_scroll_accumulates_videos_that_disappear_from_visible_dom(self):
        page = FakePage()
        snapshots = [
            [video("1")],
            [video("2")],
            [video("3")],
        ]

        def collect(_page):
            index = min(page.scrolls, len(snapshots) - 1)
            return snapshots[index]

        with patch.object(douyin_kanazawa_reviews, "collect_videos", side_effect=collect), patch.object(
            douyin_kanazawa_reviews.time, "sleep"
        ):
            rows = douyin_kanazawa_reviews.scroll_to_load(page, iterations=2, delay=0, no_growth_limit=2)

        self.assertEqual([row["video_id"] for row in rows], ["1", "2", "3"])

    def test_parse_keywords_accepts_repeated_and_comma_separated_values(self):
        keywords = douyin_kanazawa_reviews.parse_keywords(["福井, 福井旅游", "福井", "永平寺"])

        self.assertEqual(keywords, ["福井", "福井旅游", "永平寺"])

    def test_destination_presets_cover_kanazawa_and_fukui_outputs(self):
        presets = douyin_kanazawa_reviews.DESTINATION_PRESETS

        self.assertEqual(presets["kanazawa"]["output"], "data/raw/social/kanazawa_douyin_reviews.csv")
        self.assertEqual(presets["fukui"]["output"], "data/raw/social/fukui_douyin_reviews.csv")
        self.assertIn("石川旅游", presets["kanazawa"]["keywords"])
        self.assertIn("福井旅游", presets["fukui"]["keywords"])


if __name__ == "__main__":
    unittest.main()
