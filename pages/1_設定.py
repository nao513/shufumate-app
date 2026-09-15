import streamlit as st
from datetime import datetime, date

from app_core import *


# =========================================================
# 水彩アイコンのフォルダ
# =========================================================
WATERCOLOR_ICON_DIR = "ShufuMate_home_icons_8"


def watercolor_icon(filename):
    return f"{WATERCOLOR_ICON_DIR}/{filename}"


# =========================================================
# ページ設定
# ※ Streamlit命令の一番最初
# =========================================================
st.set_page_config(
    page_title="設定｜ShufuMate",
    page_icon=get_page_icon(
        watercolor_icon("settings.png"),
        "⚙️",
    ),
    layout="centered",
)


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログイン確認
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# 安全変換
# =========================================================
def local_safe_float(
    value,
    default=0.0,
):
    try:
        if value in ["", None]:
            return float(default)

        return float(value)

    except (ValueError, TypeError):
        return float(default)


def local_safe_text(
    value,
    default="",
):
    if value is None:
        return default

    return str(value).strip()


def local_safe_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    text = str(value).strip()

    if not text:
        return []

    text = (
        text
        .replace(",", "、")
        .replace("，", "、")
    )

    return [
        item.strip()
        for item in text.split("、")
        if item.strip()
    ]


def option_index(
    options,
    value,
    default=0,
):
    value = local_safe_text(value)

    try:
        return options.index(value)

    except ValueError:
        return default


# =========================================================
# 生年月日 → 年齢
# =========================================================
def calculate_age(
    birth_date_value,
):
    if not birth_date_value:
        return None

    try:
        if isinstance(
            birth_date_value,
            datetime,
        ):
            birth = birth_date_value.date()

        elif isinstance(
            birth_date_value,
            date,
        ):
            birth = birth_date_value

        else:
            birth = datetime.strptime(
                str(birth_date_value)[:10],
                "%Y-%m-%d",
            ).date()

        today = jst_today().date()

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


# =========================================================
# 保存データ取得
# =========================================================
settings = (
    load_user_settings(user_id)
    or {}
)

profile = (
    load_current_user_profile(user_id)
    or {}
)


# =========================================================
# ニックネーム
# Users側を優先
# =========================================================
saved_nickname = (
    local_safe_text(
        profile.get("nickname")
    )
    or
    local_safe_text(
        settings.get("nickname")
    )
)


# =========================================================
# 生年月日・年齢
# =========================================================
birth_date_value = profile.get(
    "birth_date",
    "",
)

age = calculate_age(
    birth_date_value
)


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="設定",
    subtitle=(
        "あなたに合った提案ができるように、"
        "基本情報や食事・運動の好みを設定します。"
    ),
    icon_file=watercolor_icon(
        "settings.png"
    ),
    emoji="⚙️",
)


# =========================================================
# 基本設定
# =========================================================
render_section_header(
    title="基本設定",
    icon_file=watercolor_icon(
        "settings.png"
    ),
    emoji="⚙️",
)

render_note(
    "体重や体脂肪率は「現在」と「目標」を分けて設定します。\n"
    "毎日の記録は「記録する」ページから入力できます。"
)


nickname = st.text_input(
    "ニックネーム",
    value=saved_nickname,
    placeholder="例：なお",
    key="settings_nickname",
)


# ---------------------------------------------------------
# 生年月日・年齢
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    st.text_input(
        "生年月日",
        value=(
            local_safe_text(
                birth_date_value
            )
            or "未登録"
        ),
        disabled=True,
        key="settings_birth_date",
    )


with col2:

    st.text_input(
        "年齢",
        value=(
            f"{age}歳"
            if age is not None
            else "未登録"
        ),
        disabled=True,
        key="settings_age",
    )


# ---------------------------------------------------------
# 身長
# ---------------------------------------------------------
height = st.number_input(
    "身長（cm）",
    min_value=0.0,
    max_value=250.0,
    value=local_safe_float(
        settings.get("height")
    ),
    step=0.1,
    format="%.1f",
    key="settings_height",
)


# ---------------------------------------------------------
# 体重
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    current_weight = st.number_input(
        "現在の体重（kg）",
        min_value=0.0,
        max_value=300.0,
        value=local_safe_float(
            settings.get(
                "current_weight"
            )
        ),
        step=0.1,
        format="%.1f",
        key="settings_current_weight",
    )


with col2:

    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=0.0,
        max_value=300.0,
        value=local_safe_float(
            settings.get(
                "target_weight"
            )
        ),
        step=0.1,
        format="%.1f",
        key="settings_target_weight",
    )


