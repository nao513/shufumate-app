# =====================
# 🔐 仮ログイン（復旧用）
# =====================
USERS = {
    "test": {
        "password": "1234",
        "nickname": "はは"
    }
}

def verify_login(login_id, password):
    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {
            "user_id": login_id,
            "nickname": user["nickname"]
        }
    return None

def create_user(login_id, password, nickname, birth_date):
    USERS[login_id] = {
        "password": password,
        "nickname": nickname
    }
    return {"user_id": login_id, "nickname": nickname}

def reset_password(login_id, new_password):
    if login_id in USERS:
        USERS[login_id]["password"] = new_password
        return True
    return False
# =====================
# 🔐 セッション管理（必須）
# =====================
def login_user(user_record):
    import streamlit as st
    st.session_state["login_user"] = user_record

def is_logged_in():
    import streamlit as st
    return "login_user" in st.session_state

def get_user_id():
    import streamlit as st
    return st.session_state.get("login_user", {}).get("user_id", "guest")

def require_login():
    import streamlit as st
    if "login_user" not in st.session_state:
        st.warning("ログインしてください")
        st.switch_page("pages/0_ログイン.py")
        st.stop()
# =====================
# 📊 設定（仮）
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

def load_latest_log(user_id):
    logs = [l for l in DIET_LOGS if l["user_id"] == user_id]

    if not logs:
        return None

    return sorted(logs, key=lambda x: x.get("log_date", ""))[-1]
# =====================
# 🍽 今日のアドバイス
# =====================
def get_today_advice(settings, latest_log):
    return {
        "朝": "軽めに整えましょう☀️",
        "昼": "バランスよく食べましょう🍱",
        "夜": "消化にやさしく🌙"
    }

# =====================
# 🏃‍♀️ 今日の運動
# =====================
def get_today_exercise(settings, latest_log):
    return "軽くストレッチから始めましょう"
# =====================
# 🕒 時間
# =====================
from datetime import datetime

def jst_now():
    return datetime.now()

def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")
# =====================
# 📅 週キー
# =====================
def get_week_key():
    from datetime import datetime
    return datetime.now().strftime("%Y-%W")
