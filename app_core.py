import streamlit as st
from datetime import datetime
import pandas as pd
import random

# =====================
# 🔥 モード切替
# =====================
USE_SHEETS = True  # ← 本番ON

# =====================
# 🔐 ログイン（ローカル fallback）
# =====================
USERS = {"test": {"password": "1234", "nickname": "はは"}}

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
# 🔐 ログイン
# =====================
def verify_login(login_id, password):

    if USE_SHEETS:
        sheet = get_sheet("Users")
        records = sheet.get_all_records()

        for user in records:
            if user["login_id"] == login_id and user["password"] == password:
                return {
                    "user_id": user["user_id"],
                    "nickname": user["nickname"]
                }
        return None

    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {"user_id": login_id, "nickname": user["nickname"]}
    return None


def create_user(login_id, password, nickname, birth_date):

    if USE_SHEETS:
        import uuid
        sheet = get_sheet("Users")

        user_id = str(uuid.uuid4())

        sheet.append_row([
            user_id,
            login_id,
            password,
            nickname,
            datetime.now().isoformat()
        ])

        return {
            "user_id": user_id,
            "nickname": nickname
        }

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
# 📒 記録保存
# =====================
DIET_LOGS = []

def save_diet_log(user_id, data):

    data["created_at"] = datetime.now().isoformat()
    data["user_id"] = user_id

    if USE_SHEETS:
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
            ", ".join(data.get("today_conditions", [])),  # ←これも重要
            data.get("created_at", ""),
            data.get("target_muscle_mass", ""),
            data.get("bmi", ""),
            data.get("goal_calories", "")
        ])

        return

    DIET_LOGS.append(data)
# =====================
# 📊 データ取得
# =====================
def load_latest_log(user_id):

    if USE_SHEETS:
        sheet = get_sheet("DietLogs")
        records = sheet.get_all_records()
    else:
        records = DIET_LOGS

    logs = [l for l in records if str(l.get("user_id")) == str(user_id)]

    return logs[-1] if logs else None


def load_weight_data(user_id):

    if USE_SHEETS:
        sheet = get_sheet("DietLogs")
        records = sheet.get_all_records()
    else:
        records = DIET_LOGS

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
        "detail": "まだ今日の記録がありません"
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
# 💬 今日の一言（体調連動）
# =====================
def get_today_message(settings, latest_log, state=None, weather="普通"):

    if state:
        if state.get("疲れ"):
            return "今日は無理しなくて大丈夫☺️ ゆっくり整えましょう"
        if state.get("食べすぎ"):
            return "昨日は気にしなくてOK。今日は軽く整えましょう"
        if state.get("冷え"):
            return "体を温めることを優先しましょう"
        if state.get("こり"):
            return "少し体を動かすと楽になりますよ"

    if weather == "寒い":
        return "温かい食事で体を整えましょう"
    if weather == "暑い":
        return "水分をしっかりとりましょう"

    return random.choice([
        "今日は軽く整えるだけでOK",
        "無理せず続けるのが一番です",
        "昨日より少し整えれば十分です",
        "できることだけやればOKです"
    ])
