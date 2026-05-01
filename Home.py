def generate_dynamic_advice(meal, base_advice, user_type="バランス重視", weather="晴れ"):

    month = datetime.now().month

    # 季節
    if month in [3,4,5]:
        season = "春"
    elif month in [6,7,8]:
        season = "夏"
    elif month in [9,10,11]:
        season = "秋"
    else:
        season = "冬"

    extra = []

    # 🌦 天気
    if weather == "雨":
        extra.append("今日は気圧の影響でゆるめでOK")
    elif weather == "暑い":
        extra.append("水分しっかりとりましょう")
    elif weather == "寒い":
        extra.append("体を温める食事がおすすめ")

    # 🌸 季節
    if season == "夏":
        extra.append("冷たいもの取りすぎ注意")
    elif season == "冬":
        extra.append("温かい食事で代謝UP")
    elif season == "春":
        extra.append("生活リズム崩れやすい時期です")
    elif season == "秋":
        extra.append("食べすぎ注意の季節です")

    # 👩‍🦰 タイプ
    if user_type == "ダイエット":
        extra.append("少しの意識で変わります☺️")
    elif user_type == "忙しい":
        extra.append("完璧じゃなくてOKです")
    elif user_type == "美容":
        extra.append("肌も食事で変わります✨")

    # 😆 ユーモア
    joke = random.choice([
        "今日はゆるくても合格です😂",
        "主婦はそれだけで十分すごいです",
        "完璧じゃなくてOK、それが続くコツ",
    ])

    # 🎯 合成
    if extra:
        return base_advice + "｜" + random.choice(extra) + "。" + joke
    else:
        return base_advice + "。" + joke
# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="💻",
    layout="centered",
)

# -----------------
# デザイン
# -----------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}

img {
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

.stButton>button {
    border-radius: 10px;
    height: 48px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# -----------------
# ログイン
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# データ取得
# -----------------
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

advice = get_today_advice(settings, latest_log)
exercise = get_today_exercise(settings, latest_log)

# -----------------
# 時間連動
# -----------------
now_hour = jst_now().hour

if now_hour < 10:
    main_meal = "朝"
elif now_hour < 15:
    main_meal = "昼"
else:
    main_meal = "夜"

# -----------------
# 週間固定
# -----------------
week_key = get_week_key()

if "weekly_plan" not in st.session_state or st.session_state.get("week_key") != week_key:
    st.session_state["weekly_plan"] = generate_weekly_plan(settings, latest_log)
    st.session_state["week_key"] = week_key

weekly_plan = st.session_state["weekly_plan"]

# -----------------
# 🟩 トップ
# -----------------
st.image("assets/home_icons/top/top_visual.png", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("### 🍽 食事も、暮らしも、ちょうどよく")

today = jst_now().strftime("%Y年%m月%d日（%a）")
st.caption(today)

# -----------------
# モード切替
# -----------------
if "mode" not in st.session_state:
    st.session_state["mode"] = "かんたん"

mode = st.radio(
    "表示モード",
    ["かんたん", "しっかり"],
    index=0 if st.session_state["mode"] == "かんたん" else 1,
    horizontal=True
)

st.session_state["mode"] = mode

st.markdown("---")

# =====================
# 🌱 かんたんモード
# =====================
if mode == "かんたん":

    st.subheader("🌿 今日のおすすめ")

    st.markdown(f"### ⭐ 今のおすすめ（{main_meal}）")

    user_type = st.session_state.get("user_type", "バランス重視")
    weather = "晴れ"

    advice_text = generate_dynamic_advice(
        main_meal,
        advice[main_meal],
        user_type,
        weather
    )

    st.write(advice_text)

    st.success(f"今は「{main_meal}」を整える時間です ☺️")
    
# =====================
# 🔧 しっかりモード（完成版）
# =====================
elif mode == "しっかり":

    st.subheader("🌿 今日のおすすめ（しっかり版）")

    user_type = st.session_state.get("user_type", "バランス重視")
    weather = "晴れ"  # ←あとでAPI化OK

    # -----------------
    # 🍽 食事
    # -----------------
    st.markdown("### 🌅 朝")
    st.write(generate_dynamic_advice("朝", advice["朝"], user_type, weather))

    st.markdown("### ☀️ 昼")
    st.write(generate_dynamic_advice("昼", advice["昼"], user_type, weather))

    st.markdown("### 🌙 夜")
    st.write(generate_dynamic_advice("夜", advice["夜"], user_type, weather))

    st.markdown("---")

    # -----------------
    # 🏃‍♀️ 運動
    # -----------------
    st.subheader("🏃‍♀️ 今日の運動")

    st.write(exercise["title"])
    st.write(exercise["body"])

    # 天気連動
    if weather == "雨":
        st.info("☔ 今日は室内ストレッチがおすすめです")
    elif weather == "暑い":
        st.info("🔥 無理せず軽め運動＋水分補給を")
    elif weather == "寒い":
        st.info("❄️ 体を温めるストレッチがおすすめ")

    st.markdown("---")

    # -----------------
    # 📦 まとめ
    # -----------------
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

                    st.session_state[key] = st.checkbox(
                        item,
                        value=st.session_state[key]
                    )

    # 🧘 補足アドバイス
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
# -----------------
# 共通ナビ
# -----------------
st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

with col4:
    if st.button("⚙️ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")
