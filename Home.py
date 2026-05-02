import streamlit as st
import random
import requests
import pandas as pd
import altair as alt

from app_core import *
from ui_parts import render_header, render_simple_mode, render_full_mode

# -----------------
# 🔐 ログイン
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# 📊 データ取得
# -----------------
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

advice = get_today_advice(settings, latest_log)
exercise = get_today_exercise(settings, latest_log)

# -----------------
# ⏰ 食事時間
# -----------------
hour = jst_now().hour
main_meal = "朝" if hour < 10 else "昼" if hour < 15 else "夜"

# -----------------
# 📅 週間データ
# -----------------
week_key = get_week_key()

if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# -----------------
# 🌤 天気
# -----------------
def get_weather():
    try:
        res = requests.get("https://wttr.in/Sendai?format=j1", timeout=3)
        temp = int(res.json()["current_condition"][0]["temp_C"])
        return "寒い" if temp <= 10 else "暑い" if temp >= 28 else "普通"
    except:
        return "普通"

weather = get_weather()

# -----------------
# 🟩 UI開始
# -----------------
render_header()

# -----------------
# 📊 今日の状態（←ここ修正済）
# -----------------
st.markdown("### 📊 今日の状態")

log_status = get_today_log_status(user_id)

if log_status["is_logged"]:
    st.success(log_status["label"])
else:
    st.info(log_status["label"])

st.caption(log_status.get("detail", ""))

st.markdown("---")

# -----------------
# 📊 グラフ（完成版）
# -----------------
st.markdown("### 📊 体の変化")

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

        # コメント
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
    st.info("体重データがまだありません")

# -----------------
# 💬 動的アドバイス
# -----------------
def generate_dynamic_advice(meal, base, user_type, weather):
    extra = []

    if weather == "寒い":
        extra.append("温かいものを取りましょう")
    elif weather == "暑い":
        extra.append("水分をしっかり")

    return base + ("｜" + random.choice(extra) if extra else "")

# -----------------
# モード
# -----------------
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

user_type = st.session_state.get("user_type", "バランス重視")

if mode == "かんたん":
    render_simple_mode(
        main_meal,
        advice,
        generate_dynamic_advice,
        user_type,
        weather,
        {}
    )
else:
    render_full_mode(
        advice,
        exercise,
        weekly_plan,
        generate_dynamic_advice,
        user_type,
        weather,
        {}
    )
