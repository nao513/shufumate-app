import streamlit as st
import pandas as pd
from app_core import *

# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered"
)

# -----------------
# ログインチェック
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# 設定読み込み
# -----------------
try:
    settings = load_user_settings(user_id)
except Exception:
    settings = {}

if not isinstance(settings, dict):
    settings = {}


# -----------------
# 目標体重との距離を判定
# -----------------
def get_weight_goal_status(settings):
    try:
        current_weight = float(
            settings.get("current_weight")
            or settings.get("start_weight")
            or 0
        )
        target_weight = float(settings.get("target_weight") or 0)
    except Exception:
        return "整える"

    if current_weight <= 0 or target_weight <= 0:
        return "整える"

    diff = current_weight - target_weight

    if diff >= 1.0:
        return "減量優先"

    if diff <= -1.0:
        return "落としすぎ注意"

    return "維持"


weight_goal_status = get_weight_goal_status(settings)
user_type_for_plan = f"{settings.get('user_type', '自分向け')}｜{weight_goal_status}"

# -----------------
# ヘッダー
# -----------------
st.title("🏠 ShufuMate")
st.caption("食事も、暮らしも、ちょうどよく")

weekday_jp = ["月", "火", "水", "木", "金", "土", "日"]
now = jst_now()
today_text = now.strftime("%Y年%m月%d日")
weekday_text = weekday_jp[now.weekday()]

st.markdown(f"### 📅 {today_text}（{weekday_text}）")
st.markdown(f"こんにちは、**{user_id} さん** 😊")

if weight_goal_status == "減量優先":
    st.caption("今は目標体重に向けて、夜を少し軽めに整える提案にしています。")
elif weight_goal_status == "落としすぎ注意":
    st.caption("今は落としすぎに注意して、軽くしすぎない提案にしています。")
elif weight_goal_status == "維持":
    st.caption("今は目標体重付近なので、維持しながら整える提案にしています。")
else:
    st.caption("今は基本の整え提案にしています。")

st.markdown("---")

# -----------------
# 表示モード
# -----------------
mode = st.radio(
    "表示モード",
    ["かんたん", "しっかり"],
    horizontal=True
)

# -----------------
# 今日の状態
# -----------------
st.markdown("### 🌿 今日の状態")

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox(
        "体調",
        ["普通", "疲れ", "むくみ"]
    )

with col2:
    weather_label = st.selectbox(
        "今日の体感",
        ["普通", "暑く感じる", "寒く感じる"]
    )

weather_map = {
    "普通": "普通",
    "暑く感じる": "暑い",
    "寒く感じる": "寒い",
}
weather_value = weather_map.get(weather_label, "普通")

# -----------------
# 運動予定
# -----------------
exercise_options = [
    "ストレッチ",
    "ヨガ",
    "ピラティス",
    "ウォーキング",
    "ランニング",
    "筋トレ",
    "なし",
]

default_exercise = settings.get("workout_today", "ストレッチ")

if default_exercise == "有酸素":
    default_exercise = "ウォーキング"

if default_exercise not in exercise_options:
    default_exercise = "ストレッチ"

exercise = st.selectbox(
    "運動予定",
    exercise_options,
    index=exercise_options.index(default_exercise)
)

st.markdown("---")

# -----------------
# 今日のプランを先に作成
# -----------------
try:
    today_plan = generate_full_plan(
        user_type=user_type_for_plan,
        weather=weather_value,
        state=state,
        exercise=exercise
    )
except Exception:
    today_plan = {}

# =====================
# 🌿 かんたんモード
# =====================
if mode == "かんたん":

    st.subheader("🌿 今日のおすすめ")

    try:
        text = generate_simple_advice(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )
        st.success(text)
    except Exception as e:
        st.warning(f"今日のおすすめを作成できませんでした: {e}")

    st.markdown("### 🏃‍♀️ 今日の運動ヒント")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は無理のない範囲で、少し体を動かしましょう。")

# =====================
# 💪 しっかりモード
# =====================
else:

    st.subheader("💪 今日のプラン")

    st.markdown("### 🍽 食事")

    if today_plan:
        for meal_time, menu in today_plan.items():
            if meal_time == "朝":
                icon = "🌅"
            elif meal_time == "昼":
                icon = "☀️"
            elif meal_time == "夜":
                icon = "🌙"
            else:
                icon = "🍽"

            st.markdown(f"{icon} **{meal_time}：** {menu}")
    else:
        st.info("今日の食事プランはまだありません。")

    st.markdown("### 🏃‍♀️ 運動")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は体調に合わせて、できる範囲で整えましょう。")

# -----------------
# 🛒 買い物リスト
# -----------------
st.markdown("---")

with st.expander("🛒 買い物リスト"):

    try:
        shopping_week_plan = generate_weekly_plan(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )

        fridge_items = settings.get("fridge_items", "")

        shopping = generate_supermarket_shopping_list(
            shopping_week_plan,
            fridge_items=fridge_items
        )

        try:
            shopping = add_deals_to_shopping(shopping)
        except Exception:
            pass

        if shopping:
            shopping_rows = []

            for category, items in shopping.items():
                if items:
                    st.markdown(f"**{category}**")

                    for item in items:
                        st.checkbox(
                            item,
                            key=f"home_week_shopping_{category}_{item}"
                        )
                        shopping_rows.append({
                            "カテゴリ": category,
                            "商品": item,
                        })

            if shopping_rows:
                df = pd.DataFrame(shopping_rows)
                csv = df.to_csv(index=False).encode("utf-8-sig")

                st.download_button(
                    "📥 買い物リストCSVをダウンロード",
                    data=csv,
                    file_name="shopping_list_week.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("買い物リストはありません")

    except Exception as e:
        st.warning(f"買い物リストを作成できませんでした: {e}")

# -----------------
# 📅 1週間プラン
# -----------------
with st.expander("📅 1週間プラン"):

    try:
        week_plan = generate_weekly_plan(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )

        for day, day_plan in week_plan.items():
            st.markdown(f"### {day}")
            st.write(f"朝：{day_plan.get('朝', '')}")
            st.write(f"昼：{day_plan.get('昼', '')}")
            st.write(f"夜：{day_plan.get('夜', '')}")

    except Exception as e:
        st.warning(f"1週間プランを作成できませんでした: {e}")

# -----------------
# ログアウト
# -----------------
st.markdown("---")

if st.button("ログアウト", use_container_width=True):
    logout()
    st.rerun()
