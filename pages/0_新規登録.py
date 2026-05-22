import streamlit as st
from datetime import date
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html


# =========================
# パス・アイコン設定
# =========================
THIS_FILE = Path(__file__).resolve()

if THIS_FILE.parent.name == "pages":
    APP_ROOT = THIS_FILE.parent.parent
else:
    APP_ROOT = THIS_FILE.parent

ICON_DIR = APP_ROOT / "assets" / "icons"


def get_page_icon(filename, fallback="🆕"):
    path = ICON_DIR / filename
    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            return fallback
    return fallback


# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="新規登録｜ShufuMate",
    page_icon=get_page_icon("register.png", "🆕"),
    layout="centered"
)


# =========================
# 画像読み込み
# =========================
def file_to_base64(path):
    if not path.exists():
        return None

    suffix = path.suffix.lower()

    if suffix == ".png":
        mime = "image/png"
    elif suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def load_icon(filename):
    if not filename:
        return None

    candidates = [
        ICON_DIR / filename,
        APP_ROOT / "assets" / "icons" / filename,
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


def safe_text(value):
    return html.escape(str(value))


def safe_html_with_br(value):
    return html.escape(str(value)).replace("\n", "<br>")


# =========================
# CSS
# =========================
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fffaf4 0%, #fff4e8 45%, #fffaf4 100%);
    }

    .block-container {
        max-width: 760px;
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }

    .top-card {
        background: #ffffff;
        border-radius: 26px;
        padding: 24px 22px;
        box-shadow: 0 8px 24px rgba(96, 65, 45, 0.10);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 18px;
    }

    .page-head {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .page-head-icon {
        width: 74px;
        min-width: 74px;
        height: 74px;
        border-radius: 22px;
        background: #fff8ef;
        border: 1px solid rgba(139, 100, 72, 0.12);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.09);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .page-head-icon img {
        width: 58px;
        height: 58px;
        object-fit: contain;
    }

    .page-head-emoji {
        font-size: 2.1rem;
        line-height: 1;
    }

    .page-title {
        font-size: 1.75rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 5px;
    }

    .page-subtitle {
        font-size: 0.95rem;
        color: #7b6658;
        line-height: 1.7;
        font-weight: 600;
    }

    .card {
        background: #ffffff;
        border-radius: 24px;
        padding: 20px 18px;
        box-shadow: 0 6px 18px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
    }

    .section-head {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 8px 0 16px 0;
    }

    .section-head-icon {
        width: 52px;
        min-width: 52px;
        height: 52px;
        border-radius: 17px;
        background: #ffffff;
        border: 1px solid rgba(139, 100, 72, 0.12);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.09);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .section-head-icon img {
        width: 40px;
        height: 40px;
        object-fit: contain;
    }

    .section-head-emoji {
        font-size: 1.45rem;
        line-height: 1;
    }

    .section-head-title {
        font-size: 1.18rem;
        font-weight: 900;
        color: #5c4033;
        line-height: 1.2;
    }

    .note-card {
        background: #fff8ef;
        border-radius: 20px;
        padding: 14px 16px;
        color: #7b6658;
        font-size: 0.88rem;
        line-height: 1.7;
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
    }

    .success-card {
        background: #eef8ef;
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(78, 140, 82, 0.14);
        color: #316c37;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #8d6e63;
        color: #ffffff;
        border: none;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 800;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #76594f;
        color: #ffffff;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {
        color: #5c4033;
        font-weight: 700;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.2rem;
        }

        .top-card {
            padding: 20px 17px;
        }

        .page-head-icon {
            width: 62px;
            min-width: 62px;
            height: 62px;
            border-radius: 19px;
        }

        .page-head-icon img {
            width: 48px;
            height: 48px;
        }

        .page-title {
            font-size: 1.45rem;
        }

        .page-subtitle {
            font-size: 0.88rem;
        }

        .section-head-icon {
            width: 46px;
            min-width: 46px;
            height: 46px;
            border-radius: 15px;
        }

        .section-head-icon img {
            width: 35px;
            height: 35px;
        }

        .section-head-title {
            font-size: 1.08rem;
        }
    }
</style>
""",
    unsafe_allow_html=True
)


# =========================
# 表示用関数
# =========================
def render_page_header(title, subtitle, icon_file="register.png", emoji="🆕"):
    icon_src = load_icon(icon_file)

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = f'<div class="page-head-emoji">{safe_text(emoji)}</div>'

    st.markdown(
        f"""
