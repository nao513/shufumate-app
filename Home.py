import streamlit as st
import random
import requests
from datetime import datetime

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
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]

        if "rain" in desc.lower():
            return "雨"
        elif temp >= 28:
            return "暑い"
        elif temp <= 10:
            return "寒い"
        else:
            return "普通"
    except:
        return "普通"

weather = get_weather()

# -----------------
# 🎯 優先順位ロジック（先に定義）
# -----------------
def apply_priority(state):
    if state["疲れ"]:
        return {"疲れ": True, "冷え": False, "こり": False, "食べすぎ": False}
    elif state["食べすぎ"]:
        return {"疲れ": False, "冷え": False, "こり": False, "食べすぎ": True}
    elif state["冷え"]:
        return {"疲れ": False, "冷え": True, "こり": False, "食べすぎ": False}
    elif state["こり"]:
        return {"疲れ": False, "冷え": False, "こり": True, "食べすぎ": False}
    return state

# -----------------
# 🧠 状態 初期化＋日付管理
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
# 🤖 自動判定
# -----------------
def detect_overeating(log):
    if not log:
        return False
    return any(k in str(log) for k in ["食べすぎ", "大盛り", "満腹", "おかわり"])

def detect_fatigue(log):
    if not log:
        return False
    return any(k in str(log) for k in ["ヨガ", "運動", "筋トレ", "ジム", "疲れた"])

def detect_cold(weather):
    return weather == "寒い"

# 自動反映
if detect_overeating(latest_log):
    st.session_state["overeating"] = True

if detect_fatigue(latest_log):
    st.session_state["fatigue"] = True

if detect_cold(weather):
    st.session_state["cold"] = True

# -----------------
# 🟩 UI開始
# -----------------
render_header()

# 今日の状態
st.markdown("### 📊 今日の状態")
log_status = get_today_log_status(user_id)

if log_status["is_logged"]:
    st.success(log_status["label"])
else:
    st.info(log_status["label"])

st.caption(log_status["detail"])
st.markdown("---")

# -----------------
# 🧠 体調UI（key付き）
# -----------------
st.markdown("### 🧠 今日の体調")
col1, col2 = st.columns(2)

with col1:
    st.session_state["fatigue"] = st.checkbox("疲れてる", key="fatigue")
    st.session_state["cold"] = st.checkbox("冷えを感じる", key="cold")

with col2:
    st.session_state["stiff"] = st.checkbox("こりがある", key="stiff")
    st.session_state["overeating"] = st.checkbox("食べすぎた", key="overeating")

# state生成
state = {
    "疲れ": st.session_state["fatigue"],
    "冷え": st.session_state["cold"],
    "こり": st.session_state["stiff"],
    "食べすぎ": st.session_state["overeating"]
}

# 優先適用
state = apply_priority(state)

st.markdown("---")

# -----------------
# 💬 動的アドバイス
# -----------------
def generate_dynamic_advice(meal, base_advice, user_type="バランス重視", weather="普通"):
    extra = []

    if weather == "雨":
        extra.append("今日はゆるめでOK")
    elif weather == "暑い":
        extra.append("水分しっかり")
    elif weather == "寒い":
        extra.append("体を温めましょう")

    jokes = ["完璧じゃなくてOK", "それだけで十分です", "今日はゆるくても合格です"]

    result = base_advice
    if extra:
        result += "｜" + random.choice(extra)
    if random.random() < 0.4:
        result += "。" + random.choice(jokes)

    return result

# -----------------
# 表示分岐
# -----------------
mode = st.radio("表示モード", ["かんたん", "しっかり"], horizontal=True)
user_type = st.session_state.get("user_type", "バランス重視")

if mode == "かんたん":
    render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, state)

else:
    render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, state)
