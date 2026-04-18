import streamlit as st
from app_core import *

st.set_page_config(page_title="アーユルヴェーダ｜ShufuMate", layout="wide")

reload_user_data_if_needed()
load_settings_into_session()

if "dosha_scores" not in st.session_state:
    st.session_state["dosha_scores"] = {"ヴァータ": 0, "ピッタ": 0, "カパ": 0}

st.header("🌿 アーユルヴェーダ")
st.caption("体質傾向と今の状態をチェックして、食事や過ごし方のヒントに活かせます。")

st.info(
    "体質チェックは、自分の傾向を知るための目安として使えます。\n"
    "結果は初期設定にも反映され、献立・相談・記録ページでも活かせます。"
)

st.subheader("🌿 体質チェック")
st.write("8項目から体質傾向をチェックします。チェックが多い体質が今の自分に近いタイプです。")

q1 = st.radio("体型", [
    "痩せ型で食べても太らない",
    "中肉中背で平均的",
    "子供の頃から太りやすい"
], key="ay_q1")

q2 = st.radio("肌", [
    "乾燥している",
    "オイリーでシミやニキビができやすい",
    "色白でもっちりしてる"
], key="ay_q2")

q3 = st.radio("髪", [
    "硬く乾燥している",
    "柔らかくて細い",
    "黒くて多い"
], key="ay_q3")

q4 = st.radio("発汗", [
    "あまりかかない",
    "汗っかき",
    "普通"
], key="ay_q4")

q5 = st.radio("体温", [
    "手足が冷たい",
    "体が熱い",
    "全体が冷たい"
], key="ay_q5")

q6 = st.radio("食欲", [
    "ムラがある・不規則",
    "食欲旺盛・食事を抜くとイライラする",
    "安定していて食べるのが好き"
], key="ay_q6")

q7 = st.radio("排便", [
    "便秘気味・硬便",
    "下痢気味・軟便",
    "中程度の硬さ・時間を要する"
], key="ay_q7")

q8 = st.radio("睡眠", [
    "眠りが浅い・途中で起きやすい",
    "普通",
    "よく眠る・居眠りが多い"
], key="ay_q8")

st.subheader("🍃 今の状態チェック")
sweet_craving = st.checkbox("甘いものが欲しい", key="state_sweet")
salty_craving = st.checkbox("しょっぱいものが欲しい", key="state_salty")
fatigue = st.checkbox("疲れやすい", key="state_fatigue")
irritable = st.checkbox("イライラしやすい", key="state_irritable")
sleepy_after_meal = st.checkbox("食後に眠くなりやすい", key="state_sleepy")
swelling = st.checkbox("むくみやすい", key="state_swelling")
coldness = st.checkbox("冷えやすい", key="state_cold")
constipation_now = st.checkbox("便秘気味", key="state_constipation")
dry_skin = st.checkbox("乾燥しやすい", key="state_dry")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌿 体質をチェック", use_container_width=True):
        answers = {
            "体型": q1,
            "肌": q2,
            "髪": q3,
            "発汗": q4,
            "体温": q5,
            "食欲": q6,
            "排便": q7,
            "睡眠": q8,
        }

        result_type, scores = diagnose_dosha_advanced(answers)
        advice = get_ayurveda_advice_advanced(result_type)
        foods = get_ayurveda_foods(result_type)

        st.session_state["dosha_type"] = result_type
        st.session_state["dosha_scores"] = scores
        save_user_settings()

        st.success(f"あなたの体質傾向は **{result_type}** です。初期設定にも反映しました。")

        c1m, c2m, c3m = st.columns(3)
        c1m.metric("ヴァータ", scores["ヴァータ"])
        c2m.metric("ピッタ", scores["ピッタ"])
        c3m.metric("カパ", scores["カパ"])

        st.subheader("🌿 体質の特徴")
        st.write(advice.get("特徴", ""))

        st.subheader("🍽 食事アドバイス")
        st.write(advice.get("食事", ""))

        st.subheader("🛀 過ごし方")
        st.write(advice.get("生活", ""))

        st.subheader("🏃 おすすめ運動")
        st.write(advice.get("運動", ""))

        st.subheader("⚖ ダイエットのコツ")
        st.write(advice.get("ダイエット", ""))

        st.subheader("🥕 おすすめ食材")
        st.write("・" + "\n・".join(foods) if foods else "おすすめ食材は未設定です")

        if st.session_state.get("fridge_items", ""):
            fridge_text = st.session_state["fridge_items"]
            match_foods = [f for f in foods if f in fridge_text]
            if match_foods:
                st.subheader("🧺 冷蔵庫にある相性食材")
                st.write("・" + "\n・".join(match_foods))
            else:
                st.subheader("🧺 冷蔵庫との相性")
                st.write("今の冷蔵庫食材との一致は少なめです。買い足し候補としておすすめ食材を活用できます。")

with col2:
    if st.button("🪷 今の状態をみる", use_container_width=True):
        selected_states = []

        if sweet_craving:
            selected_states.append("甘いものが欲しい")
        if salty_craving:
            selected_states.append("しょっぱいものが欲しい")
        if fatigue:
            selected_states.append("疲れやすい")
        if irritable:
            selected_states.append("イライラしやすい")
        if sleepy_after_meal:
            selected_states.append("食後に眠くなりやすい")
        if swelling:
            selected_states.append("むくみやすい")
        if coldness:
            selected_states.append("冷えやすい")
        if constipation_now:
            selected_states.append("便秘気味")
        if dry_skin:
            selected_states.append("乾燥しやすい")

        st.session_state["current_state_checks"] = selected_states
        save_user_settings()

        current_state_text = get_current_state_advice(
            sweet_craving,
            salty_craving,
            fatigue,
            irritable,
            sleepy_after_meal,
            swelling,
            coldness,
            constipation_now,
            dry_skin
        )

        st.success("今の状態を初期設定にも反映しました。")
        st.subheader("📝 今の乱れチェック")
        st.write(current_state_text)

with col3:
    if st.button("↺ 体質診断をリセット", use_container_width=True):
        st.session_state["dosha_type"] = ""
        st.session_state["dosha_scores"] = {"ヴァータ": 0, "ピッタ": 0, "カパ": 0}
        st.session_state["current_state_checks"] = []
        save_user_settings()
        st.success("体質診断と今の状態チェックをリセットしました。")

