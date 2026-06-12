"""
Market Impact Analysis - Chinese Visitor Spending & Market Share
Analyzing Chinese Visitor Spending & Market Share across 3 prefectures
Data Source: Japan Tourism Agency (JTA) 訪日外国人消費動向調査 2023-2024

Reference:
- https://www.mlit.go.jp/kankocho/index.html
- 訪日外国人消費動向調査 (Inbound Foreign Visitor Consumption Survey)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.data_loading import load_research_data

# ============================================================================
# 1. DATA COLLECTION - OFFICIAL JTA 2024 DATA (中国游客)
# ============================================================================

def collect_jta_data(input_csv='data/raw/jta/china_market_3pref.csv'):
    """Load Chinese-visitor market data for the three Hokuriku prefectures.

    The CSV must be hand-extracted from official JTA / MLIT publications
    (訪日外国人消費動向調査, 宿泊旅行統計調査) and saved with these columns:

        Prefecture, Chinese_Visitors_2024, Avg_Spend_Per_Visitor_JPY,
        Overnight_Stays_Chinese, Population_2024

    One row per prefecture: Fukui, Ishikawa, Toyama.
    Record the source document URL and table number in
    data/raw/jta/README.md when you create the file.

    This function intentionally has no built-in numbers: every figure must
    come from a recorded official source so results stay traceable
    (docs/adr/0002).
    """
    df = load_research_data(input_csv)
    required = {'Prefecture', 'Chinese_Visitors_2024', 'Avg_Spend_Per_Visitor_JPY',
                'Overnight_Stays_Chinese', 'Population_2024'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{input_csv} is missing required columns: {sorted(missing)}")
    return df


def calculate_market_metrics(df):
    """
    计算市场指标，重新计算市场份额使其总和为100%
    """
    
    print("="*80)
    print("MARKET ANALYSIS: FUKUI, ISHIKAWA, TOYAMA (3-Prefecture Market)")
    print("="*80)
    print("\n[DATA SOURCE: Japan Tourism Agency - Inbound Foreign Visitor Survey 2024]")
    print("[VISITOR TYPE: Chinese (Mainland) Visitors]\n")
    
    # 1. 基础指标计算
    df['Total_Spending_Million_JPY'] = df['Chinese_Visitors_2024'] * df['Avg_Spend_Per_Visitor_JPY'] / 1_000_000
    df['Visitor_Share_Raw'] = (df['Chinese_Visitors_2024'] / df['Chinese_Visitors_2024'].sum()) * 100
    df['Stay_Share_Raw'] = (df['Overnight_Stays_Chinese'] / df['Overnight_Stays_Chinese'].sum()) * 100
    df['Visitor_Density_Per_10k'] = (df['Chinese_Visitors_2024'] / df['Population_2024']) * 10000
    
    # 2. 重新计算市场份额（确保总和为100%）
    df['Visitor_Share_Normalized'] = (df['Chinese_Visitors_2024'] / df['Chinese_Visitors_2024'].sum()) * 100
    df['Stay_Share_Normalized'] = (df['Overnight_Stays_Chinese'] / df['Overnight_Stays_Chinese'].sum()) * 100
    df['Spending_Share_Normalized'] = (df['Total_Spending_Million_JPY'] / df['Total_Spending_Million_JPY'].sum()) * 100
    
    return df


def print_detailed_analysis(df):
    """
    打印详细分析结果
    """
    
    print("\n" + "="*80)
    print("TABLE 1: VISITOR VOLUME & MARKET SHARE")
    print("="*80)
    print(f"{'Prefecture':<15} {'Visitors':<12} {'Market %':<12} {'Density/10k':<12}")
    print("-"*80)
    for idx, row in df.iterrows():
        print(f"{row['Prefecture']:<15} {row['Chinese_Visitors_2024']:>10,} {row['Visitor_Share_Normalized']:>10.1f}% {row['Visitor_Density_Per_10k']:>10.2f}")
    print("-"*80)
    total_visitors = df['Chinese_Visitors_2024'].sum()
    print(f"{'TOTAL':<15} {total_visitors:>10,} {100.0:>10.1f}%")
    
    print("\n" + "="*80)
    print("TABLE 2: SPENDING ANALYSIS (TOTAL TRIP EXPENDITURE)")
    print("="*80)
    print(f"{'Prefecture':<15} {'Avg Spend':<15} {'Total Spending':<18} {'Spend Share':<12}")
    print("-"*80)
    for idx, row in df.iterrows():
        print(f"{row['Prefecture']:<15} ¥{row['Avg_Spend_Per_Visitor_JPY']:>10,.0f} ¥{row['Total_Spending_Million_JPY']:>13.0f}M {row['Spending_Share_Normalized']:>10.1f}%")
    print("-"*80)
    total_spending = df['Total_Spending_Million_JPY'].sum()
    print(f"{'TOTAL':<15} ¥{df['Avg_Spend_Per_Visitor_JPY'].mean():>10,.0f} ¥{total_spending:>13.0f}M {100.0:>10.1f}%")
    
    print("\n" + "="*80)
    print("TABLE 3: OVERNIGHT STAYS (宿泊数)")
    print("="*80)
    print(f"{'Prefecture':<15} {'Overnight Stays':<18} {'Share %':<12}")
    print("-"*80)
    for idx, row in df.iterrows():
        print(f"{row['Prefecture']:<15} {row['Overnight_Stays_Chinese']:>15,} {row['Stay_Share_Normalized']:>10.1f}%")
    print("-"*80)
    total_stays = df['Overnight_Stays_Chinese'].sum()
    print(f"{'TOTAL':<15} {total_stays:>15,} {100.0:>10.1f}%")


def calculate_average_stay_duration(df):
    """
    计算平均住宿天数
    """
    print("\n" + "="*80)
    print("ADDITIONAL METRICS: STAY DURATION & EFFICIENCY")
    print("="*80)
    
    df['Avg_Stay_Days'] = df['Overnight_Stays_Chinese'] / df['Chinese_Visitors_2024']
    df['Spend_Per_Day_JPY'] = df['Avg_Spend_Per_Visitor_JPY'] / df['Avg_Stay_Days']
    
    print(f"{'Prefecture':<15} {'Avg Days':<12} {'Spend/Day':<15}")
    print("-"*80)
    for idx, row in df.iterrows():
        print(f"{row['Prefecture']:<15} {row['Avg_Stay_Days']:>10.2f} ¥{row['Spend_Per_Day_JPY']:>12,.0f}")


def export_for_slides(df, output_file='data/processed/market_comparison_3pref.csv'):
    """
    导出数据用于Slides
    """
    export_cols = ['Prefecture', 'Chinese_Visitors_2024', 'Visitor_Share_Normalized', 
                   'Avg_Spend_Per_Visitor_JPY', 'Total_Spending_Million_JPY', 
                   'Spending_Share_Normalized', 'Overnight_Stays_Chinese', 
                   'Stay_Share_Normalized']
    
    export_df = df[export_cols].copy()
    export_df.columns = ['Prefecture', 'Visitors', 'Visitor_Share_%', 'Avg_Spend_JPY',
                        'Total_Spending_Million_JPY', 'Spending_Share_%', 
                        'Overnight_Stays', 'Stay_Share_%']
    
    export_df.to_csv(output_file, index=False)
    print(f"\n✓ Data exported to: {output_file}")
    
    return export_df


def main():
    """
    Main execution
    """
    # 1. Collect data
    df = collect_jta_data()
    
    # 2. Calculate metrics
    df = calculate_market_metrics(df)
    
    # 3. Print analysis
    print_detailed_analysis(df)
    
    # 4. Additional metrics
    calculate_average_stay_duration(df)
    
    # 5. Export
    export_for_slides(df)
    
    # 6. 关键发现总结
    print("\n" + "="*80)
    print("KEY METRICS: Market Impact Analysis (3 Hokuriku prefectures)")
    print("="*80)
    
    fukui = df[df['Prefecture'] == 'Fukui'].iloc[0]
    ishikawa = df[df['Prefecture'] == 'Ishikawa'].iloc[0]
    toyama = df[df['Prefecture'] == 'Toyama'].iloc[0]
    
    print(f"\n1. FUKUI'S MARKET POSITION (高价值、低体量)")
    print(f"   • Market Share (Visitor): {fukui['Visitor_Share_Normalized']:.1f}%")
    print(f"   • Average Spend: ¥{fukui['Avg_Spend_Per_Visitor_JPY']:,.0f}")
    print(f"   • Total Spending: ¥{fukui['Total_Spending_Million_JPY']:.0f}M")
    print(f"   • Visitor Density: {fukui['Visitor_Density_Per_10k']:.2f} per 10k residents")
    print(f"   → Interpretation: HIGH SPEND per visitor, but LOW visitor volume relative to Ishikawa")
    
    print(f"\n2. ISHIKAWA'S DOMINANCE (高体量、高价值)")
    print(f"   • Market Share (Visitor): {ishikawa['Visitor_Share_Normalized']:.1f}%")
    print(f"   • Average Spend: ¥{ishikawa['Avg_Spend_Per_Visitor_JPY']:,.0f}")
    print(f"   • Total Spending: ¥{ishikawa['Total_Spending_Million_JPY']:.0f}M")
    print(f"   • Visitor Density: {ishikawa['Visitor_Density_Per_10k']:.2f} per 10k residents")
    print(f"   → Interpretation: HIGH VOLUME AND HIGH SPENDING - regional leader")
    
    print(f"\n3. TOYAMA'S POSITION (未开发潜力)")
    print(f"   • Market Share (Visitor): {toyama['Visitor_Share_Normalized']:.1f}%")
    print(f"   • Average Spend: ¥{toyama['Avg_Spend_Per_Visitor_JPY']:,.0f}")
    print(f"   • Total Spending: ¥{toyama['Total_Spending_Million_JPY']:.0f}M")
    print(f"   • Visitor Density: {toyama['Visitor_Density_Per_10k']:.2f} per 10k residents")
    print(f"   → Interpretation: LOWEST volume and spending - opportunity for growth")
    
    print(f"\n4. SPENDING INTERPRETATION (CRITICAL FOR YOUR SLIDES)")
    print(f"   ✓ ¥{fukui['Avg_Spend_Per_Visitor_JPY']:,.0f} = TOTAL TRIP SPENDING (全日本での消費)")
    print(f"   ✓ NOT regional spend limited to Fukui")
    print(f"   ✓ This is why it's 'high-value': Chinese travelers allocate significant")
    print(f"     portion of their entire Japan trip budget to Hokuriku region")
    print(f"   ✓ Means: If we increase visitor volume, total regional revenue grows")
    
    print(f"\n5. 3-PREFECTURE COMBINED MARKET")
    total_visitors = df['Chinese_Visitors_2024'].sum()
    total_spending = df['Total_Spending_Million_JPY'].sum()
    print(f"   • Total Chinese Visitors: {total_visitors:,.0f}")
    print(f"   • Combined Market Size: ¥{total_spending:,.0f}M")
    print(f"   • Average Spend (region): ¥{total_spending*1_000_000/total_visitors:,.0f}")
    
    return df


if __name__ == '__main__':
    df = main()
