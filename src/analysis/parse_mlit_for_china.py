import os
import pandas as pd

DATA_DIR = 'data/raw/mlit'
keywords = ['中国', '中国人', '宿泊', '宿泊日数', '宿泊形態', '宿泊形態の構成比', '宿泊形態別', '宿泊施設']

found = []
for fname in os.listdir(DATA_DIR):
    if not (fname.endswith('.xls') or fname.endswith('.xlsx')):
        continue
    path = os.path.join(DATA_DIR, fname)
    try:
        xls = pd.ExcelFile(path)
    except Exception as e:
        print(f'Failed open: {fname} ({e})')
        continue
    for sheet in xls.sheet_names:
        try:
            df = xls.parse(sheet, nrows=30, header=None)
            text = ' '.join(df.fillna('').astype(str).values.flatten()).lower()
            for kw in keywords:
                if kw in text:
                    print(f'Match: {fname} | sheet: {sheet} | keyword: {kw}')
                    found.append((fname, sheet, kw))
                    break
        except Exception as e:
            print(f'Failed parse sheet: {fname} :: {sheet} ({e})')

print('\nDone. Matches found:', len(found))
