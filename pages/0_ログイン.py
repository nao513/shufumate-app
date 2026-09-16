# =========================================================
# ShufuMate
# pages/0_ログイン.py
# 完全置換版
# =========================================================

import streamlit as st

from app_core import (
    login,
    is_logged_in,
    inject_shufumate_css,
    render_page_header,
    render_note,
    get_page_icon,
)


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="ログイン｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/state.png",
        "🏠",
    ),
    layout="centered",
)

inject_shufumate_css()


# =========================================================
# ログインページ専用CSS
# =========================================================
st.markdown(
    """
<style>

.login-welcome {
    background: #fff8ef;
    border: 1px solid rgba(139,100,72,.10);
    border-radius: 20px;
    padding: 20px 22px;
    color: #705649;
    line-height: 1.8;
    margin: 14px 0 28px;
}

.login-form-box {
    background: rgba(255,255,255,.90);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 24px;
    padding: 26px 28px 22px;
    margin-bottom: 20px;
}

.login-bottom-text {
    text-align: center;
    color: #8b7568;
    font-size: .9rem;
    line-height: 1.8;
    margin-top: 20px;
}

div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# すでにログイン済みの場合
# =========================================================
if is_logged_in():

    render_page_header(
        title="ログイン",
        subtitle="ShufuMateにログインしています。",
        icon_file="ShufuMate_home_icons_8/state.png",
        emoji="🏠",
    )

    st.success("ログイン済みです。")

    if st.button(
        "Homeへ",
        key="login_already_home",
        use_container_width=True,
    ):
        st.switch_page("Home.py")

    st.stop()


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="ログイン",
    subtitle=(
        "記録や相談を続けるために、"
        "ShufuMateへログインします。"
    ),
    icon_file="ShufuMate_home_icons_8/state.png",
    emoji="🏠",
)


# =========================================================
# 案内
# =========================================================
st.markdown(
    """
<div class="login-welcome">
    <strong>おかえりなさい。</strong><br>
    登録したログインIDとパスワードを入力してください。
</div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ログインフォーム
# =========================================================
with st.form(
    "shufumate_login_form",
    clear_on_submit=False,
):

    login_id = st.text_input(
        "ログインID",
        placeholder="登録したログインID",
        key="login_page_login_id",
    )

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder="パスワード",
        key="login_page_password",
    )

    submitted = st.form_submit_button(
        "ログイン",
        use_container_width=True,
    )


# =========================================================
# ログイン処理
# =========================================================
if submitted:

    login_id_clean = str(
        login_id or ""
    ).strip()

    password_clean = str(
        password or ""
    ).strip()

    if not login_id_clean:

        st.warning(
            "ログインIDを入力してください。"
        )

    elif not password_clean:

        st.warning(
            "パスワードを入力してください。"
        )

    else:

        try:

            # -----------------------------------------
            # app_core.py の正式な認証関数
            # -----------------------------------------
            success = login(
                login_id_clean,
                password_clean,
            )

            if success:

                st.success(
                    "ログインしました。"
                )

                st.switch_page(
                    "Home.py"
                )

            else:

                st.error(
                    "ログインIDまたはパスワードが違います。"
                )

        except Exception as e:

            st.error(
                "ログイン処理中にエラーが発生しました。"
            )

            st.caption(
                str(e)
            )


# =========================================================
# 新規登録への案内
# =========================================================
st.markdown(
    """
<div class="login-bottom-text">
    はじめてShufuMateを使う場合は、<br>
    左メニューの「新規登録」から登録してください。
</div>
    """,
    unsafe_allow_html=True,
)
