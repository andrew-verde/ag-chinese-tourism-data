"""
Generate a single slide-ready quadrant visualization for Hokuriku Chinese visitor positioning.
"""

import matplotlib.pyplot as plt
import pandas as pd

# Data from current project analysis
data = {
    'Prefecture': ['Fukui', 'Ishikawa', 'Toyama'],
    'Chinese_Visitors': [8200, 17651, 4800],
    'Avg_Spend_JPY': [265000, 255000, 248000],
}

# Create DataFrame
df = pd.DataFrame(data)

df['Total_Spending_Million'] = df['Chinese_Visitors'] * df['Avg_Spend_JPY'] / 1_000_000

df['Visitor_Share_%'] = (df['Chinese_Visitors'] / df['Chinese_Visitors'].sum()) * 100

df['Spend_Share_%'] = (df['Total_Spending_Million'] / df['Total_Spending_Million'].sum()) * 100

# Plot settings
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 9), constrained_layout=True)

# Quadrant thresholds
x_mid = df['Chinese_Visitors'].mean()
y_mid = df['Avg_Spend_JPY'].mean()

ax.scatter(df['Chinese_Visitors'], df['Avg_Spend_JPY'],
           s=df['Total_Spending_Million'] * 40,
           color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
           edgecolors='black', linewidth=1.5)

for i, row in df.iterrows():
    ax.text(row['Chinese_Visitors'] * 1.03, row['Avg_Spend_JPY'] * 0.998,
            f"{row['Prefecture']}\n{row['Chinese_Visitors']:,}人\n¥{row['Avg_Spend_JPY']:,}",
            fontsize=11, fontweight='bold', va='center')

# Add quadrant lines
ax.axvline(x=x_mid, color='gray', linestyle='--', linewidth=1.2)
ax.axhline(y=y_mid, color='gray', linestyle='--', linewidth=1.2)

# Quadrant labels
ax.text(0.96, 0.92, 'High Value / High Volume\n(区域领导者)', transform=ax.transAxes,
        ha='right', va='center', fontsize=12, fontweight='bold', color='#4ECDC4')
ax.text(0.03, 0.92, 'High Value / Low Volume\n(福井: 目标增长)', transform=ax.transAxes,
        ha='left', va='center', fontsize=12, fontweight='bold', color='#FF6B6B')
ax.text(0.03, 0.08, 'Low Value / Low Volume\n(富山: 开发潜力)', transform=ax.transAxes,
        ha='left', va='center', fontsize=12, fontweight='bold', color='#45B7D1')
ax.text(0.96, 0.08, 'Low Value / High Volume\n(未出现)', transform=ax.transAxes,
        ha='right', va='center', fontsize=12, fontweight='bold', color='gray')

ax.set_title('Hokuriku Chinese Visitor Market Positioning\nVolume vs. Value Quadrant', fontsize=20, fontweight='bold')
ax.set_xlabel('Chinese Visitors (2024)', fontsize=14, fontweight='bold')
ax.set_ylabel('Average Spend per Visitor (¥)', fontsize=14, fontweight='bold')

ax.set_xlim(0, 20000)
ax.set_ylim(235000, 275000)
ax.grid(axis='both', linestyle='--', alpha=0.3)

# Add summary table on the right
table_data = df[['Prefecture', 'Chinese_Visitors', 'Visitor_Share_%', 'Avg_Spend_JPY', 'Total_Spending_Million']].copy()
table_data['Chinese_Visitors'] = table_data['Chinese_Visitors'].apply(lambda x: f"{x:,}")
table_data['Avg_Spend_JPY'] = table_data['Avg_Spend_JPY'].apply(lambda x: f"¥{x:,}")
table_data['Total_Spending_Million'] = table_data['Total_Spending_Million'].apply(lambda x: f"¥{x:.0f}M")
table_data['Visitor_Share_%'] = table_data['Visitor_Share_%'].map('{:.1f}%'.format)

table = plt.table(cellText=table_data.values,
                  colLabels=['Prefecture', 'Visitors', 'Share', 'Avg Spend', 'Revenue'],
                  cellLoc='center', colLoc='center',
                  loc='right', bbox=[1.02, 0.15, 0.45, 0.75])

table.auto_set_font_size(False)
table.set_fontsize(10)
for key, cell in table.get_celld().items():
    cell.set_edgecolor('gray')
    if key[0] == 0:
        cell.set_text_props(fontweight='bold')
        cell.set_facecolor('#F0F0F0')

# Footnote
fig.text(0.5, 0.02,
         'Note: Data is from current 2024 market analysis. Visitors are Chinese tourist counts; spend is average total trip spend per visitor.',
         ha='center', fontsize=10, color='gray')

output_path = 'slide_quadrant_positioning.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'✓ Saved: {output_path}')
