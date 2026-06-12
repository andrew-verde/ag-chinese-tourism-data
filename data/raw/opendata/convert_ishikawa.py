import csv
import json
import os
from datetime import datetime
from pathlib import Path
from safe_io import replace_with_backup, safe_write_text


BASE_DIR = Path(__file__).resolve().parent

def remove_unwanted_linebreaks(input_file_path):
    """
    改行コードLFと単独のCRを削除する（CRLFは保持）
    """
    try:
        # バイナリモードでファイルを読み込み（改行コードを正規化しない）
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()
        
        # デバッグ情報：バイナリレベルでの改行コードの数を確認
        lf_count = content_bytes.count(b'\n')
        cr_count = content_bytes.count(b'\r')
        
        # CRLFの数を正しくカウント
        crlf_count = 0
        for i in range(len(content_bytes) - 1):
            if content_bytes[i] == ord('\r') and content_bytes[i + 1] == ord('\n'):
                crlf_count += 1
        
        # 単独のCRとLFの数を計算
        standalone_cr = cr_count - crlf_count
        standalone_lf = lf_count - crlf_count
        
        print(f"デバッグ: 処理前の改行コード数")
        print(f"  LF (\\n): {lf_count}")
        print(f"  CRLF (\\r\\n): {crlf_count}")
        print(f"  CR (\\r): {cr_count}")
        print(f"  単独のLF: {standalone_lf}")
        print(f"  単独のCR: {standalone_cr}")
        
        # 文字列に変換（BOMを除去）
        if content_bytes.startswith(b'\xef\xbb\xbf'):
            content_bytes = content_bytes[3:]  # BOMを除去
        
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
        
        # タブ文字を半角スペースに置換
        content = content.replace('\t', ' ')
        
        # 不要な改行コードを削除（CRLFは保持）
        # \r\n (CRLF) を一時的に特殊文字に置換
        content = content.replace('\r\n', '___CRLF___')
        
        # 単独のLF (\n) を削除
        content = content.replace('\n', '')
        
        # 単独のCR (\r) を削除
        content = content.replace('\r', '')
        
        # 一時的な特殊文字をCRLFに戻す
        content = content.replace('___CRLF___', '\r\n')
        
        # 修正した内容をフォーマット済みファイルに出力
        formatted_file_path = Path(input_file_path).with_name(Path(input_file_path).stem + '_formatted.csv')
        if not safe_write_text(formatted_file_path, content):
            return False
        
        print(f"不要な改行コードの削除完了: {formatted_file_path}")
        return True
        
    except Exception as e:
        print(f"改行コード削除エラー: {e}")
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

def calculate_age_group(birth_year_str, survey_date_str):
    """
    生まれた年とアンケート回答日から年代を計算
    """
    if not birth_year_str or not survey_date_str:
        return ""
    
    try:
        # 生まれた年を整数に変換
        birth_year = int(birth_year_str.strip())
        
        # アンケート回答日を解析（M/d/yyyy hh:mm:ss 形式）
        survey_date = datetime.strptime(survey_date_str.strip(), '%m/%d/%Y %H:%M:%S')
        survey_year = survey_date.year
        
        # 年齢を計算
        age = survey_year - birth_year
        
        # 年代を判定
        if age < 10:
            return "10歳未満"
        elif age < 20:
            return "10代"
        elif age < 30:
            return "20代"
        elif age < 40:
            return "30代"
        elif age < 50:
            return "40代"
        elif age < 60:
            return "50代"
        elif age < 70:
            return "60代"
        elif age < 80:
            return "70代"
        else:
            return "80代以上"
            
    except (ValueError, TypeError):
        # 解析に失敗した場合は元の値をそのまま返す
        return birth_year_str

def format_date_string(date_str):
    """
    日付文字列を yyyy/MM/dd hh:mm:ss 形式に統一
    MM/dd/yyyy hh:mm:ss 形式から変換
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # MM/dd/yyyy hh:mm:ss 形式を解析
        date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y %H:%M:%S')
        # yyyy/MM/dd hh:mm:ss 形式に変換
        return date_obj.strftime('%Y/%m/%d %H:%M:%S')
    except ValueError:
        try:
            # 別の形式も試す（例: MM/dd/yyyy）
            date_obj = datetime.strptime(date_str.strip(), '%m/%d/%Y')
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

def convert_ishikawa_csv():
    # ファイルパス
    input_csv = BASE_DIR / "input/ishikawa/ishikawa_formatted.csv"
    mapping_json = BASE_DIR / "input/ishikawa/column_mapping_ishikawa.json"
    output_csv = BASE_DIR / "output/ishikawa/ishikawa_converted.csv"
    
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
            with open(input_csv, 'r', encoding=encoding) as f:
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
    with open(temp_output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # ヘッダー行を書き込み
        writer.writerow(output_headers)
        
        # データ行を処理
        for row in rows:
            output_row = []
            
            for header in output_headers:
                # 1項目目の"対象県（富山/石川/福井）"は"石川"を出力
                if header == "対象県（富山/石川/福井）":
                    output_row.append("石川")
                # 情報源関連のフラグ項目の処理
                elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                               "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                               "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                               "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                               "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                               "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                               "観光連盟やDMOのHP", "その他"]:
                    # 情報源の文字列を取得（石川の場合は「今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）」を使用）
                    information_source = row.get('今回   当施設   を訪れる際に参考にした情報源は何ですか？（複数選択可）', '')
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
                        # 「年代」の場合は生まれた年から年代を計算
                        elif header == "年代":
                            # アンケート回答日を取得
                            survey_date_field = mapping["アンケート回答日"]
                            survey_date = row.get(survey_date_field, "") if survey_date_field else ""
                            # 年代を計算
                            value = calculate_age_group(value, survey_date)
                        # 「自由意見」の場合は2つのフィールドを結合
                        elif header == "自由意見":
                            # 2つのフィールドの値を取得
                            field1 = row.get("あなたが求めている石川県の飲食、土産、アクティビティについて、ご自由にご意見をお聞かせください。(※必須項目です。無ければ「特になし」とご記入ください)", "")
                            field2 = row.get("今回の旅行またはお出かけにおいて、特に人に薦めたいと感じたものとその理由について具体的に教えてください。", "")
                            
                            # 両方のフィールドが存在する場合は半角スペースで結合
                            if field1 and field2:
                                value = f"{field1} {field2}"
                            elif field1:
                                value = field1
                            elif field2:
                                value = field2
                            else:
                                value = ""
                        
                        output_row.append(value)
                    else:
                        # 入力CSVに項目が存在しない場合は空文字を出力
                        output_row.append("")
            
            writer.writerow(output_row)
    replace_with_backup(temp_output_csv, output_csv)
    
    print(f"変換完了: {output_csv}")
    print(f"出力行数: {len(rows)}")

def main():
    """
    メイン処理
    """
    # 不要な改行コードの削除を実行
    input_csv = BASE_DIR / "input/ishikawa/ishikawa.csv"
    if os.path.exists(input_csv):
        print("不要な改行コードの削除を開始します...")
        if remove_unwanted_linebreaks(input_csv):
            print("不要な改行コードの削除が完了しました。")
        else:
            print("不要な改行コードの削除に失敗しました。")
    else:
        print(f"入力ファイルが見つかりません: {input_csv}")
        return
    
    # CSV変換を実行
    print("CSV変換を開始します...")
    convert_ishikawa_csv()

if __name__ == "__main__":
    main()
