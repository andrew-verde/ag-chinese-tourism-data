import csv
import json
import os
import codecs
import re
from datetime import datetime
from pathlib import Path
from safe_io import replace_with_backup, safe_write_text


BASE_DIR = Path(__file__).resolve().parent

def process_fukui_csv(input_file_path):
    """
    福井CSVファイルの前処理
    1. 会員ID（6桁数字）を"000000"に置換
    2. LFを空文字に置換
    3. "000000"の前にCRLFを挿入
    """
    try:
        # バイナリモードでファイルを読み込み
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()
        
        # BOMを除去
        if content_bytes.startswith(b'\xef\xbb\xbf'):
            content_bytes = content_bytes[3:]
        
        # バイト列を文字列に変換（複数のエンコーディングを試す）
        encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
        content = None
        
        for encoding in encodings:
            try:
                content = content_bytes.decode(encoding)
                print(f"エンコーディング検出: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise UnicodeDecodeError("すべてのエンコーディングでデコードに失敗しました")
        
        print(f"処理前のファイルサイズ: {len(content)} 文字")
        
        # 1. 会員ID（6桁数字）を"000000"に置換
        content = re.sub(r'\b[0-9]{6}\b', '000000', content)
        print("会員IDの置換完了")
        
        # 2. LFを空文字に置換
        content = content.replace('\n', '')
        print("LFの削除完了")
        
        # 3. "000000"の前にCRLFを挿入（最初の"000000"は除く）
        # 最初の"000000"の位置を特定
        first_000000_pos = content.find('000000')
        
        if first_000000_pos != -1:
            # 最初の"000000"より前の部分
            before_first = content[:first_000000_pos + 6]  # "000000"を含む
            # 最初の"000000"より後の部分
            after_first = content[first_000000_pos + 6:]
            
            # 残りの部分で"000000"の前にCRLFを挿入
            after_first = after_first.replace('000000', '\r\n000000')
            
            # 結合
            content = before_first + after_first
        
        print("CRLFの挿入完了")
        print(f"処理後のファイルサイズ: {len(content)} 文字")
        
        # 修正した内容をフォーマット済みファイルに出力
        formatted_file_path = Path(input_file_path).with_name(Path(input_file_path).stem + '_formatted.csv')
        if not safe_write_text(formatted_file_path, content):
            return False
        
        print(f"福井CSVファイルの前処理完了: {formatted_file_path}")
        return True
        
    except Exception as e:
        print(f"福井CSVファイル前処理エラー: {e}")
        return False

def convert_satisfaction_to_number(satisfaction_str):
    """
    満足度の文字列を数値に変換
    とても満足=5, 満足=4, どちらでもない=3, 不満=2, とても不満=1
    """
    if not satisfaction_str or satisfaction_str.strip() == "":
        return ""
    
    satisfaction_str = satisfaction_str.strip()
    
    satisfaction_mapping = {
        "とても満足": 5,
        "満足": 4,
        "どちらでもない": 3,
        "不満": 2,
        "とても不満": 1
    }
    
    return satisfaction_mapping.get(satisfaction_str, satisfaction_str)

def parse_purpose_flags(purpose_str):
    """
    目的の文字列を解析して、各フラグ項目に0または1を設定
    """
    # 目的の文字列を取得
    purpose_text = purpose_str.strip() if purpose_str else ""
    
    # 各フラグ項目の定義
    flags = {
        "宿でのんびり過ごす": ["宿でのんびり過ごす"],
        "温泉や露天風呂": ["温泉や露天風呂"],
        "地元の美味しいものを食べる": ["地元の美味しいものを食べる"],
        "花見や紅葉などの自然鑑賞": ["花見や紅葉などの自然鑑賞"],
        "名所、旧跡の観光": ["名所、旧跡の観光"],
        "テーマパーク（遊園地、動物園、博物館など）": ["テーマパーク（遊園地、動物園、博物館など）"],
        "買い物、アウトレット": ["買い物、アウトレット"],
        "お祭りやイベントへの参加・見物": ["お祭りやイベントへの参加・見物"],
        "スポーツ観戦や芸能鑑賞（コンサート等）": ["スポーツ観戦や芸能鑑賞（コンサート等）"],
        "アウトドア（海水浴、釣り、登山など）": ["アウトドア（海水浴、釣り、登山など）"],
        "まちあるき、都市散策": ["まちあるき、都市散策"],
        "各種体験（手作り、果物狩りなど）": ["各種体験（手作り、果物狩りなど）"],
        "スキー・スノボ、マリンスポーツ": ["スキー・スノボ、マリンスポーツ"],
        "その他スポーツ（ゴルフ、テニスなど）": ["その他スポーツ（ゴルフ、テニスなど）"],
        "ドライブ・ツーリング": ["ドライブ・ツーリング"],
        "友人・親戚を尋ねる": ["友人・親戚を尋ねる"],
        "出張など仕事関係": ["出張など仕事関係"],
        "その他の目的": ["その他"]
    }
    
    # 各フラグをチェック
    result = {}
    
    for flag_name, keywords in flags.items():
        flag_value = 0
        for keyword in keywords:
            if keyword in purpose_text:
                flag_value = 1
                break
        result[flag_name] = flag_value
    
    return result

def parse_transport_flags(transport_str):
    """
    交通手段の文字列を解析して、各フラグ項目に0または1を設定
    """
    # 交通手段の文字列を取得
    transport_text = transport_str.strip() if transport_str else ""
    
    # 各フラグ項目の定義
    flags = {
        "自家用車": ["自家用車"],
        "レンタカー": ["レンタカー"],
        "新幹線": ["新幹線"],
        "在来線": ["在来線"],
        "飛行機": ["飛行機"],
        "旅行会社ツアーバス": ["旅行会社ツアーバス"],
        "県外から訪れていない（福井県在住）": ["県外から訪れていない（福井県在住）"]
    }
    
    # 各フラグをチェック
    result = {}
    
    for flag_name, keywords in flags.items():
        flag_value = 0
        for keyword in keywords:
            if keyword in transport_text:
                flag_value = 1
                break
        result[flag_name] = flag_value
    
    return result

def parse_transport2_flags(transport2_str):
    """
    交通手段2の文字列を解析して、各フラグ項目に0または1を設定
    """
    # 交通手段2の文字列を取得
    transport2_text = transport2_str.strip() if transport2_str else ""
    
    # 各フラグ項目の定義
    flags = {
        "タクシー": ["タクシー"],
        "路線バス": ["路線バス"],
        "徒歩": ["徒歩"],
        "レンタサイクル": ["レンタサイクル"]
    }
    
    # 各フラグをチェック
    result = {}
    
    for flag_name, keywords in flags.items():
        flag_value = 0
        for keyword in keywords:
            if keyword in transport2_text:
                flag_value = 1
                break
        result[flag_name] = flag_value
    
    return result

def format_date_string(date_str):
    """
    日付文字列を yyyy/MM/dd hh:mm:ss 形式に統一
    yyyy-MM-dd hh:mm:ss 形式から変換
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # yyyy-MM-dd hh:mm:ss 形式を解析
        date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S')
        # yyyy/MM/dd hh:mm:ss 形式に変換
        return date_obj.strftime('%Y/%m/%d %H:%M:%S')
    except ValueError:
        try:
            # 別の形式も試す（例: yyyy-MM-dd）
            date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
            # yyyy/MM/dd 00:00:00 形式に変換
            return date_obj.strftime('%Y/%m/%d 00:00:00')
        except ValueError:
            # 解析できない場合は元の値をそのまま返す
            return date_str

def check_information_source_flags(information_source):
    """
    情報源の文字列を解析して、各フラグ項目に0または1を設定
    """
    # 情報源の文字列を取得（ダブルクォートを除去）
    source_str = information_source.strip('"') if information_source else ""
    
    # 各フラグ項目の定義
    flags = {
        "Facebook": ["Facebook"],
        "Google": ["Google"],
        "Googleマップ": ["Googleマップ"],
        "Instagram": ["Instagram"],
        "TikTok": ["TikTok"],
        "X（旧Twitter）": ["X（旧Twitter）", "X(旧：Twitter)", "Twitter"],
        "YouTube": ["YouTube", "YOUTUBE"],
        "SNS広告": ["SNS広告"],
        "ブログ": ["ブログ"],
        "まとめサイト": ["まとめサイト"],
        "インターネット・アプリ": ["インターネット・アプリ", "蜃気楼マラソン公式ページ"],
        "デジタルニュース": ["デジタルニュースサイト"],
        "宿泊予約Webサイト": ["宿泊予約Webサイト", "OTA"],
        "宿泊施設": ["宿泊施設", "宿泊施設のウェブサイト"],
        "TV・ラジオ番組やCM": ["TV・ラジオ番組やCM"],
        "ラブライブのスタンプラリー": ["ラブライブのスタンプラリー"],
        "新聞・雑誌・ガイドブック": ["新聞", "雑誌", "ガイドブック"],
        "旅行会社": ["旅行会社"],
        "友人・知人": ["友人", "知人"],
        "地元の人": ["タクシードライバー", "地元の人"],
        "観光パンフレット・ポスター": ["観光パンフレット", "ポスター"],
        "観光案内所": ["観光案内所", "観光協会等の案内所"],
        "観光展・物産展": ["観光展", "物産展"],
        "観光連盟やDMOのHP": ["観光連盟やDMOのHP"]
    }
    
    # 各フラグをチェック
    result = {}
    matched_keywords = set()
    
    for flag_name, keywords in flags.items():
        flag_value = 0
        for keyword in keywords:
            if keyword in source_str:
                flag_value = 1
                matched_keywords.add(keyword)
                break
        result[flag_name] = flag_value
    
    # "その他"の判定（上記以外の文字列が含まれる場合）
    # 情報源に何か文字列が含まれていて、かつ上記のキーワードにマッチしない場合
    if source_str and not matched_keywords:
        result["その他"] = 1
    else:
        result["その他"] = 0
    
    return result

def convert_fukui_csv():
    # ファイルパス
    input_csv = BASE_DIR / "input/fukui/fukui_formatted.csv"
    mapping_json = BASE_DIR / "input/fukui/column_mapping_fukui.json"
    output_csv = BASE_DIR / "output/fukui/fukui_converted.csv"
    
    # JSONマッピングファイルを読み込み
    with open(mapping_json, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 出力用のヘッダー（JSONのキー順）
    output_headers = list(mapping.keys())
    
    # 入力CSVを読み込み（複数のエンコーディングを試す）
    encodings = ['utf-8-sig', 'utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
    reader = None
    input_headers = None
    rows = None
    
    for encoding in encodings:
        try:
            with codecs.open(input_csv, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                input_headers = reader.fieldnames
                rows = list(reader)
            print(f"CSV読み込み成功 - エンコーディング: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if reader is None:
        raise UnicodeDecodeError("すべてのエンコーディングでCSVファイルの読み込みに失敗しました")
    if not rows:
        raise RuntimeError(f"入力CSVにデータ行がないため既存ファイルを保持しました: {output_csv}")
    
    # 出力CSVを作成
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    temp_output_csv = output_csv.with_suffix(output_csv.suffix + '.tmp')
    written_rows = 0
    with open(temp_output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行を書き込み
        writer.writerow(output_headers)
        
        # データ行を処理
        for row in rows:
            # 空行をスキップ（すべての値が空の行）
            if all(not str(v).strip() for v in row.values()):
                continue
            
            output_row = []
            
            for header in output_headers:
                # 1項目目の"対象県（富山/石川/福井）"は"福井"を出力
                if header == "対象県（富山/石川/福井）":
                    output_row.append("福井")
                # 情報源関連のフラグ項目の処理
                elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                               "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                               "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                               "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                               "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                               "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                               "観光連盟やDMOのHP", "その他"]:
                    # 情報源の文字列を取得（福井の場合は「情報収集ALL」を使用）
                    information_source = row.get('情報収集ALL', '')
                    # フラグをチェック
                    flags = check_information_source_flags(information_source)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                # 目的関連のフラグ項目の処理
                elif header in ["宿でのんびり過ごす", "温泉や露天風呂", "地元の美味しいものを食べる",
                               "花見や紅葉などの自然鑑賞", "名所、旧跡の観光", "テーマパーク（遊園地、動物園、博物館など）",
                               "買い物、アウトレット", "お祭りやイベントへの参加・見物", "スポーツ観戦や芸能鑑賞（コンサート等）",
                               "アウトドア（海水浴、釣り、登山など）", "まちあるき、都市散策", "各種体験（手作り、果物狩りなど）",
                               "スキー・スノボ、マリンスポーツ", "その他スポーツ（ゴルフ、テニスなど）",
                               "ドライブ・ツーリング", "友人・親戚を尋ねる", "出張など仕事関係", "その他の目的"]:
                    # 目的の文字列を取得
                    purpose_field = mapping["目的"]
                    purpose_text = row.get(purpose_field, "") if purpose_field else ""
                    # フラグをチェック
                    flags = parse_purpose_flags(purpose_text)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                # 交通手段関連のフラグ項目の処理
                elif header in ["自家用車", "レンタカー", "新幹線", "在来線", "飛行機", 
                               "旅行会社ツアーバス", "県外から訪れていない（福井県在住）"]:
                    # 交通手段の文字列を取得
                    transport_field = mapping["交通手段１（目的地まで）"]
                    transport_text = row.get(transport_field, "") if transport_field else ""
                    # フラグをチェック
                    flags = parse_transport_flags(transport_text)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                # 交通手段2関連のフラグ項目の処理
                elif header in ["タクシー", "路線バス", "徒歩", "レンタサイクル"]:
                    # 交通手段2の文字列を取得
                    transport2_field = mapping["交通手段２（目的地から）"]
                    transport2_text = row.get(transport2_field, "") if transport2_field else ""
                    # フラグをチェック
                    flags = parse_transport2_flags(transport2_text)
                    # 該当するフラグの値を設定
                    value = flags.get(header, 0)
                    output_row.append(value)
                # 満足度項目の処理
                elif header in ["交通の満足度", 
                               "満足度（食べ物・料理）", "満足度（宿泊施設）", 
                               "満足度（買い物（工芸品・特産品など））", "満足度買い物（観光・体験）", 
                               "満足度（旅行全体）", "満足度（商品・サービス）"]:
                    # マッピングから対応する入力項目名を取得
                    input_field = mapping[header]
                    
                    if input_field == "":
                        # マッピングが空文字の場合は空文字を出力
                        output_row.append("")
                    elif input_field in row:
                        # 入力CSVに項目が存在する場合は満足度を数値に変換
                        value = row[input_field]
                        converted_value = convert_satisfaction_to_number(value)
                        output_row.append(converted_value)
                    else:
                        # 入力CSVに項目が存在しない場合は空文字を出力
                        output_row.append("")
                else:
                    # マッピングから対応する入力項目名を取得
                    input_field = mapping[header]
                    
                    if input_field == "":
                        # マッピングが空文字の場合は空文字を出力
                        output_row.append("")
                    elif input_field in row:
                        # 入力CSVに項目が存在する場合はその値を出力
                        value = row[input_field]
                        
                        # 「アンケート回答日」の場合は日付形式を統一
                        if header == "アンケート回答日":
                            value = format_date_string(value)
                        
                        output_row.append(value)
                    else:
                        # 入力CSVに項目が存在しない場合は空文字を出力
                        output_row.append("")
            
            writer.writerow(output_row)
            written_rows += 1
    if written_rows == 0:
        temp_output_csv.unlink(missing_ok=True)
        raise RuntimeError(f"変換結果が空のため既存ファイルを保持しました: {output_csv}")
    replace_with_backup(temp_output_csv, output_csv)
    
    print(f"変換完了: {output_csv}")
    print(f"出力行数: {written_rows}")

def main():
    """
    メイン処理
    """
    # 福井CSVファイルの前処理を実行
    input_csv = BASE_DIR / "input/fukui/fukui.csv"
    if os.path.exists(input_csv):
        print("福井CSVファイルの前処理を開始します...")
        if process_fukui_csv(input_csv):
            print("福井CSVファイルの前処理が完了しました。")
        else:
            print("福井CSVファイルの前処理に失敗しました。")
            return
    else:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return
    
    # CSV変換を実行
    print("CSV変換を開始します...")
    convert_fukui_csv()

if __name__ == "__main__":
    main()
