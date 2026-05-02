import streamlit as st
from datetime import datetime
import pandas as pd

# ログイン
USERS = {"test": {"password": "1234", "nickname": "はは"}}

def verify_login(login_id, password):
    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {"user_id": login_id, "nickname": user["nickname"]}
    return None

def login_user(user):
    st.session_state["login_user"] = user

def is_logged_in():
    return "login_user" in st.session_state

def require_login():
    if not is_logged_in():
        st.switch_page("pages/0_ログイン.py")

def get_user_id():
    return st.session_state.get("login_user", {}).get("user_id", "guest")

# 記録
DIET_LOGS = []

def save_diet_log(user_id, data):
    data["user_id"] = user_id
    data["created_at"] = datetime.now().isoformat()
    DIET_LOGS.append(data)

def load_latest_log(user_id):
    logs = [l for l in DIET_LOGS if l["user_id"] == user_id]
    if not logs:
        return None
    return logs[-1]

def load_weight_data(user_id):
    df = pd.DataFrame(DIET_LOGS)
    if df.empty:
        return None
    return df[df["user_id"] == user_id]

# 時間
def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# その他
def get_today_advice(settings, latest_log):
    return {"朝": "軽め", "昼": "バランス", "夜": "軽く"}

def get_today_exercise(settings, latest_log):
    return "ストレッチ"

def load_user_settings(user_id):
    return {"nickname": "はは"}

def load_current_user_profile():
    user = st.session_state.get("login_user")
    return {"nickname": user.get("nickname", ""), "login_id": user.get("user_id", "")} if user else {}


# =====================
# 📅 週キー
# =====================
def get_week_key():
    from datetime import datetime
    return datetime.now().strftime("%Y-%W")


# =====================
# 🆕 ユーザー登録
# =====================
def create_user(login_id, password, nickname, birth_date):

    USERS[login_id] = {
        "password": password,
        "nickname": nickname
    }

    return {
        "user_id": login_id,
        "nickname": nickname
    }

# =====================
# 📅 週間プラン
# =====================
def generate_weekly_plan(settings, latest_log):
    return [
        "朝は軽め＋タンパク質",
        "昼はバランスよく",
        "夜は控えめに",
        "間食はナッツやヨーグルト",
        "水分をしっかりとる"
    ]

# =====================
# 📊 今日の記録状態
# =====================
def get_today_log_status(user_id):
    return {
        "is_logged": False,
        "label": "未記録",
        "detail": "まだ今日の記録がありません"
    }


# =====================
# 📒 初期入力値
# =====================
def get_initial_log_values(user_id):
    return {
        "weight": 50.0,
        "body_fat": 25.0
    }

# =====================
# 💬 相談サポート
# =====================
def get_support_focus_summary(settings, latest_log):
    return {
        "points": ["体調", "食事"],
        "today_conditions": []
    }


# =====================
# 🍽 食事時間判定
# =====================
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
