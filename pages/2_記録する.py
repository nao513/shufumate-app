import streamlit as st
from datetime import datetime
from app_core import *

# -----------------
# 初期設定
# -----------------
st.set_page_config(
    page_title="記録する",
    page_icon="📝",
    layout="centered"
)

require_login()
user_id = get_user_id()

# -----------------
# 安全変換
# -----------------
def safe_float(value, default):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)

# -----------------
# データ取得
# -----------------
try:
    settings = load_user_settings(user_id)
    initial = get_initial_log_values(user_id)
except Exception as e:
    st.error(f"記録画面の読み込みに失敗しました: {e}")
    st.stop()

# -----------------
# タイトル
# -----------------
st.title("📝 今日の記録")

today_label = datetime.now().strftime("%Y年%m月%d日")
today_value = datetime.now().strftime("%Y-%m-%d")

st.markdown(f"### {today_label}")
st.caption("体重・食事・運動・今日の状態をかんたんに残します")

st.markdown("---")

# -----------------
# 体重・体脂肪
# -----------------
st.subheader("📊 からだの記録")

col1, col2 = st.columns(2)

with col1:
    weight = st.number_input(
        "体重 (kg)",
        min_value=20.0,
        max_value=150.0,
        value=safe_float(initial.get("weight"), 50),
        step=0.1
    )

with col2:
    body_fat = st.number_input(
        "体脂肪 (%)",
        min_value=5.0,
        max_value=60.0,
        value=safe_float(initial.get("body_fat"), 30),
        step=0.1
    )

# -----------------
# 今日の状態
# -----------------
st.markdown("---")
st.subheader("🌿 今日の状態")

conditions = [
    "寝不足",
    "だるい",
    "むくみあり",
    "食べすぎた",
    "外食あり",
    "時間がない"
]

selected_conditions = []
cols = st.columns(3)

for i, cond in enumerate(conditions):
    with cols[i % 3]:
        if st.checkbox(cond, key=f"condition_{cond}"):
            selected_conditions.append(cond)

# -----------------
# 食事メモ
# -----------------
st.markdown("---")
st.subheader("🍽 食事メモ")

if "meal_memo" not in st.session_state:
    st.session_state["meal_memo"] = "朝：\n昼：\n夜：\n間食："

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("テンプレート挿入", use_container_width=True):
        st.session_state["meal_memo"] = "朝：\n昼：\n夜：\n間食："
        st.rerun()

with col_btn2:
    if st.button("クリア", use_container_width=True):
        st.session_state["meal_memo"] = ""
        st.rerun()

meal_memo = st.text_area(
    "今日食べたもの",
    key="meal_memo",
    height=170,
    placeholder="朝：\n昼：\n夜：\n間食："
)

# -----------------
# 運動メモ
# -----------------
st.markdown("---")
st.subheader("🏃‍♀️ 運動")

exercise_memo = st.text_area(
    "今日の運動",
    placeholder="例：ヨガ30分、散歩20分、ストレッチ10分",
    height=90
)

# -----------------
# 気分メモ
# -----------------
st.markdown("---")
st.subheader("💬 ひとことメモ")

mood_note = st.text_area(
    "今日の気分・気づいたこと",
    placeholder="例：今日はむくみが少なかった。夜は軽めにしたい。",
    height=90
)

# -----------------
# 保存ボタン
# -----------------
st.markdown("---")

if st.button("✅ 記録を保存", use_container_width=True):

    meal_sections = parse_meal_sections(meal_memo)

    log_data = {
        "log_date": today_value,
        "weight": weight,
        "body_fat": body_fat,
        "meal_memo": meal_memo,
        "breakfast": meal_sections.get("朝", ""),
        "lunch": meal_sections.get("昼", ""),
        "dinner": meal_sections.get("夜", ""),
        "snack": meal_sections.get("間食", ""),
        "exercise_memo": exercise_memo,
        "condition_note": "、".join(selected_conditions),
        "mood_note": mood_note,
        "today_conditions": selected_conditions,
    }

    save_diet_log(user_id, log_data)

    # 設定側の現在値も更新しておく
    save_user_settings(
        user_id,
        {
            "current_weight": weight,
            "current_body_fat": body_fat,
        }
    )

    st.success("記録しました！")
    st.balloons()

# -----------------
# 最新記録表示
# -----------------
st.markdown("---")

with st.expander("📌 最新の記録を確認する"):
    latest = load_latest_log(user_id)

    if latest:
        st.write(f"日付：{latest.get('log_date', latest.get('date', ''))}")
        st.write(f"体重：{latest.get('weight', '')} kg")
        st.write(f"体脂肪：{latest.get('body_fat', '')} %")
        st.write(f"状態：{latest.get('condition_note', '')}")
        st.write(f"運動：{latest.get('exercise_memo', '')}")
    else:
        st.info("まだ記録がありません")