<div class="top-card">
    <div class="page-head">
        <div class="page-head-icon">
            {icon_html}
        </div>
        <div>
            <div class="page-title">{safe_text(title)}</div>
            <div class="page-subtitle">{safe_html_with_br(subtitle)}</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True
    )


def render_section_header(title, icon_file=None, emoji=""):
    icon_src = load_icon(icon_file) if icon_file else None

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = f'<div class="section-head-emoji">{safe_text(emoji)}</div>'

    st.markdown(
        f"""
<div class="section-head">
    <div class="section-head-icon">
        {icon_html}
    </div>
    <div class="section-head-title">{safe_text(title)}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_note(text):
    st.markdown(
        f"""
<div class="note-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


def render_success(text):
    st.markdown(
        f"""
<div class="success-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


# =========================
# ヘッダー
# =========================
render_page_header(
    title="新規登録",
    subtitle="ShufuMateのアカウントを作成します。",
    icon_file="register.png",
    emoji="🆕"
)

render_note(
    "ログインID・パスワード・ニックネーム・生年月日を入力してください。"
)


# -----------------
# ログイン済みの場合
# -----------------
if is_logged_in():
    user_id = get_user_id()

    render_success(f"{user_id} さんはすでにログイン済みです。")

    if st.button("ホームへ", use_container_width=True):
        st.switch_page("Home.py")

    st.stop()


# -----------------
# 年月日
# -----------------
current_year = date.today().year
year_options = list(range(current_year, 1899, -1))


# =====================
# 新規登録フォーム
# =====================
st.markdown("<div class='card'>", unsafe_allow_html=True)

render_section_header("アカウント情報", icon_file="register.png", emoji="🆕")

with st.form("register_form"):

    login_id = st.text_input(
        "ログインID",
        placeholder="例：naomi"
    )

    password = st.text_input(
        "パスワード",
        type="password",
        placeholder="4文字以上"
    )

    password_confirm = st.text_input(
        "パスワード（確認）",
        type="password"
    )

    nickname = st.text_input(
        "ニックネーム",
        placeholder="例：なおみ"
    )

    st.markdown("**生年月日**")

    col1, col2, col3 = st.columns(3)

    with col1:
        birth_year = st.selectbox(
            "年",
            options=year_options,
            index=year_options.index(1976) if 1976 in year_options else 0,
        )

    with col2:
        birth_month = st.selectbox(
            "月",
            options=list(range(1, 13)),
            index=0,
        )

    with col3:
        birth_day = st.selectbox(
            "日",
            options=list(range(1, 32)),
            index=0,
        )

    submitted = st.form_submit_button(
        "登録する",
        use_container_width=True
    )

st.markdown("</div>", unsafe_allow_html=True)


# =====================
# 登録処理
# =====================
if submitted:

    clean_login_id = str(login_id).strip()
    clean_password = str(password).strip()
    clean_password_confirm = str(password_confirm).strip()
    clean_nickname = str(nickname).strip()

    if not clean_login_id:
        st.warning("ログインIDを入力してください")

    elif not clean_password:
        st.warning("パスワードを入力してください")

    elif clean_password != clean_password_confirm:
        st.error("パスワード確認が一致しません")

    elif len(clean_password) < 4:
        st.warning("パスワードは4文字以上にしてください")

    else:
        try:
            try:
                birth_date = date(
                    int(birth_year),
                    int(birth_month),
                    int(birth_day)
                )
            except ValueError:
                st.error("生年月日が正しくありません")
                st.stop()

            user_record = create_user(
                login_id=clean_login_id,
                password=clean_password,
                nickname=clean_nickname,
                birth_date=birth_date,
            )

            if not user_record:
                st.error("登録に失敗しました。ログインIDがすでに使われている可能性があります。")
                st.stop()

            login_user(user_record)

            st.success("登録が完了しました")
            st.switch_page("Home.py")

        except Exception:
            st.error("登録に失敗しました。入力内容を確認して、もう一度お試しください。")


# -----------------
# 下部ボタン
# -----------------
st.markdown("---")

if st.button("ログイン画面へ", use_container_width=True):
    st.switch_page("pages/0_ログイン.py")
