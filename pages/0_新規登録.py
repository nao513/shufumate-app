# =========================================================
# ShufuMate
# 0_新規登録.py
# 完全置換版
# =========================================================

import streamlit as st
from datetime import date

from app_core import *


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="新規登録｜ShufuMate",
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

.register-success {
    background: rgba(249,243,231,.95);
    border: 1px solid rgba(139,100,72,.14);
    border-radius: 20px;
    padding: 18px 20px;
    color: #60493d;
    line-height: 1.9;
    margin-bottom: 18px;
}

.register-success-title {
    color: #5c4033;
    font-weight: 900;
    font-size: 1.08rem;
    margin-bottom: 7px;
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
# すでにログイン済み
# =========================================================
if get_user_id():

    render_page_header(
        title="新規登録",
        subtitle="現在ログインしています。",
        icon_file="ShufuMate_home_icons_8/state.png",
        emoji="🌿",
    )

    logged_html = (
        '<div class="register-intro">'
        'すでにアカウントへログインしています。'
        '<br>'
        '新しく登録する必要はありません。'
        '</div>'
    )

    st.markdown(
        logged_html,
        unsafe_allow_html=True,
    )

    if st.button(
        "Homeへ",
        key="register_logged_home",
        use_container_width=True,
    ):
        st.switch_page("Home.py")

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
    icon_file="ShufuMate_home_icons_8/state.png",
    emoji="🌿",
)


intro_html = (
    '<div class="register-intro">'
    'まずはログインに必要な情報を登録します。'
    '<br>'
    '体重や食事などの詳しい設定は、'
    '登録後に「設定」ページから変更できます。'
    '</div>'
)

st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# 新規登録フォーム
# =========================================================
with st.form(
    "shufumate_register_form"
):

    st.markdown("### アカウント")

    login_id = st.text_input(
        "ログインID",
        placeholder="例：nao0513",
        key="register_login_id",
        help=(
            "ログインするときに使うIDです。"
            "半角英数字をおすすめします。"
        ),
    )

    nickname = st.text_input(
        "ニックネーム",
        placeholder="ShufuMateで表示する名前",
        key="register_nickname",
    )

    st.markdown("---")

    st.markdown("### 生年月日")

    birth_date = st.date_input(
        "生年月日",
        value=date(1980, 1, 1),
        min_value=date(1920, 1, 1),
        max_value=date.today(),
        key="register_birth_date",
    )

    st.markdown("---")

    st.markdown("### パスワード")

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder="4文字以上",
        key="register_password",
    )

    password_confirm = st.text_input(
        "パスワード（確認）",
        type="password",
        placeholder="もう一度入力",
        key="register_password_confirm",
    )

    agree = st.checkbox(
        "入力した内容をShufuMateの記録・相談機能で使用することに同意します。",
        key="register_agree",
    )

    submitted = st.form_submit_button(
        "ShufuMateをはじめる",
        use_container_width=True,
    )


# =========================================================
# パスワード案内
# =========================================================
password_note = (
    '<div class="register-note">'
    '<strong>パスワードについて</strong>'
    '<br>'
    '数字だけでも登録できますが、'
    '英字と数字を組み合わせるとより安全です。'
    '<br>'
    '他のサービスと同じパスワードの'
    '使い回しは避けてください。'
    '</div>'
)

st.markdown(
    password_note,
    unsafe_allow_html=True,
)


