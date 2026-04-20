import streamlit as st
from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    jst_today_str,
    jst_today,
    load_user_settings,
    load_latest_log,
    build_food_evaluation_from_text,
)

require_login()

st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon="📷",
    layout="centered",
)

st.title("📷 写真で記録")
st.caption("写真を使って、食事の評価や記録をかんたんに残します。")

user_id = get_user_id()
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)

tab1, tab2, tab3 = st.tabs(
    ["🍽 この食事を評価", "📝 食べたものを記録", "⚖ 体重計を記録"]
)


def preset_text_by_type(meal_type: str, meal_text: str) -> tuple[str, str, str, str]:
    breakfast = ""
    lunch = ""
    dinner = ""
    snack = ""

    if meal_type == "朝ごはん":
        breakfast = meal_text
    elif meal_type == "昼ごはん":
        lunch = meal_text
    elif meal_type == "夜ごはん":
        dinner = meal_text
    elif meal_type == "間食":
        snack = meal_text

    return breakfast, lunch, dinner, snack


# =========================================================
# 1. この食事を評価
# =========================================================
with tab1:
    st.subheader("この食事を評価")
    st.caption("写真と内容の補足から、食事を評価します。")

    eval_meal_type = st.radio(
        "食事区分",
        ["朝ごはん", "昼ごはん", "夜ごはん", "間食"],
        horizontal=True,
        key="eval_meal_type",
    )

    eval_camera = st.camera_input("食事の写真を撮る", key="eval_camera_input")
    eval_upload = st.file_uploader(
        "食事写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="eval_photo_upload",
    )

    selected_eval_image = eval_camera if eval_camera is not None else eval_upload

    if selected_eval_image is not None:
        st.image(selected_eval_image, caption="評価したい食事", use_container_width=True)

    st.markdown("### 写真に写っている内容")
    st.caption("写真だけでは伝わりにくいものを少し足すと、評価が安定します。")

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:
        st.markdown("**よくある食材例**")
        st.caption("おにぎり / ゆで卵 / 味噌汁 / 納豆 / 豆乳 / 鮭 / しらす / サラダ")

    with quick_col2:
        st.markdown("**補足すると良いこと**")
        st.caption("乾燥野菜入り / きのこ入り / 外食 / ヨガ前 / 軽め / 運動後 など")

    eval_meal_text = st.text_area(
        "この食事の内容",
        placeholder="例：しらすおにぎり、ゆで卵、きのことわかめの味噌汁、ブルーベリー",
        height=120,
        key="eval_meal_text",
    )

    with st.expander("朝・昼・夜・間食で整理して入力したい場合"):
        default_breakfast, default_lunch, default_dinner, default_snack = preset_text_by_type(
            eval_meal_type,
            eval_meal_text,
        )

        eval_breakfast = st.text_area(
            "朝",
            value=default_breakfast,
            height=70,
            key="eval_breakfast",
        )
        eval_lunch = st.text_area(
            "昼",
            value=default_lunch,
            height=70,
            key="eval_lunch",
        )
        eval_dinner = st.text_area(
            "夜",
            value=default_dinner,
            height=70,
            key="eval_dinner",
        )
        eval_snack = st.text_area(
            "間食",
            value=default_snack,
            height=70,
            key="eval_snack",
        )

    eval_note = st.text_area(
        "補足メモ（任意）",
        placeholder="例：今日はむくみあり / 外食予定 / ヨガ前 / 軽めにしたい / 朝に果物追加 など",
        height=90,
        key="eval_note",
    )

    if st.button("この食事を評価する", use_container_width=True, key="run_meal_eval"):
        sections_text = "\n".join(
            [
                f"朝: {st.session_state.get('eval_breakfast', '').strip()}",
                f"昼: {st.session_state.get('eval_lunch', '').strip()}",
                f"夜: {st.session_state.get('eval_dinner', '').strip()}",
                f"間食: {st.session_state.get('eval_snack', '').strip()}",
            ]
        )

        base_text = eval_meal_text.strip()
        merged_note = eval_note.strip()

        has_section_input = sections_text.replace("朝: ", "").replace("昼: ", "").replace("夜: ", "").replace("間食: ", "").strip()

        if has_section_input:
            if merged_note:
                merged_note += "\n"
            merged_note += "食事の流れメモ:\n" + sections_text

        st.session_state["meal_eval_result"] = build_food_evaluation_from_text(
            meal_type=eval_meal_type,
            meal_text=base_text,
            settings=settings,
            latest_log=latest_log,
            note=merged_note,
        )

    if "meal_eval_result" in st.session_state:
        result = st.session_state["meal_eval_result"]
        st.markdown("### 評価結果")
        st.info(result["title"])
        st.markdown(result["body"].replace("\n", "  \n"))


