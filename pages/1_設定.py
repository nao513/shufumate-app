import streamlit as st
from datetime import date, datetime
from app_core import *

require_login()

st.title("⚙️ 設定")
st.caption("基本設定とアカウント設定を管理します")

user_id = get_user_id()

# -----------------
# データ取得
# -----------------
try:
    settings = load_user_settings(user_id)
    profile = load_current_user_profile()
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

# -----------------
# 安全取得（ここ重要）
# -----------------
if not isinstance(profile, dict):
    profile = {}

nickname_default = profile.get("nickname", settings.get("nickname", ""))
login_id_text = profile.get("login_id", "")

birth_date_text = profile.get("birth_date", "未設定")

age_text = "未設定"
age_val = profile.get("age")
if age_val is not None:
    age_text = f"{age_val}歳"

# -----------------
# 補助関数
# -----------------
def parse_birth_date_or_default(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return date(1976, 1, 1)

birth_default = parse_birth_date_or_default(birth_date_text)
current_year = date.today().year
year_options = list(range(current_year, 1899, -1))

# -----------------
# 基本設定
# -----------------
st.subheader("基本設定")

with st.form("settings_form"):
    nickname = st.text_input("ニックネーム", value=nickname_default)

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("生年月日", value=birth_date_text, disabled=True)
    with col2:
        st.text_input("年齢", value=age_text, disabled=True)

    height_cm = st.number_input("身長(cm)", value=float(settings.get("height_cm", 160)))

    col3, col4 = st.columns(2)
    with col3:
        current_weight = st.number_input("現在体重(kg)", value=float(settings.get("current_weight", 50)))
    with col4:
        target_weight = st.number_input("目標体重(kg)", value=float(settings.get("target_weight", 48)))

    col5, col6 = st.columns(2)
    with col5:
        current_body_fat = st.number_input("現在体脂肪(%)", value=float(settings.get("current_body_fat", 30)))
    with col6:
        target_body_fat = st.number_input("目標体脂肪(%)", value=float(settings.get("target_body_fat", 28)))

    submitted = st.form_submit_button("保存", use_container_width=True)

if submitted:
    save_user_settings(
        user_id,
        {
            "nickname": nickname,
            "height_cm": height_cm,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "current_body_fat": current_body_fat,
            "target_body_fat": target_body_fat,
        },
    )
    st.success("保存しました")
    st.rerun()

# -----------------
# アカウント情報
# -----------------
st.divider()
st.subheader("アカウント")

st.text_input("ログインID", value=login_id_text, disabled=True)

# -----------------
# パスワード変更（簡易版）
# -----------------
st.subheader("🔑 パスワード変更")

new_pw = st.text_input("新しいパスワード", type="password")
new_pw2 = st.text_input("確認", type="password")

if st.button("変更する", use_container_width=True):

    if not new_pw:
        st.warning("パスワードを入力してください")

    elif new_pw != new_pw2:
        st.error("一致しません")

    else:
        reset_password(login_id_text, new_pw)
        st.success("変更しました")
