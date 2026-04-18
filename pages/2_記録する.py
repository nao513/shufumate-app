import streamlit as st
from datetime import date
from app_core import (
    get_user_id,
    get_initial_log_values,
    save_diet_log,
    load_recent_logs,
    load_log_chart_df,
)

st.title("📝 記録する")
st.caption("今日の体重・体脂肪・食事・運動を記録します")

user_id = get_user_id()

try:
    initial = get_initial_log_values(user_id)
except Exception as e:
    st.error(f"初期値の読込に失敗しました: {e}")
    st.stop()

with st.form("diet_log_form"):
    log_date = st.date_input("日付", value=date.today())

    weight = st.number_input(
        "体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(initial["weight"]),
        step=0.1,
        format="%.1f",
    )

    body_fat = st.number_input(
        "体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(initial["body_fat"]),
        step=0.1,
        format="%.1f",
    )

    meal_memo = st.text_area("食事メモ", placeholder="例：朝 納豆ごはん、昼 パスタ、夜 鮭と味噌汁")
    exercise_memo = st.text_area("運動メモ", placeholder="例：ヨガ30分、散歩20分")
    condition_note = st.text_area("体調メモ", placeholder="例：少しむくみあり、よく眠れた")
    mood_note = st.text_area("気分メモ", placeholder="例：疲れ気味、やる気あり")

    submitted = st.form_submit_button("今日の記録を保存", use_container_width=True)

if submitted:
    save_data = {
        "log_date": log_date.strftime("%Y-%m-%d"),
        "weight": float(weight),
        "body_fat": float(body_fat),
        "meal_memo": meal_memo.strip(),
        "exercise_memo": exercise_memo.strip(),
        "condition_note": condition_note.strip(),
        "mood_note": mood_note.strip(),
    }

    try:
        save_diet_log(user_id, save_data)
        st.success("今日の記録を保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")

st.divider()
st.subheader("📈 体重・体脂肪の推移")

try:
    chart_df = load_log_chart_df(user_id)

    if chart_df.empty:
        st.info("まだグラフ表示できる記録がありません")
    else:
        st.markdown("**体重(kg)**")
        st.line_chart(chart_df[["体重(kg)"]], use_container_width=True)

        st.markdown("**体脂肪(%)**")
        st.line_chart(chart_df[["体脂肪(%)"]], use_container_width=True)

except Exception as e:
    st.error(f"グラフの読込に失敗しました: {e}")

st.divider()
st.subheader("最近の記録")

try:
    recent_logs = load_recent_logs(user_id, limit=10)
    if recent_logs.empty:
        st.info("まだ記録がありません")
    else:
        st.dataframe(recent_logs, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"記録一覧の読込に失敗しました: {e}")
