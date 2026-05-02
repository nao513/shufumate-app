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
