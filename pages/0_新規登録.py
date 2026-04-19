import streamlit as st
from datetime import date
from app_core import create_user, login_user, is_logged_in

st.title("🆕 新規登録")
st.caption("ShufuMateのアカウントを作成します")

if is_logged_in():
    st.success("すでにログイン済みです")
    if st.button("ホームへ", use_container_width=True):
        st.switch_page("Home.py")
    st.stop()

with st.form("register_form"):
    login_id = st.text_input("ログインID")
    password = st.text_input("パスワード", type="password")
    password_confirm = st.text_input("パスワード（確認）", type="password")
    nickname = st.text_input("ニックネーム")
    birth_date = st.date_input(
        "生年月日",
        value=date(1976, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today(),
    )

    submitted = st.form_submit_button("登録する", use_container_width=True)

if submitted:
    try:
        if password != password_confirm:
            st.error("パスワード確認が一致しません")
        else:
            user_record = create_user(
                login_id=login_id,
                password=password,
                nickname=nickname,
                birth_date=birth_date,
            )
            login_user(user_record)
            st.success("登録が完了しました")
            st.switch_page("Home.py")
    except Exception as e:
        st.error(f"登録に失敗しました: {e}")

if st.button("ログイン画面へ", use_container_width=True):
    st.switch_page("pages/0_ログイン.py")
