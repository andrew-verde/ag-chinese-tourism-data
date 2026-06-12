"""Build the monthly Chinese-visitor time series from real MLIT Excel tables.

Fail-loud by design: if parsing fails, the script exits with an error.
It never substitutes simulated data (docs/adr/0002).
"""
import os
import pandas as pd
import numpy as np

# 24个月数据文件（请将这两个文件保存到当前目录）
INPUT_FILES = [
    'data/raw/mlit/2024年（令和6年）1月~ 12月分（年の確定値）集計結果.xlsx',
    'data/raw/mlit/2025年（令和7年）1月~12月分（年間の速報値) 集計結果.xlsx'
]

POSSIBLE_MONTH_COLUMNS = ['年月', '月', 'Month', 'date', 'Date']
POSSIBLE_CHINA_COLUMNS = ['中国', 'China', 'China Visitors', 'China_Visitors', '中国游客', '入国者数']
REFERENCE_SHEET_PREFIX = '参考第1表'


def find_column(df, choices):
    for col in df.columns:
        low = str(col).lower()
        for choice in choices:
            if str(choice).lower() in low:
                return col
    return None


def parse_reiwa_month(label):
    import re
    if not isinstance(label, str):
        return None
    m = re.search(r'令和(\d+)年\s*(\d+)月', label)
    if not m:
        return None
    year = 2018 + int(m.group(1))
    month = int(m.group(2))
    return pd.Timestamp(year=year, month=month, day=1)


def clean_number(value):
    value = str(value)
    value = value.replace(',', '')
    value = value.replace('*', '')
    value = value.strip()
    if value in ['', 'NaN', 'nan', '-']:
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def extract_reference_monthly_value(df, sheet_name):
    if REFERENCE_SHEET_PREFIX not in sheet_name:
        return None

    # Search for the '中国' column in the header rows.
    header_row = None
    for idx in range(min(10, len(df))):
        row = df.iloc[idx].astype(str).fillna('')
        if any('中国' in str(x) for x in row):
            header_row = idx
            break

    if header_row is None:
        return None

    china_col = None
    for col_idx, val in enumerate(df.iloc[header_row].astype(str).fillna('')):
        if '中国' in str(val):
            china_col = col_idx
            break

    if china_col is None:
        return None

    # Search for the month row below the header row.
    month_row = None
    month_stamp = None
    for idx in range(header_row + 1, min(header_row + 8, len(df))):
        cell = df.iloc[idx, 0]
        if isinstance(cell, str) and '令和' in cell:
            month_stamp = parse_reiwa_month(cell)
            month_row = idx
            break
        if isinstance(cell, (pd.Timestamp, pd.DatetimeTZDtype)):
            month_stamp = pd.Timestamp(cell).normalize()
            month_row = idx
            break

    if month_row is None or month_stamp is None:
        return None

    china_value = clean_number(df.iloc[month_row, china_col])
    if china_value is None:
        return None

    return {'Month': month_stamp, 'China_Visitors': china_value}


def extract_monthly_series(df):
    month_col = find_column(df, POSSIBLE_MONTH_COLUMNS)
    china_col = find_column(df, POSSIBLE_CHINA_COLUMNS)

    if month_col is None or china_col is None:
        return None

    series = df[[month_col, china_col]].copy()
    series.columns = ['Month', 'China_Visitors']
    if not np.issubdtype(series['Month'].dtype, np.datetime64):
        try:
            series['Month'] = pd.to_datetime(series['Month'].astype(str), errors='coerce')
        except Exception:
            pass
    series = series.dropna(subset=['China_Visitors'])
    return series


def load_excel_files(file_paths):
    data = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Missing file: {path}")
            continue

        xls = pd.ExcelFile(path)
        sheet_loaded = False
        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            except Exception:
                continue

            monthly = extract_reference_monthly_value(df, sheet_name)
            if monthly is not None:
                df_monthly = pd.DataFrame([monthly])
                df_monthly['Source_File'] = os.path.basename(path)
                df_monthly['Sheet'] = sheet_name
                data.append(df_monthly)
                sheet_loaded = True
                continue

            df2 = pd.read_excel(xls, sheet_name=sheet_name)
            monthly2 = extract_monthly_series(df2)
            if monthly2 is not None and len(monthly2) >= 6:
                monthly2['Source_File'] = os.path.basename(path)
                monthly2['Sheet'] = sheet_name
                data.append(monthly2)
                sheet_loaded = True
                break

        if not sheet_loaded and not any(REFERENCE_SHEET_PREFIX in name for name in xls.sheet_names):
            print(f"Could not auto-detect month/China columns in {path}. Available columns:")
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                print(f"Sheet: {sheet_name}")
                print(df.columns.tolist())
                print(df.head(3).to_string(index=False))
                print('-' * 40)

    if not data:
        return None

    combined = pd.concat(data, ignore_index=True)
    combined = combined.dropna(subset=['Month', 'China_Visitors'])
    combined['Month'] = pd.to_datetime(combined['Month'], errors='coerce')
    combined = combined.sort_values(by='Month').reset_index(drop=True)
    return combined


def main():
    df = load_excel_files(INPUT_FILES)
    if df is None:
        raise SystemExit(
            "ERROR: could not parse monthly China visitor data from the MLIT files in data/raw/mlit/.\n"
            "This script does not fall back to generated data (docs/adr/0002).\n"
            "Fix the parse (check which sheet/columns hold 月 and 中国 data) and re-run."
        )

    df = df.rename(columns={'China_Visitors': 'Visitor_Count'})
    df['Month_Label'] = df['Month'].dt.strftime('%Y-%m')
    out = 'data/processed/fukui_china_time_series.csv'
    df.to_csv(out, index=False)
    print(f"Real monthly data parsed from MLIT files and saved to {out}.")
    print("Verify the values against the source tables before citing them.")


if __name__ == '__main__':
    main()
