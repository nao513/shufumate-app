import streamlit as st
from datetime import datetime
import pandas as pd
import random

# =====================
# 🔥 モード切替
# =====================
USE_SHEETS = False  # ← 最初はFalse

# =====================
# 🔐 ログイン
# =====================
USERS = {"test": {"password": "1234", "nickname": "はは"}}

def verify_login(login_id, password):
    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {"user_id": login_id, "nickname": user["nickname"]}
    return None

def create_user(login_id, password, nickname, birth_date):
    USERS[login_id] = {"password": password, "nickname": nickname}
    return {"user_id": login_id, "nickname": nickname}

def login_user(user):
    st.session_state["login_user"] = user

def is_logged_in():
    return "login_user" in st.session_state

def require_login():
    if not is_logged_in():
        st.switch_page("pages/0_ログイン.py")

def get_user_id():
    return st.session_state.get("login_user", {}).get("user_id", "guest")

# =====================
# 📒 記録（メモリ）
# =====================
DIET_LOGS = []

def save_diet_log(user_id, data):
    data["created_at"] = datetime.now().isoformat()
    data["user_id"] = user_id
    DIET_LOGS.append(data)

def load_latest_log(user_id):
    logs = [l for l in DIET_LOGS if l.get("user_id") == user_id]
    return logs[-1] if logs else None

def load_weight_data(user_id):
    df = pd.DataFrame(DIET_LOGS)
    if df.empty:
        return None
    df = df[df["user_id"] == user_id]
    if df.empty:
        return None
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df.get("weight"), errors="coerce")
    df["body_fat"] = pd.to_numeric(df.get("body_fat"), errors="coerce")
    return df.dropna()

# =====================
# 🕒 時間
# =====================
def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# =====================
# 🍽 食事判定
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

# =====================
# 🍽 アドバイス
# =====================
def get_today_advice(settings, latest_log):
    return {"朝": "軽め", "昼": "バランス", "夜": "軽く"}

def get_today_exercise(settings, latest_log):
    return "ストレッチ"

# =====================
# 📅 補助
# =====================
def get_week_key():
    return datetime.now().strftime("%Y-%W")

def generate_weekly_plan(settings, latest_log):
    return ["朝軽め", "昼しっかり", "夜控えめ"]

def get_today_log_status(user_id):
    return {"is_logged": False, "label": "未記録", "detail": "まだ記録がありません"}

# =====================
# 👤 プロフィール
# =====================
def load_user_settings(user_id):
    return {"nickname": "はは"}

def load_current_user_profile():
    user = st.session_state.get("login_user")
    return {
        "nickname": user.get("nickname", ""),
        "login_id": user.get("user_id", "")
    } if user else {}

# =====================
# 💬 相談
# =====================
CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]

def get_support_focus_summary(settings, latest_log):
    return {"points": ["体調"], "today_conditions": []}

def generate_answer(category, question, settings, latest_log):
    return f"{category}のアドバイスです\n{question}"

# =====================
# 📒 初期値
# =====================
def get_initial_log_values(user_id):
    return {"weight": 50.0, "body_fat": 25.0}

# =====================
# 💬 今日の一言（NEW）
# =====================
def get_today_message(settings, latest_log, state=None, weather="普通"):

    messages = [
        "今日は無理しなくて大丈夫☺️",
        "小さく整えるだけでOKです",
        "完璧じゃなくていい日です",
        "昨日より少しでも整えばOK",
        "ゆるく続けるのが一番です"
    ]

    # 天気
    if weather == "寒い":
        messages.append("体を温めることを優先しましょう")
    elif weather == "暑い":
        messages.append("水分をしっかりとりましょう")

    # 状態
    if state:
        if state.get("疲れ"):
            messages.append("今日は休む勇気も大事です")
        elif state.get("食べすぎ"):
            messages.append("リセットは明日で大丈夫")
        elif state.get("冷え"):
            messages.append("温かい食事を意識しましょう")

    return random.choice(messages)
