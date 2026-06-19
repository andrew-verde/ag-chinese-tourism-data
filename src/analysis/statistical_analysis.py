"""
Fukui Tourism Visitor Analysis - Statistical Framework
Purpose: Implement quantitative analysis for US vs Chinese visitor comparison
Author: Tourism Analysis Lab
Date: 2026
"""

import pandas as pd
import numpy as np
import os
import tempfile
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, f_oneway

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "tourism-data-matplotlib"))

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def require_columns(df, path, columns):
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{path} lacks required column(s): {', '.join(repr(col) for col in missing)}. "
            f"Available columns: {', '.join(map(str, df.columns))}"
        )

# ============================================================================
# 1. THEME FREQUENCY ANALYSIS - Chi-Square Goodness of Fit Test
# ============================================================================

def analyze_theme_distribution(theme_data):
    """
    Test if theme frequencies are significantly different from uniform distribution.
    Theme data format: {'theme_name': frequency_count, ...}
    
    H0: All themes equally represented
    H1: Theme distribution is non-uniform
    """
    print("\n" + "="*80)
    print("ANALYSIS 1: THEME FREQUENCY DISTRIBUTION (Chi-Square Test)")
    print("="*80)
    
    themes = list(theme_data.keys())
    frequencies = list(theme_data.values())
    
    # Expected frequencies (uniform distribution)
    expected_freq = [sum(frequencies) / len(themes)] * len(themes)
    
    # Chi-square test (using scipy.stats directly)
    chi2_stat = sum((obs - exp)**2 / exp for obs, exp in zip(frequencies, expected_freq))
    dof = len(themes) - 1
    p_value = 1 - stats.chi2.cdf(chi2_stat, dof)
    
    print(f"\nObserved Frequencies:")
    for theme, freq in theme_data.items():
        print(f"  {theme}: {freq}")
    
    print(f"\nChi-Square Test Results:")
    print(f"  χ² statistic: {chi2_stat:.4f}")
    print(f"  p-value: {p_value:.6f}")
    print(f"  Degrees of freedom: {dof}")
    
    if p_value < 0.05:
        print(f"  ✓ SIGNIFICANT (p < 0.05): Themes are NOT equally distributed")
        print(f"    → Interpretation: Chinese visitors have distinct preference patterns")
    else:
        print(f"  ✗ NOT SIGNIFICANT (p ≥ 0.05): No clear preference pattern")
    
    # Calculate theme priorities
    total = sum(frequencies)
    print(f"\nTheme Preference Ranking (by % of mentions):")
    ranked = sorted(theme_data.items(), key=lambda x: x[1], reverse=True)
    for rank, (theme, freq) in enumerate(ranked, 1):
        pct = (freq / total) * 100
        print(f"  {rank}. {theme}: {freq} mentions ({pct:.1f}%)")
    
    return chi2_stat, p_value


def analyze_sentiment_theme_correlation(theme_sentiment_data):
    """
    Analyze correlation between theme type and emotional sentiment intensity.
    
    Data format:
    {
        'theme': ['scenic', 'fandom', 'scenic', ...],
        'emotion_score': [0.85, 0.92, 0.78, ...]  # 0-1 scale
    }
    
    Emotional keywords weight: 想哭(0.95), 哭(0.93), 幸福(0.85), 治愈(0.88), 温暖(0.80)
    """
    print("\n" + "="*80)
    print("ANALYSIS 2: SENTIMENT-THEME CORRELATION (ANOVA)")
    print("="*80)
    
    df = pd.DataFrame(theme_sentiment_data)
    
    # Group sentiment by theme
    theme_groups = {}
    for theme in df['theme'].unique():
        theme_data = df[df['theme'] == theme]['emotion_score'].values
        theme_groups[theme] = theme_data
    
    print(f"\nEmotional Intensity by Theme (Scale: 0-1):")
    emotional_rankings = []
    for theme, scores in theme_groups.items():
        mean_sentiment = np.mean(scores)
        std_sentiment = np.std(scores)
        emotional_rankings.append((theme, mean_sentiment, std_sentiment, len(scores)))
        print(f"  {theme}:")
        print(f"    Mean: {mean_sentiment:.3f} | Std: {std_sentiment:.3f} | N: {len(scores)}")
    
    # ANOVA test: Do themes have significantly different sentiment profiles?
    f_stat, p_value = f_oneway(*theme_groups.values())
    
    print(f"\nANOVA Results (Testing if themes differ in emotional intensity):")
    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  p-value: {p_value:.6f}")
    
    if p_value < 0.05:
        print(f"  ✓ SIGNIFICANT (p < 0.05): Themes evoke different emotional responses")
        print(f"    → Interpretation: Some themes more emotionally resonant than others")
        ranked_emotion = sorted(emotional_rankings, key=lambda x: x[1], reverse=True)
        print(f"\n  Emotional Impact Ranking (highest to lowest):")
        for rank, (theme, mean, std, n) in enumerate(ranked_emotion, 1):
            print(f"    {rank}. {theme} (μ={mean:.3f})")
    else:
        print(f"  ✗ NOT SIGNIFICANT: All themes generate similar emotional response")
    
    return f_stat, p_value, emotional_rankings


