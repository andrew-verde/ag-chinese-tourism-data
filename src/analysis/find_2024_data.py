import pandas as pd

files_to_try = [
    'mlit_data/001750936.xls',
    'mlit_data/001734816.xls', 
    'mlit_data/001734829.xls',
    'mlit_data/001912042.xls',
    'mlit_data/001853638.xls',
    'mlit_data/001865541.xls'
]
for fname in files_to_try:
    try:
        xls = pd.ExcelFile(fname)
        df = xls.parse('表1-1', header=None, nrows=10)
        year_row = df.iloc[:5, 0:2].to_string()
        fname_short = fname.split('/')[-1]
        print(f'{fname_short}:')
        print(year_row[:300])
        print()
    except Exception as e:
        pass
