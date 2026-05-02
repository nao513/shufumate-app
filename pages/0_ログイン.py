import streamlit as st
from app_core import verify_login, login_user, is_logged_in, reset_password

st.set_page_config(page_title="ログイン", page_icon="🔐", layout="centered")

st.title("🔐 ログイン")
st.caption("ShufuMateにログインします")

# -----------------
# ログイン済み
# -----------------
if is_logged_in():
    st.success("ログイン済みです")

    if st.button("ホームへ", use_container_width=True):
        st.switch_page("Home.py")

    if st.button("ログアウト", use_container_width=True):
        del st.session_state["login_user"]
        st.rerun()

    st.stop()

# -----------------
# タブ切替
# -----------------
tab1, tab2 = st.tabs(["ログイン", "パスワード再設定"])

# =====================
# 🔐 ログインタブ
# =====================
with tab1:

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
            st.error(f"ログインエラー: {e}")

# =====================
# 🔑 パスワード再設定
# =====================
with tab2:

    st.markdown("### 🔑 パスワード再設定")

    login_id_reset = st.text_input("ログインID（再設定用）")

    new_pw = st.text_input("新しいパスワード", type="password")
    new_pw_confirm = st.text_input("新しいパスワード（確認）", type="password")

    if st.button("パスワードを変更する", use_container_width=True):

        if not login_id_reset:
            st.warning("ログインIDを入力してください")

        elif not new_pw:
            st.warning("新しいパスワードを入力してください")

        elif new_pw != new_pw_confirm:
            st.error("パスワードが一致しません")

        elif len(new_pw) < 4:
            st.warning("パスワードは4文字以上にしてください")

        else:
            try:
                success = reset_password(login_id_reset, new_pw)

                if success:
                    st.success("パスワードを変更しました！")
                    st.info("ログインタブからログインしてください")

                else:
                    st.error("ユーザーが見つかりません")

            except Exception as e:
                st.error(f"エラー: {e}")

# -----------------
# 下部ボタン
# -----------------
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("新規登録へ", use_container_width=True):
        st.switch_page("pages/0_新規登録.py")

with col2:
    if st.button("再読み込み", use_container_width=True):
        st.rerun()
