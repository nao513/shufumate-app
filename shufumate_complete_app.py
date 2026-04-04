elif mode == "食事写真評価":
    st.header("📸 食事写真で1日評価")
    st.caption("朝・昼・夜の写真から、1日の食事バランスをやさしくチェックします。")

    with st.expander("使い方を見る"):
        st.write("① 朝・昼・夜の写真を1枚ずつ入れます")
        st.write("② 『1日の食事を評価する』を押します")
        st.write("③ 良かった点・不足しやすい栄養・調整アドバイスを確認します")

    # 朝食
    st.subheader("🍙 朝食")
    breakfast_camera = st.camera_input("朝食を撮る", key="breakfast_camera")
    breakfast_upload = st.file_uploader(
        "または朝食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="breakfast_upload"
    )
    breakfast_source = breakfast_camera if breakfast_camera is not None else breakfast_upload
    breakfast_img = resize_image(breakfast_source, max_size=768) if breakfast_source is not None else None

    if breakfast_img is not None:
        st.image(breakfast_img, use_container_width=True)

    st.divider()

    # 昼食
    st.subheader("🍱 昼食")
    lunch_camera = st.camera_input("昼食を撮る", key="lunch_camera")
    lunch_upload = st.file_uploader(
        "または昼食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="lunch_upload"
    )
    lunch_source = lunch_camera if lunch_camera is not None else lunch_upload
    lunch_img = resize_image(lunch_source, max_size=768) if lunch_source is not None else None

    if lunch_img is not None:
        st.image(lunch_img, use_container_width=True)

    st.divider()

    # 夕食
    st.subheader("🍽 夕食")
    dinner_camera = st.camera_input("夕食を撮る", key="dinner_camera")
    dinner_upload = st.file_uploader(
        "または夕食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="dinner_upload"
    )
    dinner_source = dinner_camera if dinner_camera is not None else dinner_upload
    dinner_img = resize_image(dinner_source, max_size=768) if dinner_source is not None else None

    if dinner_img is not None:
        st.image(dinner_img, use_container_width=True)

    st.divider()

    if st.button("📊 1日の食事を評価する", use_container_width=True):
        if breakfast_img is None or lunch_img is None or dinner_img is None:
            st.warning("朝・昼・夜の3枚をそろえてください。")
        else:
            client = get_openai_client()
            with st.spinner("1日の食事バランスを分析中..."):
                result = evaluate_meal_day_from_images(
                    client,
                    breakfast_img,
                    lunch_img,
                    dinner_img
                )

            st.session_state["meal_eval_result"] = result
            st.success("1日の食事評価を作成しました。")
            st.rerun()

    st.text_area(
        "評価結果",
        key="meal_eval_result",
        height=320
    )

    if st.session_state["meal_eval_result"]:
        st.download_button(
            "📥 評価結果をテキスト保存",
            data=st.session_state["meal_eval_result"],
            file_name="meal_day_evaluation.txt",
            mime="text/plain",
            use_container_width=True
        )