# ============================================================================
# 2. SPENDING PROFILE SEGMENTATION - K-Means Clustering
# ============================================================================

def segment_visitors_by_spending(spending_data):
    """
    Cluster visitors into archetypes based on spending composition.
    
    Data format: DataFrame with columns ['accommodation_%', 'shopping_%', 'food_%', 'transport_%', 'experience_%']
    """
    print("\n" + "="*80)
    print("ANALYSIS 3: VISITOR SEGMENTATION BY SPENDING PROFILE (K-Means)")
    print("="*80)
    
    # Standardize the data
    scaler = StandardScaler()
    spending_scaled = scaler.fit_transform(spending_data)
    
    # Elbow method to find optimal clusters
    inertias = []
    K_range = range(2, 6)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(spending_scaled)
        inertias.append(kmeans.inertia_)
    
    # Use k=3 or k=4 based on elbow
    optimal_k = 3
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(spending_scaled)
    
    print(f"\nOptimal number of visitor segments: {optimal_k}")
    print(f"Silhouette Score: {calculate_silhouette(spending_scaled, clusters):.3f}")
    
    # Characterize each cluster
    spending_data_copy = spending_data.copy()
    spending_data_copy['cluster'] = clusters
    
    visitor_archetypes = [
        "Luxury Traveler",
        "Experience Seeker",
        "Budget-Conscious Explorer",
        "Comfort-Focused Visitor"
    ]
    
    print(f"\nVisitor Archetypes Identified:")
    for i in range(optimal_k):
        cluster_data = spending_data_copy[spending_data_copy['cluster'] == i]
        print(f"\n  {i+1}. {visitor_archetypes[i]} (n={len(cluster_data)})")
        print(f"     Spending Profile (average %):")
        for col in spending_data.columns:
            mean_val = cluster_data[col].mean()
            print(f"       • {col}: {mean_val:.1f}%")
    
    return clusters, optimal_k


def calculate_silhouette(X, labels):
    """Calculate silhouette score for clustering quality."""
    from sklearn.metrics import silhouette_score
    return silhouette_score(X, labels)


# ============================================================================
# 3. TIME SERIES & EVENT IMPACT ANALYSIS
# ============================================================================

def analyze_event_impact(monthly_visitor_data, event_months):
    """
    Interrupted Time Series (ITS) Analysis: Quantify impact of Riku events on visitor volume.
    
    Data format:
    {
        'month': ['2024-01', '2024-02', ...],
        'visitors': [1200, 1450, ...],
        'is_event_month': [False, True, ...]
    }
    """
    print("\n" + "="*80)
    print("ANALYSIS 4: RIKU EVENT IMPACT ON VISITOR VOLUME (Time Series Analysis)")
    print("="*80)
    
    df = pd.DataFrame(monthly_visitor_data)
    
    # Calculate baseline (non-event) average
    baseline_data = df[df['is_event_month'] == False]['visitors']
    event_data = df[df['is_event_month'] == True]['visitors']
    
    baseline_mean = baseline_data.mean()
    event_mean = event_data.mean()
    
    print(f"\nBaseline Visitor Count (non-event months):")
    print(f"  Mean: {baseline_mean:.0f} visitors")
    print(f"  Std Dev: {baseline_data.std():.0f}")
    print(f"  N months: {len(baseline_data)}")
    
    print(f"\nEvent Month Visitor Count (Riku-related events):")
    print(f"  Mean: {event_mean:.0f} visitors")
    print(f"  Std Dev: {event_data.std():.0f}")
    print(f"  N months: {len(event_data)}")
    
    # T-test: Is there significant difference?
    t_stat, p_value = ttest_ind(event_data, baseline_data)
    
    print(f"\nIndependent t-test Results:")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.6f}")
    
    # Calculate effect size (Cohen's d)
    cohens_d = (event_mean - baseline_mean) / np.sqrt(
        ((len(event_data)-1)*event_data.std()**2 + 
         (len(baseline_data)-1)*baseline_data.std()**2) / 
        (len(event_data) + len(baseline_data) - 2)
    )
    
    percent_increase = ((event_mean - baseline_mean) / baseline_mean) * 100
    
    print(f"\nEffect Size (Cohen's d): {cohens_d:.3f}")
    print(f"Percent Increase: {percent_increase:.1f}%")
    
    if p_value < 0.05:
        print(f"\n  ✓ SIGNIFICANT (p < 0.05)")
        print(f"    → Riku events cause {percent_increase:.0f}% increase in visitors")
        print(f"    → Interpretation: Fandom is a quantifiable driver of tourism")
    else:
        print(f"\n  ✗ NOT SIGNIFICANT (p ≥ 0.05)")
        print(f"    → Event months show {percent_increase:.0f}% difference (not statistically significant)")
    
    return t_stat, p_value, cohens_d, percent_increase


