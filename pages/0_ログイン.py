# =========================================================
# ShufuMate
# 0_ログイン.py
# 完全置換版
# =========================================================

import streamlit as st

from app_core import *


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="ログイン｜ShufuMate",
    page_icon="🌿",
    layout="centered",
)

inject_shufumate_css()


# =========================================================
# ページ専用CSS
# =========================================================
st.markdown(
    """
<style>
.login-wrap {
    max-width: 560px;
    margin: 0 auto;
}

.login-message {
    background: rgba(255,250,244,.94);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #6d5649;
    line-height: 1.85;
    margin-bottom: 18px;
}

.login-note {
    color: #917b70;
    font-size: .86rem;
    line-height: 1.75;
    margin-top: 15px;
}

.login-account {
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 18px;
    padding: 15px 17px;
    color: #695247;
    line-height: 1.8;
    margin-top: 16px;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,.70);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 22px;
    padding: 22px;
}

div[data-baseweb="input"] > div {
    border-radius: 14px !important;
}
</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# すでにログインしている場合
# =========================================================
if get_user_id():

    render_page_header(
        title="ログイン",
        subtitle="ShufuMateへようこそ。",
        icon_file="ShufuMate_home_icons_8/state.png",
        emoji="🌿",
    )

    already_html = (
        '<div class="login-message">'
        'すでにログインしています。'
        '<br>'
        'そのままHomeへ進めます。'
        '</div>'
    )

    st.markdown(
        already_html,
        unsafe_allow_html=True,
    )

    if st.button(
        "Homeへ",
        key="login_go_home",
        use_container_width=True,
    ):
        st.switch_page(
            "Home.py"
        )

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
    icon_file="ShufuMate_home_icons_8/state.png",
    emoji="🌿",
)


welcome_html = (
    '<div class="login-message">'
    'おかえりなさい。'
    '<br>'
    '登録したログインIDとパスワードを'
    '入力してください。'
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
    "shufumate_login_form"
):

    login_id = st.text_input(
        "ログインID",
        placeholder="登録したログインID",
        key="login_id_input",
    )

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder="パスワード",
        key="login_password_input",
    )

    submitted = st.form_submit_button(
        "ログイン",
        use_container_width=True,
    )


# =========================================================
# ログイン処理
# =========================================================
if submitted:

    login_id_clean = clean_text(
        login_id
    )

    password_clean = clean_text(
        password
    )

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

            result = authenticate_user(
                login_id_clean,
                password_clean,
            )

            if result:

                # -----------------------------------------
                # app_coreのauthenticate_userが
                # user_idを返す場合
                # -----------------------------------------
                if isinstance(
                    result,
                    str,
                ):

                    st.session_state[
                        "user_id"
                    ] = result

                    st.session_state[
                        "user_id_cookie"
                    ] = result


                # -----------------------------------------
                # dictを返す場合にも対応
                # -----------------------------------------
                elif isinstance(
                    result,
                    dict,
                ):

                    authenticated_user_id = (
                        clean_text(
                            result.get(
                                "user_id"
                            )
                        )
                    )

                    if authenticated_user_id:

                        st.session_state[
                            "user_id"
                        ] = authenticated_user_id

                        st.session_state[
                            "user_id_cookie"
                        ] = authenticated_user_id


                # -----------------------------------------
                # authenticate_user側ですでに
                # session_stateを設定する場合も対応
                # -----------------------------------------
                if get_user_id():

                    st.success(
                        "ログインしました ✨"
                    )

                    st.switch_page(
                        "Home.py"
                    )

                else:

                    st.error(
                        "ログイン情報を確認できませんでした。"
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
render_divider()


register_html = (
    '<div class="login-account">'
    '<strong>はじめて使う方</strong>'
    '<br>'
    '最初に新規登録をすると、'
    '自分専用の記録を保存できるようになります。'
    '</div>'
)

st.markdown(
    register_html,
    unsafe_allow_html=True,
)


if st.button(
    "新規登録へ",
    key="login_go_register",
    use_container_width=True,
):

    st.switch_page(
        "pages/0_新規登録.py"
    )


# =========================================================
# パスワードについて
# =========================================================
note_html = (
    '<div class="login-note">'
    'パスワードは他のサービスと同じものを'
    '使い回さないことをおすすめします。'
    '</div>'
)

st.markdown(
    note_html,
    unsafe_allow_html=True,
)
