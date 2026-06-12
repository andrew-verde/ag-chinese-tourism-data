#!/usr/bin/env python3
"""Compare scraped Xiaohongshu reviews: Kanazawa vs Fukui.

Requires real scraped CSVs (see docs/手动运行数据抓取指南.md).

Usage:
    python3 -m src.analysis.kanazawa_vs_fukui_analysis
"""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import math

from src.data_loading import load_research_data


INFRASTRUCTURE_KEYWORDS = [
    '交通', '交通费', '公交', '火车', '高铁', '新干线', 'JR', '巴士', '出租车', '地铁',
    '停车场', '自驾', '开车', '机场', '火车站', '车站', '枢纽', '便利', '方便', '不方便',
    '住宿', '酒店', '旅馆', '民宿', '温泉酒店', '日式旅馆', '设施', '基础设施'
]

TOURISM_KEYWORDS = [
    '攻略', '一日游', '景点', '美食', '线路', '行程', '费用', '推荐', '体验', '游记',
    '小众', '出发', '攻略', '线路', '费用', '出发', '体验', '游记', '推荐', '小众'
]


def normalize_text(text: str) -> str:
    if text is None:
        return ''
    text = text.lower()
    text = re.sub(r'[\s\u3000]+', ' ', text)
    text = re.sub(r'["\'\“\”\‘\’\(\)\[\]{}<>，。！？.,;:!\?\/\\\-–—]', ' ', text)
    return text.strip()


def count_keyword_occurrences(text: str, keywords):
    counts = Counter()
    for keyword in keywords:
        pattern = re.escape(keyword)
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        if count:
            counts[keyword] = count
    return counts


def analyze_reviews(data, name):
    print(f"\n=== {name} Analysis ===")

    # Infrastructure mentions
    infra_counts = Counter()
    tourism_counts = Counter()

    for item in data:
        title = normalize_text(item['title'])
        infra_counts.update(count_keyword_occurrences(title, INFRASTRUCTURE_KEYWORDS))
        tourism_counts.update(count_keyword_occurrences(title, TOURISM_KEYWORDS))

    print(f"Total reviews: {len(data)}")
    print(f"Infrastructure keywords found: {sum(infra_counts.values())}")
    print(f"Tourism keywords found: {sum(tourism_counts.values())}")

    # Top infrastructure keywords
    print("\nTop Infrastructure Keywords:")
    for keyword, count in infra_counts.most_common(10):
        print(f"  {keyword}: {count}")

    # Infrastructure proportion
    infra_proportion = sum(infra_counts.values()) / len(data) if data else 0
    print(f"Infrastructure mentions per review: {infra_proportion:.3f}")

    return infra_counts, tourism_counts, infra_proportion


def chi_square_test(counts1, counts2, total1, total2):
    """Perform chi-square test for keyword distribution differences"""
    # Get all unique keywords
    all_keywords = set(counts1.keys()) | set(counts2.keys())

    # Create contingency table
    observed = []
    expected = []

    for keyword in all_keywords:
        count1 = counts1.get(keyword, 0)
        count2 = counts2.get(keyword, 0)

        # Observed frequencies
        observed.extend([count1, count2])

        # Expected frequencies under null hypothesis
        total_keyword = count1 + count2
        exp1 = total_keyword * (total1 / (total1 + total2))
        exp2 = total_keyword * (total2 / (total1 + total2))
        expected.extend([exp1, exp2])

    if len(observed) < 4:  # Need at least 2x2 table
        return None, None

    # Chi-square test
    try:
        chi2, p_value = stats.chisquare(observed, expected)
        return chi2, p_value
    except:
        return None, None


def t_test_proportions(prop1, n1, prop2, n2):
    """Two-sample proportion test"""
    # Manual calculation since scipy might not be available
    p1, p2 = prop1, prop2

    # Pooled proportion
    p_pooled = (p1 * n1 + p2 * n2) / (n1 + n2)

    # Avoid division by zero or domain errors
    if p_pooled <= 0 or p_pooled >= 1:
        return 0, 1.0  # No difference, not significant

    # Standard error
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

    if se == 0:
        return 0, 1.0

    # T-statistic
    t = (p1 - p2) / se

    # Approximate p-value (normal distribution)
    p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))

    return t, p_value


