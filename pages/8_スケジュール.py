import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
from app_core import *

ensure_headers()
reload_user_data_if_needed()

st.set_page_config(page_title="スケジュール", layout="wide")

if "schedules" not in st.session_state:
    st.session_state["schedules"] = []

if "selected_schedule_date" not in st.session_state:
    st.session_state["selected_schedule_date"] = ""

if "wake_time_str" not in st.session_state:
    st.session_state["wake_time_str"] = "06:30"


def build_month_calendar(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)  # 日曜はじまり
    return cal.monthdayscalendar(year, month)


def safe_time_str(value: str, default: str = "06:30") -> str:
    try:
        datetime.strptime(value, "%H:%M")
        return value
    except Exception:
        return default


def shift_time_str(base_time: str, minutes: int) -> str:
    dt = datetime.strptime(base_time, "%H:%M")
    shifted = dt + timedelta(minutes=minutes)
    return shifted.strftime("%H:%M")


def get_recommended_daily_schedule(wake_time_str: str):
    wake_time_str = safe_time_str(wake_time_str, "06:30")
    return {
        "起床": wake_time_str,
        "朝食": shift_time_str(wake_time_str, 30),
        "昼食": shift_time_str(wake_time_str, 330),
        "夕食": shift_time_str(wake_time_str, 690),
        "入浴": shift_time_str(wake_time_str, 870),
        "就寝": shift_time_str(wake_time_str, 930),
    }


def build_daily_timeline_df(recommended: dict):
    order = ["起床", "朝食", "昼食", "夕食", "入浴", "就寝"]
    rows = [{"項目": key, "時間": recommended[key]} for key in order if key in recommended]
    return pd.DataFrame(rows)


def time_to_hour_float(time_str: str) -> float:
    dt = datetime.strptime(time_str, "%H:%M")
    return dt.hour + dt.minute / 60.0


def render_daily_timeline_html(recommended: dict):
    order = ["起床", "朝食", "昼食", "夕食", "入浴", "就寝"]
    colors = {
        "起床": "#f6c28b",
        "朝食": "#f9e0a5",
        "昼食": "#b9d7ea",
        "夕食": "#f7b7a3",
        "入浴": "#cdb4db",
        "就寝": "#a0c4ff",
    }

    markers_html = ""
    for label in order:
        if label in recommended:
            left = (time_to_hour_float(recommended[label]) / 24) * 100
            color = colors.get(label, "#d9d9d9")
            markers_html += f"""
            <div style="
                position:absolute;
                left:{left}%;
                top:10px;
                transform:translateX(-50%);
                text-align:center;
            ">
                <div style="
                    width:14px;
                    height:14px;
                    border-radius:50%;
                    background:{color};
                    margin:0 auto 6px auto;
                    border:2px solid white;
                    box-shadow:0 1px 4px rgba(0,0,0,0.15);
                "></div>
                <div style="
                    font-size:12px;
                    color:#5b4b42;
                    white-space:nowrap;
                    font-weight:600;
                ">{label}</div>
                <div style="
                    font-size:11px;
                    color:#7a6a5f;
                    white-space:nowrap;
                ">{recommended[label]}</div>
            </div>
            """

    hour_labels = ""
    for h in range(0, 25, 3):
        left = (h / 24) * 100
        hour_labels += f"""
        <div style="
            position:absolute;
            left:{left}%;
            top:72px;
            transform:translateX(-50%);
            font-size:11px;
            color:#7a6a5f;
        ">{h}:00</div>
        """

    st.markdown(
        f"""
        <div style="
            position:relative;
            width:100%;
            height:95px;
            margin:10px 0 18px 0;
            background:#fffaf5;
            border:1px solid #eadfce;
            border-radius:16px;
            padding:0 10px;
            box-sizing:border-box;
        ">
            <div style="
                position:absolute;
                left:3%;
                right:3%;
                top:16px;
                height:4px;
                background:#eadfce;
                border-radius:999px;
            "></div>

            {markers_html}
            {hour_labels}
        </div>
        """,
        unsafe_allow_html=True
    )