# ---------------------------------------------------------
# 体脂肪率
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:

    current_body_fat = st.number_input(
        "現在の体脂肪率（%）",
        min_value=0.0,
        max_value=70.0,
        value=local_safe_float(
            settings.get(
                "current_body_fat"
            )
        ),
        step=0.1,
        format="%.1f",
        key="settings_current_body_fat",
    )


with col2:

    target_body_fat = st.number_input(
        "目標体脂肪率（%）",
        min_value=0.0,
        max_value=70.0,
        value=local_safe_float(
            settings.get(
                "target_body_fat"
            )
        ),
        step=0.1,
        format="%.1f",
        key="settings_target_body_fat",
    )


render_divider()


# =========================================================
# 相談・提案の設定
# =========================================================
render_section_header(
    title="相談・提案の設定",
    icon_file=watercolor_icon(
        "advice.png"
    ),
    emoji="🌿",
)

render_note(
    "ShufuMateが献立や体づくりを提案するときの"
    "基本的な方向性に使います。"
)


USER_TYPE_OPTIONS = [
    "特に決めていない",
    "健康を整えたい",
    "体脂肪を減らしたい",
    "筋肉を増やしたい",
    "体重を減らしたい",
    "体型を維持したい",
]


user_type = st.selectbox(
    "今いちばん近い目標",
    USER_TYPE_OPTIONS,
    index=option_index(
        USER_TYPE_OPTIONS,
        settings.get("user_type"),
    ),
    key="settings_user_type",
)


ACTIVITY_OPTIONS = [
    "あまり運動しない",
    "軽く運動する",
    "週2〜3回運動する",
    "週4回以上運動する",
    "よく体を動かす",
]


activity_level = st.selectbox(
    "普段の活動量",
    ACTIVITY_OPTIONS,
    index=option_index(
        ACTIVITY_OPTIONS,
        settings.get(
            "activity_level"
        ),
        default=1,
    ),
    key="settings_activity_level",
)


FOOD_STYLE_OPTIONS = [
    "特に決めていない",
    "バランス重視",
    "高たんぱく",
    "野菜多め",
    "糖質を少し控えたい",
    "脂質を少し控えたい",
    "時短・簡単重視",
    "節約重視",
]


food_style = st.selectbox(
    "食事で重視したいこと",
    FOOD_STYLE_OPTIONS,
    index=option_index(
        FOOD_STYLE_OPTIONS,
        settings.get("food_style"),
    ),
    key="settings_food_style",
)


CONSTITUTION_OPTIONS = [
    "冷えが気になる",
    "むくみが気になる",
    "疲れやすい",
    "便通を整えたい",
    "肩や首がこりやすい",
    "脚の張りが気になる",
    "特になし",
]


saved_constitution = local_safe_list(
    settings.get(
        "constitution_traits"
    )
)

saved_constitution = [
    item
    for item in saved_constitution
    if item in CONSTITUTION_OPTIONS
]


constitution_traits = st.multiselect(
    "気になること",
    CONSTITUTION_OPTIONS,
    default=saved_constitution,
    key="settings_constitution",
)


ADVICE_TONE_OPTIONS = [
    "やさしく",
    "簡潔に",
    "しっかり詳しく",
]


advice_tone = st.selectbox(
    "アドバイスの伝え方",
    ADVICE_TONE_OPTIONS,
    index=option_index(
        ADVICE_TONE_OPTIONS,
        settings.get("advice_tone"),
    ),
    key="settings_advice_tone",
)


render_divider()


# =========================================================
# 運動
# =========================================================
render_section_header(
    title="運動",
    icon_file="exercise.png",
    emoji="🏃",
)

render_note(
    "よく行う運動を登録しておくと、"
    "食事や休養の提案に反映しやすくなります。"
)


WORKOUT_OPTIONS = [
    "ウォーキング",
    "ランニング",
    "筋トレ",
    "ヨガ",
    "ピラティス",
    "ストレッチ",
    "自転車",
    "その他",
]


saved_workout = local_safe_list(
    settings.get(
        "workout_today"
    )
)

saved_workout = [
    item
    for item in saved_workout
    if item in WORKOUT_OPTIONS
]


workout_today = st.multiselect(
    "よく行う運動",
    WORKOUT_OPTIONS,
    default=saved_workout,
    key="settings_workout",
)


render_divider()


# =========================================================
# 食材・冷蔵庫
# =========================================================
render_section_header(
    title="食材・冷蔵庫",
    icon_file="food.png",
    emoji="🥕",
)