# =========================================================
# 登録処理
# =========================================================
if submitted:

    login_id_clean = clean_text(login_id)
    nickname_clean = clean_text(nickname)
    password_clean = clean_text(password)
    password_confirm_clean = clean_text(
        password_confirm
    )

    error_message = None


    # -----------------------------------------------------
    # 入力チェック
    # -----------------------------------------------------
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
            "ログインIDは3文字以上で入力してください。"
        )

    elif not nickname_clean:

        error_message = (
            "ニックネームを入力してください。"
        )

    elif len(password_clean) < 4:

        error_message = (
            "パスワードは4文字以上で入力してください。"
        )

    elif (
        password_clean
        != password_confirm_clean
    ):

        error_message = (
            "確認用パスワードが一致しません。"
        )

    elif not agree:

        error_message = (
            "内容を確認して同意欄にチェックしてください。"
        )


    # -----------------------------------------------------
    # エラー
    # -----------------------------------------------------
    if error_message:

        st.warning(
            error_message
        )


    # -----------------------------------------------------
    # 新規登録
    # -----------------------------------------------------
    else:

        try:

            result = create_user(
                login_id=login_id_clean,
                password=password_clean,
                nickname=nickname_clean,
                birth_date=birth_date.strftime(
                    "%Y-%m-%d"
                ),
            )


            # =================================================
            # create_userの戻り値に対応
            # =================================================
            created_user_id = ""


            if isinstance(
                result,
                str,
            ):

                created_user_id = (
                    clean_text(result)
                )


            elif isinstance(
                result,
                dict,
            ):

                created_user_id = (
                    clean_text(
                        result.get(
                            "user_id"
                        )
                    )
                )


            elif result is True:

                # ---------------------------------------------
                # create_userがTrueのみ返す場合は
                # 登録直後に認証してuser_id取得
                # ---------------------------------------------
                auth_result = authenticate_user(
                    login_id_clean,
                    password_clean,
                )

                if isinstance(
                    auth_result,
                    str,
                ):

                    created_user_id = (
                        clean_text(
                            auth_result
                        )
                    )

                elif isinstance(
                    auth_result,
                    dict,
                ):

                    created_user_id = (
                        clean_text(
                            auth_result.get(
                                "user_id"
                            )
                        )
                    )


            # =================================================
            # create_userまたはauthenticate_user側で
            # session_state設定済みの場合
            # =================================================
            if not created_user_id:

                created_user_id = (
                    clean_text(
                        get_user_id()
                    )
                )


            # =================================================
            # セッション設定
            # =================================================
            if created_user_id:

                st.session_state[
                    "user_id"
                ] = created_user_id

                st.session_state[
                    "user_id_cookie"
                ] = created_user_id


                # ---------------------------------------------
                # ログインIDも保持
                # ---------------------------------------------
                st.session_state[
                    "login_id"
                ] = login_id_clean


                # ---------------------------------------------
                # 初期設定も作成
                # ---------------------------------------------
                try:

                    initial_settings = {
                        "nickname":
                            nickname_clean,

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
                        created_user_id,
                        initial_settings,
                    )

                except Exception:
                    # 初期設定保存に失敗しても
                    # アカウント作成自体は有効
                    pass


                # ---------------------------------------------
                # 完了状態
                # ---------------------------------------------
                st.session_state[
                    "registration_complete"
                ] = True

                st.session_state[
                    "registration_nickname"
                ] = nickname_clean

                st.rerun()


            else:

                st.error(
                    "登録は行われましたが、"
                    "ログイン情報を取得できませんでした。"
                )

                st.info(
                    "ログインページから、"
                    "登録したIDとパスワードで"
                    "ログインしてください。"
                )


        except Exception as e:

            error_text = str(e)

            # ---------------------------------------------
            # 重複IDなど
            # ---------------------------------------------
            if (
                "duplicate" in error_text.lower()
                or
                "already" in error_text.lower()
                or
                "存在" in error_text
            ):

                st.error(
                    "このログインIDはすでに使用されています。"
                )

                st.info(
                    "別のログインIDを入力してください。"
                )

            else:

                st.error(
                    "新規登録中にエラーが発生しました。"
                )

                st.caption(
                    error_text
                )


# =========================================================
# 登録完了
# =========================================================
if st.session_state.get(
    "registration_complete",
    False,
):

    nickname_saved = clean_text(
        st.session_state.get(
            "registration_nickname",
            "",
        )
    )

    success_html = (
        '<div class="register-success">'
        '<div class="register-success-title">'
        '登録できました ✨'
        '</div>'
        'ShufuMateを使い始められます。'
        '<br>'
        '次に「設定」で、目標や食事・運動の'
        'スタイルを登録すると、'
        'あなたに合った提案がしやすくなります。'
        '</div>'
    )

    st.markdown(
        success_html,
        unsafe_allow_html=True,
    )


    if st.button(
        "Homeへ",
        key="register_complete_home",
        use_container_width=True,
    ):

        st.session_state[
            "registration_complete"
        ] = False

        st.switch_page(
            "Home.py"
        )


# =========================================================
# すでにアカウントがある方
# =========================================================
render_divider()


existing_html = (
    '<div class="register-note">'
    '<strong>すでに登録済みの方</strong>'
    '<br>'
    '新しく登録せず、'
    'ログインページから続けられます。'
    '</div>'
)

st.markdown(
    existing_html,
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
