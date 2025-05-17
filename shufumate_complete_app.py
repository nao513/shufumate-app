import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

# --- ヘッダー ---
st.title("👩‍🍳 ShufuMate｜主婦の味方アプリ")
st.caption("ダイエット・家計・予定・教育・人生設計・お得情報を一元管理")

# --- サイドバー機能選択 ---
mode = st.sidebar.radio("機能を選んでください", [
    "今日のおすすめ", "ダイエット管理", "家計簿", "スケジュール",
    "教育費・人生設計", "お得情報", "設定"
])

# --- 今日のおすすめ ---
if mode == "今日のおすすめ":
    st.header("🌞 今日のおすすめメニュー")
    st.write("✅ 朝：オートミールとゆで卵")
    st.write("✅ 運動：スクワット10回 × 3セット")
    st.write("✅ 家計ワンポイント：特売チラシを確認して買い物はまとめて！")

# --- ダイエット管理 ---
elif mode == "ダイエット管理":
    st.header("⚖️ ダイエット管理")
    weight = st.number_input("現在の体重（kg）", min_value=30.0, max_value=200.0, value=60.0)
    target_weight = st.number_input("目標体重（kg）", min_value=30.0, max_value=200.0, value=55.0)
    weeks = st.slider("目標達成までの期間（週）", 1, 52, 4)
    bmr = weight * 22 * 1.5
    cal_deficit = ((weight - target_weight) * 7200) / (weeks * 7)
    goal_calories = bmr - cal_deficit
    st.metric("目標摂取カロリー", f"{goal_calories:.0f} kcal/日")
    st.caption("※ BMRは活動量1.5で計算")

# --- 家計簿 ---
elif mode == "家計簿":
    st.header("💰 家計簿入力")
    with st.form("budget_form"):
        date = st.date_input("日付", datetime.today())
        category = st.selectbox("カテゴリ", ["食費", "日用品", "教育費", "交際費", "その他"])
        amount = st.number_input("金額（円）", min_value=0)
        memo = st.text_input("メモ")
        submitted = st.form_submit_button("記録する")
        if submitted:
            st.success(f"{date} に {category} : {amount}円 を記録しました（{memo}）")

# --- スケジュール ---
elif mode == "スケジュール":
    st.header("🗓 スケジュール登録")
    with st.form("schedule_form"):
        date = st.date_input("予定日", datetime.today())
        event = st.text_input("予定内容")
        s_submitted = st.form_submit_button("追加する")
        if s_submitted:
            st.success(f"{date} に『{event}』を登録しました")

# --- 教育費・人生設計 ---
elif mode == "教育費・人生設計":
    st.header("📘 教育費・人生プラン")
    num_children = st.number_input("子どもの人数", min_value=0, max_value=5, value=1)
    edu_type = st.selectbox("教育方針", ["すべて公立", "中学から私立", "高校から私立", "大学から私立", "すべて私立"])
    edu_costs = {
        "公立": {"小学校": 50, "中学校": 70, "高校": 100, "大学": 300},
        "私立": {"小学校": 150, "中学校": 200, "高校": 300, "大学": 600}
    }
    current_year = datetime.now().year
    total_cost = 0
    for i in range(num_children):
        age = st.slider(f"子ども{i+1}の現在の年齢", 0, 18, 6)
        plan = {
            "すべて公立": ["公立"] * 4,
            "中学から私立": ["公立", "私立", "私立", "私立"],
            "高校から私立": ["公立", "公立", "私立", "私立"],
            "大学から私立": ["公立"] * 3 + ["私立"],
            "すべて私立": ["私立"] * 4
        }[edu_type]
        levels = ["小学校", "中学校", "高校", "大学"]
        for j, level in enumerate(levels):
            y = current_year + (6 - age) + sum([6,3,3,0][:j])
            cost = edu_costs[plan[j]][level]
            st.write(f"{y}年 - {level}（{plan[j]}）: {cost}万円")
            total_cost += cost
    st.metric("想定教育費合計", f"{total_cost} 万円")

# --- お得情報（Google Sheets連携） ---
elif mode == "お得情報":
    st.header("📢 地域のお得情報")
    sheet_url = st.text_input("スプレッドシートCSVリンク", 
        value="https://docs.google.com/spreadsheets/d/1cLT1eqx7A-XpPvuUSqwxayfXpu5j0xy3YV3opDmcgfU/export?format=csv")
    try:
        df_info = pd.read_csv(sheet_url)
        pref = st.selectbox("地域を選択", df_info["地域"].unique())
        category = st.selectbox("カテゴリを選択", df_info["カテゴリ"].unique())
        filtered = df_info[(df_info["地域"] == pref) & (df_info["カテゴリ"] == category)]
        for _, row in filtered.iterrows():
            st.markdown(f"- {row['情報内容']}（{row['備考']}）")
    except:
        st.error("スプレッドシートの読み込みに失敗しました。")

# --- 設定 ---
elif mode == "設定":
    st.header("⚙️ アプリ設定")
    theme = st.selectbox("テーマ選択", ["ライト", "ダーク"])
    st.write(f"選択中のテーマ：{theme}")
    st.caption("※ 見た目の切り替えには再読み込みが必要な場合があります")