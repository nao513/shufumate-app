import streamlit as st
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


def get_page_icon(filename, fallback="📷"):
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
    page_title="写真で記録｜ShufuMate",
    page_icon=get_page_icon("camera.png", "📷"),
    layout="centered",
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
        max-width: 820px;
        padding-top: 3.8rem;
        padding-bottom: 2.5rem;
    }

    .top-card {
        background: #ffffff;
        border-radius: 26px;
        padding: 22px 20px;
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
        margin: 26px 0 10px 0;
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

    .section-icon-camera img {
        width: 42px;
        height: 42px;
    }

    .section-icon-food img {
        width: 42px;
        height: 42px;
    }

    .section-icon-calendar img {
        width: 54px;
        height: 54px;
        transform: scale(1.35);
    }

    .section-head-emoji {
        font-size: 1.45rem;
        line-height: 1;
    }

    .section-head-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: #5c4033;
        line-height: 1.2;
    }

    .sub-note {
        font-size: 0.86rem;
        color: #8a7465;
        margin: -2px 0 12px 64px;
        line-height: 1.6;
    }

    .auto-meal-card {
        background: #eef8ef;
        border-radius: 18px;
        padding: 14px 15px;
        border: 1px solid rgba(78, 140, 82, 0.14);
        color: #316c37;
        font-size: 0.95rem;
        font-weight: 800;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .latest-card {
        background: #fffdf8;
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        color: #5c4033;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .bottom-message {
        background: #ffffff;
        border-radius: 22px;
        padding: 16px;
        color: #7b6658;
        font-size: 0.9rem;
        line-height: 1.7;
        box-shadow: 0 5px 16px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-top: 16px;
    }

    .stButton > button {
        background-color: #8d6e63;
        color: #ffffff;
        border: none;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 800;
    }

    .stButton > button:hover {
        background-color: #76594f;
        color: #ffffff;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stCameraInput"] label {
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
            padding: 18px 16px;
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

        .section-icon-calendar img {
            width: 50px;
            height: 50px;
            transform: scale(1.3);
        }

        .section-head-title {
            font-size: 1.08rem;
        }

        .sub-note {
            margin-left: 58px;
            font-size: 0.78rem;
        }
    }
</style>
""",
    unsafe_allow_html=True
)


# =========================
# 表示用関数
# =========================
def render_page_header(title, subtitle, icon_file="camera.png", emoji="📷"):
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

    icon_class = ""
    if icon_file:
        icon_name = Path(icon_file).stem
        icon_class = f"section-icon-{icon_name}"

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = f'<div class="section-head-emoji">{safe_text(emoji)}</div>'

    st.markdown(
        f"""
<div class="section-head">
    <div class="section-head-icon {icon_class}">
        {icon_html}
    </div>
    <div class="section-head-title">{safe_text(title)}</div>
</div>
""",
        unsafe_allow_html=True
    )


def render_auto_meal_card(text):
    st.markdown(
        f"""
<div class="auto-meal-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


def render_latest_card(text):
    st.markdown(
        f"""
<div class="latest-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


# =========================
# ログイン
# =========================
require_login()
user_id = get_user_id()


# =========================
# ヘッダー
# =========================
render_page_header(
    title="写真で記録",
    subtitle="写真をアップロードして、食事内容をかんたんに記録します。",
    icon_file="camera.png",
    emoji="📷"
)


# =========================
# 写真入力
# =========================
render_section_header("写真を選ぶ", icon_file="camera.png", emoji="📷")
st.markdown(
    '<div class="sub-note">アップロード、またはカメラ撮影から選べます。</div>',
    unsafe_allow_html=True
)

input_mode = st.radio(
    "写真の入力方法",
    ["写真をアップロード", "カメラで撮影"],
    horizontal=True
)

img = None

if input_mode == "写真をアップロード":
    img = st.file_uploader(
        "写真を選んでください",
        type=["jpg", "jpeg", "png"]
    )
else:
    img = st.camera_input("食事の写真を撮る")

if img is not None:
    st.image(img, caption="選択した写真", use_container_width=True)



# =========================
# 食事内容
# =========================
render_section_header("食事内容", icon_file="food.png", emoji="🍽")

st.markdown("<div class='card'>", unsafe_allow_html=True)

auto_meal = detect_meal_type_by_time(jst_now())

render_auto_meal_card(f"👉 自動判定：{auto_meal}ごはん")

meal_options = ["朝", "昼", "夜", "間食"]

meal_type = st.radio(
    "食事区分",
    meal_options,
    index=meal_options.index(auto_meal) if auto_meal in meal_options else 0,
    horizontal=True
)

food_text = st.text_area(
    "食事内容（簡単でOK）",
    placeholder="例：鮭おにぎり、卵焼き、サラダ、味噌汁",
    height=120
)

if st.button("✅ 記録する", use_container_width=True):

    if img is None:
        st.warning("写真を選ぶか撮影してください")
    else:
        try:
            save_photo_meal_log(
                user_id=user_id,
                meal_type=meal_type,
                food_text=food_text,
                image_file=img,
            )

            st.success(f"{meal_type}ごはんを記録しました！")
            st.balloons()

        except Exception:
            st.error("写真記録の保存に失敗しました。時間をおいてもう一度お試しください。")

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 最新記録
# =========================
render_section_header("最新の写真記録", icon_file="calendar.png", emoji="📌")
st.markdown(
    '<div class="sub-note">最後に保存した写真記録を確認できます。</div>',
    unsafe_allow_html=True
)

st.markdown("<div class='card'>", unsafe_allow_html=True)

try:
    photo_logs = load_photo_logs(user_id)
except Exception:
    photo_logs = []

if photo_logs:
    latest = photo_logs[-1]

    latest_text = (
        f"日付：{latest.get('log_date', '')}\n"
        f"食事区分：{latest.get('meal_type', '')}\n"
        f"内容：{latest.get('food_text', '')}"
    )

    render_latest_card(latest_text)

    image_bytes = latest.get("image_bytes")
    if image_bytes:
        st.image(
            image_bytes,
            caption="最新の写真",
            use_container_width=True
        )

else:
    st.info("まだ写真記録がありません")

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 下部メッセージ
# =========================
st.markdown(
    """
<div class="bottom-message">
    食事内容は完璧に書かなくても大丈夫です。<br>
    写真だけでも、あとから振り返る大切な記録になります。
</div>
""",
    unsafe_allow_html=True
)
