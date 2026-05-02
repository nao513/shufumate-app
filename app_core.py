import streamlit as st
from datetime import datetime
import pandas as pd

# =====================
# 🔐 仮ログイン
# =====================
USERS = {
    "test": {"password": "1234", "nickname": "はは"}
}

def verify_login(login_id, password):
    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {"user_id": login_id, "nickname": user["nickname"]}
    return None

def create_user(login_id, password, nickname, birth_date):
    USERS[login_id] = {"password": password, "nickname": nickname}
    return {"user_id": login_id, "nickname": nickname}

def reset_password(login_id, new_password):
    if login_id in USERS:
        USERS[login_id]["password"] = new_password
        return True
    return False

# =====================
# 🔐 セッション
# =====================
def login_user(user_record):
    st.session_state["login_user"] = user_record

def is_logged_in():
    return "login_user" in st.session_state

def require_login():
    if not is_logged_in():
        st.warning("ログインしてください")
        st.switch_page("pages/0_ログイン.py")
        st.stop()

def get_user_id():
    return st.session_state.get("login_user", {}).get("user_id", "guest")

# =====================
# 📊 設定
# =====================
USER_SETTINGS = {}

def load_user_settings(user_id):
    return USER_SETTINGS.get(user_id, {
        "nickname": "はは",
        "activity_level": "普通",
        "food_style": "和食中心",
        "user_type": "バランス重視",
        "advice_tone": "やさしい",
        "constitution_traits": []
    })

def save_user_settings(user_id, data):
    USER_SETTINGS[user_id] = data

# =====================
# 📒 Google Sheets接続
# =====================
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)

@st.cache_resource
def get_dietlog_sheet():
    return get_gspread_client().open_by_key(
        st.secrets["SPREADSHEET_ID"]
    ).worksheet("DietLogs")

# =====================
# 📒 記録保存
# =====================
def save_diet_log(user_id, data):

    data["created_at"] = datetime.now().isoformat()

    ws = get_dietlog_sheet()

    ws.append_row([
        user_id,
        data.get("log_date", ""),
        data.get("weight", ""),
        data.get("body_fat", ""),
        data.get("meal_memo", ""),
        data.get("exercise_memo", ""),
        data.get("condition_note", ""),
        data.get("mood_note", ""),
        ",".join(data.get("today_conditions", [])),
        data.get("created_at", ""),
        data.get("target_muscle_mass", ""),
        data.get("bmi", ""),
        data.get("goal_calories", "")
    ])

# =====================
# 📒 読み込み
# =====================
def read_dietlog_records():
    ws = get_dietlog_sheet()
    return ws.get_all_records()

def load_latest_log(user_id):

    logs = read_dietlog_records()

    user_logs = [l for l in logs if l["user_id"] == user_id]

    if not user_logs:
        return None

    return sorted(user_logs, key=lambda x: x.get("log_date", ""))[-1]

# =====================
# 📊 グラフ
# =====================
def load_weight_data(user_id):

    logs = read_dietlog_records()

    df = pd.DataFrame(logs)

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
    return {
        "朝": "軽めに整えましょう☀️",
        "昼": "バランスよく🍱",
        "夜": "消化にやさしく🌙"
    }

def get_today_exercise(settings, latest_log):
    return "軽くストレッチから始めましょう"

# =====================
# 📅 補助
# =====================
def get_week_key():
    return datetime.now().strftime("%Y-%W")

def generate_weekly_plan(settings, latest_log):
    return ["和食中心", "野菜多め", "魚メニュー"]

def get_today_log_status(user_id):
    return {"is_logged": False, "label": "未記録", "detail": "まだ記録なし"}

# =====================
# 👤 プロフィール
# =====================
def load_current_user_profile():
    user = st.session_state.get("login_user")
    if not user:
        return {}
    return {
        "nickname": user.get("nickname", ""),
        "login_id": user.get("user_id", "")
    }

# =====================
# 💬 相談
# =====================
CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]

def get_support_focus_summary(settings, latest_log):
    return {"points": ["体調"], "today_conditions": []}

def generate_answer(category, question, settings, latest_log):
    return f"{category}についての提案です\n{question}"

# =====================
# 📒 初期値
# =====================
def get_initial_log_values(user_id):
    return {"weight": 50.0, "body_fat": 25.0}
