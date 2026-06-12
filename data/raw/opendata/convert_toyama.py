import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from safe_io import safe_copy_file, safe_write_csv


BASE_DIR = Path(__file__).resolve().parent

def convert_satisfaction_to_number(satisfaction_str):
    """
    満足度の文字列を数値に変換
    大いに満足=5, 満足=4, 普通=3, 不満=2, 大いに不満=1
    """
    if not satisfaction_str or satisfaction_str.strip() == "":
        return ""
    
    satisfaction_str = satisfaction_str.strip()
    
    satisfaction_mapping = {
        "大いに満足": 5,
        "満足": 4,
        "普通": 3,
        "不満": 2,
        "大いに不満": 1
    }
    
    return satisfaction_mapping.get(satisfaction_str, satisfaction_str)

def format_date_string(date_str):
    """
    日付文字列を yyyy/MM/dd hh:mm:ss 形式に統一
    """
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # 既存の形式を解析（例: 2025/04/18）
        date_obj = datetime.strptime(date_str.strip(), '%Y/%m/%d')
        # yyyy/MM/dd 00:00:00 形式に変換
        return date_obj.strftime('%Y/%m/%d 00:00:00')
    except ValueError:
        # 解析できない場合は元の値をそのまま返す
        return date_str

def format_amount_field(amount_str):
    """
    金額項目の「以上」の後ろに半角スペースを追加
    例: 1,000円以上3,000円未満 → 1,000円以上 3,000円未満
    """
    if not amount_str or amount_str.strip() == "":
        return amount_str
    
    # 「以上」の後ろに半角スペースを追加
    formatted = amount_str.replace("以上", "以上 ")
    
    return formatted

def convert_gender(gender_str):
    """
    性別の文字列を変換
    男性→男、女性→女
    """
    if not gender_str or gender_str.strip() == "":
        return gender_str
    
    gender_str = gender_str.strip()
    
    if gender_str == "男性":
        return "男"
    elif gender_str == "女性":
        return "女"
    else:
        # その他の場合は元の値をそのまま返す
        return gender_str

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

def format_information_source(row):
    """
    情報源（デジタル）と情報源（デジタル以外）を連結して処理
    """
    digital_source = row.get('情報源（デジタル）', '').strip()
    non_digital_source = row.get('情報源（デジタル以外）', '').strip()
    
    # 元のダブルクォーテーションを除去
    digital_source = digital_source.strip('"')
    non_digital_source = non_digital_source.strip('"')
    
    # 両方の情報源を連結（ダブルクォーテーションなしで連結）
    if digital_source and non_digital_source:
        combined = f"{digital_source}, {non_digital_source}"
    elif digital_source:
        combined = digital_source
    elif non_digital_source:
        combined = non_digital_source
    else:
        combined = ""
    
    # 先頭と最後尾のカンマを削除
    combined = combined.strip()
    if combined.startswith(','):
        combined = combined[1:].strip()
    if combined.endswith(','):
        combined = combined[:-1].strip()
    
    # 空文字の場合は空文字を返す
    if not combined:
        return ""
    
    # ダブルクォーテーションで囲まずにそのまま返す
    return combined

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
        "観光連盟やDMOのHP": ["観光連盟やDMOのHP", "富山県内市町村の観光公式サイト", "富山県観光公式サイト「とやま観光ナビ」"]
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

def copy_toyama_csv():
    """
    toyama.csvをtoyama_formatted.csvとしてコピー
    """
    source_file = BASE_DIR / "input/toyama/toyama.csv"
    target_file = BASE_DIR / "input/toyama/toyama_formatted.csv"
    
    try:
        if os.path.exists(source_file):
            if safe_copy_file(source_file, target_file):
                print(f"ファイルコピー完了: {source_file} -> {target_file}")
                return True
            return False
        else:
            print(f"ソースファイルが見つかりません: {source_file}")
            return False
    except Exception as e:
        print(f"ファイルコピーエラー: {e}")
        return False

def convert_toyama_csv():
    # ファイルパス
    input_csv = BASE_DIR / "input/toyama/toyama_formatted.csv"
    mapping_json = BASE_DIR / "input/toyama/column_mapping_toyama.json"
    output_csv = BASE_DIR / "output/toyama/toyama_converted.csv"
    
    # JSONマッピングファイルを読み込み
    with open(mapping_json, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 出力用のヘッダー（JSONのキー順）
    output_headers = list(mapping.keys())
    
    # 入力CSVを読み込み（BOMを自動除去）
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        input_headers = reader.fieldnames
        rows = list(reader)

    converted_rows = []

    # データ行を処理
    for row in rows:
        output_row = []

        for header in output_headers:
            # 1項目目の"対象県（富山/石川/福井）"は"富山"を出力
            if header == "対象県（富山/石川/福井）":
                output_row.append("富山")
            # 「情報源」項目の特別処理
            elif header == "情報源":
                value = format_information_source(row)
                output_row.append(value)
            # 情報源関連のフラグ項目の処理
            elif header in ["Facebook", "Google", "Googleマップ", "Instagram", "TikTok", 
                            "X（旧Twitter）", "YouTube", "SNS広告", "ブログ", "まとめサイト",
                            "インターネット・アプリ", "デジタルニュース", "宿泊予約Webサイト",
                            "宿泊施設", "TV・ラジオ番組やCM", "ラブライブのスタンプラリー",
                            "新聞・雑誌・ガイドブック", "旅行会社", "友人・知人", "地元の人",
                            "観光パンフレット・ポスター", "観光案内所", "観光展・物産展",
                            "観光連盟やDMOのHP", "その他"]:
                # 情報源の文字列を取得
                information_source = format_information_source(row)
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
                            "満足度（買い物（工芸品・特産品など））", "満足度（観光・体験）", 
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
                    # 性別の場合は男性→男、女性→女に変換
                    elif header == "性別":
                        value = convert_gender(value)
                    # 金額項目の場合は「以上」の後ろに半角スペースを追加
                    elif header in ["交通費", "飲食費", "宿泊費", "買い物費", "観光費"]:
                        value = format_amount_field(value)

                    output_row.append(value)
                else:
                    # 入力CSVに項目が存在しない場合は空文字を出力
                    output_row.append("")
            
        converted_rows.append(output_row)

    if not safe_write_csv(output_csv, output_headers, converted_rows):
        raise RuntimeError(f"変換結果が空のため既存ファイルを保持しました: {output_csv}")
    
    print(f"変換完了: {output_csv}")
    print(f"出力行数: {len(converted_rows)}")

def main():
    """
    メイン処理
    """
    # ファイルコピーを実行
    print("富山CSVファイルのコピーを開始します...")
    if copy_toyama_csv():
        print("富山CSVファイルのコピーが完了しました。")
    else:
        print("富山CSVファイルのコピーに失敗しました。")
        return
    
    # CSV変換を実行
    print("CSV変換を開始します...")
    convert_toyama_csv()

if __name__ == "__main__":
    main()
