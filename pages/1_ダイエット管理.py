import streamlit as st
import pandas as pd
from datetime import datetime
from app_core import *

st.set_page_config(page_title="ダイエット管理｜ShufuMate", layout="wide")

reload_user_data_if_needed()
load_settings_into_session()
sync_common_from_latest_diet_log()

st.header("📘 ダイエット管理")
st.caption("体重・体脂肪率・筋肉量などを記録して、日々の変化を見返せます。")

st.info(
    "毎日の記録を積み重ねることで、変化の流れを見やすくなります。\n"
    "無理のない範囲で、続けやすい管理にお役立てください。"
)

gender, age, height_cm, weight, target_weight, body_fat, target_body_fat, muscle_mass, target_muscle_mass = render_common_body_inputs()

bmi = round(weight / ((height_cm / 100) ** 2), 1) if height_cm > 0 else 0
goal_calories = round(weight * 22 * 1.5, 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("BMI", bmi)
with col2:
    st.metric("目標摂取カロリー", f"{int(goal_calories)} kcal")
with col3:
    st.metric("筋肉量", f"{muscle_mass:.1f} kg")
with col4:
    st.metric("目標筋肉量", f"{target_muscle_mass:.1f} kg")

st.subheader("✍ 今日の記録")

log_date = st.date_input("記録日", value=datetime.today().date(), key="diet_log_date")

if st.button("💾 今日の記録を保存", use_container_width=True):
    log = {
        "日付": str(log_date),
        "性別": gender,
        "年齢": age,
        "身長(cm)": height_cm,
        "体重(kg)": weight,
        "目標体重(kg)": target_weight,
        "体脂肪率(%)": body_fat,
        "目標体脂肪率(%)": target_body_fat,
        "筋肉量(kg)": muscle_mass,
        "目標筋肉量(kg)": target_muscle_mass,
        "BMI": bmi,
        "目標摂取カロリー": goal_calories,
    }
    upsert_diet_log(log)
    st.session_state["diet_logs"] = load_diet_logs()
    sync_common_from_latest_diet_log()
    st.success("今日の記録を保存しました。")
    st.rerun()

st.divider()
st.subheader("📈 記録一覧")

diet_logs = st.session_state.get("diet_logs", [])

if diet_logs:
    df = pd.DataFrame(diet_logs).copy()
    df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
    df = df.sort_values("日付", ascending=False)

    display_df = df.copy()
    display_df["日付"] = display_df["日付"].dt.strftime("%Y-%m-%d")

    st.dataframe(display_df, use_container_width=True)

    st.subheader("📊 推移")

    chart_df = df.sort_values("日付").set_index("日付")

    if "体重(kg)" in chart_df.columns:
        st.markdown("#### 体重の推移")
        st.line_chart(chart_df["体重(kg)"])

    if "体脂肪率(%)" in chart_df.columns:
        st.markdown("#### 体脂肪率の推移")
        st.line_chart(chart_df["体脂肪率(%)"])

    if "筋肉量(kg)" in chart_df.columns:
        st.markdown("#### 筋肉量の推移")
        st.line_chart(chart_df["筋肉量(kg)"])

    latest = df.iloc[0]
    st.subheader("📝 最新記録")
    st.write(f"日付: {latest['日付'].strftime('%Y-%m-%d') if pd.notnull(latest['日付']) else ''}")
    st.write(f"体重: {latest['体重(kg)']} kg")
    st.write(f"体脂肪率: {latest['体脂肪率(%)']} %")
    if "筋肉量(kg)" in latest.index:
        st.write(f"筋肉量: {latest['筋肉量(kg)']} kg")
    if "目標筋肉量(kg)" in latest.index:
        st.write(f"目標筋肉量: {latest['目標筋肉量(kg)']} kg")
    st.write(f"BMI: {latest['BMI']}")
else:
    st.caption("まだ記録がありません。")
