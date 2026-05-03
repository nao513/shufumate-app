import streamlit as st
from app_core import *

# -----------------
# 初期設定
# -----------------
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon="📷",
    layout="centered",
)

# -----------------
# 余白調整
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
st.caption("食事写真とメモをかんたんに残します")

# -----------------
# カメラ
# -----------------
img = st.camera_input("食事の写真を撮る")

if img is not None:
    st.image(img, caption="撮影した写真", use_container_width=True)

# -----------------
# 自動判定
# -----------------
auto_meal = detect_meal_type_by_time(jst_now())

st.markdown(f"👉 自動判定：**{auto_meal}ごはん**")

# -----------------
# 手動変更
# -----------------
meal_options = ["朝", "昼", "夜", "間食"]

meal_type = st.radio(
    "食事区分",
    meal_options,
    index=meal_options.index(auto_meal) if auto_meal in meal_options else 0,
    horizontal=True
)

# -----------------
# メモ入力
# -----------------
food_text = st.text_area(
    "食事内容（簡単でOK）",
    placeholder="例：鮭おにぎり、卵焼き、サラダ、味噌汁",
    height=110
)

# -----------------
# 保存
# -----------------
st.markdown("---")

if st.button("✅ 記録する", use_container_width=True):

    if img is None:
        st.warning("写真を撮ってください")

    else:
        save_photo_meal_log(
            user_id=user_id,
            meal_type=meal_type,
            food_text=food_text,
            image_file=img,
        )

        st.success(f"{meal_type}ごはんを記録しました！")
        st.balloons()

# -----------------
# 最新記録
# -----------------
st.markdown("---")

with st.expander("📌 最新の写真記録を確認する"):
    photo_logs = load_photo_logs(user_id)

    if photo_logs:
        latest = photo_logs[-1]

        st.write(f"日付：{latest.get('log_date', '')}")
        st.write(f"食事区分：{latest.get('meal_type', '')}")
        st.write(f"内容：{latest.get('food_text', '')}")

        image_bytes = latest.get("image_bytes")

        if image_bytes:
            st.image(image_bytes, caption="最新の写真", use_container_width=True)

    else:
        st.info("まだ写真記録がありません")
