import streamlit as st
from datetime import date, datetime
from app_core import *

st.set_page_config(
    page_title="設定",
    page_icon="⚙️",
    layout="centered"
)

require_login()

st.title("⚙️ 設定")
st.caption("基本設定とアカウント設定を管理します")

user_id = get_user_id()

# -----------------
# 安全変換
# -----------------
def safe_float(value, default):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def safe_list(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            x.strip()
            for x in value.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return []


def option_index(options, value, default=0):
    if value in options:
        return options.index(value)
    return default


# -----------------
# データ取得
# -----------------
try:
    settings = load_user_settings(user_id)
    profile = load_current_user_profile(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

if not isinstance(settings, dict):
    settings = {}

if not isinstance(profile, dict):
    profile = {}

nickname_default = profile.get("nickname") or settings.get("nickname") or user_id
login_id_text = profile.get("login_id") or user_id

birth_date_text = profile.get("birth_date") or "未設定"

age_val = profile.get("age")
age_text = f"{age_val}歳" if age_val is not None else "未設定"

# -----------------
# 基本設定
# -----------------
st.subheader("基本設定")

with st.form("settings_form"):

    nickname = st.text_input("ニックネーム", value=nickname_default)

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("生年月日", value=birth_date_text, disabled=True)

    with col2:
        st.text_input("年齢", value=age_text, disabled=True)

    height_cm = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=220.0,
        value=safe_float(settings.get("height_cm"), 155),
        step=0.1,
    )

    col3, col4 = st.columns(2)

    with col3:
        current_weight = st.number_input(
            "現在体重(kg)",
            min_value=20.0,
            max_value=150.0,
            value=safe_float(settings.get("current_weight") or settings.get("start_weight"), 50),
            step=0.1,
        )

    with col4:
        target_weight = st.number_input(
            "目標体重(kg)",
            min_value=20.0,
            max_value=150.0,
            value=safe_float(settings.get("target_weight"), 48),
            step=0.1,
        )

    col5, col6 = st.columns(2)

    with col5:
        current_body_fat = st.number_input(
            "現在体脂肪(%)",
            min_value=5.0,
            max_value=60.0,
            value=safe_float(settings.get("current_body_fat") or settings.get("start_body_fat"), 30),
            step=0.1,
        )

    with col6:
        target_body_fat = st.number_input(
            "目標体脂肪(%)",
            min_value=5.0,
            max_value=60.0,
            value=safe_float(settings.get("target_body_fat"), 28),
            step=0.1,
        )

    st.markdown("---")
    st.subheader("🌿 相談・提案の設定")

    user_type_options = [
        "自分向け",
        "自分＋家族向け",
        "子ども優先",
        "夫も満足",
        "ダイエット重視",
        "節約重視",
        "忙しい日向け",
    ]

    user_type = st.selectbox(
        "利用タイプ",
        user_type_options,
        index=option_index(user_type_options, settings.get("user_type", "自分向け")),
    )

    activity_options = [
        "少なめ",
        "ふつう",
        "多め",
        "ヨガ・ピラティスあり",
        "筋トレあり",
        "外出多め",
    ]

    activity_level = st.selectbox(
        "活動量",
        activity_options,
        index=option_index(activity_options, settings.get("activity_level", "ふつう")),
    )

    food_style_options = [
        "和食中心",
        "洋食もOK",
        "家族向け",
        "ダイエット重視",
        "節約重視",
        "外食あり",
        "コンビニ活用",
    ]

    food_style = st.selectbox(
        "食事スタイル",
        food_style_options,
        index=option_index(
            food_style_options,
            settings.get("food_style") or settings.get("meal_style", "和食中心")
        ),
    )

    constitution_options = [
        "冷えやすい",
        "むくみやすい",
        "疲れやすい",
        "寝不足になりやすい",
        "肩こり",
        "便秘気味",
        "胃腸が弱い",
        "甘いものが欲しくなる",
        "外食が多い",
        "運動不足",
    ]

    constitution_traits = st.multiselect(
        "体質・傾向",
        constitution_options,
        default=[
            x for x in safe_list(settings.get("constitution_traits"))
            if x in constitution_options
        ],
    )

    advice_tone_options = [
        "やさしく",
        "具体的に",
        "短く",
        "励ましてほしい",
        "はっきり言ってほしい",
    ]

    advice_tone = st.selectbox(
        "アドバイスの言い方",
        advice_tone_options,
        index=option_index(advice_tone_options, settings.get("advice_tone", "やさしく")),
    )

    st.markdown("---")
    st.subheader("🍽 食材・冷蔵庫")

    workout_today_options = [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "有酸素",
        "筋トレ",
        "なし",
    ]

    workout_today = st.selectbox(
        "よくする運動",
        workout_today_options,
        index=option_index(workout_today_options, settings.get("workout_today", "ストレッチ")),
    )

    fridge_items = st.text_area(
        "冷蔵庫にあるもの",
        value=settings.get("fridge_items", ""),
        placeholder="例：卵、豆腐、納豆、キャベツ、鮭",
        height=100,
    )

    avoid_foods = st.text_area(
        "避けたい食材",
        value=settings.get("avoid_foods", ""),
        placeholder="例：辛いもの、揚げ物、牛乳",
        height=80,
    )

    submitted = st.form_submit_button("保存", use_container_width=True)

# -----------------
# 保存処理
# -----------------
if submitted:

    save_user_settings(
        user_id,
        {
            "nickname": nickname,
            "height_cm": height_cm,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "current_body_fat": current_body_fat,
            "target_body_fat": target_body_fat,

            "user_type": user_type,
            "activity_level": activity_level,
            "food_style": food_style,
            "meal_style": food_style,
            "constitution_traits": constitution_traits,
            "advice_tone": advice_tone,

            "workout_today": workout_today,
            "fridge_items": fridge_items,
            "avoid_foods": avoid_foods,
        },
    )

    update_current_user_profile(
        user_id,
        nickname=nickname,
    )

    st.success("保存しました")
    st.rerun()

# -----------------
# アカウント情報
# -----------------
st.divider()
st.subheader("アカウント")

st.text_input("ログインID", value=login_id_text, disabled=True)

# -----------------
# パスワード変更
# -----------------
st.subheader("🔑 パスワード変更")

new_pw = st.text_input("新しいパスワード", type="password")
new_pw2 = st.text_input("確認", type="password")

if st.button("変更する", use_container_width=True):

    if not new_pw:
        st.warning("パスワードを入力してください")

    elif new_pw != new_pw2:
        st.error("一致しません")

    elif len(new_pw) < 4:
        st.warning("パスワードは4文字以上にしてください")

    else:
        reset_password(login_id_text, new_pw)
        st.success("変更しました")

# -----------------
# ログアウト
# -----------------
st.divider()

if st.button("ログアウト", use_container_width=True):
    logout()
    st.switch_page("pages/0_ログイン.py")