# =========================================================
# 2. 食べたものを記録
# =========================================================
with tab2:
    st.subheader("食べたものを記録")
    st.caption("食後の写真やメモを使って、食事記録をかんたんに残します。")

    log_camera = st.camera_input("食べたものを撮る", key="log_camera_input")
    log_upload = st.file_uploader(
        "食事写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="log_photo_upload",
    )

    selected_log_image = log_camera if log_camera is not None else log_upload

    if selected_log_image is not None:
        st.image(selected_log_image, caption="記録する食事写真", use_container_width=True)

    st.markdown("### 食べたもの")
    breakfast_text = st.text_area(
        "朝",
        placeholder="例：納豆ごはん、味噌汁、ゆで卵",
        height=80,
        key="photo_log_breakfast",
    )
    lunch_text = st.text_area(
        "昼",
        placeholder="例：鮭おにぎり、味噌汁、サラダチキン",
        height=80,
        key="photo_log_lunch",
    )
    dinner_text = st.text_area(
        "夜",
        placeholder="例：焼き魚、味噌汁、サラダ、ごはん少なめ",
        height=80,
        key="photo_log_dinner",
    )
    snack_text = st.text_area(
        "間食",
        placeholder="例：ヨーグルト、チョコ2個、なし",
        height=80,
        key="photo_log_snack",
    )

    log_note = st.text_area(
        "補足メモ（任意）",
        placeholder="例：外食 / お弁当 / 軽め / 運動前後 / 写真あり など",
        height=90,
        key="photo_log_note",
    )

    st.caption("食べる時間の目安：朝は起きてから2時間以内、間食は夕方まで、夜は寝る直前を避けると整えやすいです。")

    if st.button("食べたものを記録する", use_container_width=True, key="save_photo_meal_log"):
        lines = [
            f"朝: {breakfast_text.strip()}",
            f"昼: {lunch_text.strip()}",
            f"夜: {dinner_text.strip()}",
            f"間食: {snack_text.strip()}",
        ]

        if log_note.strip():
            lines.append("")
            lines.append(f"補足: {log_note.strip()}")

        meal_memo = "\n".join(lines)

        save_data = {
            "log_date": jst_today_str(),
            "weight": 0.0,
            "body_fat": 0.0,
            "meal_memo": meal_memo,
            "exercise_memo": "",
            "condition_note": "",
            "mood_note": "",
            "today_conditions": [],
        }

        try:
            save_diet_log(user_id, save_data)
            st.success("食事記録を保存しました")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")


# =========================================================
# 3. 体重計を記録
# =========================================================
with tab3:
    st.subheader("体重計を記録")
    st.caption("体重計の写真と数値を使って、今日の記録に残します。")

    scale_camera = st.camera_input("体重計を撮る", key="scale_camera_input")
    scale_upload = st.file_uploader(
        "体重計写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="scale_photo_upload",
    )

    selected_scale_image = scale_camera if scale_camera is not None else scale_upload

    if selected_scale_image is not None:
        st.image(selected_scale_image, caption="体重計写真", use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        weight = st.number_input(
            "体重(kg)",
            min_value=0.0,
            max_value=200.0,
            value=0.0,
            step=0.1,
            format="%.1f",
            key="scale_weight_input",
        )

    with col2:
        body_fat = st.number_input(
            "体脂肪(%)",
            min_value=0.0,
            max_value=70.0,
            value=0.0,
            step=0.1,
            format="%.1f",
            key="scale_bodyfat_input",
        )

    scale_note = st.text_area(
        "補足メモ（任意）",
        placeholder="例：朝いち / 入浴後 / いつもの体重計と差がある など",
        height=100,
        key="scale_note_input",
    )

    if st.button("この数値で記録する", use_container_width=True, key="save_scale_log"):
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
st.caption(f"記録日：{jst_today().strftime('%Y/%m/%d')}")
