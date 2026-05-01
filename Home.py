import streamlit as st
import random
from datetime import datetime

import requests

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
)

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
# ⏰ 時間で食事決定
# -----------------
hour = jst_now().hour

if hour < 10:
    main_meal = "朝"
elif hour < 15:
    main_meal = "昼"
else:
    main_meal = "夜"

# -----------------
# 📅 週間データ
# -----------------
week_key = get_week_key()

if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# -----------------
# 🌤 動的アドバイス
# -----------------
def generate_dynamic_advice(meal, base_advice, user_type="バランス重視", weather="晴れ"):

    month = datetime.now().month

    if month in [3,4,5]:
        season = "春"
    elif month in [6,7,8]:
        season = "夏"
    elif month in [9,10,11]:
        season = "秋"
    else:
        season = "冬"

    extra = []

    if weather == "雨":
        extra.append("今日はゆるめでOK")
    elif weather == "暑い":
        extra.append("水分しっかり")
    elif weather == "寒い":
        extra.append("体を温めましょう")

    if season == "夏":
        extra.append("冷たいもの取りすぎ注意")
    elif season == "冬":
        extra.append("温かい食事で代謝UP")

    
    
    joke = random.choice([
        "今日はゆるくても合格です😂",
        "完璧じゃなくてOK",
        "それだけで十分です◎",
    ])

    return base_advice + "｜" + random.choice(extra) + "。" + joke if extra else base_advice

def get_weather():
    try:
        # 👇 地域固定（ここ変えればどこでもOK）
        url = "https://wttr.in/Sendai?format=j1"

        res = requests.get(url, timeout=3)
        data = res.json()

        temp = int(data["current_condition"][0]["temp_C"])
        weather_desc = data["current_condition"][0]["weatherDesc"][0]["value"]

        # 🌧 雨判定（最優先）
        if "rain" in weather_desc.lower():
            return "雨"

        # 🌡 気温判定
        if temp >= 28:
            return "暑い"
        elif temp <= 10:
            return "寒い"
        else:
            return "普通"

    except:
        return "普通"

# -----------------
# 🟩 UI
# -----------------
render_header()

mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)

user_type = st.session_state.get("user_type", "バランス重視")
weather = get_weather()

# -----------------
# 🧠 状態（仮：あとでUI化）
# -----------------
state = {
    "疲れ": False,
    "冷え": False,
    "こり": True,
    "食べすぎ": False
}

if mode == "かんたん":
    render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, state)


elif mode == "しっかり":
    render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, state)
