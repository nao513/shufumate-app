import streamlit as st
from datetime import datetime
from app_core import jst_now

from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    load_latest_log,
    get_today_advice,
    get_today_exercise,
    generate_weekly_plan,
    generate_shopping_list_from_week,
    get_week_key,
)

# -----------------
# ページ設定（最初に）
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="💻",
    layout="centered",
)

# -----------------
# デザイン（影＋余白）
# -----------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}

/* 画像デザイン */
img {
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

/* ボタン少し丸く */
.stButton>button {
    border-radius: 10px;
    height: 48px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# -----------------
# ログイン
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# データ取得
# -----------------
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

advice = get_today_advice(settings, latest_log)
exercise = get_today_exercise(settings, latest_log)

# -----------------
# 週間献立（1週間固定）
# -----------------
week_key = get_week_key()

if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# -----------------
# 🟩 トップ（世界観）
# -----------------
st.image("assets/home_icons/top/top_visual.png", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### 🍽 食事も、暮らしも、ちょうどよく")

today = jst_now().strftime("%Y年%m月%d日")
st.caption(today)

st.markdown("---")

# =====================
# 🟩 今日のおすすめ
# =====================
st.subheader("🌿 今日のおすすめ")

st.write(advice["食事"])

st.markdown("**🌅 朝**")
st.write(advice["朝"])

st.markdown("**☀️ 昼**")
st.write(advice["昼"])

st.markdown("**🌙 夜**")
st.write(advice["夜"])

st.caption(advice["ひとこと"])

st.markdown("---")

# =====================
# 🟨 すぐやる
# =====================
st.subheader("🚀 すぐやる")

col1, col2 = st.columns(2)

with col1:
    if st.button("📷 写真で記録", use_container_width=True):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

st.markdown("---")

# =====================
# 🟦 まとめ
# =====================
st.subheader("📦 まとめ")

# -------- 週間献立 --------
with st.expander("🗓 週間献立"):
    for day, meal in weekly_plan.items():
        st.write(f"{day}：{meal}")

# -------- 買い物リスト --------
with st.expander("🛒 買い物リスト"):
    shopping = generate_shopping_list_from_week(weekly_plan)

    for category, items in shopping.items():
        if items:
            st.markdown(f"**{category}**")

            for item in items:
                key = f"{category}_{item}"

                if key not in st.session_state:
                    st.session_state[key] = False

                st.session_state[key] = st.checkbox(
                    item,
                    value=st.session_state[key]
                )

# -------- 運動 --------
with st.expander("🏃‍♀️ 運動"):
    st.write(exercise["title"])
    st.write(exercise["body"])

st.markdown("---")

# =====================
# その他
# =====================
col3, col4 = st.columns(2)

with col3:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

with col4:
    if st.button("⚙️ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")
