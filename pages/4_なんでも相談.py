import streamlit as st
from app_core import *

st.set_page_config(page_title="なんでも相談｜ShufuMate", layout="wide")

reload_user_data_if_needed()
load_settings_into_session()
sync_common_from_latest_diet_log()

st.header("💬 なんでも相談")
st.caption("食事・運動・外食・今日の困りごとを気軽に相談できます。")

st.info(
    "ShufuMateは、主婦の毎日に寄り添う参考アプリとして作成中のお試し版です。\n"
    "毎日の食事・運動・暮らしのヒントとしてご活用ください。\n"
    "体調や状況には個人差があるため、無理のない範囲で参考にし、不安が強い場合は専門家へご相談ください。"
)

gender, age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()

category = st.selectbox(
    "相談カテゴリ",
    ["食事相談", "運動相談", "外食相談", "体調・気分相談", "その他"],
    key="advice_category"
)

if category == "外食相談":
    prefecture = st.session_state.get("home_prefecture", "")
    default_area = st.session_state.get("home_area_custom", "").strip() or st.session_state.get("home_area", "")

    if prefecture or default_area:
        st.caption(f"初期設定の地域: {prefecture} {default_area}".strip())

    st.text_input(
        "相談エリア",
        value=default_area,
        placeholder="例：長命ヶ丘、吉成、仙台駅周辺",
        key="advice_area"
    )
else:
    st.session_state["advice_area"] = ""

st.text_area(
    "相談内容",
    placeholder="例：今日の夕飯どうしたらいい？\n例：運動前に何を食べたらいい？\n例：運動後、近所でどういう店を選べばいい？",
    key="quick_advice_question",
    height=140
)

if st.button("✨ 相談してみる", use_container_width=True):
    question = st.session_state.get("quick_advice_question", "").strip()
    area = st.session_state.get("advice_area", "").strip()

    if not question:
        st.warning("相談内容を入力してください。")
    else:
        client = get_openai_client()
        with st.spinner("相談内容を整理しています..."):
            result = ask_shufumate_advice(
                client=client,
                question=question,
                gender=gender,
                age=age,
                height_cm=height_cm,
                weight=weight,
                body_fat=body_fat,
                target_weight=target_weight,
                target_body_fat=target_body_fat,
                dosha_type=st.session_state.get("dosha_type", ""),
                fridge_items=st.session_state.get("fridge_items", ""),
                avoid_foods=st.session_state.get("avoid_foods", ""),
                favorite_meals=st.session_state.get("favorite_meals", ""),
                favorite_protein_onigiri=st.session_state.get("favorite_protein_onigiri", ""),
                favorite_misodama_soup=st.session_state.get("favorite_misodama_soup", ""),
                daily_flow=st.session_state.get("daily_flow", "普通"),
                workout_today=st.session_state.get("workout_today", False),
                body_goal=st.session_state.get("body_goal", "バランス"),
                lunch_style=st.session_state.get("lunch_style", "指定なし"),
                category=category,
                area=area,
                site_hint=st.session_state.get("site_hint", "syufuosusume.com")
            )

        st.session_state["quick_advice_result"] = result
        append_advice_log(category=category, area=area, question=question, answer=result)
        st.session_state["advice_logs"] = load_advice_logs()
        st.success("回答を作成しました。")

st.subheader("相談結果")

result_text = st.session_state.get("quick_advice_result", "")

if result_text:
    safe_result = (
        result_text
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
            margin-bottom:8px;
        ">
        {safe_result}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.caption("ここに回答が表示されます。")

st.info("※回答は参考用です。最終判断は、その日の体調・予定・空腹具合に合わせて無理なく調整してください。")

st.subheader("💡 相談例")
st.write("・今日の夕飯どうしたらいい？")
st.write("・運動前に何を食べたらいい？")
st.write("・運動後、長命ヶ丘でどういう店を選べばいい？")
st.write("・夕飯前にお腹が空きすぎた時どうする？")

st.divider()
st.subheader("🕘 相談履歴")

advice_logs = st.session_state.get("advice_logs", [])

if advice_logs:
    for log in advice_logs[:10]:
        area_label = log["地域"] if log["地域"] else "地域なし"

        q_text = (
            log["相談内容"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        a_text = (
            log["回答"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

        with st.expander(f"{log['日時']}｜{log['カテゴリ']}｜{area_label}"):
            st.markdown("**相談内容**")
            st.markdown(
                f"""
                <div style="
                    background:#f9fafb;
                    border:1px solid #e5e7eb;
                    border-radius:12px;
                    padding:14px;
                    color:#111827;
                    line-height:1.8;
                    margin-bottom:12px;
                ">
                {q_text}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("**回答**")
            st.markdown(
                f"""
                <div style="
                    background:#ffffff;
                    border:1px solid #d1d5db;
                    border-radius:12px;
                    padding:14px;
                    color:#111827;
                    line-height:1.9;
                ">
                {a_text}
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.caption("まだ相談履歴はありません。")
