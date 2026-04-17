import streamlit as st
from datetime import datetime
from app_core import *

st.set_page_config(page_title="献立・運動プラン｜ShufuMate", layout="wide")

reload_user_data_if_needed()
load_settings_into_session()
sync_common_from_latest_diet_log()

st.header("🍽 献立・運動プラン")
st.caption("その日の状態や目標に合わせて、1日のプランを作成できます。")

st.info(
    "食事スタイルや冷蔵庫の食材、日々の流れに合わせて、"
    "続けやすい献立と運動のヒントを提案します。"
)

gender, age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()

plan_date = st.date_input("プラン日", value=datetime.today().date(), key="plan_date")

meal_style = st.radio(
    "食事スタイル",
    ["和食中心", "バランス", "おしゃれカフェ風", "タンパク質おにぎり＆味噌玉味噌汁"],
    horizontal=True,
    key="meal_style"
)
ease_level = st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
staple_preference = st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")

plan_type = st.radio("プランタイプ", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
lunch_style = st.selectbox("平日のお昼スタイル", ["指定なし", "お弁当", "コンビニ", "おすすめ定番", "外食", "自宅"], key="lunch_style")
real_mode = st.checkbox("主婦リアル提案モード", key="real_mode")
daily_flow = st.selectbox("今日の食事の流れ", ["普通", "朝しっかり・昼軽め", "食べすぎた", "あまり食べてない"], key="daily_flow")
workout_today = st.checkbox("今日は運動した / する", key="workout_today")
body_goal = st.selectbox("目的", ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"], key="body_goal")

st.text_area("冷蔵庫の食材", key="fridge_items")
st.text_area("避けたい食べ物", key="avoid_foods")
st.text_area("定番・好きな食事", key="favorite_meals")

if st.button("🪄 今日のプランを作る", use_container_width=True):
    client = get_openai_client()
    with st.spinner("プランを作成中..."):
        result = create_plan_for_date(
            client=client,
            date_str=str(plan_date),
            gender=gender,
            age=age,
            height_cm=height_cm,
            weight=weight,
            body_fat=body_fat,
            target_weight=target_weight,
            target_body_fat=target_body_fat,
            dosha_type=st.session_state.get("dosha_type", ""),
            meal_style=meal_style,
            ease_level=ease_level,
            staple_preference=staple_preference,
            fridge_items=st.session_state.get("fridge_items", ""),
            avoid_foods=st.session_state.get("avoid_foods", ""),
            favorite_meals=st.session_state.get("favorite_meals", ""),
            favorite_protein_onigiri=st.session_state.get("favorite_protein_onigiri", ""),
            favorite_misodama_soup=st.session_state.get("favorite_misodama_soup", ""),
            plan_type=plan_type,
            lunch_style=lunch_style,
            real_mode=real_mode,
            daily_flow=daily_flow,
            workout_today=workout_today,
            body_goal=body_goal
        )

    st.session_state["today_plan_text"] = result
    st.session_state["today_plan_date"] = str(plan_date)
    st.success("プランを作成しました。")

st.subheader("📄 プラン結果")

plan_text = st.session_state.get("today_plan_text", "")

if plan_text:
    safe_text = (
        plan_text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )
    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1px solid #d1d5db;
            border-radius:14px;
            padding:18px;
            color:#111827;
            font-size:16px;
            line-height:1.9;
            box-shadow:0 1px 2px rgba(0,0,0,0.04);
        ">
        {safe_text}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.caption("ここにプラン結果が表示されます。")
