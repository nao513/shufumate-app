import streamlit as st
from app_core import generate_shopping_list_from_week

# ======================
# 🌿 ヘッダー
# ======================
def render_header():
    st.image("assets/home_icons/top/top_visual.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🍽 食事も、暮らしも、ちょうどよく")


# ======================
# 🧠 状態連動運動
# ======================
def get_personal_plan(weather, hour, state):

    if hour < 10:
        base = "朝ストレッチ"
    elif hour < 15:
        base = "軽い運動"
    else:
        base = "リラックス"

    if state.get("疲れ"):
        return "今日は無理せずストレッチ＋深呼吸"

    if state.get("こり"):
        return "肩・首・股関節をほぐすストレッチ"

    if state.get("冷え"):
        return "体を温めるストレッチ＋白湯"

    if state.get("食べすぎ"):
        return "軽めウォーキング"

    if weather == "雨":
        return "室内ストレッチ"
    elif weather == "暑い":
        return "軽めストレッチ＋水分補給"
    elif weather == "寒い":
        return "温めるヨガ"

    return base


# ======================
# 🌱 かんたんモード
# ======================
def render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, state):

    st.subheader("🌿 今日のおすすめ")

    st.markdown(f"### ⭐ 今のおすすめ（{main_meal}）")

    st.write(generate_dynamic_advice(main_meal, advice[main_meal], user_type, weather))

    st.success(f"今は「{main_meal}」を整える時間です ☺️")

    st.markdown("---")

    st.subheader("🏃‍♀️ 今日の運動")

    from datetime import datetime
    hour = datetime.now().hour

    st.write(get_personal_plan(weather, hour, state))


# ======================
# 🔧 しっかりモード
# ======================
def render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, state):

    st.subheader("🌿 今日のおすすめ（しっかり版）")

    st.markdown("### 🌅 朝")
    st.write(generate_dynamic_advice("朝", advice["朝"], user_type, weather))

    st.markdown("### ☀️ 昼")
    st.write(generate_dynamic_advice("昼", advice["昼"], user_type, weather))

    st.markdown("### 🌙 夜")
    st.write(generate_dynamic_advice("夜", advice["夜"], user_type, weather))

    st.markdown("---")

    st.subheader("🏃‍♀️ 今日の運動")

    from datetime import datetime
    hour = datetime.now().hour

    st.write(get_personal_plan(weather, hour, state))

    st.markdown("---")

    st.subheader("📦 まとめ")

    with st.expander("🗓 週間献立"):
        for day, meal in weekly_plan.items():
            st.write(f"{day}：{meal}")

    with st.expander("🛒 買い物リスト"):
        shopping = generate_shopping_list_from_week(weekly_plan)

        for category, items in shopping.items():
            if items:
                st.markdown(f"**{category}**")
                for item in items:
                    key = f"{category}_{item}"
                    if key not in st.session_state:
                        st.session_state[key] = False

                    st.session_state[key] = st.checkbox(item, value=st.session_state[key])
