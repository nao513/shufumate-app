import streamlit as st
from app_core import *

# -----------------
# 🔐 ログインチェック
# -----------------
require_login()

user_id = get_user_id()

# -----------------
# 🏠 ヘッダー
# -----------------
st.title("🏠 ShufuMate")
st.caption("食事も、暮らしも、ちょうどよく")

st.markdown(f"こんにちは、**{user_id} さん** 😊")

st.markdown("---")

# -----------------
# ⚙️ モード選択
# -----------------
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

# -----------------
# 🧠 状態入力
# -----------------
st.markdown("### 🌿 今日の状態")

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox("体調", ["普通", "疲れ", "むくみ"])

with col2:
    weather = st.selectbox("天気", ["普通", "暑い", "寒い"])

exercise = st.selectbox("運動予定", ["なし", "ストレッチ", "有酸素", "筋トレ"])

st.markdown("---")

# =====================
# 🌿 かんたんモード
# =====================
if mode == "かんたん":

    st.subheader("🌿 今日のおすすめ")

    text = generate_simple_advice(
        user_type="バランス",
        weather=weather,
        state=state,
        exercise=exercise
    )

    st.success(text)

# =====================
# 💪 しっかりモード
# =====================
else:

    st.subheader("💪 今日のプラン")

    # -----------------
    # 🍽 食事
    # -----------------
    st.markdown("### 🍽 食事")

    plan = generate_full_plan(
        user_type="バランス",
        weather=weather,
        state=state,
        exercise=exercise
    )

    for k, v in plan.items():
        if k == "朝":
            icon = "🌅"
        elif k == "昼":
            icon = "☀️"
        elif k == "夜":
            icon = "🌙"
        else:
            icon = "🍽"

        st.markdown(f"{icon} **{k}：** {v}")

    # -----------------
    # 🏃‍♀️ 運動
    # -----------------
    st.markdown("### 🏃‍♀️ 運動")

    if exercise == "なし":
        st.write("ストレッチがおすすめです")
    elif exercise == "ストレッチ":
        st.write("軽めに体をほぐしましょう")
    elif exercise == "有酸素":
        st.write("ウォーキングや軽い運動がおすすめ")
    elif exercise == "筋トレ":
        st.write("タンパク質をしっかり摂りましょう")

    st.markdown("---")

    # -----------------
    # 🛒 買い物リスト
    # -----------------
    with st.expander("🛒 買い物リスト"):

        shopping = generate_smart_shopping_list(
            plan,
            fridge_items=st.session_state.get("fridge_items", [])
        )

        shopping = add_deals_to_shopping(shopping)

        for category, items in shopping.items():
            st.markdown(f"**{category}**")

            for item in items:
                st.checkbox(item)

# -----------------
# 📅 1週間プラン
# -----------------
with st.expander("📅 1週間プラン"):

    week_plan = generate_weekly_plan(
        user_type="バランス",
        weather=weather,
        state=state,
        exercise=exercise
    )

    for day, plan in week_plan.items():
        st.markdown(f"### {day}")

        for k, v in plan.items():
            st.write(f"{k}：{v}")

# -----------------
# 🚪 ログアウト
# -----------------
st.markdown("---")

if st.button("ログアウト"):
    logout()
    st.rerun()
