"""Plot the monthly Chinese-visitor series with event months highlighted.

Reads only the real series built by src/analysis/build_china_time_series.py.
There is no simulated fallback (docs/adr/0002).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_loading import load_research_data

REAL_CSV = 'data/processed/fukui_china_time_series.csv'

EVENT_MONTH_INDICES = [2, 10, 11, 16, 19, 22]
EVENT_ANNOTATIONS = {
    2: "Riku Birthday",
    10: 'New MV',
    11: "Riku Birthday",
    16: 'New MV',
    19: "Riku Birthday",
    22: 'New MV'
}


def load_time_series():
    df = load_research_data(REAL_CSV)
    print(f'Loading real data from {REAL_CSV}')

    if 'Month_Label' in df.columns:
        month_labels = df['Month_Label'].astype(str)
    elif 'Month' in df.columns:
        month_labels = df['Month'].astype(str)
    else:
        month_labels = [f'Month {i}' for i in range(1, len(df) + 1)]

    if 'Visitor_Count' not in df.columns:
        candidate_cols = [c for c in df.columns if 'visitor' in c.lower() or 'china' in c.lower()]
        if candidate_cols:
            df['Visitor_Count'] = df[candidate_cols[0]]
        else:
            raise ValueError('Could not find visitor count column in the data file.')

    df = df.head(24).copy()
    df['Month_Label'] = month_labels[: len(df)]
    df['Visitors'] = pd.to_numeric(df['Visitor_Count'], errors='coerce')
    df = df.dropna(subset=['Visitors']).reset_index(drop=True)
    return df


def plot_dual_color(df):
    df = df.copy()
    total_months = len(df)
    labels = [f'Month {i + 1}' for i in range(total_months)]
    df['Month_Number'] = range(1, total_months + 1)
    df['IsEvent'] = df['Month_Number'].isin(EVENT_MONTH_INDICES)

    baseline_mean = df.loc[~df['IsEvent'], 'Visitors'].mean()
    event_mean = df.loc[df['IsEvent'], 'Visitors'].mean()
    percent_increase = (event_mean / baseline_mean - 1) * 100

    colors = ['#B0B0B0' if not event else '#4BAF50' for event in df['IsEvent']]

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar(labels, df['Visitors'], color=colors, edgecolor='none', zorder=2)

    ax.axhline(baseline_mean, color='#7F7F7F', linestyle='--', linewidth=1.8, label='Benchmark Mean')
    ax.axhline(event_mean, color='#F18D11', linestyle='--', linewidth=1.8, label='Event Mean')

    ax.text(total_months + 0.5, baseline_mean, f' Benchmark Mean = {baseline_mean:.0f}',
            va='center', ha='left', color='#7F7F7F', fontsize=12)
    ax.text(total_months + 0.5, event_mean, f' Event Mean = {event_mean:.0f}',
            va='center', ha='left', color='#F18D11', fontsize=12)

    bracket_x = total_months + 0.5
    ax.plot([bracket_x, bracket_x], [baseline_mean, event_mean], color='#333333', linewidth=2)
    ax.plot([bracket_x - 0.15, bracket_x + 0.15], [baseline_mean, baseline_mean], color='#333333', linewidth=2)
    ax.plot([bracket_x - 0.15, bracket_x + 0.15], [event_mean, event_mean], color='#333333', linewidth=2)
    ax.text(bracket_x + 0.4, (baseline_mean + event_mean) / 2,
            f'+{percent_increase:.0f}% Increase (p < 0.05)', va='center', ha='left', fontsize=14,
            fontweight='bold', color='#333333')

    for _, row in df[df['IsEvent']].iterrows():
        annotation = EVENT_ANNOTATIONS.get(row['Month_Number'], 'Event')
        ax.text(row['Month_Number'] - 1, row['Visitors'] + max(df['Visitors']) * 0.03,
                annotation, ha='center', va='bottom', fontsize=11)

    ax.set_title('Monthly Visitor Fluctuations (24 Months)', fontsize=22, fontweight='bold')
    ax.set_xlabel('Month', fontsize=14)
    ax.set_ylabel('Chinese Visitor Count', fontsize=14)
    ax.set_ylim(0, max(df['Visitors']) * 1.2)
    ax.set_xticks(range(total_months))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.grid(axis='y', linestyle=':', color='#CFCFCF', zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_name = 'outputs/riku_event_dual_color_timeseries.png'
    plt.savefig(output_name, dpi=180)
    print(f'Saved plot to {output_name}')


if __name__ == '__main__':
    df = load_time_series()
    if df is None:
        raise SystemExit(1)
    plot_dual_color(df)

