# =========================================================
# ShufuMate
# pages/0_ログイン.py
# 最終完全版
# =========================================================

import streamlit as st

from app_core import (
    login,
    is_logged_in,
    logout,
    get_login_id,
    get_nickname,
    inject_shufumate_css,
    render_page_header,
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


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログインページ専用CSS
# =========================================================
st.markdown(
    """
<style>

/* -----------------------------------------
   ログイン案内
----------------------------------------- */
.login-welcome-card {
    background: #fff8ef;
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 20px 22px;
    color: #705649;
    line-height: 1.8;
    margin: 14px 0 28px;
}

.login-welcome-title {
    color: #5c4033;
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 4px;
}


/* -----------------------------------------
   フォーム
----------------------------------------- */
div[data-testid="stForm"] {
    background: rgba(255,255,255,.76);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 22px;
    padding: 22px 24px;
}

div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #a98a79 !important;
    box-shadow:
        0 0 0 1px rgba(141,110,99,.18)
        !important;
}


/* -----------------------------------------
   下部案内
----------------------------------------- */
.login-help {
    text-align: center;
    color: #8a7466;
    font-size: .90rem;
    line-height: 1.8;
    margin-top: 24px;
    margin-bottom: 10px;
}


/* -----------------------------------------
   ログイン済み
----------------------------------------- */
.logged-in-card {
    background: #f4f8ef;
    border: 1px solid rgba(92,130,83,.16);
    border-radius: 20px;
    padding: 18px 20px;
    color: #50644c;
    line-height: 1.8;
    margin: 15px 0 20px;
}

.logged-in-name {
    font-weight: 800;
    font-size: 1.05rem;
    color: #4e6349;
    margin-bottom: 3px;
}


/* -----------------------------------------
   モバイル
----------------------------------------- */
@media (max-width: 640px) {

    .login-welcome-card {
        padding: 17px 18px;
    }

    .logged-in-card {
        padding: 16px 18px;
    }

    div[data-testid="stForm"] {
        padding: 18px;
    }
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ログイン済みの場合
# =========================================================
if is_logged_in():

    render_page_header(
        title="ログイン",
        subtitle="ShufuMateにログインしています。",
        icon_file="ShufuMate_home_icons_8/state.png",
        emoji="🏠",
    )

    nickname = (
        get_nickname()
        or get_login_id()
        or "ユーザー"
    )

    # -----------------------------------------
    # 表示用HTMLは連結方式
    # -----------------------------------------
    logged_in_html = (
        '<div class="logged-in-card">'
        '<div class="logged-in-name">'
        f'{nickname} さん'
        '</div>'
        '現在ログインしています。'
        '</div>'
    )

    st.markdown(
        logged_in_html,
        unsafe_allow_html=True,
    )


    # -----------------------------------------
    # Homeへ
    # -----------------------------------------
    if st.button(
        "Homeへ",
        key="login_loggedin_home",
        use_container_width=True,
    ):

        st.switch_page(
            "Home.py"
        )


    # -----------------------------------------
    # ログアウト
    # -----------------------------------------
    if st.button(
        "ログアウト",
        key="login_loggedin_logout",
        use_container_width=True,
    ):

        logout()

        st.success(
            "ログアウトしました。"
        )

        st.rerun()


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
# おかえりなさい
# =========================================================
welcome_html = (
    '<div class="login-welcome-card">'
    '<div class="login-welcome-title">'
    'おかえりなさい。'
    '</div>'
    '登録したログインIDとパスワードを入力してください。'
    '</div>'
)

st.markdown(
    welcome_html,
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
        placeholder="登録したパスワード",
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


    # -----------------------------------------
    # ログインID未入力
    # -----------------------------------------
    if not login_id_clean:

        st.warning(
            "ログインIDを入力してください。"
        )


    # -----------------------------------------
    # パスワード未入力
    # -----------------------------------------
    elif not password_clean:

        st.warning(
            "パスワードを入力してください。"
        )


    # -----------------------------------------
    # 認証
    # -----------------------------------------
    else:

        try:

            # =====================================
            # app_core.py の正式なログイン関数
            # =====================================
            success = login(
                login_id_clean,
                password_clean,
            )


            # =====================================
            # ログイン成功
            # =====================================
            if success:

                st.success(
                    "ログインしました。"
                )

                st.switch_page(
                    "Home.py"
                )


            # =====================================
            # IDまたはパスワード不一致
            # =====================================
            else:

                st.error(
                    "ログインIDまたは"
                    "パスワードが違います。"
                )


        except Exception as e:

            st.error(
                "ログイン処理中に"
                "エラーが発生しました。"
            )

            # 開発中は原因確認用に表示
            st.caption(
                f"エラー内容：{e}"
            )


# =========================================================
# 新規登録案内
# =========================================================
help_html = (
    '<div class="login-help">'
    'はじめてShufuMateを使う場合は、<br>'
    '「新規登録」からアカウントを作成してください。'
    '</div>'
)

st.markdown(
    help_html,
    unsafe_allow_html=True,
)


# =========================================================
# 新規登録へ
# =========================================================
if st.button(
    "新規登録へ",
    key="login_to_signup",
    use_container_width=True,
):

    st.switch_page(
        "pages/0_新規登録.py"
    )
