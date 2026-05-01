import pandas as pd
from datetime import datetime, timedelta

# -----------------
# 🕒 時間
# -----------------
def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# -----------------
# 🔐 ユーザー（仮DB）
# -----------------
USERS = {
    "test": {
        "password": "1234",
        "nickname": "はは",
        "birth_date": "1976-05-13"
    }
}

# -----------------
# 🔐 ログイン
# -----------------
def verify_login(login_id, password):
    user = USERS.get(login_id)

    if user and user["password"] == password:
        return {
            "user_id": login_id,
            "nickname": user.get("nickname", "")
        }

    return None

def login_user(user_record):
    import streamlit as st
    st.session_state["login_user"] = user_record

def is_logged_in():
    import streamlit as st
    return "login_user" in st.session_state

def require_login():
    import streamlit as st
    if not is_logged_in():
        st.warning("ログインしてください")
        st.switch_page("pages/0_ログイン.py")
        st.stop()

def get_user_id():
    import streamlit as st
    if "login_user" in st.session_state:
        return st.session_state["login_user"]["user_id"]
    return "guest"

# -----------------
# 🆕 ユーザー登録
# -----------------
def create_user(login_id, password, nickname, birth_date):

    if not login_id or not password:
        raise ValueError("ログインIDとパスワードは必須です")

    if login_id in USERS:
        raise ValueError("このIDは使われています")

    USERS[login_id] = {
        "password": password,
        "nickname": nickname,
        "birth_date": str(birth_date)
    }

    return {
        "user_id": login_id,
        "nickname": nickname
    }

# -----------------
# 👤 プロフィール
# -----------------
def load_current_user_profile():
    import streamlit as st
    user_id = get_user_id()
    user = USERS.get(user_id)

    if not user:
        return None

    birth = user.get("birth_date")
    age = None

    if birth:
        try:
            birth_dt = datetime.strptime(birth, "%Y-%m-%d")
            age = int((datetime.now() - birth_dt).days / 365)
        except:
            pass

    return {
        "login_id": user_id,
        "nickname": user.get("nickname", ""),
        "birth_date": birth,
        "age": age
    }

# -----------------
# 📊 設定
# -----------------
USER_SETTINGS = {}

def load_user_settings(user_id):
    return USER_SETTINGS.get(user_id, {
        "nickname": "はは",
        "height_cm": 160,
        "current_weight": 50,
        "target_weight": 48,
        "current_body_fat": 30,
        "target_body_fat": 28,
        "activity_level": "普通",
        "food_style": "和食中心",
        "user_type": "バランス重視",
        "advice_tone": "やさしい",
        "constitution_traits": []
    })

def save_user_settings(user_id, data):
    USER_SETTINGS[user_id] = data
    return True

# -----------------
# 📊 選択肢
# -----------------
ACTIVITY_LEVEL_OPTIONS = ["低い", "普通", "高い"]
FOOD_STYLE_OPTIONS = ["和食中心", "バランス型", "外食多め"]
USER_TYPE_OPTIONS = ["バランス重視", "ダイエット重視", "健康維持"]
ADVICE_TONE_OPTIONS = ["やさしい", "しっかり", "ストレート"]
CONSTITUTION_TRAIT_OPTIONS = ["冷え性", "むくみやすい", "疲れやすい", "代謝が低い"]

# -----------------
# 🔐 アカウント変更
# -----------------
def change_login_id(user_id, current_password, new_login_id):
    user = USERS.get(user_id)

    if user["password"] != current_password:
        raise ValueError("パスワードが違います")

    if new_login_id in USERS:
        raise ValueError("IDが使われています")

    USERS[new_login_id] = USERS.pop(user_id)

def change_birth_date(user_id, current_password, new_birth_date):
    user = USERS.get(user_id)

    if user["password"] != current_password:
        raise ValueError("パスワードが違います")

    user["birth_date"] = str(new_birth_date)

def change_password(user_id, current_password, new_password, new_password_confirm):
    user = USERS.get(user_id)

    if user["password"] != current_password:
        raise ValueError("現在のパスワードが違います")

    if new_password != new_password_confirm:
        raise ValueError("新パスワードが一致しません")

    user["password"] = new_password

# -----------------
# 📒 記録（仮DB）
# -----------------
DIET_LOGS = []

def save_diet_log(user_id, data):
    data["user_id"] = user_id
    DIET_LOGS.append(data)
    return True

def read_dietlog_records():
    return DIET_LOGS

def load_latest_log(user_id):
    logs = [l for l in DIET_LOGS if l["user_id"] == user_id]
    if not logs:
        return None
    return sorted(logs, key=lambda x: x["log_date"])[-1]

def get_initial_log_values(user_id):
    latest = load_latest_log(user_id)

    if not latest:
        return {"weight": 50.0, "body_fat": 25.0}

    return {
        "weight": float(latest.get("weight", 50)),
        "body_fat": float(latest.get("body_fat", 25))
    }

# -----------------
# 📊 グラフ
# -----------------
def load_weight_data(user_id):
    logs = [l for l in DIET_LOGS if l["user_id"] == user_id]

    if not logs:
        return None

    df = pd.DataFrame(logs)

    df["log_date"] = pd.to_datetime(df["log_date"])
    df["weight"] = pd.to_numeric(df.get("weight"), errors="coerce")

    if "body_fat" in df.columns:
        df["body_fat"] = pd.to_numeric(df["body_fat"], errors="coerce")

    return df.dropna()

# -----------------
# 🔥 継続日数
# -----------------
def get_streak_days(user_id):
    logs = read_dietlog_records()

    df = pd.DataFrame(logs)
    df = df[df["user_id"] == user_id]

    if df.empty:
        return 0

    df["log_date"] = pd.to_datetime(df["log_date"])
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
# 📊 今日状態
# -----------------
def get_today_log_status(user_id):
    latest = load_latest_log(user_id)

    if not latest:
        return {"is_logged": False, "label": "未記録", "detail": "記録なし"}

    if latest["log_date"] == jst_today_str():
        return {"is_logged": True, "label": "記録済み", "detail": "今日記録あり"}

    return {"is_logged": False, "label": "未記録", "detail": "まだです"}

# -----------------
# 🍽 食事時間判定
# -----------------
def detect_meal_type_by_time(now):
    h = now.hour
    if h < 10:
        return "朝"
    elif h < 15:
        return "昼"
    elif h < 20:
        return "夜"
    else:
        return "間食"

# -----------------
# 🍽 アドバイス
# -----------------
def get_today_advice(settings, latest_log):
    return "バランスよく食べましょう"

def get_today_exercise(settings, latest_log):
    return "軽く動きましょう"

# -----------------
# 🛒 買い物
# -----------------
def generate_shopping_list_from_week(plan):
    return {
        "野菜": ["キャベツ", "にんじん"],
        "肉": ["鶏むね肉"],
        "その他": ["卵", "豆腐"]
    }

# -----------------
# 💬 相談
# -----------------
CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]

def get_support_focus_summary(settings, latest_log):
    return {"points": ["体調"], "today_conditions": []}

def generate_answer(category, question, settings, latest_log):
    return f"{category}についてアドバイスします。\n{question}"
