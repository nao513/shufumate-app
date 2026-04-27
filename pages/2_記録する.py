import streamlit as st
from datetime import datetime
from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    save_diet_log,
    get_initial_log_values,
)

# -----------------
# 初期設定
# -----------------
st.set_page_config(page_title="記録する", page_icon="📝", layout="centered")

require_login()
user_id = get_user_id()

settings = load_user_settings(user_id)
initial = get_initial_log_values(user_id)

# -----------------
# タイトル
# -----------------
st.title("📝 今日の記録")

today = datetime.now().strftime("%Y年%m月%d日")
st.markdown(f"### {today}")

st.markdown("---")

# -----------------
# 体重・体脂肪
# -----------------
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input(
        "体重 (kg)",
        value=float(initial["weight"]),
        step=0.1
    )

with col2:
    body_fat = st.number_input(
        "体脂肪 (%)",
        value=float(initial["body_fat"]),
        step=0.1
    )

# -----------------
# 今日の状態（ボタン化）
# -----------------
st.markdown("### 🌿 今日の状態")

conditions = [
    "寝不足", "だるい", "むくみあり",
    "食べすぎた", "外食あり", "時間がない"
]

selected_conditions = []
cols = st.columns(3)

for i, cond in enumerate(conditions):
    with cols[i % 3]:
        if st.checkbox(cond):
            selected_conditions.append(cond)

# -----------------
# 食事メモ（神UI）
# -----------------
st.markdown("### 🍽 食事メモ")

if "meal_memo" not in st.session_state:
    st.session_state["meal_memo"] = ""

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("テンプレート挿入"):
        st.session_state["meal_memo"] = "朝：\n昼：\n夜：\n間食："

with col_btn2:
    if st.button("クリア"):
        st.session_state["meal_memo"] = ""

meal_memo = st.text_area(
    "",
    value=st.session_state["meal_memo"],
    height=150
)

# -----------------
# 運動メモ（軽く）
# -----------------
st.markdown("### 🏃‍♀️ 運動")

exercise_memo = st.text_area(
    "",
    placeholder="例：ヨガ30分、散歩20分",
    height=80
)

# -----------------
# 保存ボタン（目立たせる）
# -----------------
st.markdown("---")

if st.button("✅ 記録を保存", use_container_width=True):

    save_diet_log(user_id, {
        "log_date": datetime.now().strftime("%Y-%m-%d"),
        "weight": weight,
        "body_fat": body_fat,
        "meal_memo": meal_memo,
        "exercise_memo": exercise_memo,
        "condition_note": "",
        "mood_note": "",
        "today_conditions": selected_conditions,
    })

    st.success("記録しました！")
    st.balloons()
