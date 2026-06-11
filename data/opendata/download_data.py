#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データダウンロードモジュール
各県のアンケートデータを自動的にダウンロードする機能を提供
"""

import csv
import json
import re
import shutil
import tempfile
import traceback
import urllib.request
from pathlib import Path
from safe_io import safe_copy_file, safe_write_bytes, safe_write_csv


class DataDownloader:
    """データダウンロードクラス"""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent

    def resolve_path(self, relative_path: str | Path) -> Path:
        return self.base_dir / relative_path
    
    def download_file(self, url: str, output_path: Path) -> bool:
        """URLからファイルをダウンロード"""
        try:
            print(f"  ダウンロード中: {url}")
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
            if not safe_write_bytes(output_path, data):
                return False
            print(f"  ✓ ダウンロード完了: {output_path}")
            return True
        except Exception as e:
            print(f"  ✗ ダウンロードエラー: {e}")
            return False
    
    def download_toyama_data(self) -> bool:
        """富山のデータをダウンロード"""
        print("\n=== 富山県データのダウンロード ===")
        url = "https://toyama-pref.box.com/shared/static/6tpwiv96wzngxsk3rio1t1vi1dhordnn.csv"
        output_path = self.resolve_path("input/toyama/toyama.csv")
        return self.download_file(url, output_path)
    
    def download_ishikawa_data(self) -> bool:
        """石川のデータをダウンロード（GoogleスプレッドシートからCSV形式で）"""
        print("\n=== 石川県データのダウンロード ===")
        # GoogleスプレッドシートのCSVエクスポートURL
        # https://docs.google.com/spreadsheets/d/1riK_ufkmF6Ql7Tujwlm22FtHOLz7hwUzf6Zi6JAG_QI/edit?gid=0#gid=0
        spreadsheet_id = "1riK_ufkmF6Ql7Tujwlm22FtHOLz7hwUzf6Zi6JAG_QI"
        gid = "0"
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
        output_path = self.resolve_path("input/ishikawa/ishikawa.csv")
        return self.download_file(url, output_path)
    
    def download_fukui_data(self) -> bool:
        """福井のデータをダウンロード（GitHubリポジトリから2023年以降のCSVを取得してマージ）"""
        print("\n=== 福井県データのダウンロード ===")
        try:
            # GitHub APIを使用してfiscalyearlyフォルダ内のファイル一覧を取得
            api_url = "https://api.github.com/repos/code4fukui/fukui-kanko-survey/contents/fiscalyearly"
            print(f"  GitHub APIからファイル一覧を取得中: {api_url}")
            
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                files_data = json.loads(response.read().decode('utf-8'))
            
            # 2023年以降のCSVファイルをフィルタリング
            csv_files = []
            for file_info in files_data:
                if file_info['type'] == 'file' and file_info['name'].endswith('.csv'):
                    # ファイル名から年度を抽出（例: 2023.csv, 2024.csv, fiscal2023.csvなど）
                    filename = file_info['name']
                    year_match = re.search(r'20[2-9][0-9]', filename)
                    if year_match:
                        year = int(year_match.group())
                        if year >= 2023:
                            csv_files.append({
                                'name': filename,
                                'download_url': file_info['download_url'],
                                'year': year
                            })
            
            if not csv_files:
                print("  ✗ 2023年以降のCSVファイルが見つかりませんでした")
                return False
            
            # 年度でソート
            csv_files.sort(key=lambda x: x['year'])
            print(f"  見つかったCSVファイル: {len(csv_files)}件")
            for f in csv_files:
                print(f"    - {f['name']} ({f['year']}年)")
            
            # 一時ディレクトリにダウンロード
            temp_dir = Path(tempfile.mkdtemp())
            downloaded_files = []
            
            for file_info in csv_files:
                temp_file = temp_dir / file_info['name']
                print(f"  {file_info['name']} をダウンロード中...")
                if self.download_file(file_info['download_url'], temp_file):
                    downloaded_files.append(temp_file)
            
            if not downloaded_files:
                print("  ✗ ファイルのダウンロードに失敗しました")
                return False
            
            # CSVファイルをマージ
            print(f"  {len(downloaded_files)}件のCSVファイルをマージ中...")
            output_path = self.resolve_path("input/fukui/fukui.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            merged_headers = None
            merged_data = []
            
            for csv_file in downloaded_files:
                try:
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.reader(f)
                        headers = next(reader)
                        
                        if merged_headers is None:
                            merged_headers = headers
                        elif headers != merged_headers:
                            print(f"    警告: {csv_file.name} のヘッダーが異なります。スキップします。")
                            continue
                        
                        data = list(reader)
                        merged_data.extend(data)
                        print(f"    {csv_file.name}: {len(data)}行を追加")
                        
                except Exception as e:
                    print(f"    ✗ {csv_file.name} の読み込みエラー: {e}")
                    continue
            
            if not safe_write_csv(output_path, merged_headers or [], merged_data):
                print("  ✗ マージ結果が空のため、既存の福井データを保持しました")
                return False
            
            print(f"  ✓ マージ完了: {output_path} ({len(merged_data)}行)")
            
            # 一時ディレクトリにダウンロードしたCSVファイルをinput/fukui/にコピー
            print("  ダウンロードしたCSVファイルをinput/fukui/に保存中...")
            for csv_file in downloaded_files:
                # ファイル名の先頭に「fukui_」を付加
                original_name = csv_file.name
                new_name = f"fukui_{original_name}"
                dest_file = output_path.parent / new_name
                if safe_copy_file(csv_file, dest_file):
                    print(f"    ✓ {original_name} を {dest_file.name} に保存")
            
            return True
            
        except Exception as e:
            print(f"  ✗ 福井データのダウンロードエラー: {e}")
            traceback.print_exc()
            return False
        finally:
            if 'temp_dir' in locals() and temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def download_all_data(self) -> bool:
        """すべてのデータをダウンロード"""
        print("=== データダウンロード ===")
        
        success = True
        success = self.download_toyama_data() and success
        success = self.download_ishikawa_data() and success
        success = self.download_fukui_data() and success
        
        if success:
            print("\n✓ すべてのデータのダウンロードが完了しました")
        else:
            print("\n✗ 一部のデータのダウンロードに失敗しました")
        
        return success


def main():
    """メイン関数（テスト用）"""
    import sys
    
    downloader = DataDownloader()
    
    # コマンドライン引数で特定の県だけをダウンロードするか判定
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--toyama':
            print("=== 富山県データのみダウンロード ===")
            success = downloader.download_toyama_data()
        elif arg == '--ishikawa':
            print("=== 石川県データのみダウンロード ===")
            success = downloader.download_ishikawa_data()
        elif arg == '--fukui':
            print("=== 福井県データのみダウンロード ===")
            success = downloader.download_fukui_data()
        else:
            print(f"不明な引数: {arg}")
            print("使用可能なオプション: --toyama, --ishikawa, --fukui")
            return 1
    else:
        # デフォルトはすべてのデータをダウンロード
        success = downloader.download_all_data()
    
    if success:
        print("\nデータダウンロードが正常に完了しました。")
    else:
        print("\nデータダウンロードにエラーが発生しました。")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
