# =========================================================
# ShufuMate
# pages/0_新規登録.py
# メールアドレス対応 完全版
# =========================================================

import re
from datetime import date

import streamlit as st

from app_core import *


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="新規登録｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/state.png",
        "🌿",
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

.register-intro {
    background: rgba(255,250,244,.94);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #6d5649;
    line-height: 1.85;
    margin-bottom: 18px;
}

.register-note {
    background: rgba(255,255,255,.76);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 17px;
    padding: 14px 16px;
    color: #806b60;
    font-size: .87rem;
    line-height: 1.75;
    margin-top: 13px;
    margin-bottom: 16px;
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
# メール形式
# =========================================================
def valid_email(email):

    email = clean_text(
        email
    ).lower()

    pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    return bool(
        re.match(
            pattern,
            email,
        )
    )


# =========================================================
# ログイン済み
# =========================================================
if is_logged_in():

    render_page_header(
        title="新規登録",
        subtitle="現在ログインしています。",
        icon_file=(
            "ShufuMate_home_icons_8/"
            "state.png"
        ),
        emoji="🌿",
    )

    st.info(
        "すでにアカウントへ"
        "ログインしています。"
    )

    if st.button(
        "Homeへ",
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
    title="新規登録",
    subtitle=(
        "ShufuMateをあなた専用にするための"
        "最初の設定です。"
    ),
    icon_file=(
        "ShufuMate_home_icons_8/"
        "state.png"
    ),
    emoji="🌿",
)


intro_html = (
    '<div class="register-intro">'
    'まずはログインに必要な情報を登録します。'
    '<br>'
    'メールアドレスは、将来パスワードを'
    '忘れた場合の本人確認に使用します。'
    '</div>'
)

st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# 登録フォーム
# =========================================================
with st.form(
    "shufumate_register_form",
    clear_on_submit=False,
):

    st.markdown(
        "### アカウント"
    )

    login_id = st.text_input(
        "ログインID",
        placeholder="例：nao0513",
        help=(
            "ログインするときに使うIDです。"
            "半角英数字をおすすめします。"
        ),
    )

    nickname = st.text_input(
        "ニックネーム",
        placeholder=(
            "ShufuMateで表示する名前"
        ),
    )

    email = st.text_input(
        "メールアドレス",
        placeholder=(
            "例：sample@example.com"
        ),
        help=(
            "パスワードを忘れた場合の"
            "本人確認に使用します。"
        ),
    )

    st.markdown("---")

    st.markdown(
        "### 生年月日"
    )

    birth_date = st.date_input(
        "生年月日",
        value=date(
            1980,
            1,
            1,
        ),
        min_value=date(
            1920,
            1,
            1,
        ),
        max_value=date.today(),
        format="YYYY/MM/DD",
    )

    st.markdown("---")

    st.markdown(
        "### パスワード"
    )

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder=(
            "英字と数字を組み合わせて8文字以上"
        ),
    )

    password_confirm = st.text_input(
        "パスワード（確認）",
        type="password",
        placeholder=(
            "もう一度入力"
        ),
    )

    agree = st.checkbox(
        "入力した内容をShufuMateの"
        "記録・相談機能で使用することに"
        "同意します。"
    )

    submitted = (
        st.form_submit_button(
            "ShufuMateをはじめる",
            use_container_width=True,
        )
    )


# =========================================================
# パスワード案内
# =========================================================
note_html = (
    '<div class="register-note">'
    '<strong>パスワードについて</strong>'
    '<br>'
    '英字と数字を組み合わせた'
    '8文字以上をおすすめします。'
    '<br>'
    '他のサービスと同じパスワードの'
    '使い回しは避けてください。'
    '</div>'
)

st.markdown(
    note_html,
    unsafe_allow_html=True,
)