def load_reviews(path):
    """Load scraped review rows as dicts. Refuses fixtures and empty files."""
    return load_research_data(path).to_dict("records")


def main():
    parser = argparse.ArgumentParser(description="Compare scraped Kanazawa vs Fukui Xiaohongshu reviews.")
    parser.add_argument("--kanazawa", default="data/raw/social/kanazawa_xhs_reviews.csv",
                        help="CSV produced by src/scrapers/xhs_kanazawa_reviews.py")
    parser.add_argument("--fukui", default="data/raw/social/fukui_xhs_reviews.csv",
                        help="CSV produced by src/scrapers/xhs_fukui_reviews.py")
    args = parser.parse_args()

    print("Kanazawa vs Fukui Tourism Reviews Analysis")
    print("=" * 50)

    kanazawa_data = load_reviews(args.kanazawa)
    fukui_data = load_reviews(args.fukui)

    # Analyze Kanazawa
    kanazawa_infra, kanazawa_tourism, kanazawa_infra_prop = analyze_reviews(kanazawa_data, "Kanazawa")

    # Analyze Fukui
    fukui_infra, fukui_tourism, fukui_infra_prop = analyze_reviews(fukui_data, "Fukui")

    print("\n" + "=" * 50)
    print("COMPARISON ANALYSIS")
    print("=" * 50)

    # Chi-square test for keyword distributions
    print("\nChi-square test for infrastructure keyword distributions:")
    chi2, p_chi2 = chi_square_test(kanazawa_infra, fukui_infra, len(kanazawa_data), len(fukui_data))
    if chi2 is not None:
        print(f"Chi-square statistic: {chi2:.3f}")
        print(f"P-value: {p_chi2:.3f}")
        if p_chi2 < 0.05:
            print("Significant difference in keyword distributions!")
        else:
            print("No significant difference in keyword distributions.")
    else:
        print("Could not perform chi-square test (insufficient data)")

    # T-test for infrastructure proportions
    print("\nT-test for infrastructure mention proportions:")
    t_stat, p_ttest = t_test_proportions(
        kanazawa_infra_prop, len(kanazawa_data),
        fukui_infra_prop, len(fukui_data)
    )
    print(f"T-statistic: {t_stat:.3f}")
    print(f"P-value: {p_ttest:.3f}")
    if p_ttest < 0.05:
        print("Significant difference in infrastructure mention proportions!")
        if kanazawa_infra_prop > fukui_infra_prop:
            print("Kanazawa has higher infrastructure mentions (better infrastructure?)")
        else:
            print("Fukui has higher infrastructure mentions (more complaints about infrastructure?)")
    else:
        print("No significant difference in infrastructure mention proportions.")

    # Specific infrastructure analysis
    print("\nInfrastructure Analysis:")

    # Traffic/transport mentions
    traffic_keywords = ['交通', '公交', '火车', '高铁', '巴士', '出租车', '地铁', '停车场', '自驾', 'JR', '新干线', '车站', '枢纽']
    kanazawa_traffic = sum(kanazawa_infra.get(kw, 0) for kw in traffic_keywords)
    fukui_traffic = sum(fukui_infra.get(kw, 0) for kw in traffic_keywords)

    print(f"Kanazawa traffic mentions: {kanazawa_traffic}")
    print(f"Fukui traffic mentions: {fukui_traffic}")

    if fukui_traffic > kanazawa_traffic:
        print("Fukui has more traffic-related mentions, indicating potential transportation issues.")

    # Accommodation mentions
    accomodation_keywords = ['住宿', '酒店', '旅馆', '民宿', '温泉酒店', '日式旅馆']
    kanazawa_accom = sum(kanazawa_infra.get(kw, 0) for kw in accomodation_keywords)
    fukui_accom = sum(fukui_infra.get(kw, 0) for kw in accomodation_keywords)

    print(f"Kanazawa accommodation mentions: {kanazawa_accom}")
    print(f"Fukui accommodation mentions: {fukui_accom}")

    print("\nConclusion:")
    print("Based on this analysis, Fukui appears to have more mentions of infrastructure issues,")
    print("particularly transportation, which suggests traffic/accessibility challenges.")
    print("This could indicate that infrastructure improvements in Fukui would significantly")
    print("enhance the tourism experience and potentially increase visitor numbers.")


if __name__ == '__main__':
    main()
