# merged_survey_csv_py

Python script to standardize and merge survey CSV data from Toyama, Ishikawa, and Fukui prefectures

## Overview

This project is a tool for converting tourism survey data collected from three prefectures (Toyama, Ishikawa, and Fukui) into a unified format and merging them into CSV files. The pipeline processes over 54,000 responses from visitors to the Hokuriku region, standardizing them into 126 unified columns.

### Key Features

- **Data Standardization**: Convert CSV data in different formats from each prefecture to a unified 126-column schema
- **Column Mapping**: JSON-based flexible column mapping system (Toyama: 52 columns, Ishikawa: 43 columns, Fukui: 90 columns)
- **Data Preprocessing**: Normalizing line codes, anonymizing member IDs, standardizing date formats
- **Information Source Flag Generation**: Automatically extract and generate flags for various media and channels (social media, search engines, traditional media, travel agencies, etc.)
- **CSV Merging**: Consolidate converted data from all three prefectures into single/year-split files
- **Automatic Data Download**: Automatically retrieve the latest data from GitHub repositories and public data sources
- **Year-based File Splitting**: Split output files by year (2023-2026)
- **Automatic Cleanup**: Automatically delete old output files before processing

## File Structure

```
merged_survey_csv_py/
├── download_data.py           # Data download script
├── convert_toyama.py          # Toyama prefecture data conversion script
├── convert_ishikawa.py        # Ishikawa prefecture data conversion script
├── convert_fukui.py           # Fukui prefecture data conversion script
├── merge_survey.py            # Main execution script (download + convert + merge)
├── .github/
│   └── workflows/
│       └── run_python.yml     # GitHub Actions automation settings
├── input/                     # Input data
│   ├── toyama/
│   │   ├── toyama.csv                    # Toyama survey data (auto-downloaded)
│   │   └── column_mapping_toyama.json    # Toyama column mapping definition
│   ├── ishikawa/
│   │   ├── ishikawa.csv                  # Ishikawa survey data (auto-downloaded)
│   │   └── column_mapping_ishikawa.json  # Ishikawa column mapping definition
│   └── fukui/
│       ├── fukui.csv                     # Fukui survey data (merged after auto-download)
│       ├── fukui_2023.csv                # Fukui 2023 data (auto-downloaded)
│       ├── fukui_2024.csv                # Fukui 2024 data (auto-downloaded)
│       └── column_mapping_fukui.json     # Fukui column mapping definition
├── output/                    # Converted data
│   ├── toyama/
│   │   ├── toyama_converted.csv          # Converted data (not pushed to GitHub)
│   │   ├── toyama_converted_2023.csv     # 2023 split data
│   │   ├── toyama_converted_2024.csv     # 2024 split data
│   │   └── ...
│   ├── ishikawa/
│   │   ├── ishikawa_converted.csv        # Converted data (not pushed to GitHub)
│   │   ├── ishikawa_converted_2023.csv   # 2023 split data
│   │   ├── ishikawa_converted_2024.csv   # 2024 split data
│   │   └── ...
│   └── fukui/
│       ├── fukui_converted.csv           # Converted data (not pushed to GitHub)
│       ├── fukui_converted_2023.csv      # 2023 split data
│       ├── fukui_converted_2024.csv      # 2024 split data
│       └── ...
└── output_merge/              # Merged data
    ├── merged_survey.csv      # Final output file (not pushed to GitHub)
    ├── merged_survey_2023.csv # 2023 split data
    ├── merged_survey_2024.csv # 2024 split data
    └── ...
```

For detailed execution instructions and data conversion details, please refer to the [Developer Documentation](docs/development.md).

## Dataset Information

### Overall Dataset Statistics
- **Total Responses**: 54,695 responses from April 2023 to February 2026
- **Standardized Schema**: 126 unified columns
- **Data Types**: 57 integer columns, 37 string columns, 32 float columns
- **Coverage**: 3 prefectures (Toyama, Ishikawa, Fukui)

### Input Data by Prefecture

| Prefecture | Size | Rows | Source Columns | Format |
|-----------|------|------|---|---|
| **Fukui 2023** | 21.55 MB | 23,258 | 90 | FTAS JSON→CSV |
| **Fukui 2024** | 25.74 MB | 27,862 | 90 | FTAS JSON→CSV |
| **Fukui 2025** | 17.77 MB | 19,355 | 90 | FTAS JSON→CSV |
| **Ishikawa** | 6.14 MB | 6,977 | 43 | QR Survey Data |
| **Toyama** | 4.89 MB | 5,106 | 52 | CKAN Data Platform |

### Output Schema (126 Standardized Columns)

The standardized output includes columns for:
- **Demographics** (7): Residence prefecture, gender, age group, occupation, household income, response date
- **Accommodation** (13): Lodging area, night counts, meal plans by location
- **Transportation** (15): Transportation modes, satisfaction ratings
- **Visit Patterns** (3): Visit frequency counts
- **Purpose & Activities** (20): Primary purpose, activity flags (hot springs, food, sightseeing, shopping, etc.)
- **Information Sources** (26): Media channel flags (social media, search engines, travel agencies, traditional media, etc.)
- **Spending** (6): Transportation, food, accommodation, shopping, facility spending
- **Satisfaction & Feedback** (6): Overall satisfaction, revisit intention, recommendation score
- **Additional Fields** (14): Privacy consent, location details, user agent, registration data

