# =========================================================
# ShufuMate
# pages/0_ログイン.py
# パスワード忘れ案内対応 完全版
# =========================================================

import html

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

inject_shufumate_css()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

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

.login-help {
    text-align: center;
    color: #8a7466;
    font-size: .90rem;
    line-height: 1.8;
    margin: 22px 0 10px;
}

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
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,.76);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 22px;
    padding: 22px 24px;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,.65);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 18px;
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ログイン済み
# =========================================================
if is_logged_in():

    render_page_header(
        title="ログイン",
        subtitle=(
            "ShufuMateにログインしています。"
        ),
        icon_file=(
            "ShufuMate_home_icons_8/"
            "state.png"
        ),
        emoji="🏠",
    )

    nickname = (
        get_nickname()
        or get_login_id()
        or "ユーザー"
    )

    logged_html = (
        '<div class="logged-in-card">'
        '<div class="logged-in-name">'
        f'{html.escape(str(nickname))} さん'
        '</div>'
        '現在ログインしています。'
        '</div>'
    )

    st.markdown(
        logged_html,
        unsafe_allow_html=True,
    )

    if st.button(
        "Homeへ",
        key="login_loggedin_home",
        use_container_width=True,
    ):

        st.switch_page(
            "Home.py"
        )

    if st.button(
        "ログアウト",
        key="login_loggedin_logout",
        use_container_width=True,
    ):

        logout()
        st.rerun()

    st.stop()


# =========================================================
# ヘッダー
# =========================================================
render_page_header(
    title="ログイン",
    subtitle=(
        "記録や相談を続けるために、"
        "ShufuMateへログインします。"
    ),
    icon_file=(
        "ShufuMate_home_icons_8/"
        "state.png"
    ),
    emoji="🏠",
)


welcome_html = (
    '<div class="login-welcome-card">'
    '<div class="login-welcome-title">'
    'おかえりなさい。'
    '</div>'
    '登録したログインIDと'
    'パスワードを入力してください。'
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
        placeholder=(
            "登録したログインID"
        ),
    )

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder=(
            "登録したパスワード"
        ),
    )

    submitted = (
        st.form_submit_button(
            "ログイン",
            use_container_width=True,
        )
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
                    "ログインIDまたは"
                    "パスワードが違います。"
                )

        except Exception as e:

            st.error(
                "ログイン処理中に"
                "エラーが発生しました。"
            )

            st.caption(
                f"エラー内容：{e}"
            )


# =========================================================
# パスワードを忘れた場合
# =========================================================
with st.expander(
    "パスワードを忘れた方",
    expanded=False,
):

    st.markdown(
        """
登録したメールアドレスを使った
**パスワード再設定機能を準備中です。**

現在のテスト期間中にパスワードを
忘れた場合は、管理者へお問い合わせください。

安全のため、ログインIDだけで
パスワードを変更することはできません。
        """
    )


# =========================================================
# 新規登録
# =========================================================
help_html = (
    '<div class="login-help">'
    'はじめてShufuMateを使う場合は、<br>'
    '「新規登録」からアカウントを'
    '作成してください。'
    '</div>'
)

st.markdown(
    help_html,
    unsafe_allow_html=True,
)


if st.button(
    "新規登録へ",
    key="login_to_signup",
    use_container_width=True,
):

    st.switch_page(
        "pages/0_新規登録.py"
    )
