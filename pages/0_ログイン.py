import streamlit as st
from app_core import verify_login, login_user, is_logged_in

st.title("🔐 ログイン")
st.caption("ShufuMateにログインします")

if is_logged_in():
    st.success("ログイン済みです")
    if st.button("ホームへ", use_container_width=True):
        st.switch_page("Home.py")
    st.stop()

with st.form("login_form"):
    login_id = st.text_input("ログインID")
    password = st.text_input("パスワード", type="password")
    submitted = st.form_submit_button("ログイン", use_container_width=True)

if submitted:
    try:
        user_record = verify_login(login_id, password)
        if user_record:
            login_user(user_record)
            st.success("ログインしました")
            st.switch_page("Home.py")
        else:
            st.error("ログインIDまたはパスワードが違います")
    except Exception as e:
        st.error(f"ログインに失敗しました: {e}")

col1, col2 = st.columns(2)

with col1:
    if st.button("新規登録へ", use_container_width=True):
        st.switch_page("pages/0_新規登録.py")

with col2:
    if st.button("ホームへ戻る", use_container_width=True):
        st.switch_page("Home.py")
