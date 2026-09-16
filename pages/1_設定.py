# =========================================================
# ShufuMate
# pages/1_設定.py
# 完全置換版
# =========================================================

import streamlit as st
from datetime import date, datetime

from app_core import *


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="設定｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/settings.png",
        "⚙️",
    ),
    layout="centered",
)

inject_shufumate_css()
require_login()

user_id = get_user_id()


# =========================================================
# ページ専用CSS
# =========================================================
st.markdown(
    """
<style>

.settings-intro {
    background: rgba(255,250,244,.94);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #70594d;
    line-height: 1.85;
    margin-bottom: 20px;
}

.settings-age-card {
    background: rgba(255,250,244,.90);
    border: 1px solid rgba(139,100,72,.13);
    border-radius: 18px;
    padding: 15px 18px;
    color: #705346;
    font-size: 1rem;
    margin-top: 8px;
    margin-bottom: 15px;
}

.settings-section-title {
    color: #5e4336;
    font-size: 1.38rem;
    font-weight: 900;
    margin-top: 28px;
    margin-bottom: 14px;
}

.settings-description {
    color: #806a5d;
    line-height: 1.8;
    margin-bottom: 15px;
}

.settings-current-note {
    background: rgba(244,248,239,.92);
    border: 1px solid rgba(92,130,83,.14);
    border-radius: 16px;
    padding: 12px 15px;
    color: #5f7059;
    font-size: .88rem;
    line-height: 1.7;
    margin: 8px 0 16px;
}

.account-card {
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(139,100,72,.13);
    border-radius: 20px;
    padding: 18px 20px;
    margin-top: 8px;
    margin-bottom: 16px;
}

.account-label {
    color: #947d70;
    font-size: .84rem;
    margin-bottom: 4px;
}

.account-value {
    color: #5e463a;
    font-weight: 800;
    font-size: 1.05rem;
}

div[data-baseweb="input"] > div {
    border-radius: 14px !important;
}

div[data-baseweb="select"] > div {
    border-radius: 14px !important;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 14px !important;
}

div[data-testid="stNumberInput"] > div {
    border-radius: 14px !important;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,.68);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 18px;
}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def to_float(value, default=0.0):

    try:
        value = clean_text(value)

        if value == "":
            return float(default)

        return float(value)

    except Exception:
        return float(default)


def calculate_age(birth_date_value):

    if not birth_date_value:
        return None

    try:

        if isinstance(birth_date_value, str):

            birth = datetime.strptime(
                birth_date_value[:10],
                "%Y-%m-%d",
            ).date()

        elif isinstance(birth_date_value, datetime):

            birth = birth_date_value.date()

        else:

            birth = birth_date_value

        today = date.today()

        return (
            today.year
            - birth.year
            - (
                (today.month, today.day)
                <
                (birth.month, birth.day)
            )
        )

    except Exception:
        return None


def parse_birth_date(value):

    if not value:
        return date(1980, 1, 1)

    try:

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = clean_text(value)

        return datetime.strptime(
            text[:10],
            "%Y-%m-%d",
        ).date()

    except Exception:
        return date(1980, 1, 1)


def get_latest_numeric(df, column):

    if (
        df is None
        or df.empty
        or column not in df.columns
    ):
        return None

    temp = df[
        ["log_date", column]
    ].copy()

    temp[column] = pd.to_numeric(
        temp[column],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[column]
    )

    temp = temp[
        temp[column] > 0
    ]

    if temp.empty:
        return None

    if "log_date" in temp.columns:

        temp = temp.sort_values(
            "log_date"
        )

    return float(
        temp.iloc[-1][column]
    )


# =========================================================
# 設定読み込み
# =========================================================
try:

    settings = (
        load_user_settings(user_id)
        or {}
    )

except Exception:

    settings = {}


# =========================================================
# DietLogs読み込み
# 現在値は「記録する」の最新データを使う
# =========================================================
try:

    diet_df = load_diet_dataframe(
        user_id
    )

except Exception:

    diet_df = pd.DataFrame()


latest_weight = get_latest_numeric(
    diet_df,
    "weight",
)

latest_body_fat = get_latest_numeric(
    diet_df,
    "body_fat",
)

latest_muscle_mass = get_latest_numeric(
    diet_df,
    "muscle_mass",
)


# =========================================================
# 初期値
# =========================================================
nickname_default = clean_text(
    settings.get(
        "nickname",
        "",
    )
)


# UserSettingsに無い場合はUsersのプロフィールも確認
profile = {}

try:
    profile = (
        load_current_user_profile(
            user_id
        )
        or {}
    )
except Exception:
    profile = {}


if not nickname_default:

    nickname_default = clean_text(
        profile.get(
            "nickname",
            "",
        )
    )


birth_source = clean_text(
    settings.get(
        "birth_date",
        "",
    )
)

if not birth_source:

    birth_source = clean_text(
        profile.get(
            "birth_date",
            "",
        )
    )


birth_default = parse_birth_date(
    birth_source
)


height_default = to_float(
    settings.get(
        "height",
        "",
    ),
    155.0,
)


target_weight_default = to_float(
    settings.get(
        "target_weight",
        "",
    ),
    0.0,
)


target_body_fat_default = to_float(
    settings.get(
        "target_body_fat",
        "",
    ),
    0.0,
)


target_muscle_mass_default = to_float(
    settings.get(
        "target_muscle_mass",
        "",
    ),
    0.0,
)


user_type_default = clean_text(
    settings.get(
        "user_type",
        "健康維持",
    )
)


activity_default = clean_text(
    settings.get(
        "activity_level",
        "普通",
    )
)


food_style_default = clean_text(
    settings.get(
        "food_style",
        "特に決めていない",
    )
)


advice_tone_default = clean_text(
    settings.get(
        "advice_tone",
        "やさしく",
    )
)


workout_default = clean_text(
    settings.get(
        "workout_today",
        "",
    )
)


fridge_default = clean_text(
    settings.get(
        "fridge_items",
        "",
    )
)


avoid_default = clean_text(
    settings.get(
        "avoid_foods",
        "",
    )
)


favorite_default = clean_text(
    settings.get(
        "favorite_meals",
        "",
    )
)


# =========================================================
# からだで気になること
# =========================================================
saved_traits = settings.get(
    "constitution_traits",
    [],
)


if isinstance(saved_traits, str):

    saved_traits = (
        saved_traits
        .replace(",", "、")
        .split("、")
    )

    saved_traits = [
        item.strip()
        for item in saved_traits
        if item.strip()
    ]


if not isinstance(
    saved_traits,
    list,
):
    saved_traits = []


# =========================================================
# 選択肢
# =========================================================
goal_options = [
    "健康維持",
    "体重を減らしたい",
    "体脂肪を減らしたい",
    "筋肉をつけたい",
    "体力をつけたい",
    "食生活を整えたい",
]


activity_options = [
    "少ない",
    "普通",
    "多い",
]


food_style_options = [
    "特に決めていない",
    "バランス重視",
    "たんぱく質を意識",
    "野菜を多めにしたい",
    "糖質を少し控えたい",
    "脂質を少し控えたい",
]


trait_options = [
    "冷え",
    "むくみ",
    "疲れやすい",
    "肩・首こり",
    "腰の疲れ",
    "便通",
    "睡眠",
    "食欲の波",
]


tone_options = [
    "やさしく",
    "シンプルに",
    "しっかり",
]


# =========================================================
# 不正な保存値への対応
# =========================================================
if user_type_default not in goal_options:
    user_type_default = "健康維持"


if activity_default not in activity_options:
    activity_default = "普通"


if food_style_default not in food_style_options:
    food_style_default = (
        "特に決めていない"
    )


if advice_tone_default not in tone_options:
    advice_tone_default = "やさしく"


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
        "ShufuMate_home_icons_8/"
        "settings.png"
    ),
    emoji="⚙️",
)


# =========================================================
# 基本設定
# =========================================================
st.markdown(
    '<div class="settings-section-title">'
    '基本設定'
    '</div>',
    unsafe_allow_html=True,
)


intro_html = (
    '<div class="settings-intro">'
    'ここで設定した内容は、'
    'ShufuMateの相談やおすすめを'
    'あなた向けに調整するために使います。'
    '</div>'
)


st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# ニックネーム
# =========================================================
nickname = st.text_input(
    "ニックネーム",
    value=nickname_default,
    placeholder="表示する名前",
    key="settings_nickname",
)


# =========================================================
# 生年月日
# =========================================================
birth_date_value = st.date_input(
    "生年月日",
    value=birth_default,
    min_value=date(1920, 1, 1),
    max_value=date.today(),
    format="YYYY/MM/DD",
    key="settings_birth_date",
)


age = calculate_age(
    birth_date_value
)


if age is not None:

    age_html = (
        '<div class="settings-age-card">'
        '現在の年齢：'
        f'<strong>{age}歳</strong>'
        '</div>'
    )

    st.markdown(
        age_html,
        unsafe_allow_html=True,
    )


# =========================================================
# 身長
# =========================================================
height = st.number_input(
    "身長（cm）",
    min_value=100.0,
    max_value=220.0,
    value=max(
        100.0,
        min(
            220.0,
            height_default,
        ),
    ),
    step=0.1,
    format="%.1f",
    key="settings_height",
)


# =========================================================
# 体組成
# =========================================================
st.markdown(
    '<div class="settings-section-title">'
    '体組成'
    '</div>',
    unsafe_allow_html=True,
)


current_note = (
    '<div class="settings-current-note">'
    '現在値は「記録する」の最新記録から'
    '自動で反映されます。'
    '</div>'
)


st.markdown(
    current_note,
    unsafe_allow_html=True,
)


# =========================================================
# 体重
# =========================================================
col1, col2 = st.columns(2)


with col1:

    st.number_input(
        "現在の体重（kg）",
        min_value=0.0,
        max_value=250.0,
        value=(
            float(latest_weight)
            if latest_weight is not None
            else 0.0
        ),
        step=0.1,
        format="%.1f",
        disabled=True,
        key="settings_current_weight",
    )


with col2:

    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=0.0,
        max_value=250.0,
        value=target_weight_default,
        step=0.1,
        format="%.1f",
        key="settings_target_weight",
    )


# =========================================================
# 体脂肪率
# =========================================================
col1, col2 = st.columns(2)


with col1:

    st.number_input(
        "現在の体脂肪率（%）",
        min_value=0.0,
        max_value=70.0,
        value=(
            float(latest_body_fat)
            if latest_body_fat is not None
            else 0.0
        ),
        step=0.1,
        format="%.1f",
        disabled=True,
        key="settings_current_body_fat",
    )


with col2:

    target_body_fat = st.number_input(
        "目標体脂肪率（%）",
        min_value=0.0,
        max_value=70.0,
        value=target_body_fat_default,
        step=0.1,
        format="%.1f",
        key="settings_target_body_fat",
    )


# =========================================================
# 筋肉量
# =========================================================
col1, col2 = st.columns(2)


with col1:

    st.number_input(
        "現在の筋肉量（kg）",
        min_value=0.0,
        max_value=100.0,
        value=(
            float(latest_muscle_mass)
            if latest_muscle_mass is not None
            else 0.0
        ),
        step=0.1,
        format="%.1f",
        disabled=True,
        key="settings_current_muscle_mass",
    )


with col2:

    target_muscle_mass = st.number_input(
        "目標筋肉量（kg）",
        min_value=0.0,
        max_value=100.0,
        value=target_muscle_mass_default,
        step=0.1,
        format="%.1f",
        key="settings_target_muscle_mass",
    )


# =========================================================
# 相談・提案
# =========================================================
render_section_header(
    title="相談・提案",
    icon_file=(
        "ShufuMate_home_icons_8/"
        "advice.png"
    ),
    emoji="🌿",
)


description_html = (
    '<div class="settings-description">'
    '今の目的や生活スタイルを設定すると、'
    '食事・運動の提案を調整しやすくなります。'
    '</div>'
)


st.markdown(
    description_html,
    unsafe_allow_html=True,
)


user_type = st.selectbox(
    "今の目的",
    goal_options,
    index=goal_options.index(
        user_type_default
    ),
    key="settings_user_type",
)


activity_level = st.selectbox(
    "普段の活動量",
    activity_options,
    index=activity_options.index(
        activity_default
    ),
    key="settings_activity_level",
)


food_style = st.selectbox(
    "食事スタイル",
    food_style_options,
    index=food_style_options.index(
        food_style_default
    ),
    key="settings_food_style",
)


constitution_traits = st.multiselect(
    "からだで気になること",
    trait_options,
    default=[
        item
        for item in saved_traits
        if item in trait_options
    ],
    placeholder="選択してください",
    key="settings_constitution_traits",
)


advice_tone = st.selectbox(
    "アドバイスの雰囲気",
    tone_options,
    index=tone_options.index(
        advice_tone_default
    ),
    key="settings_advice_tone",
)


# =========================================================
# 運動
# =========================================================
render_section_header(
    title="運動",
    icon_file=(
        "ShufuMate_home_icons_8/"
        "exercise.png"
    ),
    emoji="🧘",
)


exercise_description = (
    '<div class="settings-description">'
    '普段よく行う運動を入力してください。'
    '複数ある場合は「、」で区切って入力できます。'
    '</div>'
)


st.markdown(
    exercise_description,
    unsafe_allow_html=True,
)


workout_today = st.text_area(
    "よく行う運動",
    value=workout_default,
    placeholder=(
        "例：ヨガ、筋トレ、"
        "ウォーキング、ランニング"
    ),
    height=90,
    key="settings_workout",
)


# =========================================================
# 食材・冷蔵庫
# =========================================================
render_section_header(
    title="食材・冷蔵庫",
    icon_file=(
        "ShufuMate_home_icons_8/"
        "fridge.png"
    ),
    emoji="🥕",
)


fridge_items = st.text_area(
    "よく家にある食材",
    value=fridge_default,
    placeholder=(
        "例：卵、納豆、豆腐、"
        "鶏肉、しめじ、青菜"
    ),
    height=90,
    key="settings_fridge_items",
)


avoid_foods = st.text_area(
    "避けたい食品・苦手なもの",
    value=avoid_default,
    placeholder=(
        "例：辛すぎるもの、脂っこいもの"
    ),
    height=80,
    key="settings_avoid_foods",
)


favorite_meals = st.text_area(
    "好きなメニュー・定番メニュー",
    value=favorite_default,
    placeholder=(
        "例：味噌汁、おにぎり、"
        "豚しゃぶ、納豆うどん"
    ),
    height=90,
    key="settings_favorite_meals",
)


# =========================================================
# 保存
# =========================================================
render_divider()


if st.button(
    "設定を保存する",
    key="settings_save_button",
    use_container_width=True,
):

    settings_data = {

        "nickname":
            clean_text(nickname),

        "birth_date":
            birth_date_value.strftime(
                "%Y-%m-%d"
            ),

        "height":
            height,

        # 現在値も最新DietLogs値を保存しておく
        # 他ページとの互換用
        "current_weight":
            (
                latest_weight
                if latest_weight is not None
                else ""
            ),

        "target_weight":
            target_weight,

        "current_body_fat":
            (
                latest_body_fat
                if latest_body_fat is not None
                else ""
            ),

        "target_body_fat":
            target_body_fat,

        "current_muscle_mass":
            (
                latest_muscle_mass
                if latest_muscle_mass is not None
                else ""
            ),

        "target_muscle_mass":
            target_muscle_mass,

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
            clean_text(
                workout_today
            ),

        "fridge_items":
            clean_text(
                fridge_items
            ),

        "avoid_foods":
            clean_text(
                avoid_foods
            ),

        "favorite_meals":
            clean_text(
                favorite_meals
            ),
    }


    try:

        save_user_settings(
            user_id,
            settings_data,
        )

        # Usersシート側のニックネームも同期
        update_current_user_profile(
            user_id,
            nickname=nickname,
        )

        st.success(
            "設定を保存しました ✨"
        )

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
render_divider()


st.markdown(
    '<div class="settings-section-title">'
    'アカウント'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# ログインID
# =========================================================
login_id_display = clean_text(
    get_login_id()
)


if not login_id_display:

    login_id_display = clean_text(
        profile.get(
            "login_id",
            "",
        )
    )


if not login_id_display:
    login_id_display = user_id


account_html = (
    '<div class="account-card">'
    '<div class="account-label">'
    'ログインID'
    '</div>'
    '<div class="account-value">'
    f'{safe_text(login_id_display)}'
    '</div>'
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
        key=(
            "settings_password_change_button"
        ),
        use_container_width=True,
    ):

        new_password_clean = clean_text(
            new_password
        )

        confirm_clean = clean_text(
            new_password_confirm
        )


        if len(
            new_password_clean
        ) < 4:

            st.warning(
                "パスワードは4文字以上で"
                "入力してください。"
            )


        elif (
            new_password_clean
            != confirm_clean
        ):

            st.warning(
                "確認用パスワードが"
                "一致しません。"
            )


        else:

            try:

                changed = reset_password(
                    login_id_display,
                    new_password_clean,
                )

                if changed:

                    st.success(
                        "パスワードを変更しました。"
                    )

                else:

                    st.error(
                        "パスワードを変更できませんでした。"
                    )

            except Exception as e:

                st.error(
                    "パスワードを変更できませんでした。"
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