### Data Quality Notes
- Early data (2023) has many empty columns that were added to the schema later
- All input files must be UTF-8 encoded
- Missing data is clearly marked and distinguished from "no response" entries

## Automatic Execution (GitHub Actions)

This project automatically updates data daily using GitHub Actions.

### Execution Schedule

- **Execution Time**: 6:00 AM every day (Japan Standard Time)
- **Execution Content**:
  1. Download latest data
  2. Data conversion and merging
  3. File splitting by year
  4. Automatic push to GitHub

### Files Pushed to GitHub

Only the following files are pushed to GitHub:

- Year-split merged files: `output_merge/merged_survey_*.csv`
- Year-split converted files: `output/*/*_converted_*.csv`
- Input data: `input/toyama/toyama.csv`, `input/ishikawa/ishikawa.csv`, `input/fukui/fukui_*.csv`

The following files are not pushed due to `.gitignore` (may exceed 50MB):

- `output_merge/merged_survey.csv`
- `output/toyama/toyama_converted.csv`
- `output/ishikawa/ishikawa_converted.csv`
- `output/fukui/fukui_converted.csv`
- `input/fukui/fukui.csv`

## Use Cases

This dataset enables analysis of:

### Tourism Analytics
- Visitor demographics and travel patterns
- Spending behavior by visitor type and purpose
- Origin-destination analysis (where visitors come from)
- Satisfaction drivers and pain points
- Seasonal trends and preferences

### Marketing Intelligence
- Information source effectiveness (social media vs traditional advertising)
- Competitive analysis (which destinations are considered as alternatives)
- Visitor experience quality and satisfaction trends

### Infrastructure & Service Planning
- Transportation mode preferences and demand
- Accommodation type preferences
- Popular routes and attraction zones
- Service gaps and improvement opportunities

### Regional Strategy
- Performance comparison between Toyama, Ishikawa, and Fukui
- Unique strengths and attractions of each prefecture
- Cross-prefecture tourist flow patterns

## Technical Implementation

### Column Mapping System
Each prefecture has a JSON mapping file that defines:
- Source column names from raw data
- Target standardized column names
- Empty values indicate columns to be generated/extracted from other fields

Example mapping entries:
- Simple mapping: `"source_column": "target_column"`
- Generated/extracted: `"source_column": ""`

### Data Processing Steps
1. **Download**: Fetch latest data from GitHub and public data platforms
2. **Validate**: Check JSON mapping files and CSV format
3. **Transform**: Apply column mappings and data preprocessing
4. **Generate**: Create flags for information sources and activity preferences
5. **Merge**: Combine data from all three prefectures
6. **Split**: Separate output by year
7. **Cleanup**: Remove old non-split output files

### Preprocessing Operations
- **Newline Normalization**: Handle different line ending formats (CRLF, LF)
- **Member ID Anonymization**: Hash/anonymize visitor IDs for privacy
- **Date Standardization**: Normalize various date formats to unified format
- **Text Field Processing**: Parse and extract flags from comma-separated and free-text fields

## Notes

- Input CSV files must be in UTF-8 encoding
- Column mapping JSON files must be in valid JSON format
- Output directories are created automatically
- If an error occurs, detailed error messages will be displayed in the console
- Maximum input file size: ~26 MB (Fukui 2024 data) - ensure sufficient available RAM for processing
- Merged CSV files can exceed 100 MB - year-split files provided for easier handling
- Large files (>50MB) are not pushed to GitHub; only year-split files are versioned
- Full merged CSV available as GitHub Actions artifact with 30-day retention

## License

- [CC-BY (Attribution)](https://creativecommons.org/licenses/by/4.0/) Hokuriku Inbound Tourism DX and Data Consortium

- Anyone is free to use this data as long as you provide attribution to the source.

## Attribution

(This tourism survey data aggregation program is a modified version of the following works.)

- For Toyama Prefecture data: [Toyama Prefecture Data Collaboration Platform CKAN Toyama Prefecture Tourism Web Survey Data](https://ckan.tdcp.pref.toyama.jp/dataset/kanko_data), Toyama Prefecture, [CC-BY (Attribution)](https://opendefinition.org/licenses/cc-by/)

- For Ishikawa Prefecture data: [Ishikawa Tourism QR Survey Data - Aggregated Data - Tabular Data - All Areas](https://sites.google.com/view/milli-ishikawa-pref/data), Ishikawa Prefecture, [CC-BY (Attribution) 2.1](http://creativecommons.org/licenses/by/2.1/jp/)

- For Fukui Prefecture data: [Open data published by Fukui Prefecture Tourism Data System "FTAS"](https://github.com/code4fukui/fukui-kanko-survey), Fukui Tourist Association, [CC-BY (Attribution)](https://creativecommons.org/licenses/by/4.0/)
