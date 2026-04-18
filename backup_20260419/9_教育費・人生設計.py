import streamlit as st
from datetime import datetime
from app_core import *

ensure_headers()
reload_user_data_if_needed()

st.set_page_config(page_title="教育費・人生設計", layout="wide")

st.header("📘 教育費・人生設計")

num_children = st.number_input("子どもの人数", min_value=0, max_value=5, value=1)
edu_type = st.selectbox(
    "教育方針",
    ["すべて公立", "中学から私立", "高校から私立", "大学から私立", "すべて私立"]
)

edu_costs = {
    "公立": {"小学校": 50, "中学校": 70, "高校": 100, "大学": 300},
    "私立": {"小学校": 150, "中学校": 200, "高校": 300, "大学": 600}
}

current_year = datetime.now().year
total_cost = 0

for i in range(num_children):
    child_age = st.slider(f"子ども{i+1}の現在の年齢", 0, 18, 6, key=f"child_age_{i}")

    plan = {
        "すべて公立": ["公立"] * 4,
        "中学から私立": ["公立", "私立", "私立", "私立"],
        "高校から私立": ["公立", "公立", "私立", "私立"],
        "大学から私立": ["公立"] * 3 + ["私立"],
        "すべて私立": ["私立"] * 4
    }[edu_type]

    levels = ["小学校", "中学校", "高校", "大学"]
    offsets = [0, 6, 9, 12]

    st.subheader(f"👧 子ども{i+1}の教育費目安")

    for j, level in enumerate(levels):
        y = current_year + (6 - child_age) + offsets[j]
        cost = edu_costs[plan[j]][level]
        st.write(f"{y}年 - {level}（{plan[j]}）: {cost}万円")
        total_cost += cost

st.metric("想定教育費合計", f"{total_cost} 万円")

st.divider()
st.subheader("💡 使い方の目安")
st.write("・教育方針ごとのざっくりした差を見たいときに使えます。")
st.write("・毎月の積立や、家計全体の見直しの参考にできます。")
st.write("・今後は教育費以外の人生設計にも広げやすい形です。")

