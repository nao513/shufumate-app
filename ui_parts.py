import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------
# 🏠 ヘッダー
# -----------------
def render_header():
    st.title("🏠 ShufuMate")
    st.caption("食事も、暮らしも、ちょうどよく")

# -----------------
# 🌿 かんたんモード
# -----------------
def render_simple_mode(main_meal, advice, generate_dynamic_advice, user_type, weather, state):

    st.subheader("🌿 今日のおすすめ")

    # 安全に文字列として扱う
    try:
        text = generate_dynamic_advice(main_meal, advice, user_type, weather)
    except:
        text = advice

    st.markdown(f"### ⭐ 今のおすすめ（{main_meal}）")
    st.write(text)

    st.success(f"今は「{main_meal}」を整える時間です☺️")

    st.markdown("---")

    st.subheader("🚀 すぐやる")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📷 写真で記録"):
            st.switch_page("写真で記録")

    with col2:
        if st.button("📝 記録する"):
            st.switch_page("記録する")

# -----------------
# 💪 しっかりモード
# -----------------
def render_full_mode(advice, exercise, weekly_plan, generate_dynamic_advice, user_type, weather, state):

    st.subheader("💪 今日のプラン")

    st.markdown("### 🍽 食事")
    st.write(advice)

    st.markdown("### 🏃‍♀️ 運動")
    st.write(exercise)

    st.markdown("---")

    # -----------------
    # 🛒 買い物リスト
    # -----------------
    with st.expander("🛒 買い物リスト"):

        from app_core import generate_shopping_list_from_week
        shopping = generate_shopping_list_from_week(weekly_plan)

        render_shopping_list(shopping)

# -----------------
# 🛒 買い物リスト（完全安定版）
# -----------------
def render_shopping_list(shopping):

    st.subheader("🛒 買い物リスト")

    today = datetime.now().strftime("%Y-%m-%d")

    # -----------------
    # 日付リセット
    # -----------------
    if "shopping_date" not in st.session_state:
        st.session_state["shopping_date"] = today

    if st.session_state["shopping_date"] != today:
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("shopping_")]
        for k in keys_to_delete:
            del st.session_state[k]

        st.session_state["shopping_date"] = today

    checked_items = []

    # -----------------
    # 表示＆チェック
    # -----------------
    for category, items in shopping.items():
        if items:
            st.markdown(f"**{category}**")

            for item in items:
                key = f"shopping_{category}_{item}"

                if key not in st.session_state:
                    st.session_state[key] = False

                checked = st.checkbox(item, key=key)

                if checked:
                    checked_items.append((category, item))

    st.markdown("---")

    # -----------------
    # 📥 ダウンロード
    # -----------------
    if checked_items:
        df_download = pd.DataFrame([
            {"カテゴリ": c, "商品": i}
            for c, i in checked_items
        ])

        csv = df_download.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="📥 チェック済みをダウンロード",
            data=csv,
            file_name=f"shopping_list_{today}.csv",
            mime="text/csv"
        )
    else:
        st.info("チェックした商品がありません")

    # -----------------
    # 📱 LINE共有
    # -----------------
    if checked_items:

        text = "🛒 買い物リスト\n\n"

        current_category = ""
        for c, i in checked_items:
            if c != current_category:
                text += f"\n【{c}】\n"
                current_category = c
            text += f"・{i}\n"

        st.text_area("📱 LINEで送る（コピー用）", text, height=200)

    # -----------------
    # 🧹 リセット（完全安全版）
    # -----------------
    if st.button("🧹 買い物完了（リストをリセット）"):

        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("shopping_")]

        for k in keys_to_delete:
            del st.session_state[k]

        st.success("リストをリセットしました✨")

        # Streamlitの安全再描画
        st.experimental_rerun()

    st.markdown("---")
