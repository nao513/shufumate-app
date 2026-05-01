import streamlit as st
import random
import requests
import pandas as pd
import altair as alt

# -----------------
# app_core
# -----------------
from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    load_latest_log,
    get_today_advice,
    get_today_exercise,
    generate_weekly_plan,
    get_week_key,
    jst_now,
    get_today_log_status,
    load_weight_data,
    get_streak_days
)

# -----------------
# UI
# -----------------
from ui_parts import render_header, render_simple_mode, render_full_mode

# -----------------
# ログイン
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# データ
# -----------------
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

advice = get_today_advice(settings, latest_log)
exercise = get_today_exercise(settings, latest_log)

# -----------------
# 時間
# -----------------
hour = jst_now().hour
main_meal = "朝" if hour < 10 else "昼" if hour < 15 else "夜"

# -----------------
# 週間
# -----------------
week_key = get_week_key()
if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# -----------------
# 天気
# -----------------
def get_weather():
    try:
        res = requests.get("https://wttr.in/Sendai?format=j1", timeout=3)
        data = res.json()
        temp = int(data["current_condition"][0]["temp_C"])
        if temp <= 10:
            return "寒い"
        elif temp >= 28:
            return "暑い"
        else:
            return "普通"
    except:
        return "普通"

weather = get_weather()

# -----------------
# 体調 state
# -----------------
today_str = jst_now().strftime("%Y-%m-%d")

defaults = {"fatigue": False, "cold": False, "stiff": True, "overeating": False}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "state_date" not in st.session_state:
    st.session_state["state_date"] = today_str

if st.session_state["state_date"] != today_str:
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state["state_date"] = today_str

# -----------------
# UI開始
# -----------------
render_header()

# 今日の状態
st.markdown("### 📊 今日の状態")
log_status = get_today_log_status(user_id)

st.success(log_status["label"]) if log_status["is_logged"] else st.info(log_status["label"])
st.caption(log_status["detail"])

# -----------------
# 🔥 継続日数
# -----------------
streak = get_streak_days(user_id)

if streak > 0:
    st.markdown(f"### 🔥 {streak}日連続記録中！")
else:
    st.info("今日からスタートしましょう☺️")

# -----------------
# 🧠 体調
# -----------------
st.markdown("### 🧠 今日の体調")

col1, col2 = st.columns(2)
with col1:
    st.checkbox("疲れてる", key="fatigue")
    st.checkbox("冷え", key="cold")
with col2:
    st.checkbox("こり", key="stiff")
    st.checkbox("食べすぎ", key="overeating")

state = {
    "疲れ": st.session_state["fatigue"],
    "冷え": st.session_state["cold"],
    "こり": st.session_state["stiff"],
    "食べすぎ": st.session_state["overeating"]
}

# -----------------
# 🌿 体調スコア
# -----------------
score = 5
for v in state.values():
    if v:
        score -= 1
score = max(1, score)

stars = "★" * score + "☆" * (5 - score)
st.markdown(f"### 🌿 今日の調子 {stars}")

# -----------------
# 📊 グラフ
# -----------------
st.markdown("### 📊 体の変化")

weight_df = load_weight_data(user_id)

if weight_df is not None and not weight_df.empty:

    df = weight_df.copy()
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
        df["体脂肪"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna()

    if not df.empty:

        target_weight = st.session_state.get("target_weight", 48)

        base = alt.Chart(df).encode(x="log_date:T")

        chart = base.mark_line(color="blue").encode(y="weight:Q")

        if "体脂肪" in df.columns:
            chart += base.mark_line(color="orange").encode(y="体脂肪:Q")

        chart += alt.Chart(df).mark_rule(color="red").encode(y=alt.datum(target_weight))

        st.altair_chart(chart, use_container_width=True)
        st.caption(f"目標体重：{target_weight}kg")

        # -----------------
        # 🎯 達成率
        # -----------------
        start = df["weight"].iloc[0]
        current = df["weight"].iloc[-1]

        total = start - target_weight
        progress = start - current

        if total > 0:
            rate = max(0, min(progress / total, 1))
            st.progress(rate)
            st.write(f"達成率：{int(rate*100)}%")
            st.caption(f"あと {round(current - target_weight,1)}kg")

        # -----------------
        # 💬 コメント
        # -----------------
        if len(df) >= 2:
            diff = current - df["weight"].iloc[-2]

            if diff < 0:
                st.success("順調です😊")
            elif diff > 0.3:
                st.warning("少し増えていますが大丈夫☺️")
            else:
                st.info("キープできています👌")

    else:
        st.info("データがありません")
else:
    st.info("体重データがありません")

# -----------------
# モード
# -----------------
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

def generate_dynamic_advice(meal, base, user_type, weather):
    return base

if mode == "かんたん":
    render_simple_mode(main_meal, advice, generate_dynamic_advice, None, weather, state)
else:
    render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, None, weather, state)
