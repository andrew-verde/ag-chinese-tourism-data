#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アンケートCSVマージプログラム
convert_toyama.py, convert_ishikawa.py, convert_fukui.pyを順に実行し、
その結果のCSVファイルをマージするプログラム
"""

import argparse
import csv
import os
import sys
import subprocess
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
from download_data import DataDownloader
from safe_io import safe_write_csv


BASE_DIR = Path(__file__).resolve().parent

class SurveyMerger:
    def __init__(self, input_dir: str = "output", output_dir: str = "output_merge"):
        self.base_dir = BASE_DIR
        self.input_dir = self.base_dir / input_dir
        self.output_dir = self.base_dir / output_dir
        self.downloader = DataDownloader(self.base_dir)
        
    def run_conversion_scripts(self) -> bool:
        """3つの変換スクリプトを順に実行"""
        scripts = [
            "convert_toyama.py",
            "convert_ishikawa.py", 
            "convert_fukui.py"
        ]
        
        print("=== 変換スクリプトの実行 ===")
        
        for script in scripts:
            print(f"\n{script} を実行中...")
            try:
                script_path = self.base_dir / script
                # スクリプトを実行
                result = subprocess.run([sys.executable, str(script_path)], 
                                      capture_output=True, 
                                      text=True, 
                                      encoding='utf-8',
                                      cwd=self.base_dir)
                
                if result.returncode == 0:
                    print(f"✓ {script} が正常に完了しました")
                    if result.stdout:
                        print(f"  出力: {result.stdout.strip()}")
                else:
                    print(f"✗ {script} でエラーが発生しました")
                    if result.stderr:
                        print(f"  エラー: {result.stderr.strip()}")
                    return False
                    
            except Exception as e:
                print(f"✗ {script} の実行に失敗しました: {e}")
                return False
        
        print("\n✓ すべての変換スクリプトが正常に完了しました")
        return True
        
    def check_directories(self) -> bool:
        """ディレクトリの存在確認"""
        if not self.input_dir.exists():
            print(f"エラー: 入力ディレクトリ '{self.input_dir}' が見つかりません。")
            return False
            
        # 出力ディレクトリが存在しない場合は作成
        self.output_dir.mkdir(exist_ok=True)
        print(f"出力ディレクトリ '{self.output_dir}' を確認/作成しました。")
            
        return True
    
    def find_csv_files(self) -> List[Path]:
        """マージ対象の変換済みCSVファイルを検索"""
        csv_files = []

        for prefecture in ["toyama", "ishikawa", "fukui"]:
            prefecture_dir = self.input_dir / prefecture
            merged_file = prefecture_dir / f"{prefecture}_converted.csv"
            if merged_file.exists():
                csv_files.append(merged_file)
                continue

            yearly_files = sorted(prefecture_dir.glob(f"{prefecture}_converted_[0-9][0-9][0-9][0-9].csv"))
            csv_files.extend(yearly_files)

        if not csv_files:
            print(f"エラー: '{self.input_dir}' 配下に変換済みCSVファイルが見つかりません。")
            return []

        print(f"マージ対象CSVファイル: {len(csv_files)}件")
        for file_path in csv_files:
            print(f"  - {file_path}")

        return csv_files
    
    def read_csv_data(self, file_path: Path) -> Tuple[List[str], List[List[str]]]:
        """CSVファイルのヘッダーとデータを読み込み（BOM対応）"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                data = list(reader)
                return headers, data
        except Exception as e:
            print(f"エラー: ファイル '{file_path}' の読み込みに失敗しました: {e}")
            return [], []
    
    def merge_csv_files(self, csv_files: List[Path]) -> bool:
        """CSVファイルをマージ"""
        if not csv_files:
            return False
        
        # 最初のファイルのヘッダーを基準とする
        first_file = csv_files[0]
        base_headers, base_data = self.read_csv_data(first_file)
        
        if not base_headers:
            print(f"エラー: 最初のファイル '{first_file}' の読み込みに失敗しました。")
            return False
        
        print(f"基準ヘッダー: {base_headers}")
        
        # マージされたデータを格納
        merged_data = []
        
        # 最初のファイルのデータを追加
        merged_data.extend(base_data)
        print(f"'{first_file.name}' から {len(base_data)} 行を追加")
        
        # 残りのファイルのデータを追加
        for file_path in csv_files[1:]:
            headers, data = self.read_csv_data(file_path)
            
            if not headers:
                print(f"警告: ファイル '{file_path}' の読み込みに失敗しました。スキップします。")
                continue
            
            # ヘッダーが一致するかチェック
            if headers != base_headers:
                print(f"警告: ファイル '{file_path}' のヘッダーが基準と異なります。")
                print(f"  基準: {base_headers}")
                print(f"  実際: {headers}")
                print("  スキップします。")
                continue
            
            merged_data.extend(data)
            print(f"'{file_path.name}' から {len(data)} 行を追加")
        
        # マージされたデータをCSVファイルに出力
        output_file = self.output_dir / "merged_survey.csv"
        try:
            if not safe_write_csv(output_file, base_headers, merged_data):
                return False
            
            print(f"マージ完了: '{output_file}' に {len(merged_data)} 件の回答を保存しました。")
            
            # 年ごとにファイルを分割
            self.split_by_year(output_file, base_headers, merged_data)
            
            # 各変換後のCSVファイルも年毎に分割
            self.split_converted_csv_files()
            
            return True
            
        except Exception as e:
            print(f"エラー: 出力ファイルの作成に失敗しました: {e}")
            return False
    
    def extract_year_from_date(self, date_str: str) -> int:
        """日付文字列から年を抽出"""
        if not date_str or date_str.strip() == "":
            return None
        
        # 日付形式を解析（例: 2023/04/28 21:25:52, 2025/5/4 00:00:00）
        date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
        if date_match:
            return int(date_match.group(1))
        
        return None
    
    def split_by_year(self, merged_file: Path, headers: List[str], data: List[List[str]]) -> bool:
        """マージされたCSVファイルを年ごとに分割"""
        try:
            # アンケート回答日のカラムインデックスを取得
            date_column_index = None
            for i, header in enumerate(headers):
                if header == "アンケート回答日":
                    date_column_index = i
                    break
            
            if date_column_index is None:
                print("警告: 'アンケート回答日' カラムが見つかりません。年ごとの分割をスキップします。")
                return False
            
            # 年ごとにデータを分類
            year_data: Dict[int, List[List[str]]] = {}
            
            for row in data:
                if len(row) <= date_column_index:
                    continue
                
                date_str = row[date_column_index]
                year = self.extract_year_from_date(date_str)
                
                if year is None:
                    print(f"警告: 日付が解析できませんでした: {date_str}")
                    continue
                
                if year not in year_data:
                    year_data[year] = []
                
                year_data[year].append(row)
            
            # 年ごとにファイルを出力
            print(f"\n=== 年ごとのファイル分割 ===")
            for year in sorted(year_data.keys()):
                output_file = self.output_dir / f"merged_survey_{year}.csv"
                year_rows = year_data[year]
                
                if not safe_write_csv(output_file, headers, year_rows):
                    return False
                
                print(f"  {year}年: {output_file} に {len(year_rows)} 件の回答を保存しました。")
            
            return True
            
        except Exception as e:
            print(f"エラー: 年ごとの分割に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def split_converted_csv_files(self):
        """各変換後のCSVファイルを年毎に分割"""
        converted_files = [
            self.base_dir / "output/toyama/toyama_converted.csv",
            self.base_dir / "output/ishikawa/ishikawa_converted.csv",
            self.base_dir / "output/fukui/fukui_converted.csv"
        ]
        
        print(f"\n=== 変換後CSVファイルの年毎分割 ===")
        
        for csv_file in converted_files:
            if not csv_file.exists():
                print(f"  スキップ: {csv_file} が見つかりません")
                continue
            
            try:
                # CSVファイルを読み込み
                headers, data = self.read_csv_data(csv_file)
                
                if not headers:
                    print(f"  警告: {csv_file} の読み込みに失敗しました")
                    continue
                
                # 年毎に分割
                output_dir = csv_file.parent
                base_name = csv_file.stem  # ファイル名から拡張子を除く
                
                # アンケート回答日のカラムインデックスを取得
                date_column_index = None
                for i, header in enumerate(headers):
                    if header == "アンケート回答日":
                        date_column_index = i
                        break
                
                if date_column_index is None:
                    print(f"  警告: {csv_file} に'アンケート回答日'カラムが見つかりません。スキップします。")
                    continue
                
                # 年ごとにデータを分類
                year_data: Dict[int, List[List[str]]] = {}
                
                for row in data:
                    if len(row) <= date_column_index:
                        continue
                    
                    date_str = row[date_column_index]
                    year = self.extract_year_from_date(date_str)
                    
                    if year is None:
                        # 日付が解析できない場合はスキップ（警告は出さない）
                        continue
                    
                    if year not in year_data:
                        year_data[year] = []
                    
                    year_data[year].append(row)
                
                # 年ごとにファイルを出力
                if year_data:
                    for year in sorted(year_data.keys()):
                        output_file = output_dir / f"{base_name}_{year}.csv"
                        year_rows = year_data[year]
                        
                        if not safe_write_csv(output_file, headers, year_rows):
                            continue
                        
                        print(f"  {csv_file.name} → {output_file.name}: {len(year_rows)}件 ({year}年)")
                else:
                    print(f"  警告: {csv_file} に有効なデータが見つかりませんでした")
                    
            except Exception as e:
                print(f"  エラー: {csv_file} の分割に失敗しました: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    def cleanup_output_directories(self):
        """過去の出力は削除しない。各出力ファイルは安全書き込みで更新する。"""
        print("=== 出力ディレクトリのクリーンアップ ===")
        print("  既存の研究出力を保護するため、物理削除は行いません。")
        print()
    
    def run(self, skip_download: bool = False):
        """メイン処理"""
        print("=== アンケートCSVマージプログラム ===")
        print()

        # 1. データのダウンロード
        if skip_download:
            print("=== データダウンロード ===")
            print("  --skip-download が指定されたため、既存の入力ファイルを使用します。")
        elif not self.downloader.download_all_data():
            print("エラー: データのダウンロードに失敗したため、既存データを保護して処理を停止します。")
            return False

        print()
        
        # 2. 出力ディレクトリのクリーンアップ（古いファイルを削除）
        self.cleanup_output_directories()
        
        # 3. 変換スクリプトの実行
        if not self.run_conversion_scripts():
            return False
        
        print("\n=== CSVファイルのマージ ===")
        
        # 4. ディレクトリの確認
        if not self.check_directories():
            return False
        
        # 5. CSVファイルの検索
        csv_files = self.find_csv_files()
        if not csv_files:
            return False
        
        # 6. マージ実行
        success = self.merge_csv_files(csv_files)
        return success

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="アンケートCSVを変換・マージします。")
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="ネットワークから再ダウンロードせず、既存の input/ ファイルを使います。",
    )
    args = parser.parse_args()

    merger = SurveyMerger()
    success = merger.run(skip_download=args.skip_download)
    
    if success:
        print("\nプログラムが正常に完了しました。")
    else:
        print("\nプログラムがエラーで終了しました。")
        sys.exit(1)

if __name__ == "__main__":
    main() 
