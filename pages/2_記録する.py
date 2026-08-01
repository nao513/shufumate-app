import streamlit as st
import pandas as pd
from datetime import datetime

from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    load_diet_logs,
)

require_login()

st.set_page_config(page_title="記録する｜ShufuMate", page_icon="📝")

st.title("📝 記録する")

user_id = get_user_id()

# =========================
# 入力エリア
# =========================
st.markdown("## 今日の記録")

col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("体重(kg)", value=50.0, step=0.1)
with col2:
    body_fat = st.number_input("体脂肪(%)", value=20.0, step=0.1)

muscle_mass = st.number_input("筋肉量(kg)", value=0.0, step=0.1)

st.markdown("### 食事")
breakfast = st.text_input("朝")
lunch = st.text_input("昼")
dinner = st.text_input("夜")
snack = st.text_input("間食")

memo = st.text_area("メモ")

# =========================
# 保存
# =========================
if st.button("保存する"):
    today = datetime.now().strftime("%Y-%m-%d")

    meal_memo = f"""
朝: {breakfast}
昼: {lunch}
夜: {dinner}
間食: {snack}
メモ: {memo}
"""

    log = {
        "user_id": user_id,

        # グラフ用
        "log_date": today,
        "weight": round(weight, 1),
        "body_fat": round(body_fat, 1),
        "muscle_mass": round(muscle_mass, 1),

        # 表示用
        "日付": today,
        "体重(kg)": round(weight, 1),
        "体脂肪率(%)": round(body_fat, 1),

        "meal_memo": meal_memo,
    }

    save_diet_log(user_id, log)
    st.success("保存しました")

# =========================
# グラフ＋分析
# =========================
st.markdown("---")
st.markdown("## 📊 からだの変化")

logs = load_diet_logs(user_id)

if logs:
    df = pd.DataFrame(logs)

    # 日付
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")
    df = df.dropna(subset=["log_date"])
    df = df.sort_values("log_date")

    # 数値
    for col in ["weight", "body_fat", "muscle_mass"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.set_index("log_date")

    # グラフ
    cols = [c for c in ["weight", "body_fat", "muscle_mass"] if c in df.columns]

    st.line_chart(df[cols])

    # =========================
    # 分析
    # =========================
    st.markdown("## 🧠 分析コメント")

    latest = df.iloc[-1]
    first = df.iloc[0]

    comments = []

    # 体重
    if "weight" in df.columns:
        diff = latest["weight"] - first["weight"]

        if diff < -1:
            comments.append("体重はしっかり減少しています（かなり良い流れ）")
        elif diff > 1:
            comments.append("体重は増加傾向です（食事見直しポイントあり）")
        else:
            comments.append("体重は安定しています")

    # 体脂肪
    if "body_fat" in df.columns:
        diff = latest["body_fat"] - first["body_fat"]

        if diff < -1:
            comments.append("体脂肪が減少しています（理想的）")
        elif diff > 1:
            comments.append("体脂肪が増え気味です（間食・油チェック）")
        else:
            comments.append("体脂肪は安定しています")

    # 筋肉量
    if "muscle_mass" in df.columns:
        if not df["muscle_mass"].isna().all():
            diff = latest["muscle_mass"] - first["muscle_mass"]

            if diff > 0.3:
                comments.append("筋肉量が増えています（かなり良い状態）")
            elif diff < -0.3:
                comments.append("筋肉量が少し減っています（タンパク質＋運動）")
            else:
                comments.append("筋肉量は維持できています")

    st.markdown("### 📝 総合")

    for c in comments:
        st.write("・" + c)

    # 一言
    st.markdown("### 💡 今日のアドバイス")

    text = "".join(comments)

    if "減少しています（理想的）" in text:
        st.success("かなり良い流れです。このままキープでOK")
    elif "筋肉量が少し減っています" in text:
        st.warning("タンパク質を少し増やすと改善しやすいです")
    elif "増加傾向" in text:
        st.error("夜ごはん・間食を少し見直すと変わります")
    else:
        st.info("無理せず、このまま続ければOKです")

else:
    st.info("まだ記録がありません")
