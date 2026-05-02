import streamlit as st
from datetime import datetime
import pandas as pd

# =====================
# 🔥 モード切替
# =====================
USE_SHEETS = False  # ← 最初はFalse → 後でTrue

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

# =====================
# 📒 Sheets保存
# =====================
def save_diet_log_to_sheet(user_id, data):
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        st.secrets["SPREADSHEET_ID"]
    ).worksheet("DietLogs")

    sheet.append_row([
        user_id,
        data.get("log_date", ""),
        data.get("weight", ""),
        data.get("body_fat", ""),
        data.get("meal_memo", ""),
        data.get("exercise_memo", "")
    ])

# =====================
# 📒 Sheets読み込み
# =====================
def read_dietlog_from_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        st.secrets["SPREADSHEET_ID"]
    ).worksheet("DietLogs")

    return sheet.get_all_records()

# =====================
# 📒 保存（分岐）
# =====================
def save_diet_log(user_id, data):
    data["created_at"] = datetime.now().isoformat()

    if USE_SHEETS:
        save_diet_log_to_sheet(user_id, data)
        return

    data["user_id"] = user_id
    DIET_LOGS.append(data)

# =====================
# 📒 最新取得
# =====================
def load_latest_log(user_id):

    if USE_SHEETS:
        records = read_dietlog_from_sheet()
    else:
        records = DIET_LOGS

    logs = [l for l in records if l.get("user_id") == user_id]

    if not logs:
        return None

    return logs[-1]

# =====================
# 📊 グラフ
# =====================
def load_weight_data(user_id):

    if USE_SHEETS:
        records = read_dietlog_from_sheet()
    else:
        records = DIET_LOGS

    df = pd.DataFrame(records)

    if df.empty:
        return None

    df = df[df["user_id"] == user_id]

    if df.empty:
        return None

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")

    if "weight" in df.columns:
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
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
    return [
        "朝は軽め＋タンパク質",
        "昼はバランスよく",
        "夜は控えめに"
    ]

def get_today_log_status(user_id):
    return {"is_logged": False, "label": "未記録"}

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
