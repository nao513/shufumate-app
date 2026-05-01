import streamlit as st
import random
import requests
from datetime import datetime
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
    load_weight_data
)

# -----------------
# UIパーツ
# -----------------
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
# ⏰ 食事時間判定
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
# 🌤 天気取得
# -----------------
def get_weather():
    try:
        url = "https://wttr.in/Sendai?format=j1"
        res = requests.get(url, timeout=3)
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
# 🧠 体調 state
# -----------------
today_str = jst_now().strftime("%Y-%m-%d")

defaults = {
    "fatigue": False,
    "cold": False,
    "stiff": True,
    "overeating": False
}

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

# -----------------
# 状態表示
# -----------------
st.markdown("### 📊 今日の状態")
log_status = get_today_log_status(user_id)

if log_status["is_logged"]:
    st.success(log_status["label"])
else:
    st.info(log_status["label"])

st.caption(log_status["detail"])
st.markdown("---")

# -----------------
# 🧠 体調UI
# -----------------
st.markdown("### 🧠 今日の体調")

col1, col2 = st.columns(2)

with col1:
    st.checkbox("疲れてる", key="fatigue")
    st.checkbox("冷えを感じる", key="cold")

with col2:
    st.checkbox("こりがある", key="stiff")
    st.checkbox("食べすぎた", key="overeating")

state = {
    "疲れ": st.session_state["fatigue"],
    "冷え": st.session_state["cold"],
    "こり": st.session_state["stiff"],
    "食べすぎ": st.session_state["overeating"]
}

st.markdown("---")

# -----------------
# 📊 体重データ取得（←ここ重要）
# -----------------
weight_df = load_weight_data(user_id)

# -----------------
# 📊 グラフ
# -----------------
st.markdown("### 📊 体の変化")

if weight_df is not None and not weight_df.empty:

    df = weight_df.copy()

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
        df["体脂肪"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna()

    if not df.empty:

        target_weight = 48

        base = alt.Chart(df).encode(x="log_date:T")

        weight_line = base.mark_line(color="blue").encode(y="weight:Q")

        fat_line = None
        if "体脂肪" in df.columns:
            fat_line = base.mark_line(color="orange").encode(y="体脂肪:Q")

        target_line = alt.Chart(df).mark_rule(color="red", strokeDash=[5,5]).encode(
            y=alt.datum(target_weight)
        )

        chart = weight_line + target_line
        if fat_line:
            chart += fat_line

        st.altair_chart(chart, use_container_width=True)

        # -----------------
        # 💬 コメント
        # -----------------
        if len(df) >= 2:
            weight_diff = df["weight"].iloc[-1] - df["weight"].iloc[-2]

            fat_diff = None
            if "体脂肪" in df.columns:
                fat_diff = df["体脂肪"].iloc[-1] - df["体脂肪"].iloc[-2]

            if weight_diff < 0 and (fat_diff is not None and fat_diff < 0):
                st.success("体重・体脂肪ともにいい流れです✨")

            elif weight_diff < 0:
                st.success("体重は順調に減っています😊")

            elif fat_diff is not None and fat_diff < 0:
                st.info("体脂肪が減っています✨いい変化です")

            elif weight_diff > 0.3:
                st.warning("少し増えていますが大丈夫。整えていきましょう☺️")

            else:
                st.info("キープできています👌その調子です")

    else:
        st.info("データがまだありません")

else:
    st.info("体重データがまだありません")

# -----------------
# モード
# -----------------
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

if mode == "かんたん":
    render_simple_mode(main_meal, advice, None, None, weather, state)
else:
    render_full_mode(advice, exercise, weekly_plan, None, None, weather, state)
