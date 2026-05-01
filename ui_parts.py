import streamlit as st
import random
from datetime import datetime
from app_core import generate_shopping_list_from_week

# ======================
# 🌿 ヘッダー
# ======================
def render_header():
    st.image("assets/home_icons/top/top_visual.png", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🍽 食事も、暮らしも、ちょうどよく")
    
    today = jst_now().strftime("%Y年%m月%d日（%a）")
    st.caption(today)


# ======================
# 🧠 状態連動運動
# ======================
def get_personal_plan(weather, hour, state):

    if hour < 10:
        base = "朝ストレッチ（軽め）"
    elif hour < 15:
        base = "軽い運動（ヨガ・ウォーキング）"
    else:
        base = "リラックスストレッチ"

    if state.get("疲れ"):
        return "今日は無理せずストレッチ＋深呼吸だけでOK"

    if state.get("こり"):
        return "肩・首・股関節をほぐすストレッチ"

    if state.get("冷え"):
        return "体を温めるストレッチ＋白湯"

    if state.get("食べすぎ"):
        return "軽めウォーキング＋消化を助ける動き"

    if weather == "雨":
        return "☔ 室内ストレッチ（5分）"
    elif weather == "暑い":
        return "🔥 軽めストレッチ＋水分補給"
    elif weather == "寒い":
        return "❄️ 体を温めるヨガ"

    return base


# ======================
# 🌱 かんたんモード
# ======================
def render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, state):

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

    st.subheader("🏃‍♀️ 今日の運動")

    hour = datetime.now().hour
    st.write(get_personal_plan(weather, hour, state))


# ======================
# 🔧 しっかりモード
# ======================
def render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, state):

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

    hour = datetime.now().hour
    st.write(get_personal_plan(weather, hour, state))

    st.markdown("---")

    # 📦 まとめ
    st.subheader("📦 まとめ")

    # 🗓 週間献立
    with st.expander("🗓 週間献立"):
        for day, meal in weekly_plan.items():
            st.write(f"{day}：{meal}")

    # 🛒 買い物リスト
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

    # 💬 今日のひとこと
    st.markdown("---")
    st.subheader("💡 今日のひとこと")

    messages = [
        "今日はゆるめでも十分整います☺️",
        "完璧じゃなくてOK、続けることが大事です",
        "少し整えるだけでも体はちゃんと応えてくれます",
        "主婦はそれだけで毎日すごいです",
        "今日は自分を甘やかす日でもOKです🌿"
    ]

    # 状態優先
    if state.get("疲れ"):
        msg = "今日は休むのも大事な選択です"
    elif state.get("こり"):
        msg = "少しほぐすだけで体は軽くなります"
    elif state.get("冷え"):
        msg = "体を温める意識でかなり変わります"
    else:
        msg = random.choice(messages)

    st.info(msg)
