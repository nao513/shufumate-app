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

current_year = date.today().year

with st.form("register_form"):
    login_id = st.text_input("ログインID")
    password = st.text_input("パスワード", type="password")
    password_confirm = st.text_input("パスワード（確認）", type="password")
    nickname = st.text_input("ニックネーム")

    st.markdown("**生年月日**")
    col1, col2, col3 = st.columns(3)

    with col1:
        birth_year = st.selectbox(
            "年",
            options=list(range(current_year, 1899, -1)),
            index=list(range(current_year, 1899, -1)).index(1976) if 1976 in list(range(current_year, 1899, -1)) else 0,
        )

    with col2:
        birth_month = st.selectbox(
            "月",
            options=list(range(1, 13)),
            index=0,
        )

    with col3:
        birth_day = st.selectbox(
            "日",
            options=list(range(1, 32)),
            index=0,
        )

    submitted = st.form_submit_button("登録する", use_container_width=True)

if submitted:
    try:
        if password != password_confirm:
            st.error("パスワード確認が一致しません")
        else:
            try:
                birth_date = date(int(birth_year), int(birth_month), int(birth_day))
            except ValueError:
                st.error("生年月日が正しくありません")
                st.stop()

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
