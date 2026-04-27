import streamlit as st

from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    jst_today_str,
    jst_now,
    detect_meal_type_by_time,  # ← 追加
)

# -----------------
# 初期設定
# -----------------
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon="📷",
    layout="centered",
)

# -----------------
# 余白調整（見切れ対策）
# -----------------
st.markdown("""
<style>
.block-container {
    padding-top: 3rem !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------
# ログイン
# -----------------
require_login()
user_id = get_user_id()

# -----------------
# タイトル
# -----------------
st.title("📷 写真で記録")

# -----------------
# カメラ
# -----------------
img = st.camera_input("食事の写真を撮る")

# -----------------
# 自動判定（ここが今回のメイン）
# -----------------
auto_meal = detect_meal_type_by_time(jst_now())

st.markdown(f"👉 自動判定：**{auto_meal}ごはん**")

# -----------------
# 手動変更（超重要）
# -----------------
meal_type = st.radio(
    "食事区分",
    ["朝", "昼", "夜", "間食"],
    index=["朝", "昼", "夜", "間食"].index(auto_meal),
    horizontal=True
)

# -----------------
# メモ入力
# -----------------
food_text = st.text_area(
    "食事内容（簡単でOK）",
    placeholder="例：鮭、卵焼き、サラダ",
    height=100
)

# -----------------
# 保存
# -----------------
if st.button("記録する", use_container_width=True):

    if not img:
        st.warning("写真を撮ってください")
    else:
        save_diet_log(user_id, {
            "log_date": jst_today_str(),
            "meal_memo": f"{meal_type}：{food_text}",
            "created_at": jst_now().isoformat(),
        })

        st.success(f"{meal_type}ごはんを記録しました！")
        st.balloons()
