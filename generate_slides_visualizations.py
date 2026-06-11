"""
Generate Visualizations for Statistical Journey 3: Impact & Market
用于Slides的可视化图表生成脚本
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 读取数据
data = {
    'Prefecture': ['Fukui', 'Ishikawa', 'Toyama'],
    'Visitors': [8200, 17651, 4800],
    'Visitor_Share_%': [26.75, 57.59, 15.66],
    'Avg_Spend_JPY': [265000, 255000, 248000],
    'Total_Spending_Million_JPY': [2173.0, 4501.0, 1190.4],
    'Spending_Share_%': [27.63, 57.23, 15.14],
}

df = pd.DataFrame(data)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# Figure 1: 市场份额分布 (Market Share - Pie Charts)
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Statistical Journey 3: Chinese Visitor Market Distribution', 
             fontsize=14, fontweight='bold', y=0.98)

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

# Pie chart 1: Visitor share
ax1 = axes[0]
wedges, texts, autotexts = ax1.pie(df['Visitor_Share_%'], 
                                     labels=df['Prefecture'],
                                     autopct='%1.1f%%',
                                     colors=colors,
                                     startangle=90,
                                     textprops={'fontsize': 11, 'weight': 'bold'})
ax1.set_title('Visitor Share\n(Chinese Visitors Distribution)', fontsize=12, fontweight='bold', pad=10)

# Make percentage text more visible
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_weight('bold')

# Pie chart 2: Spending share
ax2 = axes[1]
wedges, texts, autotexts = ax2.pie(df['Spending_Share_%'], 
                                     labels=df['Prefecture'],
                                     autopct='%1.1f%%',
                                     colors=colors,
                                     startangle=90,
                                     textprops={'fontsize': 11, 'weight': 'bold'})
ax2.set_title('Spending Share\n(Total Market Revenue)', fontsize=12, fontweight='bold', pad=10)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_weight('bold')

plt.tight_layout()
plt.savefig('slide_1_market_share.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_1_market_share.png")
plt.close()

# ============================================================================
# Figure 2: 访客数量对比 (Visitor Volume Comparison)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(df))
width = 0.35

bars1 = ax.bar(x - width/2, df['Visitors'], width, 
               label='Number of Visitors', color='#FF6B6B', alpha=0.8)
ax.axhline(y=df['Visitors'].mean(), color='red', linestyle='--', 
           linewidth=2, alpha=0.7, label=f'Average: {df["Visitors"].mean():.0f}')

ax.set_ylabel('Number of Visitors', fontsize=12, fontweight='bold')
ax.set_title('Chinese Visitor Volume by Prefecture (2024)', 
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df['Prefecture'], fontsize=11, fontweight='bold')
ax.legend(fontsize=10)

# Add value labels on bars
for i, (idx, row) in enumerate(df.iterrows()):
    ax.text(i - width/2, row['Visitors'] + 300, f"{row['Visitors']:,}", 
            ha='center', va='bottom', fontweight='bold', fontsize=11)

# Add market share percentage
for i, (idx, row) in enumerate(df.iterrows()):
    ax.text(i - width/2, row['Visitors']/2, f"{row['Visitor_Share_%']:.1f}%", 
            ha='center', va='center', fontweight='bold', fontsize=10, color='white')

ax.set_ylim(0, max(df['Visitors']) * 1.15)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('slide_2_visitor_volume.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_2_visitor_volume.png")
plt.close()

# ============================================================================
# Figure 3: 平均消费对比 (Average Spending Comparison)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(df['Prefecture'], df['Avg_Spend_JPY']/1000, 
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_ylabel('Average Spending (¥ Thousands)', fontsize=12, fontweight='bold')
ax.set_title('Average Spending per Chinese Visitor (2024)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, 300)

# Add value labels and ranking
for i, (idx, row) in enumerate(df.iterrows()):
    height = row['Avg_Spend_JPY']/1000
    ax.text(i, height + 5, f"¥{row['Avg_Spend_JPY']:,.0f}", 
            ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add ranking
    if row['Avg_Spend_JPY'] == df['Avg_Spend_JPY'].max():
        ax.text(i, height - 20, '🥇 HIGHEST', 
                ha='center', va='top', fontweight='bold', fontsize=9, color='gold')
    elif row['Avg_Spend_JPY'] == df['Avg_Spend_JPY'].min():
        ax.text(i, height - 20, '🥉 LOWEST', 
                ha='center', va='top', fontweight='bold', fontsize=9, color='lightblue')

# Add average line
avg_spend = df['Avg_Spend_JPY'].mean()
ax.axhline(y=avg_spend/1000, color='green', linestyle='--', 
           linewidth=2, alpha=0.7, label=f'Regional Avg: ¥{avg_spend:,.0f}')
ax.legend(fontsize=10)

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('slide_3_avg_spending.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_3_avg_spending.png")
plt.close()

# ============================================================================
# Figure 4: 总收入对比 (Total Revenue Comparison)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(df['Prefecture'], df['Total_Spending_Million_JPY'], 
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_ylabel('Total Spending (¥ Millions)', fontsize=12, fontweight='bold')
ax.set_title('Total Market Revenue - Chinese Visitors (2024)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_ylim(0, max(df['Total_Spending_Million_JPY']) * 1.2)

# Add value labels
for i, (idx, row) in enumerate(df.iterrows()):
    height = row['Total_Spending_Million_JPY']
    ax.text(i, height + 100, f"¥{height:.0f}M\n({row['Spending_Share_%']:.1f}%)", 
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# Add total line
total = df['Total_Spending_Million_JPY'].sum()
ax.text(0.5, 0.95, f'Total Market: ¥{total:.0f}M', 
        transform=ax.transAxes, ha='center', va='top',
        fontsize=12, fontweight='bold', 
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('slide_4_total_revenue.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_4_total_revenue.png")
plt.close()

# ============================================================================
# Figure 5: 关键指标仪表板 (KPI Dashboard)
# ============================================================================

fig = plt.figure(figsize=(14, 8))
fig.suptitle('Statistical Journey 3: Key Performance Indicators', 
             fontsize=16, fontweight='bold', y=0.98)

# Create 2x2 grid
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

# Panel 1: Market Dominance (Ishikawa)
ax1 = fig.add_subplot(gs[0, 0])
ax1.text(0.5, 0.8, 'MARKET LEADER', ha='center', fontsize=14, fontweight='bold', color='#4ECDC4')
ax1.text(0.5, 0.6, 'Ishikawa', ha='center', fontsize=16, fontweight='bold')
ax1.text(0.5, 0.4, '17,651 Visitors\n57.6% Market Share\n¥4,501M Revenue', 
         ha='center', fontsize=11, fontweight='bold', 
         bbox=dict(boxstyle='round', facecolor='#4ECDC4', alpha=0.3))
ax1.axis('off')

# Panel 2: Fukui Position (Premium Secondary)
ax2 = fig.add_subplot(gs[0, 1])
ax2.text(0.5, 0.8, 'PREMIUM SECONDARY', ha='center', fontsize=14, fontweight='bold', color='#FF6B6B')
ax2.text(0.5, 0.6, 'Fukui', ha='center', fontsize=16, fontweight='bold')
ax2.text(0.5, 0.4, '8,200 Visitors\n26.8% Market Share\n¥265k Avg Spend (HIGHEST)', 
         ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='#FF6B6B', alpha=0.3))
ax2.axis('off')

# Panel 3: Toyama (Growth Opportunity)
ax3 = fig.add_subplot(gs[1, 0])
ax3.text(0.5, 0.8, 'GROWTH OPPORTUNITY', ha='center', fontsize=14, fontweight='bold', color='#45B7D1')
ax3.text(0.5, 0.6, 'Toyama', ha='center', fontsize=16, fontweight='bold')
ax3.text(0.5, 0.4, '4,800 Visitors\n15.7% Market Share\n¥248k Avg Spend', 
         ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='#45B7D1', alpha=0.3))
ax3.axis('off')

# Panel 4: Strategic Insight
ax4 = fig.add_subplot(gs[1, 1])
ax4.text(0.5, 0.85, 'STRATEGIC INSIGHT', ha='center', fontsize=14, fontweight='bold')
insight_text = ('Fukui attracts affluent travelers\nbut at lower volume than Ishikawa.\n\n'
                'Growth strategy: Increase volume\nwhile maintaining premium positioning.\n\n'
                '+20% visitors = +¥435M revenue')
ax4.text(0.5, 0.42, insight_text, ha='center', va='center', fontsize=10, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
ax4.axis('off')

plt.savefig('slide_5_kpi_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_5_kpi_dashboard.png")
plt.close()

# ============================================================================
# Figure 6: 增长情景 (Growth Scenario)
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 7))

scenarios = ['Current\n(2024)', '+10%\nVisitors', '+15%\nVisitors', '+20%\nVisitors']
fukui_visitors = [8200, 8200*1.1, 8200*1.15, 8200*1.2]
fukui_revenue = [2173, 2173*1.1, 2173*1.15, 2173*1.2]

x = np.arange(len(scenarios))
width = 0.35

ax2_1 = ax
ax2_2 = ax.twinx()

bars1 = ax2_1.bar(x - width/2, fukui_visitors, width, label='Visitors', 
                  color='#FF6B6B', alpha=0.8)
bars2 = ax2_2.bar(x + width/2, fukui_revenue, width, label='Revenue (¥M)', 
                  color='#4ECDC4', alpha=0.8)

ax2_1.set_ylabel('Number of Visitors', fontsize=12, fontweight='bold', color='#FF6B6B')
ax2_2.set_ylabel('Total Revenue (¥ Millions)', fontsize=12, fontweight='bold', color='#4ECDC4')
ax2_1.set_title('Fukui Growth Scenarios: Impact of Increased Visitor Volume', 
                fontsize=14, fontweight='bold', pad=15)
ax2_1.set_xticks(x)
ax2_1.set_xticklabels(scenarios, fontsize=11, fontweight='bold')

# Add value labels
for i, (v, r) in enumerate(zip(fukui_visitors, fukui_revenue)):
    ax2_1.text(i - width/2, v + 200, f"{v:,.0f}", ha='center', va='bottom', 
              fontweight='bold', fontsize=10, color='#FF6B6B')
    ax2_2.text(i + width/2, r + 50, f"¥{r:.0f}M", ha='center', va='bottom', 
              fontweight='bold', fontsize=10, color='#4ECDC4')

# Add delta calculations
for i in range(1, len(scenarios)):
    delta_v = fukui_visitors[i] - fukui_visitors[0]
    delta_r = fukui_revenue[i] - fukui_revenue[0]
    ax2_1.text(i, max(fukui_visitors)*0.5, f'+{delta_v:,.0f}\n+¥{delta_r:.0f}M', 
              ha='center', va='center', fontweight='bold', fontsize=9,
              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Legend
lines1, labels1 = ax2_1.get_legend_handles_labels()
lines2, labels2 = ax2_2.get_legend_handles_labels()
ax2_1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

ax2_1.set_ylim(0, max(fukui_visitors) * 1.3)
ax2_2.set_ylim(0, max(fukui_revenue) * 1.3)
ax2_1.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('slide_6_growth_scenarios.png', dpi=300, bbox_inches='tight')
print("✓ Saved: slide_6_growth_scenarios.png")
plt.close()

print("\n" + "="*80)
print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*80)
print("\nFiles created for your slides:")
print("  1. slide_1_market_share.png - Market distribution pie charts")
print("  2. slide_2_visitor_volume.png - Visitor volume comparison")
print("  3. slide_3_avg_spending.png - Average spending comparison")
print("  4. slide_4_total_revenue.png - Total revenue comparison")
print("  5. slide_5_kpi_dashboard.png - Strategic KPI summary")
print("  6. slide_6_growth_scenarios.png - Growth impact scenarios")
print("\nAll images are 300 DPI, suitable for presentations.")
