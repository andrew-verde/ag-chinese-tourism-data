"""
Extract China visitor lodging data from MLIT Excel files
目标：为福井、富山、石川三县计算：
1. 平均宿泊日数（nights/visit）
2. 宿泊形態の構成比（%）- 分母为访日游客人数
"""
import pandas as pd
import os
from pathlib import Path
import re

# Key metrics to extract
TARGET_PREFS = ['福井', '富山', '石川']
DATA_DIR = 'data/raw/mlit'
CHINA_KEYWORDS = ['中国', '中国人', 'チャイナ', 'China']
LODGING_TYPES = ['ホテル', '旅館', '民宿', '簡易宿所', 'ゲストハウス', 'Airbnb', 'キャンプ']

def scan_all_files():
    """Scan all Excel files and extract China visitor data"""
    results = {}
    
    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xls', '.xlsx'))]
    
    for filename in sorted(excel_files)[-15:]:  # Check most recent files
        filepath = os.path.join(DATA_DIR, filename)
        print(f'\nProcessing {filename}...')
        
        try:
            xls = pd.ExcelFile(filepath)
            
            for sheet_name in xls.sheet_names:
                try:
                    df = xls.parse(sheet_name, header=None, nrows=100)
                    
                    # Convert to string for searching
                    df_str = df.astype(str).values.flatten()
                    full_text = ' '.join(df_str)
                    
                    # Check if sheet contains China and lodging data
                    has_china = any(kw in full_text for kw in CHINA_KEYWORDS)
                    has_lodging = any(lt in full_text for lt in LODGING_TYPES)
                    has_pref = any(p in full_text for p in TARGET_PREFS)
                    
                    if has_china and (has_lodging or has_pref):
                        print(f'  ✓ {sheet_name}: China + lodging/pref data found')
                        
                        # Try to locate China row
                        for i, row in enumerate(df.values):
                            row_str = ' '.join(str(x) for x in row if pd.notna(x))
                            if '中国' in row_str and ('宿泊' in row_str or '日数' in row_str or '形態' in row_str):
                                print(f'    └─ Row {i}: {row_str[:100]}...')
                                
                except Exception as e:
                    pass
                    
        except Exception as e:
            print(f'  Error: {e}')
    
if __name__ == '__main__':
    scan_all_files()
    print('\n--- Scan complete ---')
