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

    st.write("・軽いストレッチ（3分）")
    st.write("・深呼吸＋肩回し")


# ======================
# 🔧 しっかりモード
# ======================
def render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather):

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

    st.write(exercise["title"])
    st.write(exercise["body"])

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
