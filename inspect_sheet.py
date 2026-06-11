import pandas as pd

# Directly extract data from known files
p = 'mlit_data/001912042.xls'  # Try file with China data
xls = pd.ExcelFile(p)
print('File:', p)
print('Sheets:', xls.sheet_names[:15])

# Try each potential sheet
for sheet in ['表3-1', '表4-1', '表5-1', '参考1']:
    try:
        df = xls.parse(sheet, header=None, nrows=30)
        df_text = df.astype(str).values.flatten()
        full = ' '.join(df_text)
        
        if '中国' in full:
            print(f'\n✓ {sheet} contains 中国')
            print(df.iloc[:15, 0:6].to_string())
            break
    except:
        pass
