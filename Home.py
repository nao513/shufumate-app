import streamlit as st
import random
import requests
from datetime import datetime
from app_core import load_weight_data

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
# 🎯 優先順位ロジック
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

# 自動反映（※ここでは代入OK）
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
# 🧠 体調UI（重要：代入しない）
# -----------------
st.markdown("### 🧠 今日の体調")
col1, col2 = st.columns(2)

with col1:
    st.checkbox("疲れてる", key="fatigue")
    st.checkbox("冷えを感じる", key="cold")

with col2:
    st.checkbox("こりがある", key="stiff")
    st.checkbox("食べすぎた", key="overeating")

# state生成（ここで読む）
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

st.markdown("### 📊 体重の変化")

# 仮データ（あとで実データに置き換え）
weight_data = [
    ("2024-04-01", 52.0),
    ("2024-04-02", 51.8),
    ("2024-04-03", 51.6),
    ("2024-04-04", 51.7),
    ("2024-04-05", 51.5),
]

# データ整形
import pandas as pd

df = pd.DataFrame(weight_data, columns=["日付", "体重"])
df["日付"] = pd.to_datetime(df["日付"])

# グラフ表示（Streamlit標準）
st.line_chart(df.set_index("日付"))

st.markdown("### 📊 体脂肪の変化")

fat_data = [
    ("2024-04-01", 26.0),
    ("2024-04-02", 25.8),
    ("2024-04-03", 25.6),
    ("2024-04-04", 25.7),
    ("2024-04-05", 25.5),
]

df2 = pd.DataFrame(fat_data, columns=["日付", "体脂肪"])
df2["日付"] = pd.to_datetime(df2["日付"])

st.line_chart(df2.set_index("日付"))

import altair as alt

st.markdown("### 📊 体の変化")

if weight_df is not None and not weight_df.empty:
    df = weight_df.copy()

    import pandas as pd
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    # 体脂肪
    if "body_fat" in df.columns:
        df["体脂肪"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna()

    if not df.empty:

        # 🎯 目標体重（ここ変えられる）
        target_weight = 48

# -----------------
# 📊 データ取得
# -----------------
weight_df = load_weight_data(user_id)

# -----------------
# 📊 グラフ
# -----------------
st.markdown("### 📊 体の変化")

if weight_df is not None and not weight_df.empty:
    df = weight_df.copy()

    import pandas as pd
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "body_fat" in df.columns:
        df["体脂肪"] = pd.to_numeric(df["body_fat"], errors="coerce")

    df = df.dropna()

    if not df.empty:
        st.line_chart(df.set_index("log_date"), use_container_width=True)
    else:
        st.info("データがまだありません")
else:
    st.info("データがまだありません")

# -----------------
# 💬 自動コメント
# -----------------
if len(df) >= 2:
    latest = df["weight"].iloc[-1]
    prev = df["weight"].iloc[-2]

    diff = latest - prev

    if diff < -0.3:
        msg = "順調に減っています😊いい流れです！"
    elif diff < 0:
        msg = "少しずつ減っています👍その調子です"
    elif diff < 0.3:
        msg = "キープできています👌無理しなくてOK"
    else:
        msg = "少し増えていますが大丈夫。整えていきましょう☺️"

    st.success(msg)
# -----------------
# 🧠 体調連動コメント
# -----------------
if len(df) >= 2:

    latest = df["weight"].iloc[-1]
    prev = df["weight"].iloc[-2]
    diff = latest - prev

    fatigue = state["疲れ"]
    overeating = state["食べすぎ"]
    cold = state["冷え"]

    # 🎯 パターン分岐
    if fatigue and diff > 0:
        msg = "今日は少し疲れが出ているかも。無理せず整えましょう☺️"

    elif overeating and diff > 0:
        msg = "昨日少し食べた分ですね😊今日は軽めでOKです"

    elif cold and diff > 0:
        msg = "体が冷えて巡りが落ちているかも。温めていきましょう🔥"

    elif diff < -0.3:
        msg = "順調に減っています✨いい流れです！"

    elif diff < 0:
        msg = "少しずついい変化が出ています👍"

    elif diff < 0.3:
        msg = "キープできています👌十分です"

    else:
        msg = "大丈夫。焦らず整えていきましょう☺️"

    st.success(msg)
# -----------------
# グラフ作成
# -----------------
chart = weight_line + target_line
if fat_line:
    chart = chart + fat_line

# -----------------
# グラフ表示
# -----------------
st.altair_chart(chart, use_container_width=True)

# -----------------
# 💬 コメント（整理版）
# -----------------
if len(df) >= 2:
    weight_diff = df["weight"].iloc[-1] - df["weight"].iloc[-2]

    fat_diff = None
    if "体脂肪" in df.columns:
        fat_diff = df["体脂肪"].iloc[-1] - df["体脂肪"].iloc[-2]

    # 🎯 メイン判定
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
    if fat_diff < 0:
        st.info("体脂肪も減っています✨いい変化です")
