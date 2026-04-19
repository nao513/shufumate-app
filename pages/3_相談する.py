import streamlit as st
from app_core import (
    require_login,
    CATEGORY_OPTIONS,
    get_user_id,
    load_user_settings,
    load_current_user_profile,
    load_latest_log,
    get_support_focus_summary,
    generate_answer,
)

require_login()

st.title("💬 相談する")
st.caption("体質・今日の状態・現在の設定をもとに提案します")

user_id = get_user_id()
settings = load_user_settings(user_id)
profile = load_current_user_profile()
latest_log = load_latest_log(user_id)
focus = get_support_focus_summary(settings, latest_log)

nickname = profile["nickname"].strip() if profile else settings["nickname"].strip()
st.info(f"{nickname}さん向けに提案します。" if nickname else "現在の設定をもとに提案します。")

st.markdown("**今整えたいポイント**")
st.write(" / ".join(focus["points"]) if focus["points"] else "基本の整え")

if focus["today_conditions"]:
    st.caption("今日の状態：" + " / ".join(focus["today_conditions"]))

category = st.radio(
    "相談カテゴリ",
    CATEGORY_OPTIONS,
    horizontal=True,
)

example_text = {
    "食事": "例：今日は何を食べたら整いやすい？ 夜ごはんはどうする？",
    "運動": "例：今日はだるいけど何をしたらいい？ 5分だけ動くなら？",
    "体調": "例：むくみが気になる。寝不足の日はどうしたらいい？",
    "外食調整": "例：今日パスタ外食です。どう選べばいい？ 焼肉のときの調整は？",
}[category]

question = st.text_area(
    "相談内容",
    placeholder=example_text,
    height=140,
)

if st.button("相談する", use_container_width=True):
    st.session_state["last_answer"] = generate_answer(category, question, settings, latest_log)

if "last_answer" in st.session_state:
    st.subheader("回答")
    st.write(st.session_state["last_answer"])

st.divider()
st.subheader("いまの設定")
st.write(f"利用タイプ：{settings['user_type']}")
st.write(f"活動量：{settings['activity_level']}")
st.write(f"食事スタイル：{settings['food_style']}")
st.write(f"体質・傾向：{' / '.join(settings['constitution_traits']) if settings['constitution_traits'] else '未設定'}")
st.write(f"アドバイスの言い方：{settings['advice_tone']}")

st.caption("※ この相談機能は簡易版です。医療判断が必要な内容は医療機関に相談してください。")