st.header("🗓 スケジュール管理")

today = datetime.today()
col_y, col_m = st.columns(2)
with col_y:
    view_year = st.number_input("年", min_value=2024, max_value=2100, value=today.year, step=1)
with col_m:
    view_month = st.selectbox("月", list(range(1, 13)), index=today.month - 1)

st.subheader(f"📅 {view_year}年 {view_month}月カレンダー")

week_labels = ["日", "月", "火", "水", "木", "金", "土"]
cols = st.columns(7)
for i, label in enumerate(week_labels):
    cols[i].markdown(f"**{label}**")

month_matrix = build_month_calendar(view_year, view_month)

for week in month_matrix:
    week_cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            week_cols[i].write("")
        else:
            date_str = f"{view_year}-{view_month:02d}-{day:02d}"
            day_events = [
                s for s in st.session_state["schedules"]
                if s.get("日付") == date_str
            ]

            label = str(day)
            if day_events:
                label += f" ✅{len(day_events)}"

            if week_cols[i].button(label, key=f"cal_{date_str}"):
                st.session_state["selected_schedule_date"] = date_str

selected_date = st.session_state.get("selected_schedule_date", "")
if not selected_date:
    selected_date = today.strftime("%Y-%m-%d")

st.divider()
st.subheader("⏰ 生活リズム目安")

st.text_input("起きる時間（HH:MM）", key="wake_time_str")

recommended = get_recommended_daily_schedule(st.session_state["wake_time_str"])

r1, r2, r3 = st.columns(3)
r1.metric("起床", recommended["起床"])
r2.metric("朝食", recommended["朝食"])
r3.metric("昼食", recommended["昼食"])

r4, r5, r6 = st.columns(3)
r4.metric("夕食", recommended["夕食"])
r5.metric("入浴", recommended["入浴"])
r6.metric("就寝", recommended["就寝"])

st.caption("※目安として、睡眠7時間以上・就寝1時間前までの入浴を意識します。")

st.subheader("🕒 24時間タイムライン")

timeline_df = build_daily_timeline_df(recommended)
if not timeline_df.empty:
    st.dataframe(timeline_df[["項目", "時間"]], use_container_width=True, hide_index=True)

render_daily_timeline_html(recommended)

st.caption("※0〜24時の中で、起床・食事・入浴・就寝の目安時間を1日の流れとして見える化しています。")

st.divider()
st.subheader("➕ 選択日の予定を追加")
st.write(f"選択中の日付: **{selected_date}**")

with st.form("schedule_form"):
    event_type = st.selectbox(
        "種類",
        ["起床", "朝食", "昼食", "夕食", "入浴", "就寝", "運動", "買い物", "献立準備", "学校", "通院", "その他"]
    )
    event_time = st.text_input("時間（例 07:00）", "")
    event = st.text_input("予定内容")
    s_submitted = st.form_submit_button("追加する")

if s_submitted:
    st.session_state["schedules"].append({
        "日付": selected_date,
        "種類": event_type,
        "時間": event_time,
        "内容": event
    })
    st.success("予定を登録しました。")
    st.rerun()

st.divider()
st.subheader("📋 選択日の予定一覧")

selected_events = [
    s for s in st.session_state["schedules"]
    if s.get("日付") == selected_date
]

if selected_events:
    df_sched = pd.DataFrame(selected_events)
    if "時間" in df_sched.columns:
        df_sched = df_sched.sort_values(by=["時間", "種類"], na_position="last")
    st.dataframe(df_sched, use_container_width=True, hide_index=True)
else:
    st.info("この日の予定はまだありません。")

st.divider()
st.subheader("🛏 睡眠・入浴チェック")

sleep_time = recommended["就寝"]
bath_time = recommended["入浴"]
st.write(f"理想の目安：**入浴 {bath_time} → 就寝 {sleep_time}**")
st.write("睡眠は **7時間以上確保** を目標にしましょう。")
