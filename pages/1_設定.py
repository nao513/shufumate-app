# =========================================================
# ShufuMate
# 1_設定.py
# 完全版
# =========================================================

import streamlit as st
from datetime import datetime, date
from app_core import *


# =========================================================
# ページ設定
# ※ 必ず最初のStreamlit命令
# =========================================================
st.set_page_config(
    page_title="設定｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/settings.png",
        "⚙️",
    ),
    layout="centered",
)


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログイン
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# このページ専用CSS
# =========================================================
st.markdown(
    """
    <style>

    /* -----------------------------------------
       設定グループ説明
    ----------------------------------------- */

    .setting-help {
        color: #897469;
        font-size: 0.88rem;
        line-height: 1.75;
        margin-top: -4px;
        margin-bottom: 14px;
    }


    /* -----------------------------------------
       年齢表示
    ----------------------------------------- */

    .age-card {
        background: #fff8ef;
        border: 1px solid rgba(139,100,72,.12);
        border-radius: 16px;
        padding: 13px 15px;
        margin-top: 5px;
        margin-bottom: 12px;
        color: #765747;
    }

    .age-card strong {
        color: #5c4033;
        font-size: 1.05rem;
    }


    /* -----------------------------------------
       アカウント情報
    ----------------------------------------- */

    .account-card {
        background: rgba(255,255,255,.90);
        border: 1px solid rgba(139,100,72,.12);
        border-radius: 18px;
        padding: 16px 18px;
        color: #665044;
        line-height: 1.8;
        margin-bottom: 15px;
    }

    .account-label {
        color: #947b6d;
        font-size: .82rem;
    }

    .account-value {
        color: #5c4033;
        font-weight: 800;
    }


    /* -----------------------------------------
       expander
    ----------------------------------------- */

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,.60);
        border: 1px solid rgba(139,100,72,.12);
        border-radius: 17px;
        overflow: hidden;
    }


    /* -----------------------------------------
       スマホ
    ----------------------------------------- */

    @media (max-width: 640px) {

        .age-card {
            padding: 11px 13px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ローカル補助関数
# =========================================================
def local_text(value):

    return clean_text(value)


def local_float(
    value,
    default=0.0,
):

    try:

        if value is None:
            return float(default)

        text = clean_text(value)

        if not text:
            return float(default)

        return float(text)

    except Exception:

        return float(default)


def option_index(
    options,
    current_value,
    default_index=0,
):

    current_value = clean_text(
        current_value
    )

    if current_value in options:

        return options.index(
            current_value
        )

    return default_index


def calculate_age(
    birth_value
):

    birth_text = clean_text(
        birth_value
    )

    if not birth_text:
        return None

    try:

        birth = datetime.strptime(
            birth_text,
            "%Y-%m-%d",
        ).date()

    except Exception:

        return None

    today = jst_today().date()

    age = (
        today.year
        - birth.year
        - (
            (today.month, today.day)
            <
            (birth.month, birth.day)
        )
    )

    return age


# =========================================================
# 設定読み込み
# =========================================================
try:

    settings = (
        load_user_settings(
            user_id
        )
        or {}
    )

except Exception as e:

    st.error(
        "設定データを読み込めませんでした。"
    )

    st.caption(
        str(e)
    )

    settings = {}


# =========================================================
# Usersプロフィール
# =========================================================
try:

    profile = (
        load_current_user_profile(
            user_id
        )
        or {}
    )

except Exception:

    profile = {}


# =========================================================
# 初期値
# =========================================================
nickname_default = (
    local_text(
        profile.get("nickname")
    )
    or
    local_text(
        settings.get("nickname")
    )
)


birth_date_text = local_text(
    profile.get("birth_date")
)

age = calculate_age(
    birth_date_text
)


height_default = local_float(
    settings.get("height"),
    155.0,
)

current_weight_default = local_float(
    settings.get("current_weight"),
    50.0,
)

target_weight_default = local_float(
    settings.get("target_weight"),
    50.0,
)

current_fat_default = local_float(
    settings.get("current_body_fat"),
    20.0,
)

target_fat_default = local_float(
    settings.get("target_body_fat"),
    20.0,
)


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="設定",
    subtitle=(
        "あなたに合った提案ができるように、"
        "からだ・食事・運動の情報を設定します。"
    ),
    icon_file=(
        "ShufuMate_home_icons_8/settings.png"
    ),
    emoji="⚙️",
)


# =========================================================
# 基本設定
# =========================================================
render_section_header(
    title="基本設定",
    icon_file=(
        "ShufuMate_home_icons_8/settings.png"
    ),
    emoji="⚙️",
)

render_note(
    "ここで設定した内容は、"
    "ShufuMateの相談やおすすめを"
    "あなた向けに調整するために使います。"
)


# =========================================================
# ニックネーム
# =========================================================
nickname = st.text_input(
    "ニックネーム",
    value=nickname_default,
    placeholder="例：nao",
)


# =========================================================
# 生年月日
# =========================================================
if birth_date_text:

    try:

        birth_date_value = (
            datetime.strptime(
                birth_date_text,
                "%Y-%m-%d",
            ).date()
        )

        st.date_input(
            "生年月日",
            value=birth_date_value,
            disabled=True,
        )

    except Exception:

        st.text_input(
            "生年月日",
            value=birth_date_text,
            disabled=True,
        )

else:

    st.text_input(
        "生年月日",
        value="未設定",
        disabled=True,
    )


if age is not None:

    st.markdown(
        f"""
        <div class="age-card">
            現在の年齢：
            <strong>{age}歳</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 身長
# =========================================================
height = st.number_input(
    "身長（cm）",
    min_value=100.0,
    max_value=220.0,
    value=float(height_default),
    step=0.1,
    format="%.1f",
)


# =========================================================
# 体重
# =========================================================
weight_col1, weight_col2 = (
    st.columns(2)
)

with weight_col1:

    current_weight = st.number_input(
        "現在の体重（kg）",
        min_value=30.0,
        max_value=200.0,
        value=float(
            current_weight_default
        ),
        step=0.1,
        format="%.1f",
    )

with weight_col2:

    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=30.0,
        max_value=200.0,
        value=float(
            target_weight_default
        ),
        step=0.1,
        format="%.1f",
    )


