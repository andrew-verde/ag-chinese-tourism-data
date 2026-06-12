#!/usr/bin/env python3
"""Analyze Xiaohongshu Fukui review note results.

Usage:
    python3 xhs_fukui_analysis.py --input fukui_xhs_reviews.csv
"""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from src.pipeline_io import UnsafeWriteError, safe_write_csv


FAN_KEYWORDS = [
    'riku', 'wish', 'nctwish', 'nct', '粉丝', '打卡', '巡礼', '同款', '偶像', '家乡', '朝圣',
    '粉圈', 'wish同款', '同款照', '粉丝打卡', '巡礼地', '同款景点'
]
TRAVEL_KEYWORDS = [
    '攻略', '一日游', '景点', '美食', '交通', '交通费', '民宿', '东寻坊', '永平寺',
    '冬季', '京都', '大阪', 'vlog', '线路', '小众', '酒店', '行程', '费用', '出发',
    '两天', '三天', '往返', '慢游', '体验', '游记', '推荐', '住宿'
]

KEYWORD_CANDIDATES = [
    '福井', 'riku', 'wish', 'nctwish', 'nct', '打卡', '巡礼', '攻略', '一日游', '美食',
    '交通', '东寻坊', '永平寺', '冬季', '京都', '民宿', '酒店', '行程', '往返', '费用',
    'vlog', '同款', '偶像', '粉丝', '小众', '景点', '出发', '体验', '游记', '推荐',
    '慢游', '吃好吃的', '家乡', 'riku的家乡'
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


def classify_note_title(title: str):
    text = normalize_text(title)
    fan_counts = count_keyword_occurrences(text, FAN_KEYWORDS)
    travel_counts = count_keyword_occurrences(text, TRAVEL_KEYWORDS)
    fan_score = sum(fan_counts.values())
    travel_score = sum(travel_counts.values())

    if fan_score > travel_score:
        return 'fan', fan_score, travel_score
    if travel_score > fan_score:
        return 'travel', fan_score, travel_score

    # fallback: if any fan keyword appears at all, treat as fan
    if fan_counts:
        return 'fan', fan_score, travel_score
    if travel_counts:
        return 'travel', fan_score, travel_score
    return 'ordinary', fan_score, travel_score


def analyze_notes(notes):
    total = len(notes)
    keyword_hit = Counter()
    keyword_occurrence = Counter()
    theme_counts = Counter()
    theme_examples = defaultdict(list)

    for note in notes:
        title = note.get('title', '') or ''
        normalized = normalize_text(title)
        for kw in KEYWORD_CANDIDATES:
            count = len(re.findall(re.escape(kw), normalized, flags=re.IGNORECASE))
            if count > 0:
                keyword_occurrence[kw] += count
                keyword_hit[kw] += 1

        theme, fan_score, travel_score = classify_note_title(title)
        theme_counts[theme] += 1
        if len(theme_examples[theme]) < 5:
            theme_examples[theme].append({'title': title, 'fan_score': fan_score, 'travel_score': travel_score})

    return {
        'total_notes': total,
        'keyword_hit': keyword_hit,
        'keyword_occurrence': keyword_occurrence,
        'theme_counts': theme_counts,
        'theme_examples': theme_examples,
    }


def load_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def print_summary(report, top_n=20):
    total = report['total_notes']
    theme_counts = report['theme_counts']
    print(f'Total notes: {total}')
    print('Theme proportions:')
    for theme in ['fan', 'travel', 'ordinary']:
        count = theme_counts.get(theme, 0)
        ratio = count / total * 100 if total else 0
        print(f'  {theme}: {count} ({ratio:.1f}%)')

    print(f'\n关键词命中比例 (前{top_n}):')
    if total:
        keywords = sorted(report['keyword_hit'].items(), key=lambda x: x[1], reverse=True)
        for kw, hit in keywords[:top_n]:
            occurrence = report['keyword_occurrence'][kw]
            ratio = hit / total * 100
            print(f'  {kw}: notes={hit} ({ratio:.1f}%), occurrences={occurrence}')

    if report['theme_examples']:
        print('\nTheme examples:')
        for theme, examples in report['theme_examples'].items():
            print(f'  {theme}:')
            for item in examples:
                print(f'    - {item["title"]} (fan={item["fan_score"]}, travel={item["travel_score"]})')


def save_classification(notes, path: Path):
    if not notes:
        return
    fieldnames = list(notes[0].keys())
    return safe_write_csv(
        notes,
        path,
        fieldnames,
        key_fields=['note_id', 'note_url'],
        merge_existing=False,
        allow_empty=False,
        allow_shrink=False,
    )


def main():
    parser = argparse.ArgumentParser(description='Analyze Xiaohongshu Fukui review notes for keyword and theme proportions.')
    parser.add_argument('--input', default='data/raw/social/fukui_xhs_reviews.csv', help='Input CSV file from scraper')
    parser.add_argument('--output', default='data/processed/fukui_xhs_analysis.csv', help='Optional output CSV file for classification results')
    parser.add_argument('--top', type=int, default=20, help='Number of top keywords to print')
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        raise SystemExit(f'Input file not found: {path}')

    notes = load_csv(path)
    report = analyze_notes(notes)
    print_summary(report, top_n=args.top)

    classified = []
    for note in notes:
        theme, fan_score, travel_score = classify_note_title(note.get('title', ''))
        note = dict(note)
        note['theme'] = theme
        note['fan_score'] = fan_score
        note['travel_score'] = travel_score
        classified.append(note)

    try:
        save_result = save_classification(classified, Path(args.output))
    except UnsafeWriteError as exc:
        raise SystemExit(str(exc)) from exc
    if save_result is None:
        print(f'Classification output not written because {args.input} contained no rows')
        return
    total_rows, backup_path = save_result
    if backup_path:
        print(f'Backed up previous classification output to {backup_path}')
    print(f'Classification output saved to {args.output} ({total_rows} rows)')


if __name__ == '__main__':
    main()
