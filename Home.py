import streamlit as st
from app_core import *

# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered"
)

# -----------------
# ログインチェック
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# 設定読み込み
# -----------------
try:
    settings = load_user_settings(user_id)
except Exception:
    settings = {}

# -----------------
# ヘッダー
# -----------------
st.title("🏠 ShufuMate")
st.caption("食事も、暮らしも、ちょうどよく")

st.markdown(f"こんにちは、**{user_id} さん** 😊")

st.markdown("---")

# -----------------
# 表示モード
# -----------------
mode = st.radio(
    "表示モード",
    ["かんたん", "しっかり"],
    horizontal=True
)

# -----------------
# 今日の状態
# -----------------
st.markdown("### 🌿 今日の状態")

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox(
        "体調",
        ["普通", "疲れ", "むくみ"]
    )

with col2:
    weather_label = st.selectbox(
        "今日の体感",
        ["普通", "暑く感じる", "寒く感じる"]
    )

# 内部処理用に変換
weather_map = {
    "普通": "普通",
    "暑く感じる": "暑い",
    "寒く感じる": "寒い",
}

weather_value = weather_map.get(weather_label, "普通")

# -----------------
# 運動予定
# -----------------
try:
    exercise_options = get_exercise_options()
except Exception:
    exercise_options = [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "有酸素",
        "筋トレ",
        "なし",
    ]

default_exercise = settings.get("workout_today", "ストレッチ")

if default_exercise not in exercise_options:
    default_exercise = "ストレッチ"

exercise = st.selectbox(
    "運動予定",
    exercise_options,
    index=exercise_options.index(default_exercise)
)

st.markdown("---")

# =====================
# 🌿 かんたんモード
# =====================
if mode == "かんたん":

    st.subheader("🌿 今日のおすすめ")

    text = generate_simple_advice(
        user_type=settings.get("user_type", "自分向け"),
        weather=weather_value,
        state=state,
        exercise=exercise
    )

    st.success(text)

    st.markdown("### 🏃‍♀️ 今日の運動ヒント")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は無理のない範囲で、少し体を動かしましょう。")

# =====================
# 💪 しっかりモード
# =====================
else:

    st.subheader("💪 今日のプラン")

    # -----------------
    # 食事プラン
    # -----------------
    plan = generate_full_plan(
        user_type=settings.get("user_type", "自分向け"),
        weather=weather_value,
        state=state,
        exercise=exercise
    )

    st.markdown("### 🍽 食事")

    for meal_time, menu in plan.items():

        if meal_time == "朝":
            icon = "🌅"
        elif meal_time == "昼":
            icon = "☀️"
        elif meal_time == "夜":
            icon = "🌙"
        else:
            icon = "🍽"

        st.markdown(f"{icon} **{meal_time}：** {menu}")

    # -----------------
    # 運動
    # -----------------
    st.markdown("### 🏃‍♀️ 運動")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は体調に合わせて、できる範囲で整えましょう。")

    st.markdown("---")

    # -----------------
    # 買い物リスト
    # -----------------
    with st.expander("🛒 買い物リスト"):

        try:
            shopping = generate_smart_shopping_list(
                plan,
                fridge_items=st.session_state.get("fridge_items", [])
            )

            try:
                shopping = add_deals_to_shopping(shopping)
            except Exception:
                pass

            if shopping:
                for category, items in shopping.items():
                    st.markdown(f"**{category}**")

                    for item in items:
                        st.checkbox(
                            item,
                            key=f"home_shopping_{category}_{item}"
                        )
            else:
                st.info("買い物リストはありません")

        except Exception as e:
            st.warning(f"買い物リストを作成できませんでした: {e}")

# -----------------
# 1週間プラン
# -----------------
with st.expander("📅 1週間プラン"):

    try:
        week_plan = generate_weekly_plan(
            user_type=settings.get("user_type", "自分向け"),
            weather=weather_value,
            state=state,
            exercise=exercise
        )

        for day, day_plan in week_plan.items():
            st.markdown(f"### {day}")

            st.write(f"朝：{day_plan.get('朝', '')}")
            st.write(f"昼：{day_plan.get('昼', '')}")
            st.write(f"夜：{day_plan.get('夜', '')}")

    except Exception as e:
        st.warning(f"1週間プランを作成できませんでした: {e}")

# -----------------
# ログアウト
# -----------------
st.markdown("---")

if st.button("ログアウト", use_container_width=True):
    logout()
    st.rerun()
