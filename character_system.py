import json

# セーブファイルの名前を定数として定義
SAVE_FILE = "character_data.json"

def get_default_stats():
    """初期ステータスを返す"""
    return {
        'HP': 20,
        'MP': 10,
        'こうげき': 5,
        'ぼうぎょ': 5
    }

def save_stats(stats):
    """ステータスをJSONファイルに保存する関数"""
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

def load_stats():
    """JSONファイルからステータスを読み込む関数"""
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # セーブファイルがない場合、初期ステータスを作成して保存する
        default_stats = get_default_stats()
        save_stats(default_stats)
        return default_stats

def determine_job(stats):
    """現在のステータスから職業を決定する関数"""
    attack = stats.get('こうげき', 0)
    defense = stats.get('ぼうぎょ', 0)
    mp = stats.get('MP', 0)
    
    if attack > 40 and mp > 40: return "魔法剣士"
    if defense > 50 and attack > 30: return "パラディン"
    if mp > 50: return "大魔道士"
    if attack > 50: return "ウォーロード"
    if defense > 50: return "ガーディアン"
    if attack > 20 and mp > 20: return "魔法戦士"
    if mp > 25: return "魔道士"
    if attack > 25: return "戦士"
    if defense > 25: return "騎士"
    return "見習い"

def show_current_status():
    """ファイルから最新のステータスを読み込んで表示する関数"""
    print("\n--- 現在のステータス ---")
    stats = load_stats()
    job = determine_job(stats)
    print(f"ステータス  職業：{job}")
    print(f"HP: {stats['HP']}")
    print(f"MP: {stats['MP']}")
    print(f"こうげき: {stats['こうげき']}")
    print(f"ぼうぎょ: {stats['ぼうぎょ']}")
    print("------------------------")

def modify_stat(stat_name, value):
    """
    外部から特定のステータスを変更し、自動でセーブする関数
    """
    stats = load_stats()
    if stat_name in stats:
        stats[stat_name] += value
        save_stats(stats)
        print(f"\n>> {stat_name} が {value:+} 変化しました！ (セーブ済み)")
    else:
        print(f"\n>>エラー: '{stat_name}' というステータスはありません。")
