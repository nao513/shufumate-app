import streamlit as st
from app_core import *

st.set_page_config(page_title="写真で記録｜ShufuMate", layout="wide")

reload_user_data_if_needed()
load_settings_into_session()
sync_common_from_latest_diet_log()

st.header("📷 写真で記録")
st.caption("冷蔵庫や体重計の写真を使って、日々の記録に活かせます。")

tab1, tab2 = st.tabs(["冷蔵庫写真", "体重計写真・動画"])

with tab1:
    st.subheader("🥬 冷蔵庫スキャン")
    st.caption("写真から食材を整理して、献立づくりに役立てられます。")
    st.caption("スマホでは1枚ずつ撮って追加していく使い方がおすすめです。")
    st.caption("※ Take Photo＝静止画、Upload＝保存済み写真を追加")

    if "fridge_scan_images" not in st.session_state:
        st.session_state["fridge_scan_images"] = []
    if "photo_fridge_items" not in st.session_state:
        st.session_state["photo_fridge_items"] = ""
    if "processed_fridge_upload_hashes" not in st.session_state:
        st.session_state["processed_fridge_upload_hashes"] = []
    if "fridge_photo_uploader_version" not in st.session_state:
        st.session_state["fridge_photo_uploader_version"] = 0

    fridge_camera = st.camera_input("冷蔵庫を写真で撮る", key="fridge_camera_scan_final")

    col1, col2 = st.columns(2)

    with col1:
        if fridge_camera is not None and st.button("➕ この写真を使う", key="add_fridge_camera_final"):
            resized = resize_image(fridge_camera, max_size=768)
            st.session_state["fridge_scan_images"].append(resized)
            st.success("冷蔵庫写真を追加しました。")
            st.rerun()

    with col2:
        if st.button("🧹 冷蔵庫画像を全部クリア", key="clear_fridge_images_final"):
            st.session_state["fridge_scan_images"] = []
            st.session_state["processed_fridge_upload_hashes"] = []
            st.session_state["photo_fridge_items"] = ""
            st.session_state["fridge_photo_uploader_version"] += 1
            st.rerun()

    fridge_photos = st.file_uploader(
        "冷蔵庫写真をアップロード（複数OK）",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"fridge_photo_upload_{st.session_state['fridge_photo_uploader_version']}"
    )

    if fridge_photos:
        st.caption(f"アップロード済み写真: {len(fridge_photos)}枚")
        if st.button("📥 アップロードした写真を追加", key="add_uploaded_fridge_photos_final"):
            added_count = 0
            for photo in fridge_photos:
                sig = uploaded_file_signature(photo)
                if sig not in st.session_state["processed_fridge_upload_hashes"]:
                    resized = resize_image(photo, max_size=768)
                    st.session_state["fridge_scan_images"].append(resized)
                    st.session_state["processed_fridge_upload_hashes"].append(sig)
                    added_count += 1

            st.session_state["fridge_photo_uploader_version"] += 1

            if added_count > 0:
                st.success(f"冷蔵庫写真を {added_count} 枚追加しました。")
            else:
                st.info("新しく追加された写真はありませんでした。")
            st.rerun()

    image_count = len(st.session_state["fridge_scan_images"])

    if image_count > 0:
        st.write(f"保存中の冷蔵庫画像: {image_count}枚")

        max_preview = 8
        preview_images = st.session_state["fridge_scan_images"][:max_preview]

        if image_count > max_preview:
            st.caption(f"表示は先頭 {max_preview} 枚までです。")

        for i, img in enumerate(preview_images):
            st.image(img, caption=f"冷蔵庫画像 {i + 1}", use_container_width=True)

            if st.button(f"🗑 この画像を削除 {i + 1}", key=f"delete_fridge_each_{i}", use_container_width=True):
                st.session_state["fridge_scan_images"].pop(i)
                st.rerun()

        if st.button("🥬 複数画像から食材を読み取る", key="extract_fridge_items_final"):
            client = get_openai_client()
            with st.spinner("AIが食材を読み取り中..."):
                result = extract_foods_from_images(client, st.session_state["fridge_scan_images"])

            st.session_state["photo_fridge_items"] = result
            st.success("食材候補を抽出しました。")
            st.rerun()

    st.text_area("読み取った食材候補", key="photo_fridge_items", height=180)

    col3, col4 = st.columns(2)

    with col3:
        if st.button("🧹 読み取り結果をクリア", use_container_width=True, key="clear_fridge_result_final"):
            st.session_state["photo_fridge_items"] = ""
            st.rerun()

    with col4:
        if st.button("➡ 冷蔵庫食材に反映", use_container_width=True, key="apply_fridge_items_final"):
            text = st.session_state.get("photo_fridge_items", "")
            if "食材候補:" in text:
                text = text.split("食材候補:")[-1].strip()
            st.session_state["fridge_items"] = text
            st.success("冷蔵庫の食材に反映しました。")

