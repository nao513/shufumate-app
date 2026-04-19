def change_birth_date(user_id: str, current_password: str, new_birth_date):
    if not user_id:
        raise ValueError("ユーザー情報が見つかりません。")
    if not current_password:
        raise ValueError("現在のパスワードを入力してください。")

    current_user = find_user_by_user_id(user_id)
    if not current_user:
        raise ValueError("現在のユーザーが見つかりません。")

    password_salt = to_str(current_user.get("password_salt", ""))
    password_hash = to_str(current_user.get("password_hash", ""))

    if not verify_password(current_password, password_salt, password_hash):
        raise ValueError("現在のパスワードが違います。")

    if isinstance(new_birth_date, date):
        birth_date_str = new_birth_date.strftime("%Y-%m-%d")
    else:
        birth_date_str = to_str(new_birth_date).strip()

    if not birth_date_str:
        raise ValueError("生年月日を入力してください。")

    new_age = calculate_age_from_birth_date(birth_date_str)
    if new_age is None:
        raise ValueError("生年月日が正しくありません。")

    # Users 更新
    users_ws = get_users_sheet()
    user_row_index = find_user_row_by_user_id(users_ws, user_id)
    if not user_row_index:
        raise ValueError("Usersシートの更新行が見つかりません。")

    updated_user_row = [
        user_id,
        to_str(current_user.get("login_id", "")).strip(),
        password_hash,
        password_salt,
        to_str(current_user.get("nickname", "")).strip(),
        birth_date_str,
        to_str(current_user.get("created_at", "")).strip(),
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        to_str(current_user.get("is_active", "1")).strip() or "1",
    ]

    users_end_col = chr(64 + len(USERS_HEADERS))
    users_ws.update(f"A{user_row_index}:{users_end_col}{user_row_index}", [updated_user_row])

    # Settings の age も更新しておく
    settings_ws = get_settings_sheet()
    settings_row_index = find_user_row_by_user_id(settings_ws, user_id)

    if settings_row_index:
        current_settings = load_user_settings(user_id)

        updated_settings_row = [
            user_id,
            to_str(current_settings.get("nickname", "")).strip(),
            new_age,
            current_settings.get("height_cm", 160.0),
            current_settings.get("current_weight", 50.0),
            current_settings.get("target_weight", 48.0),
            current_settings.get("current_body_fat", 30.0),
            current_settings.get("target_body_fat", 28.0),
            to_str(current_settings.get("activity_level", "ふつう")) or "ふつう",
            to_str(current_settings.get("food_style", "バランス重視")) or "バランス重視",
            to_str(current_settings.get("user_type", "自分だけ向け")) or "自分だけ向け",
            jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        ]

        settings_end_col = chr(64 + len(SETTINGS_HEADERS))
        settings_ws.update(
            f"A{settings_row_index}:{settings_end_col}{settings_row_index}",
            [updated_settings_row],
        )

    clear_sheet_caches()
