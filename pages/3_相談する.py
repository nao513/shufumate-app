import streamlit as st
from app_core import (
    require_login,
    CATEGORY_OPTIONS,
    get_user_id,
    load_user_settings,
    load_current_user_profile,
    generate_answer,
)

require_login()

st.title("💬 相談する")
st.caption("食事・運動・体調・外食の相談に答えます")

user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
    profile = load_current_user_profile()
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

nickname = profile["nickname"].strip() if profile else settings["nickname"].strip()
if nickname:
    st.info(f"{nickname}さん向けに、現在の設定をもとに提案します。")
else:
    st.info("現在の設定をもとに提案します。")

category = st.radio(
    "相談カテゴリ",
    CATEGORY_OPTIONS,
    horizontal=True,
)

example_text = {
    "食事": "例：運動前に何を食べたらいい？ 今日は夜何を食べるのがおすすめ？",
    "運動": "例：今日は疲れてるけど何をしたらいい？ 5分だけ動くなら？",
    "体調": "例：むくみが気になる。だるい日はどうしたらいい？",
    "外食調整": "例：今日パスタ外食です。どう選べばいい？ 焼肉のときの調整は？",
}[category]

question = st.text_area(
    "相談内容",
    placeholder=example_text,
    height=140,
)

if st.button("相談する", use_container_width=True):
    try:
        answer = generate_answer(category, question, settings)
        st.session_state["last_answer"] = answer
    except Exception as e:
        st.error(f"回答の生成に失敗しました: {e}")

if "last_answer" in st.session_state:
    st.subheader("回答")
    st.write(st.session_state["last_answer"])

st.divider()
st.subheader("いまの設定")
st.write(f"利用タイプ：{settings['user_type']}")
st.write(f"活動量：{settings['activity_level']}")
st.write(f"食事スタイル：{settings['food_style']}")

if profile and profile.get("age") is not None:
    st.write(f"年齢：{profile['age']}歳")

st.caption("※ この相談機能は簡易版です。医療判断が必要な内容は医療機関に相談してください。")
