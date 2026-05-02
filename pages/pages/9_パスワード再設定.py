import streamlit as st
from app_core import reset_password

st.set_page_config(
    page_title="パスワード再設定",
    page_icon="🔑",
    layout="centered"
)

st.title("🔑 パスワード再設定")
st.caption("ログインできない場合はこちらで再設定できます")

st.markdown("---")

# -----------------
# 入力
# -----------------
login_id = st.text_input("ログインID")

new_password = st.text_input("新しいパスワード", type="password")
new_password_confirm = st.text_input("新しいパスワード（確認）", type="password")

st.markdown("---")

# -----------------
# ボタン
# -----------------
if st.button("パスワードを変更する", use_container_width=True):

    if not login_id:
        st.warning("ログインIDを入力してください")

    elif not new_password:
        st.warning("新しいパスワードを入力してください")

    elif new_password != new_password_confirm:
        st.error("パスワードが一致しません")

    elif len(new_password) < 4:
        st.warning("パスワードは4文字以上にしてください")

    else:
        try:
            success = reset_password(login_id, new_password)

            if success:
                st.success("パスワードを変更しました！")
                st.info("ログイン画面からログインしてください")

            else:
                st.error("ユーザーが見つかりません")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

st.markdown("---")

# -----------------
# 戻る
# -----------------
if st.button("ログイン画面へ戻る", use_container_width=True):
    st.switch_page("pages/0_ログイン.py")
