import pandas as pd
from datetime import datetime
import streamlit as st
import hashlib
import uuid

# =====================
# 🔐 Google Sheets
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
def get_users_sheet():
    return get_gspread_client().open_by_key(
        st.secrets["SPREADSHEET_ID"]
    ).worksheet("Users")

# =====================
# 🕒 時間
# =====================
def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# =====================
# 🔐 パスワード
# =====================
def generate_salt():
    return uuid.uuid4().hex

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, salt, password_hash):
    return hash_password(password, salt) == password_hash

# =====================
# 🔐 ログイン
# =====================
def verify_login(login_id, password):

    ws = get_users_sheet()
    records = ws.get_all_records()

    for user in records:
        if user["login_id"] == login_id:

            if verify_password(password, user["password_salt"], user["password_hash"]):
                return {
                    "user_id": user["user_id"],
                    "nickname": user["nickname"]
                }

    return None

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
# 🆕 ユーザー登録
# =====================
def create_user(login_id, password, nickname, birth_date):

    ws = get_users_sheet()
    records = ws.get_all_records()

    for user in records:
        if user["login_id"] == login_id:
            raise ValueError("このIDは使用されています")

    salt = generate_salt()
    password_hash = hash_password(password, salt)

    user_id = uuid.uuid4().hex

    ws.append_row([
        user_id,
        login_id,
        password_hash,
        salt,
        nickname,
        str(birth_date),
        jst_now().isoformat(),
        jst_now().isoformat(),
        "1"
    ])

    return {
        "user_id": user_id,
        "nickname": nickname
    }

# =====================
# 🔑 パスワード再設定
# =====================
def reset_password(login_id, new_password):

    ws = get_users_sheet()
    records = ws.get_all_records()

    for i, user in enumerate(records, start=2):
        if user["login_id"] == login_id:

            salt = generate_salt()
            password_hash = hash_password(new_password, salt)

            ws.update(f"C{i}", password_hash)
            ws.update(f"D{i}", salt)

            return True

    return False

# =====================
# 📊 設定（簡易）
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
# 📒 記録（仮）
# =====================
DIET_LOGS = []

def save_diet_log(user_id, data):
    data["user_id"] = user_id
    DIET_LOGS.append(data)

def read_dietlog_records():
    return DIET_LOGS

def load_latest_log(user_id):
    logs = [l for l in DIET_LOGS if l["user_id"] == user_id]
    if not logs:
        return None
    return sorted(logs, key=lambda x: x.get("log_date", ""))[-1]

def get_initial_log_values(user_id):
    latest = load_latest_log(user_id)
    if not latest:
        return {"weight": 50.0, "body_fat": 25.0}
    return {
        "weight": float(latest.get("weight", 50)),
        "body_fat": float(latest.get("body_fat", 25))
    }

# =====================
# 📊 グラフ
# =====================
def load_weight_data(user_id):

    logs = read_dietlog_records()
    if not logs:
        return None

    df = pd.DataFrame(logs)
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
# 🍽 食事時間
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
    return "今日は無理せず整えましょう"

def get_today_exercise(settings, latest_log):
    return "軽く動くだけでOKです"

# =====================
# 🛒 買い物
# =====================
def generate_shopping_list_from_week(plan):
    return {
        "野菜": ["キャベツ", "にんじん"],
        "肉": ["鶏むね肉"],
        "その他": ["卵", "豆腐"]
    }

# =====================
# 💬 相談
# =====================
CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]

def get_support_focus_summary(settings, latest_log):
    return {"points": ["体調"], "today_conditions": []}

def generate_answer(category, question, settings, latest_log):
    return f"{category}についての提案です。\n{question}"
