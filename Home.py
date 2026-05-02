import streamlit as st
import random
import requests
import pandas as pd
import altair as alt

from app_core import *
from ui_parts import render_header, render_simple_mode, render_full_mode

# =====================
# 🎨 デザイン（統一）
# =====================
st.markdown("""
<style>
body {
    background-color: #f7f3ef;
}
.card {
    background-color: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 18px;
}
.title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}
.small {
    color: #777;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 🔐 ログイン
# =====================
require_login()
user_id = get_user_id()

# =====================
# 📊 データ
# =====================
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

advice = get_today_advice(settings, latest_log)
exercise = get_today_exercise(settings, latest_log)

# =====================
# ⏰ 食事時間
# =====================
hour = jst_now().hour
main_meal = "朝" if hour < 10 else "昼" if hour < 15 else "夜"

# =====================
# 📅 週間
# =====================
week_key = get_week_key()
if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# =====================
# 🌤 天気
# =====================
def get_weather():
    try:
        res = requests.get("https://wttr.in/Sendai?format=j1", timeout=3)
        temp = int(res.json()["current_condition"][0]["temp_C"])
        return "寒い" if temp <= 10 else "暑い" if temp >= 28 else "普通"
    except:
        return "普通"

weather = get_weather()

# =====================
# 🟩 UI開始
# =====================
render_header()

# =====================
# 📊 今日の状態
# =====================
log_status = get_today_log_status(user_id)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">📊 今日の状態</div>', unsafe_allow_html=True)

if log_status["is_logged"]:
    st.success(log_status["label"])
else:
    st.info(log_status["label"])

st.markdown(f'<div class="small">{log_status.get("detail","")}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 🌿 今日のおすすめ
# =====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">🌿 今日のおすすめ</div>', unsafe_allow_html=True)

st.markdown(f"### ⭐ 今のおすすめ（{main_meal}）")

recommend_text = advice.get(main_meal, "整えましょう")
st.success(recommend_text)

st.caption(f"今は「{main_meal}」を整える時間です☺️")

st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 💬 今日の一言（NEW）
# =====================
message = get_today_message(settings, latest_log, {}, weather)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">💬 今日の一言</div>', unsafe_allow_html=True)

st.success(message)

st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 🚀 すぐやる
# =====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">🚀 すぐやる</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📷 写真で記録", use_container_width=True):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 📊 グラフ
# =====================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">📊 体の変化</div>', unsafe_allow_html=True)

df = load_weight_data(user_id)

if df is not None and not df.empty:

    df = df.copy()
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")

    if "weight" in df.columns:
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
        df["body_fat"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna()

    if not df.empty:

        target_weight = st.session_state.get("target_weight", 48)

        base = alt.Chart(df).encode(x="log_date:T")

        weight_line = base.mark_line(
            color="#4A90E2",
            strokeWidth=3
        ).encode(y="weight:Q")

        chart = weight_line

        if "body_fat" in df.columns:
            fat_line = base.mark_line(
                color="#F5A623",
                strokeDash=[5,2]
            ).encode(y="body_fat:Q")
            chart += fat_line

        target_line = alt.Chart(df).mark_rule(
            color="red",
            strokeDash=[5,5]
        ).encode(y=alt.datum(target_weight))

        chart += target_line

        st.altair_chart(chart, use_container_width=True)
        st.caption(f"🎯 目標体重：{target_weight}kg")

        if len(df) >= 2:
            diff = df["weight"].iloc[-1] - df["weight"].iloc[-2]

            if diff < 0:
                st.success("🔥 いい感じに減ってます！")
            elif diff > 0.5:
                st.warning("⚠ 少し増え気味。でも大丈夫！")
            else:
                st.info("👌 キープできています")

    else:
        st.info("データがまだありません")

else:
    st.info("まだ記録がありません")

st.markdown('</div>', unsafe_allow_html=True)

# =====================
# 💬 動的アドバイス
# =====================
def generate_dynamic_advice(meal, base, user_type, weather):
    extra = []

    if weather == "寒い":
        extra.append("温かいものを取りましょう")
    elif weather == "暑い":
        extra.append("水分をしっかり")

    return base + ("｜" + random.choice(extra) if extra else "")

# =====================
# モード
# =====================
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

user_type = st.session_state.get("user_type", "バランス重視")

if mode == "かんたん":
    render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, {})
else:
    render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, {})