render_note(
    "よく家にある食材や避けたい食品を登録すると、"
    "献立提案がより実用的になります。\n"
    "複数ある場合は「、」で区切って入力できます。"
)


fridge_items = st.text_area(
    "冷蔵庫・常備している食材",
    value=local_safe_text(
        settings.get(
            "fridge_items"
        )
    ),
    placeholder=(
        "例：卵、納豆、豆腐、"
        "鶏むね肉、きのこ、わかめ"
    ),
    height=100,
    key="settings_fridge_items",
)


avoid_foods = st.text_area(
    "避けたい食品・苦手なもの",
    value=local_safe_text(
        settings.get(
            "avoid_foods"
        )
    ),
    placeholder=(
        "例：辛すぎるもの、"
        "脂っこいもの"
    ),
    height=90,
    key="settings_avoid_foods",
)


favorite_meals = st.text_area(
    "好きなメニュー・よく作るもの",
    value=local_safe_text(
        settings.get(
            "favorite_meals"
        )
    ),
    placeholder=(
        "例：豚しゃぶ、"
        "具だくさん味噌汁、"
        "おにぎり"
    ),
    height=100,
    key="settings_favorite_meals",
)


# =========================================================
# 保存
# =========================================================
st.write("")

if st.button(
    "設定を保存する",
    type="primary",
    use_container_width=True,
    key="save_settings_button",
):

    save_data = {
        "nickname": nickname,
        "height": height,
        "current_weight": current_weight,
        "target_weight": target_weight,
        "current_body_fat": (
            current_body_fat
        ),
        "target_body_fat": (
            target_body_fat
        ),
        "user_type": user_type,
        "activity_level": (
            activity_level
        ),
        "food_style": food_style,
        "constitution_traits": (
            constitution_traits
        ),
        "advice_tone": advice_tone,
        "workout_today": workout_today,
        "fridge_items": fridge_items,
        "avoid_foods": avoid_foods,
        "favorite_meals": (
            favorite_meals
        ),
    }

    try:

        settings_saved = (
            save_user_settings(
                user_id,
                save_data,
            )
        )

        profile_saved = (
            update_current_user_profile(
                user_id,
                nickname=nickname,
            )
        )

        if (
            settings_saved
            and profile_saved
        ):

            st.success(
                "設定を保存しました。"
            )

        elif settings_saved:

            st.success(
                "設定を保存しました。"
            )

            st.warning(
                "ニックネームの更新だけ"
                "確認できませんでした。"
            )

        else:

            st.error(
                "設定を保存できませんでした。"
            )

    except Exception as e:

        st.error(
            "設定の保存中に"
            "エラーが発生しました。"
        )

        st.caption(
            str(e)
        )


render_divider()


# =========================================================
# アカウント
# =========================================================
render_section_header(
    title="アカウント",
    icon_file=watercolor_icon(
        "settings.png"
    ),
    emoji="👤",
)


login_id = (
    get_login_id()
    or local_safe_text(
        profile.get("login_id")
    )
)


render_card(
    "ログインID\n"
    f"{login_id}"
)


# =========================================================
# パスワード変更
# =========================================================
render_section_header(
    title="パスワード変更",
    emoji="🔑",
)

render_note(
    "新しいパスワードは4文字以上で設定してください。"
)


new_password = st.text_input(
    "新しいパスワード",
    type="password",
    key="settings_new_password",
)


new_password_confirm = st.text_input(
    "新しいパスワード（確認）",
    type="password",
    key="settings_new_password_confirm",
)


if st.button(
    "パスワードを変更する",
    use_container_width=True,
    key="change_password_button",
):

    if len(new_password) < 4:

        st.warning(
            "パスワードは4文字以上で"
            "入力してください。"
        )

    elif (
        new_password
        != new_password_confirm
    ):

        st.warning(
            "確認用パスワードが"
            "一致していません。"
        )

    elif not login_id:

        st.error(
            "ログインIDを"
            "確認できませんでした。"
        )

    else:

        try:

            changed = reset_password(
                login_id,
                new_password,
            )

            if changed:

                st.success(
                    "パスワードを変更しました。"
                )

            else:

                st.error(
                    "パスワードを"
                    "変更できませんでした。"
                )

        except Exception as e:

            st.error(
                "パスワード変更中に"
                "エラーが発生しました。"
            )

            st.caption(
                str(e)
            )


render_divider()


# =========================================================
# ログアウト
# =========================================================
if st.button(
    "ログアウト",
    use_container_width=True,
    key="settings_logout_button",
):

    logout()

    st.switch_page(
        "pages/0_ログイン.py"
    )