with tab2:
    st.subheader("⚖ 体重計写真・動画から記録候補を管理")
    st.caption("写真や動画から数値を読み取り、記録に反映できます。")
    st.caption("※ 自動反映は体重・体脂肪率・筋肉量に対応します。")
    st.caption("※ 目標筋肉量は初期設定の値をそのまま使います。")

    if "scale_scan_images" not in st.session_state:
        st.session_state["scale_scan_images"] = []
    if "selected_scale_index" not in st.session_state:
        st.session_state["selected_scale_index"] = 0
    if "photo_scale_result" not in st.session_state:
        st.session_state["photo_scale_result"] = ""
    if "processed_scale_upload_hashes" not in st.session_state:
        st.session_state["processed_scale_upload_hashes"] = []
    if "scale_photo_uploader_version" not in st.session_state:
        st.session_state["scale_photo_uploader_version"] = 0
    if "scale_video_uploader_version" not in st.session_state:
        st.session_state["scale_video_uploader_version"] = 0

    scale_camera = st.camera_input("体重計を写真で撮る", key="scale_camera_input_final2")

    col5, col6 = st.columns(2)

    with col5:
        if scale_camera is not None and st.button("➕ この写真を使う", key="add_scale_camera_final2"):
            resized = resize_image(scale_camera, max_size=768)
            st.session_state["scale_scan_images"].append(resized)
            st.success("体重計写真を追加しました。")
            st.rerun()

    with col6:
        if st.button("🧹 体重計画像を全部クリア", key="clear_scale_images_final2"):
            st.session_state["scale_scan_images"] = []
            st.session_state["processed_scale_upload_hashes"] = []
            st.session_state["photo_scale_result"] = ""
            st.session_state["selected_scale_index"] = 0
            st.session_state["scale_photo_uploader_version"] += 1
            st.session_state["scale_video_uploader_version"] += 1
            st.rerun()

    scale_photos = st.file_uploader(
        "体重計写真をアップロード（複数OK）",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"scale_photo_upload_multi_{st.session_state['scale_photo_uploader_version']}"
    )

    if scale_photos:
        st.caption(f"アップロード済み写真: {len(scale_photos)}枚")
        if st.button("📥 アップロードした写真を追加", key="add_uploaded_scale_photos_final2"):
            added_count = 0
            for photo in scale_photos:
                sig = uploaded_file_signature(photo)
                if sig not in st.session_state["processed_scale_upload_hashes"]:
                    resized = resize_image(photo, max_size=768)
                    st.session_state["scale_scan_images"].append(resized)
                    st.session_state["processed_scale_upload_hashes"].append(sig)
                    added_count += 1

            st.session_state["scale_photo_uploader_version"] += 1

            if added_count > 0:
                st.success(f"体重計写真を {added_count} 枚追加しました。")
            else:
                st.info("新しく追加された写真はありませんでした。")
            st.rerun()

    scale_video = st.file_uploader(
        "体重計動画をアップロード（mp4 / mov / m4v）",
        type=["mp4", "mov", "m4v"],
        key=f"scale_video_upload_{st.session_state['scale_video_uploader_version']}"
    )

    if scale_video is not None:
        st.caption("動画を使う場合は、下の『🎞 動画から画像を取り込む』を押してください。")
        st.caption("現在の設定: 3秒ごとに1枚、最大8枚")

        if st.button("🎞 動画から画像を取り込む", key="extract_scale_video_frames_final2"):
            frames = extract_frames_from_video(
                scale_video,
                interval_sec=3.0,
                max_frames=8,
                max_size=768
            )
            st.session_state["scale_video_uploader_version"] += 1

            if frames:
                st.session_state["scale_scan_images"].extend(frames)
                st.success(f"動画から {len(frames)} 枚の画像を取り込みました。")
            else:
                st.warning("動画から画像を取り込めませんでした。")
            st.rerun()

    image_count = len(st.session_state["scale_scan_images"])

    if image_count > 0:
        st.write(f"保存中の体重計画像: {image_count}枚")

        if st.session_state["selected_scale_index"] >= image_count:
            st.session_state["selected_scale_index"] = max(0, image_count - 1)

        selected_scale_index = st.selectbox(
            "読み取りに使う画像を選んでください",
            list(range(image_count)),
            index=st.session_state["selected_scale_index"],
            format_func=lambda x: f"体重計画像 {x + 1}",
            key="selected_scale_index_final2"
        )
        st.session_state["selected_scale_index"] = selected_scale_index

        max_preview = 8
        preview_images = st.session_state["scale_scan_images"][:max_preview]

        if image_count > max_preview:
            st.caption(f"表示は先頭 {max_preview} 枚までです。")

        for i, img in enumerate(preview_images):
            st.image(img, caption=f"体重計画像 {i + 1}", use_container_width=True)

            if st.button(f"🗑 この画像を削除 {i + 1}", key=f"delete_scale_each_{i}", use_container_width=True):
                st.session_state["scale_scan_images"].pop(i)
                if st.session_state["selected_scale_index"] >= len(st.session_state["scale_scan_images"]):
                    st.session_state["selected_scale_index"] = max(0, len(st.session_state["scale_scan_images"]) - 1)
                st.rerun()

        selected_img = st.session_state["scale_scan_images"][selected_scale_index]
        st.markdown("#### 現在選択中の画像")
        st.image(selected_img, caption=f"体重計画像 {selected_scale_index + 1}", use_container_width=True)

        col7, col8 = st.columns(2)

        with col7:
            if st.button("⚖ 選択した1枚を読み取る", key="extract_scale_values_single_final2"):
                client = get_openai_client()
                with st.spinner("AIが選択画像を読み取り中..."):
                    result = extract_scale_values_from_image(client, selected_img)

                st.session_state["photo_scale_result"] = result
                st.success("選択画像から数値候補を抽出しました。")
                st.rerun()

        with col8:
            if image_count >= 2 and st.button("⚖ 複数画像をまとめて読み取る", key="extract_scale_values_all_final2"):
                client = get_openai_client()
                with st.spinner("AIが複数画像を見比べて読み取り中..."):
                    result = extract_scale_values_from_images(client, st.session_state["scale_scan_images"])

                st.session_state["photo_scale_result"] = result
                st.success("複数画像から数値候補を抽出しました。")
                st.rerun()

    st.text_area(
        "読み取った数値候補メモ",
        placeholder="例：体重: 51.2\n体脂肪率: 25.6\n筋肉量: 35.4\n骨格筋率: 27.2",
        key="photo_scale_result",
        height=220
    )

    st.subheader("📌 現在の体情報")
    info1, info2, info3, info4 = st.columns(4)
    with info1:
        st.metric("現在の体重", f"{st.session_state.get('common_weight', 50.0):.1f} kg")
    with info2:
        st.metric("現在の体脂肪率", f"{st.session_state.get('common_body_fat', 28.0):.1f} %")
    with info3:
        st.metric("現在の筋肉量", f"{st.session_state.get('common_muscle_mass', 35.0):.1f} kg")
    with info4:
        st.metric("目標筋肉量", f"{st.session_state.get('common_target_muscle_mass', 38.0):.1f} kg")

    col9, col10, col11 = st.columns(3)

    with col9:
        if st.button("🧹 数値候補をクリア", use_container_width=True, key="clear_scale_result_final2"):
            st.session_state["photo_scale_result"] = ""
            st.rerun()

    with col10:
        if st.button("📌 読み取った数値を自動反映", key="apply_weight_and_fat_final2"):
            parsed = parse_scale_values(st.session_state.get("photo_scale_result", ""))
            updated = False

            if parsed["weight"] is not None:
                st.session_state["common_weight"] = parsed["weight"]
                updated = True

            if parsed["body_fat"] is not None:
                st.session_state["common_body_fat"] = parsed["body_fat"]
                updated = True

            if parsed["muscle_mass"] is not None:
                st.session_state["common_muscle_mass"] = parsed["muscle_mass"]
                updated = True

            if updated:
                st.success("体重・体脂肪率・筋肉量を自動反映しました。")
            else:
                st.warning("反映できる数値が見つかりませんでした。")

    with col11:
        if st.button("📝 読み取った数値で今日の記録を保存", key="save_today_from_scale_final2"):
            ok, message = save_today_log_from_scale_result()
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.warning(message)
