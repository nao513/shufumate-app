import streamlit as st
from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    load_current_user_profile,
    save_user_settings,
    change_login_id,
    change_password,
    ACTIVITY_LEVEL_OPTIONS,
    FOOD_STYLE_OPTIONS,
    USER_TYPE_OPTIONS,
)

st.title("⚙️ 設定")
st.caption("提案に使う基本情報を保存します")

require_login()
user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
    profile = load_current_user_profile()
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

nickname_default = profile["nickname"] if profile else settings["nickname"]
age_text = f"{profile['age']}歳" if profile and profile.get("age") is not None else "不明"
login_id_text = profile["login_id"] if profile else ""

with st.form("settings_form"):
    st.text_input("ログインID", value=login_id_text, disabled=True)
    nickname = st.text_input("ニックネーム", value=nickname_default)
    st.text_input("年齢", value=age_text, disabled=True)

    height_cm = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=220.0,
        value=float(settings["height_cm"]),
        step=0.5,
        format="%.1f",
    )

    current_weight = st.number_input(
        "現在体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(settings["current_weight"]),
        step=0.1,
        format="%.1f",
    )

    target_weight = st.number_input(
        "目標体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(settings["target_weight"]),
        step=0.1,
        format="%.1f",
    )

    current_body_fat = st.number_input(
        "現在体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(settings["current_body_fat"]),
        step=0.1,
        format="%.1f",
    )

    target_body_fat = st.number_input(
        "目標体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(settings["target_body_fat"]),
        step=0.1,
        format="%.1f",
    )

    activity_level = st.selectbox(
        "活動量",
        ACTIVITY_LEVEL_OPTIONS,
        index=ACTIVITY_LEVEL_OPTIONS.index(settings["activity_level"])
        if settings["activity_level"] in ACTIVITY_LEVEL_OPTIONS
        else 1,
    )

    food_style = st.selectbox(
        "食事スタイル",
        FOOD_STYLE_OPTIONS,
        index=FOOD_STYLE_OPTIONS.index(settings["food_style"])
        if settings["food_style"] in FOOD_STYLE_OPTIONS
        else 0,
    )

    user_type = st.selectbox(
        "利用タイプ",
        USER_TYPE_OPTIONS,
        index=USER_TYPE_OPTIONS.index(settings["user_type"])
        if settings["user_type"] in USER_TYPE_OPTIONS
        else 0,
    )

    submitted = st.form_submit_button("基本設定を保存", use_container_width=True)

if submitted:
    save_data = {
        "nickname": nickname.strip(),
        "height_cm": float(height_cm),
        "current_weight": float(current_weight),
        "target_weight": float(target_weight),
        "current_body_fat": float(current_body_fat),
        "target_body_fat": float(target_body_fat),
        "activity_level": activity_level,
        "food_style": food_style,
        "user_type": user_type,
    }

    try:
        save_user_settings(user_id, save_data)
        st.success("設定を保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")

st.divider()
st.subheader("🔑 ログインID変更")
st.caption("変更には現在のパスワード確認が必要です")

with st.form("change_login_id_form"):
    new_login_id = st.text_input("新しいログインID")
    current_password_for_id = st.text_input("現在のパスワード", type="password", key="current_password_for_id")
    change_id_submitted = st.form_submit_button("ログインIDを変更", use_container_width=True)

if change_id_submitted:
    try:
        change_login_id(
            user_id=user_id,
            current_password=current_password_for_id,
            new_login_id=new_login_id,
        )
        st.success("ログインIDを変更しました。次回から新しいIDでログインできます。")
        st.rerun()
    except Exception as e:
        st.error(f"ログインID変更に失敗しました: {e}")

st.divider()
st.subheader("🔒 パスワード変更")
st.caption("現在のパスワード確認が必要です")

with st.form("change_password_form"):
    current_password = st.text_input("現在のパスワード", type="password", key="current_password")
    new_password = st.text_input("新しいパスワード", type="password", key="new_password")
    new_password_confirm = st.text_input("新しいパスワード（確認）", type="password", key="new_password_confirm")
    change_pw_submitted = st.form_submit_button("パスワードを変更", use_container_width=True)

if change_pw_submitted:
    try:
        change_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
            new_password_confirm=new_password_confirm,
        )
        st.success("パスワードを変更しました。次回から新しいパスワードでログインできます。")
        st.rerun()
    except Exception as e:
        st.error(f"パスワード変更に失敗しました: {e}")
