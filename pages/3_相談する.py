import streamlit as st
from app_core import *

st.set_page_config(
    page_title="相談する",
    page_icon="💬",
    layout="centered"
)

require_login()

st.title("💬 相談する")
st.caption("体質・今日の状態・現在の設定をもとに提案します")

user_id = get_user_id()

# -----------------
# データ取得
# -----------------
try:
    settings = load_user_settings(user_id)
    settings = normalize_consult_settings(settings)

    profile = load_current_user_profile(user_id)
    latest_log = load_latest_log(user_id)
    focus = get_support_focus_summary(settings, latest_log)

except Exception as e:
    st.error(f"相談ページの読込に失敗しました: {e}")
    st.stop()

# -----------------
# 表示名
# -----------------
nickname = ""

if isinstance(profile, dict):
    nickname = str(profile.get("nickname", "")).strip()

if not nickname:
    nickname = str(settings.get("nickname", "")).strip()

if not nickname:
    nickname = user_id or ""

if nickname:
    st.info(f"{nickname}さん向けに提案します。")
else:
    st.info("現在の設定をもとに提案します。")

# -----------------
# 今整えたいポイント
# -----------------
st.markdown("### 🌿 今整えたいポイント")

if focus.get("points"):
    st.write(" / ".join(focus["points"]))
else:
    st.write("基本の整え")

if focus.get("today_conditions"):
    st.caption("今日の状態：" + " / ".join(focus["today_conditions"]))
else:
    st.caption("今日の状態：まだ記録がありません")

st.markdown("---")

# -----------------
# 相談カテゴリ
# -----------------
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
}

question = st.text_area(
    "相談内容",
    placeholder=example_text.get(category, "相談したいことを書いてください"),
    height=140,
)

# -----------------
# 相談ボタン
# -----------------
if st.button("相談する", use_container_width=True):

    answer = generate_answer(
        category=category,
        question=question,
        settings=settings,
        latest_log=latest_log,
    )

    st.session_state["last_answer"] = answer

# -----------------
# 回答表示
# -----------------
if "last_answer" in st.session_state:
    st.subheader("回答")
    st.write(st.session_state["last_answer"])

# -----------------
# 現在の設定
# -----------------
st.divider()
st.subheader("いまの設定")

st.write(f"利用タイプ：{settings.get('user_type', '自分向け')}")
st.write(f"活動量：{settings.get('activity_level', 'ふつう')}")
st.write(f"食事スタイル：{settings.get('food_style', settings.get('meal_style', '和食中心'))}")

traits = settings.get("constitution_traits", [])

if isinstance(traits, list):
    traits_text = " / ".join(traits) if traits else "未設定"
else:
    traits_text = str(traits) if traits else "未設定"

st.write(f"体質・傾向：{traits_text}")
st.write(f"アドバイスの言い方：{settings.get('advice_tone', 'やさしく')}")

st.caption("※ この相談機能は簡易版です。医療判断が必要な内容は医療機関に相談してください。")