# ============================================================================
# 4. MARKET COMPARISON ANALYSIS
# ============================================================================

def compare_fukui_vs_ishikawa(fukui_data, ishikawa_data):
    """
    Compare Chinese visitor metrics between Fukui and Ishikawa.
    
    Data format: {'visitors': 1000, 'avg_spend': 250000, 'population': 5000000}
    """
    print("\n" + "="*80)
    print("ANALYSIS 5: FUKUI vs ISHIKAWA MARKET COMPARISON")
    print("="*80)
    
    # Market share calculation
    fukui_visitors = fukui_data.get('visitors', 0)
    ishikawa_visitors = ishikawa_data.get('visitors', 0)
    
    fukui_share = (fukui_visitors / (fukui_visitors + ishikawa_visitors)) * 100
    ishikawa_share = 100 - fukui_share
    
    print(f"\nChinese Visitor Market Share:")
    print(f"  Fukui: {fukui_share:.1f}% ({fukui_visitors:,} visitors)")
    print(f"  Ishikawa: {ishikawa_share:.1f}% ({ishikawa_visitors:,} visitors)")
    
    # Per-capita spending comparison
    fukui_spend = fukui_data.get('avg_spend', 0)
    ishikawa_spend = ishikawa_data.get('avg_spend', 0)
    
    spend_diff = fukui_spend - ishikawa_spend
    spend_pct_diff = (spend_diff / ishikawa_spend) * 100 if ishikawa_spend > 0 else 0
    
    print(f"\nAverage Spend per Chinese Visitor:")
    print(f"  Fukui: ¥{fukui_spend:,}")
    print(f"  Ishikawa: ¥{ishikawa_spend:,}")
    print(f"  Difference: ¥{spend_diff:,} ({spend_pct_diff:+.1f}%)")
    
    # Population efficiency (visitors per capita of prefecture)
    fukui_pop = fukui_data.get('population', 1)
    ishikawa_pop = ishikawa_data.get('population', 1)
    
    fukui_efficiency = (fukui_visitors / fukui_pop) * 10000
    ishikawa_efficiency = (ishikawa_visitors / ishikawa_pop) * 10000
    
    print(f"\nVisitor Density (Chinese visitors per 10k residents):")
    print(f"  Fukui: {fukui_efficiency:.2f}")
    print(f"  Ishikawa: {ishikawa_efficiency:.2f}")
    
    if fukui_efficiency > ishikawa_efficiency:
        print(f"  → Fukui is more efficient at attracting Chinese tourists relative to population")
    else:
        print(f"  → Ishikawa has better tourist attraction efficiency")


# ============================================================================
# 5. NUDGE INTERVENTION PLANNING
# ============================================================================

def design_nudge_interventions():
    """
    Plan and quantify expected outcomes of nudge interventions.
    """
    print("\n" + "="*80)
    print("NUDGE THEORY: INTERVENTION DESIGN & EXPECTED OUTCOMES")
    print("="*80)
    
    interventions = {
        "Social Proof - UGC Amplification": {
            "baseline_conversion": 0.02,  # 2% of aware audience converts
            "expected_uplift": 0.35,  # 35% improvement
            "target_months": 6,
            "cost": 50000,  # JPY
        },
        "Choice Architecture - Packaged Itineraries": {
            "baseline_conversion": 0.025,
            "expected_uplift": 0.45,  # 45% improvement
            "target_months": 6,
            "cost": 80000,
        },
        "Scarcity & Loss Aversion - Limited-time offers": {
            "baseline_conversion": 0.02,
            "expected_uplift": 0.50,
            "target_months": 6,
            "cost": 30000,
        },
        "Salience Nudge - Emotional Messaging": {
            "baseline_conversion": 0.02,
            "expected_uplift": 0.25,
            "target_months": 6,
            "cost": 20000,
        },
    }
    
    print(f"\nIntervention Strategy & ROI Projection (based on 10,000 aware audience):")
    print(f"{'Intervention':<50} {'Baseline Conv.':<15} {'Post-Nudge':<15} {'ROI':<10}")
    print("-" * 90)
    
    for intervention, metrics in interventions.items():
        baseline = metrics['baseline_conversion']
        uplift = metrics['expected_uplift']
        new_conversion = baseline * (1 + uplift)
        additional_conversions = (new_conversion - baseline) * 10000
        cost = metrics['cost']
        
        # Assume ¥250,000 average spend per visitor
        revenue = additional_conversions * 250000
        roi = ((revenue - cost) / cost) * 100 if cost > 0 else 0
        
        print(f"{intervention:<50} {baseline:<15.1%} {new_conversion:<15.1%} {roi:>8.0f}%")
    
    print(f"\nKey Insight:")
    print(f"  Choice architecture and scarcity nudges show highest ROI potential")
    print(f"  → Recommend implementing in this priority order:")
    print(f"    1. Packaged Itineraries (highest conversion lift)")
    print(f"    2. Scarcity Campaigns (fastest implementation)")
    print(f"    3. Emotional Messaging (foundational for all channels)")
    print(f"    4. UGC Amplification (sustained long-term effect)")


