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


def get_page_icon(filename, fallback="💬"):
    path = ICON_DIR / filename
    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            return fallback
    return fallback


# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="相談する｜ShufuMate",
    page_icon=get_page_icon("chat.png", "💬"),
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

    .soft-card {
        background: #fffdf8;
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        color: #6b4c3b;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .focus-card {
        background: #eef8ef;
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(78, 140, 82, 0.14);
        color: #316c37;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .answer-card {
        background: #fffdf8;
        border-radius: 22px;
        padding: 18px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.06);
        color: #5c4033;
        font-size: 0.95rem;
        line-height: 1.8;
        margin-bottom: 18px;
    }

    .setting-row {
        background: #fff8ef;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
        border: 1px solid rgba(139, 100, 72, 0.08);
        color: #5c4033;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .note-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 14px 16px;
        color: #8a7465;
        font-size: 0.85rem;
        line-height: 1.7;
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

    div[data-testid="stTextArea"] label,
    div[data-testid="stRadio"] label {
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
def render_page_header(title, subtitle, icon_file="chat.png"):
    icon_src = load_icon(icon_file)

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = '<div class="section-head-emoji">💬</div>'

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
        unsafe_allow_html=True,
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
        unsafe_allow_html=True,
    )


def render_soft_card(text):
    st.markdown(
        f"""
<div class="soft-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_focus_card(text):
    st.markdown(
        f"""
<div class="focus-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_answer_card(text):
    st.markdown(
        f"""
<div class="answer-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_setting_row(label, value):
    st.markdown(
        f"""
<div class="setting-row">
    <strong>{safe_text(label)}</strong><br>
    {safe_text(value)}
</div>
""",
        unsafe_allow_html=True,
    )


# =========================
# 安全呼び出し
# =========================
def call_if_exists(func_name, default=None, *args, **kwargs):
    func = globals().get(func_name)

    if callable(func):
        try:
            return func(*args, **kwargs)
        except Exception:
            return default

    return default


# =========================
# ログイン
# =========================
require_login()
user_id = get_user_id()


# =========================
# データ取得
# =========================
try:
    settings = load_user_settings(user_id)

    if not isinstance(settings, dict):
        settings = {}

    if callable(globals().get("normalize_consult_settings")):
        settings = normalize_consult_settings(settings)

    profile = call_if_exists("load_current_user_profile", {}, user_id)
    latest_log = call_if_exists("load_latest_log", {}, user_id)
    focus = call_if_exists(
        "get_support_focus_summary",
        {"points": [], "today_conditions": []},
        settings,
        latest_log,
    )

    if not isinstance(profile, dict):
        profile = {}

    if not isinstance(latest_log, dict):
        latest_log = {}

    if not isinstance(focus, dict):
        focus = {"points": [], "today_conditions": []}

except Exception:
    st.error("相談ページの読込に失敗しました。時間をおいてもう一度お試しください。")
    st.stop()


# =========================
# 表示名
# =========================
nickname = ""

if isinstance(profile, dict):
    nickname = str(profile.get("nickname", "")).strip()

if not nickname:
    nickname = str(settings.get("nickname", "")).strip()

if not nickname:
    nickname = user_id or ""


# =========================
# ヘッダー
# =========================
render_page_header(
    title="相談する",
    subtitle="体質・今日の状態・現在の設定をもとに、食事・運動・体調の整え方を提案します。",
    icon_file="chat.png",
)


# =========================
# ユーザー案内
# =========================
if nickname:
    render_soft_card(f"{nickname}さん向けに提案します。")
else:
    render_soft_card("現在の設定をもとに提案します。")


# =========================
# 今整えたいポイント
# =========================
render_section_header("今整えたいポイント", icon_file="state.png", emoji="🌿")

points = focus.get("points", [])
today_conditions = focus.get("today_conditions", [])

if points:
    focus_text = " / ".join(points)
else:
    focus_text = "基本の整え"

if today_conditions:
    condition_text = "今日の状態：" + " / ".join(today_conditions)
else:
    condition_text = "今日の状態：まだ記録がありません"

render_focus_card(f"{focus_text}\n{condition_text}")


# =========================
# 相談入力
# =========================
render_section_header("相談内容", icon_file="chat.png", emoji="💬")

category_options = globals().get(
    "CATEGORY_OPTIONS",
    ["食事", "運動", "体調", "外食調整"]
)

category = st.radio(
    "相談カテゴリ",
    category_options,
    horizontal=True,
)

example_text = {
    "食事": "例：今日は何を食べたら整いやすい？ 夜ごはんはどうする？",
    "運動": "例：今日はだるいけど何をしたらいい？ 5分だけ動くなら？",
    "体調": "例：むくみが気になる。寝不足の日はどうしたらいい？",
    "外食調整": "例：今日パスタ外食です。どう選べばいい？ 焼肉のときの調整は？",
}

question = st.text_area(
    "相談内容",
    placeholder=example_text.get(category, "相談したいことを書いてください"),
    height=150,
)

if st.button("相談する", use_container_width=True):

    try:
        answer = generate_answer(
            category=category,
            question=question,
            settings=settings,
            latest_log=latest_log,
        )

        st.session_state["last_answer"] = answer

    except Exception:
        st.warning("回答を作成できませんでした。時間をおいてもう一度お試しください。")



# =========================
# 回答表示
# =========================
if "last_answer" in st.session_state:
    render_section_header("回答", icon_file="chat.png", emoji="💬")
    render_answer_card(st.session_state["last_answer"])


# =========================
# 現在の設定
# =========================
render_section_header("いまの設定", icon_file="settings.png", emoji="⚙️")

st.markdown("<div class='card'>", unsafe_allow_html=True)

render_setting_row(
    "利用タイプ",
    settings.get("user_type", "自分向け")
)

render_setting_row(
    "活動量",
    settings.get("activity_level", "ふつう")
)

render_setting_row(
    "食事スタイル",
    settings.get("food_style", settings.get("meal_style", "和食中心"))
)

traits = settings.get("constitution_traits", [])

if isinstance(traits, list):
    traits_text = " / ".join(traits) if traits else "未設定"
else:
    traits_text = str(traits) if traits else "未設定"

render_setting_row(
    "体質・傾向",
    traits_text
)

render_setting_row(
    "アドバイスの言い方",
    settings.get("advice_tone", "やさしく")
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 注意書き
# =========================
st.markdown(
    """
<div class="note-card">
    ※ この相談機能は簡易版です。医療判断が必要な内容は、医療機関に相談してください。
</div>
""",
    unsafe_allow_html=True,
)