# =========================================================
# 体脂肪率
# =========================================================
fat_col1, fat_col2 = (
    st.columns(2)
)

with fat_col1:

    current_body_fat = (
        st.number_input(
            "現在の体脂肪率（%）",
            min_value=5.0,
            max_value=60.0,
            value=float(
                current_fat_default
            ),
            step=0.1,
            format="%.1f",
        )
    )

with fat_col2:

    target_body_fat = (
        st.number_input(
            "目標体脂肪率（%）",
            min_value=5.0,
            max_value=60.0,
            value=float(
                target_fat_default
            ),
            step=0.1,
            format="%.1f",
        )
    )


# =========================================================
# 相談・提案設定
# =========================================================
render_section_header(
    title="相談・提案",
    icon_file=(
        "ShufuMate_home_icons_8/advice.png"
    ),
    emoji="💡",
)

st.markdown(
    """
    <div class="setting-help">
        今の目的や生活スタイルを設定すると、
        食事・運動の提案を調整しやすくなります。
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 目的
# =========================================================
goal_options = [
    "健康維持",
    "体脂肪を減らしたい",
    "筋肉を増やしたい",
    "体重を減らしたい",
    "体力をつけたい",
    "生活習慣を整えたい",
]

user_type = st.selectbox(
    "今の目的",
    goal_options,
    index=option_index(
        goal_options,
        settings.get("user_type"),
        0,
    ),
)


# =========================================================
# 活動量
# =========================================================
activity_options = [
    "少なめ",
    "普通",
    "やや多め",
    "多め",
]

activity_level = st.selectbox(
    "普段の活動量",
    activity_options,
    index=option_index(
        activity_options,
        settings.get(
            "activity_level"
        ),
        1,
    ),
)


# =========================================================
# 食事スタイル
# =========================================================
food_style_options = [
    "特に決めていない",
    "和食中心",
    "たんぱく質を意識",
    "野菜を多めに意識",
    "糖質を控えめに意識",
    "バランス重視",
]

food_style = st.selectbox(
    "食事スタイル",
    food_style_options,
    index=option_index(
        food_style_options,
        settings.get("food_style"),
        0,
    ),
)


# =========================================================
# 気になること
# =========================================================
constitution_options = [
    "疲れやすい",
    "冷えが気になる",
    "むくみが気になる",
    "便通を整えたい",
    "肩・首がこりやすい",
    "腰が気になる",
    "睡眠を整えたい",
    "筋力低下が気になる",
    "特になし",
]

saved_constitution = (
    settings_text_to_list(
        settings.get(
            "constitution_traits"
        )
    )
)

saved_constitution = [
    item
    for item in saved_constitution
    if item in constitution_options
]

constitution_traits = (
    st.multiselect(
        "からだで気になること",
        constitution_options,
        default=saved_constitution,
    )
)


# =========================================================
# アドバイスの雰囲気
# =========================================================
tone_options = [
    "やさしく",
    "簡潔に",
    "しっかり詳しく",
    "励ましながら",
]

advice_tone = st.selectbox(
    "アドバイスの雰囲気",
    tone_options,
    index=option_index(
        tone_options,
        settings.get("advice_tone"),
        0,
    ),
)


# =========================================================
# 運動
# =========================================================
render_section_header(
    title="運動",
    icon_file="exercise.png",
    emoji="🧘",
)

st.markdown(
    """
    <div class="setting-help">
        普段よく行う運動を入力してください。
        複数ある場合は「、」で区切って入力できます。
    </div>
    """,
    unsafe_allow_html=True,
)


workout_today = st.text_area(
    "よく行う運動",
    value=local_text(
        settings.get("workout_today")
    ),
    placeholder=(
        "例：ヨガ、筋トレ、"
        "ウォーキング、ランニング"
    ),
    height=85,
)


# =========================================================
# 食材・冷蔵庫
# =========================================================
render_section_header(
    title="食材・冷蔵庫",
    icon_file="food.png",
    emoji="🥕",
)


fridge_items = st.text_area(
    "よく家にある食材",
    value=local_text(
        settings.get("fridge_items")
    ),
    placeholder=(
        "例：卵、納豆、豆腐、鶏肉、"
        "しめじ、青菜"
    ),
    height=90,
)


avoid_foods = st.text_area(
    "避けたい食品・苦手なもの",
    value=local_text(
        settings.get("avoid_foods")
    ),
    placeholder=(
        "例：辛すぎるもの、"
        "脂っこいもの"
    ),
    height=80,
)


favorite_meals = st.text_area(
    "好きなメニュー・定番メニュー",
    value=local_text(
        settings.get("favorite_meals")
    ),
    placeholder=(
        "例：味噌汁、おにぎり、"
        "豚しゃぶ、豆乳うどん"
    ),
    height=90,
)


# =========================================================
# 保存
# =========================================================
render_divider()


if st.button(
    "設定を保存する",
    key="save_settings",
    use_container_width=True,
):

    settings_data = {

        "nickname":
            nickname,

        "height":
            round(
                float(height),
                1,
            ),

        "current_weight":
            round(
                float(current_weight),
                1,
            ),

        "target_weight":
            round(
                float(target_weight),
                1,
            ),

        "current_body_fat":
            round(
                float(current_body_fat),
                1,
            ),

        "target_body_fat":
            round(
                float(target_body_fat),
                1,
            ),

        "user_type":
            user_type,

        "activity_level":
            activity_level,

        "food_style":
            food_style,

        "constitution_traits":
            constitution_traits,

        "advice_tone":
            advice_tone,

        "workout_today":
            workout_today,

        "fridge_items":
            fridge_items,

        "avoid_foods":
            avoid_foods,

        "favorite_meals":
            favorite_meals,
    }

    try:

        save_user_settings(
            user_id,
            settings_data,
        )

        update_current_user_profile(
            user_id,
            nickname=nickname,
        )

        st.success(
            "設定を保存しました ✨"
        )

        st.rerun()

    except Exception as e:

        st.error(
            "設定の保存中にエラーが発生しました。"
        )

        st.caption(
            str(e)
        )
# =========================================================
# アカウント
# =========================================================
render_section_header(
    title="アカウント",
    icon_file="ShufuMate_home_icons_8/settings.png",
    emoji="👤",
)

login_id = get_login_id()

account_html = (
    '<div class="account-card">'
    '<div class="account-label">ログインID</div>'
    f'<div class="account-value">{safe_text(login_id or "—")}</div>'
    '</div>'
)

st.markdown(
    account_html,
    unsafe_allow_html=True,
)


# =========================================================
# パスワード変更
# =========================================================
with st.expander(
    "パスワードを変更する",
    expanded=False,
):

    new_password = st.text_input(
        "新しいパスワード",
        type="password",
        key="settings_password_new",
    )

    new_password_confirm = st.text_input(
        "新しいパスワード（確認）",
        type="password",
        key="settings_password_confirm",
    )

    if st.button(
        "パスワードを変更",
        key="settings_password_change_button",
        use_container_width=True,
    ):

        new_password = clean_text(
            new_password
        )

        new_password_confirm = clean_text(
            new_password_confirm
        )

        if len(new_password) < 4:

            st.warning(
                "パスワードは4文字以上で入力してください。"
            )

        elif new_password != new_password_confirm:

            st.warning(
                "確認用パスワードが一致しません。"
            )

        else:

            try:

                success = reset_password(
                    login_id,
                    new_password,
                )

                if success:

                    st.success(
                        "パスワードを変更しました。"
                    )

                else:

                    st.error(
                        "パスワードを変更できませんでした。"
                    )

            except Exception as e:

                st.error(
                    "パスワード変更中にエラーが発生しました。"
                )

                st.caption(
                    str(e)
                )


# =========================================================
# ログアウト
# =========================================================
render_divider()

if st.button(
    "ログアウト",
    key="settings_logout_button",
    use_container_width=True,
):

    logout()

    st.switch_page(
        "pages/0_ログイン.py"
    )

