import streamlit as st
from datetime import datetime

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
# ページ設定（最初に！）
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="💻",
    layout="centered",
)

# -----------------
# ログイン
# -----------------
require_login()

# -----------------
# ユーザー取得
# -----------------
user_id = get_user_id()

# -----------------
# データ取得
# -----------------
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

# -----------------
# 今日の提案
# -----------------
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
# タイトル
# -----------------
st.title("💻 ShufuMate")

today = datetime.now().strftime("%Y年%m月%d日")
st.markdown(f"### {today}")

st.markdown("---")

# -----------------
# 今日の食事
# -----------------
st.subheader("🍽 今日の食事")

st.write(f"▶ {advice['食事']}")

st.markdown("🌅 朝")
st.write(advice["朝"])

st.markdown("☀️ 昼（お弁当・外食対応）")
st.write(advice["昼"])

st.markdown("🌙 夜")
st.write(advice["夜"])

st.markdown("---")

# -----------------
# 運動
# -----------------
st.subheader("🏃‍♀️ 今日の運動")
st.write(exercise["title"])
st.write(exercise["body"])

st.markdown("---")

# -----------------
# 週間献立
# -----------------
st.subheader("🗓 今週の献立")

with st.expander("今週の献立を見る"):
    for day, meal in weekly_plan.items():
        st.write(f"{day}：{meal}")

    if st.button("🛒 買い物リストを作る"):
        shopping = generate_shopping_list_from_week(weekly_plan)

        st.markdown("### 🛒 買い物リスト")

        for category, items in shopping.items():
            if items:
                st.markdown(f"**{category}**")
                for item in items:
                    st.checkbox(item, key=f"{category}_{item}")

st.markdown("---")

# -----------------
# ナビゲーション
# -----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("📷 写真で記録", use_container_width=True):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

col3, col4 = st.columns(2)

with col3:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

with col4:
    if st.button("⚙️ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")
