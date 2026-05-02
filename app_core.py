import streamlit as st
from datetime import datetime
import pandas as pd
import random
import hashlib

# =====================
# 🔥 モード切替
# =====================
USE_SHEETS = True

# =====================
# 🧾 Sheets接続
# =====================
def get_sheet(name):
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["SPREADSHEET_ID"]).worksheet(name)

# =====================
# 🔐 パスワード処理
# =====================
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

# =====================
# 🔐 ログイン
# =====================
def verify_login(login_id, password):

    sheet = get_sheet("Users")
    records = sheet.get_all_records()

    password_hash = hash_password(password)

    for user in records:
        if (
            str(user.get("login_id")).strip() == str(login_id).strip()
            and
            str(user.get("password_hash")).strip() == password_hash
        ):
            return {
                "user_id": user["user_id"],
                "nickname": user["nickname"]
            }

    return None


def create_user(login_id, password, nickname, birth_date):

    import uuid

    sheet = get_sheet("Users")

    user_id = str(uuid.uuid4())

    password_hash = hash_password(password)

    sheet.append_row([
        user_id,
        str(login_id),
        password_hash,
        "",  # salt（未使用）
        str(nickname),
        str(birth_date),
        datetime.now().isoformat(),
        "",  # updated_at
        True
    ])

    return {
        "user_id": user_id,
        "nickname": nickname
    }


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
# 📒 記録保存
# =====================
def save_diet_log(user_id, data):

    data["created_at"] = datetime.now().isoformat()
    data["user_id"] = user_id

    sheet = get_sheet("DietLogs")

    sheet.append_row([
        user_id,
        data.get("log_date", ""),
        data.get("weight", ""),
        data.get("body_fat", ""),
        data.get("meal_memo", ""),
        data.get("exercise_memo", ""),
        data.get("condition_note", ""),
        data.get("mood_note", ""),
        ", ".join(data.get("today_conditions", [])),
        data.get("created_at", ""),
        data.get("target_muscle_mass", ""),
        data.get("bmi", ""),
        data.get("goal_calories", "")
    ])

# =====================
# 📊 データ取得
# =====================
def load_latest_log(user_id):

    sheet = get_sheet("DietLogs")
    records = sheet.get_all_records()

    logs = [l for l in records if str(l.get("user_id")) == str(user_id)]

    return logs[-1] if logs else None


def load_weight_data(user_id):

    sheet = get_sheet("DietLogs")
    records = sheet.get_all_records()

    df = pd.DataFrame(records)

    if df.empty:
        return None

    df = df[df["user_id"].astype(str) == str(user_id)]

    if df.empty:
        return None

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df["body_fat"] = pd.to_numeric(df["body_fat"], errors="coerce")

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
    return {
        "is_logged": False,
        "label": "未記録",
        "detail": "まだ記録がありません"
    }

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
# 💬 今日の一言
# =====================
def get_today_message(settings, latest_log, state=None, weather="普通"):

    if state:
        if state.get("疲れ"):
            return "今日は無理しなくて大丈夫☺️"
        if state.get("食べすぎ"):
            return "昨日は気にしなくてOK。今日は整えましょう"
        if state.get("冷え"):
            return "体を温めましょう"
        if state.get("こり"):
            return "少し動くと楽になります"

    return random.choice([
        "今日は軽く整えるだけでOK",
        "無理せず続けましょう",
        "できることだけでOK"
    ])
