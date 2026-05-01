import pandas as pd
from datetime import datetime, timedelta

# -----------------
# 🕒 JST
# -----------------
def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# -----------------
# 🔐 ログイン（仮）
# -----------------
def require_login():
    return True

def get_user_id():
    return "guest"

# -----------------
# 📊 設定
# -----------------
def load_user_settings(user_id):
    return {
        "target_weight": 48,
        "user_type": "バランス重視",
        "activity_level": "普通",
        "food_style": "和食中心",
        "constitution_traits": [],
        "advice_tone": "やさしい",
        "nickname": "はは"
    }

# -----------------
# 👤 プロフィール
# -----------------
def load_current_user_profile():
    return {
        "nickname": "はは"
    }

# -----------------
# 📒 ダミーデータ
# -----------------
def read_dietlog_records():
    return [
        {"user_id": "guest", "log_date": "2024-04-01", "weight": 52.0, "body_fat": 26.0},
        {"user_id": "guest", "log_date": "2024-04-02", "weight": 51.8, "body_fat": 25.8},
        {"user_id": "guest", "log_date": "2024-04-03", "weight": 51.6, "body_fat": 25.6},
        {"user_id": "guest", "log_date": "2024-04-04", "weight": 51.7, "body_fat": 25.7},
        {"user_id": "guest", "log_date": "2024-04-05", "weight": 51.5, "body_fat": 25.5},
    ]

# -----------------
# 📊 初期値（記録ページ）
# -----------------
def get_initial_log_values(user_id):
    records = read_dietlog_records()

    if not records:
        return {"weight": 50.0, "body_fat": 25.0}

    df = pd.DataFrame(records)
    df = df[df["user_id"] == user_id]

    if df.empty:
        return {"weight": 50.0, "body_fat": 25.0}

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    latest = df.sort_values("log_date").iloc[-1]

    return {
        "weight": float(latest.get("weight", 50.0)),
        "body_fat": float(latest.get("body_fat", 25.0))
    }

# -----------------
# 📊 体重データ
# -----------------
def load_weight_data(user_id):
    records = read_dietlog_records()

    if not records:
        return None

    df = pd.DataFrame(records)
    df = df[df["user_id"] == user_id]

    if df.empty:
        return None

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
        df["body_fat"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna().sort_values("log_date")

    return df

# -----------------
# 🔥 継続日数
# -----------------
def get_streak_days(user_id):
    records = read_dietlog_records()

    if not records:
        return 0

    df = pd.DataFrame(records)
    df = df[df["user_id"] == user_id]

    if df.empty:
        return 0

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    dates = df["log_date"].dt.date.unique()

    today = datetime.now().date()
    streak = 0

    for i in range(len(dates)):
        if (today - timedelta(days=i)) in dates:
            streak += 1
        else:
            break

    return streak

# -----------------
# 📊 今日の状態
# -----------------
def get_today_log_status(user_id):
    records = read_dietlog_records()

    if not records:
        return {"is_logged": False, "label": "未記録", "detail": "記録がありません"}

    df = pd.DataFrame(records)
    df = df[df["user_id"] == user_id]

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")

    today = datetime.now().date()

    if today in df["log_date"].dt.date.values:
        return {"is_logged": True, "label": "記録済み", "detail": "今日の記録があります"}
    else:
        return {"is_logged": False, "label": "未記録", "detail": "まだ記録していません"}

# -----------------
# 🍽 食事アドバイス
# -----------------
def get_today_advice(settings, latest_log):
    return "バランスよく食べましょう"

# -----------------
# 🏃‍♀️ 運動
# -----------------
def get_today_exercise(settings, latest_log):
    return "軽いストレッチがおすすめです"

# -----------------
# 📅 週間
# -----------------
def generate_weekly_plan(settings, latest_log):
    return ["和食中心", "魚メニュー", "野菜多め"]

def get_week_key():
    return datetime.now().strftime("%Y-%W")

# -----------------
# 📒 最新ログ
# -----------------
def load_latest_log(user_id):
    records = read_dietlog_records()

    if not records:
        return None

    df = pd.DataFrame(records)
    df = df[df["user_id"] == user_id]

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")

    return df.sort_values("log_date").iloc[-1].to_dict()

# -----------------
# 🍽 食事時間判定
# -----------------
def detect_meal_type_by_time(now):
    hour = now.hour
    if hour < 10:
        return "朝"
    elif hour < 15:
        return "昼"
    elif hour < 20:
        return "夜"
    else:
        return "間食"

# -----------------
# 💾 保存（仮）
# -----------------
def save_diet_log(user_id, data):
    print("保存:", user_id, data)
    return True

# -----------------
# 🛒 買い物リスト
# -----------------
def generate_shopping_list_from_week(weekly_plan):
    return {
        "野菜": ["キャベツ", "にんじん", "ほうれん草"],
        "肉・魚": ["鶏むね肉", "鮭"],
        "その他": ["豆腐", "卵"]
    }

# -----------------
# 💬 相談機能
# -----------------
CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]

def get_support_focus_summary(settings, latest_log):
    return {
        "points": ["体重調整"],
        "today_conditions": []
    }

def generate_answer(category, question, settings, latest_log):

    base = {
        "食事": "バランスよく食べるのがポイントです",
        "運動": "軽いストレッチから始めましょう",
        "体調": "無理せず整えることを優先しましょう",
        "外食調整": "量とバランスを意識しましょう"
    }

    answer = base.get(category, "整えていきましょう")

    if question:
        answer += f"\n\n「{question}」については無理のない範囲で調整していきましょう。"

    return answer
