import streamlit as st
import pandas as pd

from app_core import (
    require_login,
    get_user_id,
    load_diet_logs,
    jst_today,
)

# =========================
# 初期設定
# =========================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered",
)

require_login()

user_id = get_user_id()

st.title("🏠 ShufuMate")

# =========================
# 今日の状態
# =========================
st.markdown("## 🌿 今日の状態")

logs = load_diet_logs(user_id)

if logs:
    df = pd.DataFrame(logs)

    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df = df.dropna(subset=["log_date"])
    df = df.sort_values("log_date")

    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("体重", f"{latest.get('weight', 0)} kg")

    with col2:
        st.metric("体脂肪", f"{latest.get('body_fat', 0)} %")

    with col3:
        bmi = 0
        if latest.get("weight") and latest.get("height_cm"):
            bmi = latest["weight"] / ((latest["height_cm"] / 100) ** 2)
        st.metric("BMI", f"{round(bmi,1) if bmi else '--'}")

else:
    st.info("まだ記録がありません")

# =========================
# 今日のアドバイス
# =========================
st.markdown("## 💡 今日の整え方")

if logs:
    comments = []

    first = df.iloc[0]
    latest = df.iloc[-1]

    # 体重
    if "weight" in df.columns:
        diff = latest["weight"] - first["weight"]

        if diff < -1:
            comments.append("体重は良い流れで減っています")
        elif diff > 1:
            comments.append("体重は少し増加傾向です")
        else:
            comments.append("体重は安定しています")

    # 体脂肪
    if "body_fat" in df.columns:
        diff = latest["body_fat"] - first["body_fat"]

        if diff < -1:
            comments.append("体脂肪が減っていて理想的です")
        elif diff > 1:
            comments.append("体脂肪が少し増えています")
        else:
            comments.append("体脂肪は安定しています")

    # 筋肉量
    if "muscle_mass" in df.columns:
        if not df["muscle_mass"].isna().all():
            diff = latest["muscle_mass"] - first["muscle_mass"]

            if diff > 0.3:
                comments.append("筋肉量が増えています（とても良いです）")
            elif diff < -0.3:
                comments.append("筋肉量が少し減っています")
            else:
                comments.append("筋肉量は維持できています")

    for c in comments:
        st.write("・" + c)

    # ワンポイント
    text = "".join(comments)

    if "減っていて理想的" in text:
        st.success("かなり良い流れです。このまま続けましょう")
    elif "増加傾向" in text:
        st.warning("夜の食事や間食を少し意識すると変わります")
    else:
        st.info("無理せず整える意識でOKです")

# =========================
# クイックメニュー（カード風）
# =========================
st.markdown("---")
st.markdown("## 📋 メニュー")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

    if st.button("📷 写真で記録", use_container_width=True):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

    if st.button("⚙ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")

# =========================
# フッター
# =========================
st.markdown("---")
st.caption(f"今日の日付：{jst_today().strftime('%Y/%m/%d')}")
