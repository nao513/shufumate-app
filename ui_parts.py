import streamlit as st
from app_core import generate_shopping_list_from_week

def get_dynamic_exercise(weather, hour):
    
    # ⏰ 時間
    if hour < 10:
        base = "朝の軽いストレッチ（5分）"
    elif hour < 15:
        base = "軽めのヨガ or 体をほぐす運動"
    else:
        base = "リラックスヨガ or ストレッチ"

    # 🌦 天気
    if weather == "雨":
        return "☔ 室内ストレッチ（5〜10分）＋深呼吸"
    elif weather == "暑い":
        return "🔥 無理せず軽めストレッチ＋水分補給"
    elif weather == "寒い":
        return "❄️ 体を温めるヨガ（肩回し・股関節）"
    else:
        return f"🌿 {base}"

# ======================
# 🌿 ヘッダー
# ======================
def render_header():
    st.image("assets/home_icons/top/top_visual.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🍽 食事も、暮らしも、ちょうどよく")


# ======================
# 🌱 かんたんモード
# ======================
def render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather):

    st.subheader("🌿 今日のおすすめ")

    st.markdown(f"### ⭐ 今のおすすめ（{main_meal}）")

    st.write(
        generate_dynamic_advice(
            main_meal,
            advice[main_meal],
            user_type,
            weather
        )
    )

    st.success(f"今は「{main_meal}」を整える時間です ☺️")

    st.markdown("---")

    st.subheader("🚀 すぐやる")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📸 写真で記録", use_container_width=True):
            st.switch_page("pages/photo.py")

    with col2:
        if st.button("📝 記録する", use_container_width=True):
            st.switch_page("pages/log.py")

    st.markdown("---")

    st.subheader("🏃‍♀️ 今日の運動（軽め）")

    from datetime import datetime

    hour = datetime.now().hour

    st.write(get_dynamic_exercise(weather, hour))


# ======================
# 🔧 しっかりモード
# ======================
def render_full_mode(..., weather, state):

    st.subheader("🌿 今日のおすすめ（しっかり版）")

    # 🍽 食事
    st.markdown("### 🌅 朝")
    st.write(generate_dynamic_advice("朝", advice["朝"], user_type, weather))

    st.markdown("### ☀️ 昼")
    st.write(generate_dynamic_advice("昼", advice["昼"], user_type, weather))

    st.markdown("### 🌙 夜")
    st.write(generate_dynamic_advice("夜", advice["夜"], user_type, weather))

    st.markdown("---")

    # 🏃‍♀️ 運動
    st.subheader("🏃‍♀️ 今日の運動")

    from datetime import datetime

    hour = datetime.now().hour

    plan = get_personal_plan(weather, hour, state)

    st.write(plan)

    if weather == "雨":
        st.info("☔ 今日は室内ストレッチがおすすめ")
    elif weather == "暑い":
        st.info("🔥 無理せず軽め＋水分補給")
    elif weather == "寒い":
        st.info("❄️ 体を温めるストレッチ")
    elif weather == "普通":
        st.info("🌿 軽く体を動かすのに良い日です")

    if weather == "雨":
        st.info("☔ 室内ストレッチがおすすめ")
    elif weather == "暑い":
        st.info("🔥 軽め運動＋水分補給")
    elif weather == "寒い":
        st.info("❄️ 体を温めるストレッチ")

    st.markdown("---")

    # 📦 まとめ
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

    st.markdown("---")

    st.subheader("💡 今日のひとこと")

    st.info(
        generate_dynamic_advice(
            "夜",
            "今日は少し整えるだけでもOKな日です",
            user_type,
            weather
        )
    )
