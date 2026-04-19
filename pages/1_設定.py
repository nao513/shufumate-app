import streamlit as st
from datetime import date, datetime
from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    load_current_user_profile,
    save_user_settings,
    change_login_id,
    change_birth_date,
    change_password,
    ACTIVITY_LEVEL_OPTIONS,
    FOOD_STYLE_OPTIONS,
    USER_TYPE_OPTIONS,
    ADVICE_TONE_OPTIONS,
    CONSTITUTION_TRAIT_OPTIONS,
)

require_login()

st.title("⚙️ 設定")
st.caption("基本設定とアカウント設定を管理します")

user_id = get_user_id()

settings = load_user_settings(user_id)
profile = load_current_user_profile()

nickname_default = profile["nickname"] if profile else settings["nickname"]
login_id_text = profile["login_id"] if profile else ""
birth_date_text = profile["birth_date"] if profile else "未設定"
age_text = f"{profile['age']}歳" if profile and profile.get("age") is not None else "未設定"


def parse_birth_date_or_default(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return date(1976, 1, 1)


birth_default = parse_birth_date_or_default(birth_date_text)
current_year = date.today().year
year_options = list(range(current_year, 1899, -1))

st.subheader("基本設定")

with st.form("settings_form"):
    nickname = st.text_input("ニックネーム", value=nickname_default)

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("生年月日", value=birth_date_text, disabled=True)
    with col2:
        st.text_input("年齢", value=age_text, disabled=True)

    height_cm = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=220.0,
        value=float(settings["height_cm"]),
        step=0.5,
        format="%.1f",
    )

    col3, col4 = st.columns(2)
    with col3:
        current_weight = st.number_input(
            "現在体重(kg)",
            min_value=20.0,
            max_value=200.0,
            value=float(settings["current_weight"]),
            step=0.1,
            format="%.1f",
        )
    with col4:
        target_weight = st.number_input(
            "目標体重(kg)",
            min_value=20.0,
            max_value=200.0,
            value=float(settings["target_weight"]),
            step=0.1,
            format="%.1f",
        )

    col5, col6 = st.columns(2)
    with col5:
        current_body_fat = st.number_input(
            "現在体脂肪(%)",
            min_value=0.0,
            max_value=70.0,
            value=float(settings["current_body_fat"]),
            step=0.1,
            format="%.1f",
        )
    with col6:
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
        if settings["activity_level"] in ACTIVITY_LEVEL_OPTIONS else 1,
    )

    food_style = st.selectbox(
        "食事スタイル",
        FOOD_STYLE_OPTIONS,
        index=FOOD_STYLE_OPTIONS.index(settings["food_style"])
        if settings["food_style"] in FOOD_STYLE_OPTIONS else 0,
    )

    user_type = st.selectbox(
        "利用タイプ",
        USER_TYPE_OPTIONS,
        index=USER_TYPE_OPTIONS.index(settings["user_type"])
        if settings["user_type"] in USER_TYPE_OPTIONS else 0,
    )

    advice_tone = st.selectbox(
        "アドバイスの言い方",
        ADVICE_TONE_OPTIONS,
        index=ADVICE_TONE_OPTIONS.index(settings["advice_tone"])
        if settings["advice_tone"] in ADVICE_TONE_OPTIONS else 0,
    )

    constitution_traits = st.multiselect(
        "体質・傾向",
        CONSTITUTION_TRAIT_OPTIONS,
        default=settings.get("constitution_traits", []),
    )

    submitted = st.form_submit_button("基本設定を保存", use_container_width=True)

if submitted:
    save_user_settings(
        user_id,
        {
            "nickname": nickname.strip(),
            "height_cm": float(height_cm),
            "current_weight": float(current_weight),
            "target_weight": float(target_weight),
            "current_body_fat": float(current_body_fat),
            "target_body_fat": float(target_body_fat),
            "activity_level": activity_level,
            "food_style": food_style,
            "user_type": user_type,
            "advice_tone": advice_tone,
            "constitution_traits": constitution_traits,
        },
    )
    st.success("基本設定を保存しました")
    st.rerun()

st.divider()
st.subheader("アカウント設定")
st.text_input("現在のログインID", value=login_id_text, disabled=True)

with st.expander("ログインIDを変更"):
    with st.form("change_login_id_form"):
        new_login_id = st.text_input("新しいログインID")
        current_password_for_id = st.text_input(
            "現在のパスワード",
            type="password",
            key="current_password_for_id",
        )
        change_id_submitted = st.form_submit_button("ログインIDを変更", use_container_width=True)

    if change_id_submitted:
        change_login_id(
            user_id=user_id,
            current_password=current_password_for_id,
            new_login_id=new_login_id,
        )
        st.success("ログインIDを変更しました")
        st.rerun()

with st.expander("生年月日を変更"):
    st.caption("変更すると年齢表示も自動で更新されます")
    with st.form("change_birth_date_form"):
        col7, col8, col9 = st.columns(3)

        with col7:
            birth_year = st.selectbox(
                "年",
                options=year_options,
                index=year_options.index(birth_default.year)
                if birth_default.year in year_options else 0,
            )

        with col8:
            birth_month = st.selectbox(
                "月",
                options=list(range(1, 13)),
                index=birth_default.month - 1,
            )

        with col9:
            birth_day = st.selectbox(
                "日",
                options=list(range(1, 32)),
                index=birth_default.day - 1,
            )

        current_password_for_birth = st.text_input(
            "現在のパスワード",
            type="password",
            key="current_password_for_birth",
        )

        change_birth_submitted = st.form_submit_button("生年月日を変更", use_container_width=True)

    if change_birth_submitted:
        new_birth_date = date(int(birth_year), int(birth_month), int(birth_day))
        change_birth_date(
            user_id=user_id,
            current_password=current_password_for_birth,
            new_birth_date=new_birth_date,
        )
        st.success("生年月日を変更しました")
        st.rerun()

with st.expander("パスワードを変更"):
    with st.form("change_password_form"):
        current_password = st.text_input(
            "現在のパスワード",
            type="password",
            key="current_password",
        )
        new_password = st.text_input(
            "新しいパスワード",
            type="password",
            key="new_password",
        )
        new_password_confirm = st.text_input(
            "新しいパスワード（確認）",
            type="password",
            key="new_password_confirm",
        )
        change_pw_submitted = st.form_submit_button("パスワードを変更", use_container_width=True)

    if change_pw_submitted:
        change_password(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
            new_password_confirm=new_password_confirm,
        )
        st.success("パスワードを変更しました")
        st.rerun()
