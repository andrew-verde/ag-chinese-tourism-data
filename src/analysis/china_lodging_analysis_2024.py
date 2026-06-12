"""
China Visitor Lodging Analysis - Fukui, Toyama, Ishikawa (2024)
================================================================================
分析目标：
1. Average Length of Stay (平均宿泊日数) by prefecture
2. Accommodation Type Distribution (宿泊形態の構成比 %) by prefecture - 以访日游客人数为分母

Data Source: MLIT (Japan Tourism Agency) 2024 Inbound Traveler Survey
宿泊旅行統計調査 2024年度
================================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime

from src.data_loading import load_research_data

# ============================================================================
# SECTION 1: Load or create base data for Chinese visitors
# ============================================================================

def create_base_data(input_csv='data/processed/china_lodging_base_2024.csv'):
    """Load per-prefecture Chinese visitor and overnight-stay counts.

    The CSV must be produced from real MLIT 宿泊旅行統計調査 tables
    (see src/analysis/extract_mlit_china_lodging.py) with columns:

        Prefecture, Prefecture_JP, Pref_Code, China_Visitors, Overnight_Stays

    This function loads a file instead of containing numbers so that every
    figure stays traceable to its source table (docs/adr/0002).
    """
    df = load_research_data(input_csv)
    required = {'Prefecture', 'China_Visitors', 'Overnight_Stays'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{input_csv} is missing required columns: {sorted(missing)}")
    return df

def calculate_stay_metrics(df):
    """
    Calculate average length of stay
    指标：nights per visit（夜/訪問）
    """
    df['Avg_Stay_Days'] = df['Overnight_Stays'] / df['China_Visitors']
    df['Avg_Stay_Days'] = df['Avg_Stay_Days'].round(3)
    return df

# ============================================================================
# SECTION 2: Accommodation type distribution
# ============================================================================

def load_lodging_distribution(df, input_csv='data/processed/china_lodging_distribution_2024.csv'):
    """Load accommodation-type shares (%) per prefecture from real MLIT data.

    Required columns: Prefecture, Hotel_pct, Ryokan_pct, Minshuku_pct, Other_pct.
    Shares must come from actual 宿泊旅行統計調査 tables, not estimated
    patterns (docs/adr/0002).
    """
    lodging_types = load_research_data(input_csv)
    required = {'Prefecture', 'Hotel_pct', 'Ryokan_pct', 'Minshuku_pct', 'Other_pct'}
    missing = required - set(lodging_types.columns)
    if missing:
        raise ValueError(f"{input_csv} is missing required columns: {sorted(missing)}")

    lodging_types = lodging_types.reset_index(drop=True)
    for pref_idx, pref in enumerate(lodging_types['Prefecture']):
        visitors = df.loc[df['Prefecture'] == pref, 'China_Visitors'].values[0]
        for kind in ('Hotel', 'Ryokan', 'Minshuku', 'Other'):
            lodging_types.loc[pref_idx, f'{kind}_Count'] = (
                visitors * lodging_types.loc[pref_idx, f'{kind}_pct'] / 100
            )
    return lodging_types

# ============================================================================
# SECTION 3: Generate outputs
# ============================================================================

def generate_report(df, lodging_df):
    """
    Generate formatted report with both analyses
    """
    
    print("\n" + "="*90)
    print("ANALYSIS 1: AVERAGE LENGTH OF STAY (平均宿泊日数)")
    print("China Visitors to Fukui, Toyama, Ishikawa (2024)")
    print("="*90)
    print(f"\nMetric: nights per visit (夜/訪問)")
    print(f"Denominator: Number of China visitor arrivals")
    print(f"Formula: Overnight_Stays / China_Visitors\n")
    
    print(f"{'Prefecture':<15} {'Visitors':<12} {'Overnight Stays':<18} {'Avg Stay (nights)':<18}")
    print("-"*90)
    for idx, row in df.iterrows():
        print(f"{row['Prefecture']:<15} {row['China_Visitors']:>10,} {row['Overnight_Stays']:>16,} {row['Avg_Stay_Days']:>16.3f}")
    print("-"*90)
    
    print("\n" + "="*90)
    print("ANALYSIS 2: ACCOMMODATION TYPE DISTRIBUTION (宿泊形態の構成比)")
    print("China Visitors to Fukui, Toyama, Ishikawa (2024)")
    print("="*90)
    print(f"\nMetric: % share by accommodation type (宿泊形態別構成比)")
    print(f"Denominator: Number of China visitor arrivals (by prefecture)")
    print(f"Source: MLIT 宿泊旅行統計調査 2024 (data/processed/china_lodging_distribution_2024.csv)\n")
    
    for pref in df['Prefecture']:
        pref_data = lodging_df[lodging_df['Prefecture'] == pref].iloc[0]
        visitors = df[df['Prefecture'] == pref].iloc[0]['China_Visitors']
        
        print(f"\n{pref}県 (Fukui Prefecture)" if pref == 'Fukui' else f"\n{pref}県 (Toyama Prefecture)" if pref == 'Toyama' else f"\n{pref}県 (Ishikawa Prefecture)")
        print(f"Total China Visitors: {visitors:,}")
        print("-" * 70)
        print(f"{'Accommodation Type':<25} {'Count':<12} {'Percentage':<15}")
        print("-" * 70)
        print(f"{'Hotel (ホテル)':<25} {pref_data['Hotel_Count']:>10,.0f} {pref_data['Hotel_pct']:>13.1f}%")
        print(f"{'Ryokan (旅館)':<25} {pref_data['Ryokan_Count']:>10,.0f} {pref_data['Ryokan_pct']:>13.1f}%")
        print(f"{'Minshuku (民宿)':<25} {pref_data['Minshuku_Count']:>10,.0f} {pref_data['Minshuku_pct']:>13.1f}%")
        print(f"{'Other (その他)':<25} {pref_data['Other_Count']:>10,.0f} {pref_data['Other_pct']:>13.1f}%")
        print("-" * 70)
        total_pct = pref_data['Hotel_pct'] + pref_data['Ryokan_pct'] + pref_data['Minshuku_pct'] + pref_data['Other_pct']
        print(f"{'TOTAL':<25} {visitors:>10,} {total_pct:>13.1f}%")

def export_csv(df, lodging_df):
    """
    Export analysis results to CSV for further use
    """
    
    # Export 1: Average stay by prefecture
    stay_export = df[['Prefecture', 'China_Visitors', 'Overnight_Stays', 'Avg_Stay_Days']].copy()
    stay_export.to_csv('data/processed/analysis_1_avg_stay_days.csv', index=False)
    print(f"\n✓ Exported: analysis_1_avg_stay_days.csv")
    
    # Export 2: Accommodation distribution by prefecture
    lodging_export = lodging_df[['Prefecture', 'Hotel_pct', 'Ryokan_pct', 'Minshuku_pct', 'Other_pct']].copy()
    lodging_export.columns = ['Prefecture', 'Hotel (%)', 'Ryokan (%)', 'Minshuku (%)', 'Other (%)']
    lodging_export.to_csv('data/processed/analysis_2_accommodation_distribution.csv', index=False)
    print(f"✓ Exported: analysis_2_accommodation_distribution.csv")
    
    # Combined export
    combined = df.merge(lodging_df, on='Prefecture')
    combined.to_csv('data/processed/china_visitor_analysis_2024_combined.csv', index=False)
    print(f"✓ Exported: china_visitor_analysis_2024_combined.csv")

def main():
    """Main execution"""
    print("\n" + "="*90)
    print("CHINA VISITOR LODGING ANALYSIS - 2024")
    print("="*90)
    
    # Create base data
    df = create_base_data()
    print("\n✓ Base data loaded: China visitors to 3 prefectures")
    
    # Calculate stay metrics
    df = calculate_stay_metrics(df)
    print("✓ Calculated: Average length of stay")
    
    # Estimate accommodation distribution
    lodging_df = load_lodging_distribution(df)
    print("✓ Estimated: Accommodation type distribution")
    
    # Generate report
    generate_report(df, lodging_df)
    
    # Export results
    print("\n" + "="*90)
    print("EXPORTING RESULTS")
    print("="*90)
    export_csv(df, lodging_df)
    
    print("\n" + "="*90)
    print("ANALYSIS COMPLETE")
    print("="*90)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nData Source: MLIT 訪日外国人消費動向調査 2024年度")
    print("Visitor Type: China (Mainland) visitors only (中国大陸からの訪日者のみ)")

if __name__ == '__main__':
    main()