# =========================================================
# 登録
# =========================================================
if submitted:

    login_id_clean = clean_text(
        login_id
    )

    nickname_clean = clean_text(
        nickname
    )

    email_clean = clean_text(
        email
    ).lower()

    password_clean = clean_text(
        password
    )

    password_confirm_clean = clean_text(
        password_confirm
    )

    error_message = ""


    if not login_id_clean:

        error_message = (
            "ログインIDを入力してください。"
        )

    elif " " in login_id_clean:

        error_message = (
            "ログインIDに空白は使用できません。"
        )

    elif len(login_id_clean) < 3:

        error_message = (
            "ログインIDは3文字以上で"
            "入力してください。"
        )

    elif not nickname_clean:

        error_message = (
            "ニックネームを入力してください。"
        )

    elif not email_clean:

        error_message = (
            "メールアドレスを入力してください。"
        )

    elif not valid_email(
        email_clean
    ):

        error_message = (
            "メールアドレスの形式を"
            "確認してください。"
        )

    elif len(password_clean) < 8:

        error_message = (
            "パスワードは8文字以上で"
            "入力してください。"
        )

    elif not any(
        c.isalpha()
        for c in password_clean
    ):

        error_message = (
            "パスワードには英字を"
            "1文字以上入れてください。"
        )

    elif not any(
        c.isdigit()
        for c in password_clean
    ):

        error_message = (
            "パスワードには数字を"
            "1文字以上入れてください。"
        )

    elif (
        password_clean
        != password_confirm_clean
    ):

        error_message = (
            "確認用パスワードが"
            "一致しません。"
        )

    elif not agree:

        error_message = (
            "内容を確認して同意欄に"
            "チェックしてください。"
        )


    if error_message:

        st.warning(
            error_message
        )

    else:

        try:

            result = create_user(
                login_id=login_id_clean,
                password=password_clean,
                nickname=nickname_clean,
                birth_date=birth_date,
                email=email_clean,
            )


            # ---------------------------------
            # ID重複
            # ---------------------------------
            if (
                isinstance(result, dict)
                and
                result.get("error")
                ==
                "duplicate_login_id"
            ):

                st.error(
                    "このログインIDは"
                    "すでに使用されています。"
                )


            # ---------------------------------
            # メール重複
            # ---------------------------------
            elif (
                isinstance(result, dict)
                and
                result.get("error")
                ==
                "duplicate_email"
            ):

                st.error(
                    "このメールアドレスは"
                    "すでに登録されています。"
                )


            # ---------------------------------
            # 登録失敗
            # ---------------------------------
            elif not result:

                st.error(
                    "アカウントを"
                    "作成できませんでした。"
                )


            # ---------------------------------
            # 登録成功
            # ---------------------------------
            else:

                # 正式なlogin()を使って
                # ログイン状態にする
                success = login(
                    login_id_clean,
                    password_clean,
                )

                if not success:

                    st.warning(
                        "登録は完了しましたが、"
                        "自動ログインできませんでした。"
                    )

                    st.info(
                        "ログインページから"
                        "ログインしてください。"
                    )

                else:

                    user_id = get_user_id()

                    # -------------------------
                    # 初期設定
                    # -------------------------
                    initial_settings = {

                        "nickname":
                            nickname_clean,

                        "birth_date":
                            birth_date.strftime(
                                "%Y-%m-%d"
                            ),

                        "height":
                            "",

                        "current_weight":
                            "",

                        "target_weight":
                            "",

                        "current_body_fat":
                            "",

                        "target_body_fat":
                            "",

                        "current_muscle_mass":
                            "",

                        "target_muscle_mass":
                            "",

                        "user_type":
                            "健康維持",

                        "activity_level":
                            "普通",

                        "food_style":
                            "特に決めていない",

                        "constitution_traits":
                            [],

                        "advice_tone":
                            "やさしく",

                        "workout_today":
                            "",

                        "fridge_items":
                            "",

                        "avoid_foods":
                            "",

                        "favorite_meals":
                            "",
                    }

                    save_user_settings(
                        user_id,
                        initial_settings,
                    )

                    st.success(
                        "登録できました ✨"
                    )

                    st.info(
                        "続けて、目標や食事・"
                        "運動について設定しましょう。"
                    )

                    if st.button(
                        "設定へ進む",
                        key=(
                            "register_to_settings"
                        ),
                        use_container_width=True,
                    ):

                        st.switch_page(
                            "pages/1_設定.py"
                        )


        except Exception as e:

            st.error(
                "新規登録中に"
                "エラーが発生しました。"
            )

            st.caption(
                str(e)
            )


# =========================================================
# ログインへ
# =========================================================
render_divider()

st.markdown(
    '<div class="register-note">'
    '<strong>すでに登録済みの方</strong>'
    '<br>'
    '新しく登録せず、ログインページから'
    '続けられます。'
    '</div>',
    unsafe_allow_html=True,
)


if st.button(
    "ログインへ",
    key="register_go_login",
    use_container_width=True,
):

    st.switch_page(
        "pages/0_ログイン.py"
    )
