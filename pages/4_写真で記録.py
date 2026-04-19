import streamlit as st
from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    jst_today_str,
    jst_today,
)

require_login()

st.title("📷 写真で記録")
st.caption("食前チェックや食後記録に使う写真をまとめるページです。")

user_id = get_user_id()

tab1, tab2 = st.tabs(["🍽 食事写真", "⚖ 体重計写真"])

# -----------------------------
# 食事写真
# -----------------------------
with tab1:
    st.subheader("食事写真で記録")
    st.caption("まずは写真を残して、必要なら内容を補足する形にします。")

    meal_type = st.radio(
        "食事区分",
        ["朝", "昼", "夜", "間食"],
        horizontal=True,
    )

    meal_camera = st.camera_input("食事を撮る", key="meal_camera_input")

    meal_upload = st.file_uploader(
        "食事写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="meal_photo_upload",
    )

    meal_note = st.text_area(
        "補足メモ（任意）",
        placeholder="例：鮭定食、お弁当、パスタなど",
        height=100,
    )

    if meal_camera is not None:
        st.image(meal_camera, caption="撮影した写真", use_container_width=True)

    if meal_upload is not None:
        st.image(meal_upload, caption="アップロードした写真", use_container_width=True)

    if st.button("この食事を仮記録する", use_container_width=True, key="save_meal_photo_log"):
        meal_memo = f"{meal_type}: 写真で記録"
        if meal_note.strip():
            meal_memo += f"\n補足: {meal_note.strip()}"

        save_data = {
            "log_date": jst_today_str(),
            "weight": 0,
            "body_fat": 0,
            "meal_memo": meal_memo,
            "exercise_memo": "",
            "condition_note": "",
            "mood_note": "",
            "today_conditions": [],
        }

        try:
            save_diet_log(user_id, save_data)
            st.success("食事写真の記録を保存しました")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")

# -----------------------------
# 体重計写真
# -----------------------------
with tab2:
    st.subheader("体重計写真で記録")
    st.caption("まずは写真保存と手入力補助から始めます。")

    scale_camera = st.camera_input("体重計を撮る", key="scale_camera_input")

    scale_upload = st.file_uploader(
        "体重計写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="scale_photo_upload",
    )

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(
            "体重(kg)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=0.1,
            format="%.1f",
        )
    with col2:
        body_fat = st.number_input(
            "体脂肪(%)",
            min_value=0.0,
            max_value=70.0,
            value=0.0,
            step=0.1,
            format="%.1f",
        )

    scale_note = st.text_area(
        "補足メモ（任意）",
        placeholder="例：朝一、入浴後など",
        height=100,
    )

    if scale_camera is not None:
        st.image(scale_camera, caption="撮影した体重計写真", use_container_width=True)

    if scale_upload is not None:
        st.image(scale_upload, caption="アップロードした体重計写真", use_container_width=True)

    if st.button("この数値で今日の記録を保存", use_container_width=True, key="save_scale_log"):
        save_data = {
            "log_date": jst_today_str(),
            "weight": float(weight),
            "body_fat": float(body_fat),
            "meal_memo": "",
            "exercise_memo": "",
            "condition_note": scale_note.strip(),
            "mood_note": "",
            "today_conditions": [],
        }

        try:
            save_diet_log(user_id, save_data)
            st.success("体重・体脂肪の記録を保存しました")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")

st.divider()
st.caption(f"記録日: {jst_today().strftime('%Y/%m/%d')}")