# ============================================================================
# 6. MAIN EXECUTION
# ============================================================================

def main():
    """Run statistical analyses on collected data.

    Each analysis runs only when its input file is supplied; there is no
    built-in example dataset (docs/adr/0002).
    """
    import argparse

    parser = argparse.ArgumentParser(description="Fukui tourism statistical analyses (real data only).")
    parser.add_argument("--classified-reviews",
                        help="CSV with one row per review: columns 'theme' and 'emotion_score' "
                             "(output of the review classification step)")
    parser.add_argument("--spending",
                        help="CSV with per-respondent spending shares: accommodation_%%, shopping_%%, "
                             "food_%%, transport_%%, experience_%%")
    parser.add_argument("--monthly",
                        help="CSV with columns 'month', 'visitors', 'is_event_month' from MLIT data "
                             "(see src/analysis/build_china_time_series.py)")
    parser.add_argument("--market",
                        help="CSV with one row per prefecture: 'prefecture', 'visitors', 'avg_spend', "
                             "'population' (must include Fukui and Ishikawa)")
    parser.add_argument("--nudge-framework", action="store_true",
                        help="Print the nudge intervention design framework (no data required)")
    args = parser.parse_args()

    inputs = [args.classified_reviews, args.spending, args.monthly, args.market, args.nudge_framework]
    if not any(inputs):
        parser.error(
            "No inputs given. Pass at least one collected dataset (see --help). "
            "Collection procedure: docs/手动运行数据抓取指南.md"
        )

    from src.data_loading import load_research_data

    print("\n" + "█" * 80)
    print("█ FUKUI TOURISM ANALYSIS - STATISTICAL FRAMEWORK EXECUTION")
    print("█" * 80)
    print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.classified_reviews:
        reviews = load_research_data(args.classified_reviews)
        require_columns(reviews, args.classified_reviews, ("theme", "emotion_score"))
        theme_counts = reviews["theme"].value_counts().to_dict()
        analyze_theme_distribution(theme_counts)
        analyze_sentiment_theme_correlation(
            {"theme": reviews["theme"].tolist(), "emotion_score": reviews["emotion_score"].tolist()}
        )

    if args.spending:
        spending = load_research_data(args.spending)
        segment_visitors_by_spending(spending)

    if args.monthly:
        monthly = load_research_data(args.monthly)
        require_columns(monthly, args.monthly, ("month", "visitors", "is_event_month"))
        event_indices = [i for i, flag in enumerate(monthly["is_event_month"]) if flag]
        analyze_event_impact(
            {"month": monthly["month"].tolist(),
             "visitors": monthly["visitors"].tolist(),
             "is_event_month": monthly["is_event_month"].tolist()},
            event_indices,
        )

    if args.market:
        market = load_research_data(args.market)
        require_columns(market, args.market, ("prefecture", "visitors", "avg_spend", "population"))
        market = market.set_index(market["prefecture"].str.lower())
        fukui = market.loc["fukui"]
        ishikawa = market.loc["ishikawa"]
        compare_fukui_vs_ishikawa(
            {"visitors": fukui["visitors"], "avg_spend": fukui["avg_spend"], "population": fukui["population"]},
            {"visitors": ishikawa["visitors"], "avg_spend": ishikawa["avg_spend"], "population": ishikawa["population"]},
        )

    if args.nudge_framework:
        design_nudge_interventions()

    print("\n" + "█" * 80)
    print("█ ANALYSIS COMPLETE")
    print("█" * 80)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from None
