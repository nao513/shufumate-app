import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import base64
import html
from urllib.parse import quote


# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="ShufuMate｜主婦の味方アプリ",
    page_icon="🌿",
    layout="centered"
)


# =========================
# 基本関数
# =========================
def jst_now():
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def japanese_date():
    now = jst_now()
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return f"{now.year}年{now.month}月{now.day}日（{weekdays[now.weekday()]}）"


def greeting():
    hour = jst_now().hour
    if 5 <= hour < 10:
        return "おはようございます"
    elif 10 <= hour < 17:
        return "こんにちは"
    elif 17 <= hour < 22:
        return "こんばんは"
    else:
        return "今日もおつかれさまです"


def page_url(page_name):
    if page_name == "home":
        return "/"
    return "/" + quote(page_name)


def get_login_user():
    for key in ["login_user", "login_id", "user_id", "username", "current_user"]:
        value = st.session_state.get(key)
        if value:
            return value
    return None


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


def load_asset(filename):
    root = Path(__file__).resolve().parent

    candidates = [
        root / "assets" / filename,
        Path.cwd() / "assets" / filename,
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


def load_home_icon(filename):
    root = Path(__file__).resolve().parent

    candidates = [
        root / "assets" / "home_icons" / filename,
        root / "assets" / filename,
        Path.cwd() / "assets" / "home_icons" / filename,
        Path.cwd() / "assets" / filename,
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


# =========================
# CSS
# =========================
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fffaf4 0%, #fff5eb 45%, #fffaf4 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 760px;
    }

    .top-visual-wrap {
        background: #ffffff;
        border-radius: 28px;
        padding: 10px;
        box-shadow: 0 8px 26px rgba(96, 65, 45, 0.12);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 16px;
    }

    .top-visual {
        width: 100%;
        border-radius: 22px;
        display: block;
    }

    .top-card {
        background: #ffffff;
        border-radius: 26px;
        padding: 22px 20px;
        box-shadow: 0 8px 24px rgba(96, 65, 45, 0.10);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 18px;
    }

    .date-pill {
        display: inline-block;
        background: #f4e5d6;
        color: #6b4c3b;
        border-radius: 999px;
        padding: 7px 14px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .main-title {
        font-size: 1.85rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 6px;
        letter-spacing: 0.02em;
    }

    .main-message {
        font-size: 0.98rem;
        color: #7b6658;
        line-height: 1.7;
    }

    .recommend-box {
        background: #fff8ef;
        border-radius: 22px;
        padding: 16px 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
    }

    .recommend-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #5c4033;
        margin-bottom: 6px;
    }

    .recommend-text {
        font-size: 0.9rem;
        color: #7b6658;
        line-height: 1.6;
    }

    .section-title {
        font-size: 1.18rem;
        font-weight: 900;
        color: #5c4033;
        margin: 24px 0 10px 0;
    }

    .section-subtitle {
        font-size: 0.9rem;
        color: #8a7465;
        margin-bottom: 12px;
    }

    .nav-card {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #ffffff;
        border-radius: 24px;
        padding: 15px 14px;
        margin-bottom: 14px;
        min-height: 96px;
        text-decoration: none !important;
        color: inherit !important;
        box-shadow: 0 6px 18px rgba(96, 65, 45, 0.10);
        border: 1px solid rgba(139, 100, 72, 0.12);
        transition: all 0.18s ease;
    }

    .nav-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 26px rgba(96, 65, 45, 0.16);
        background: #fffdf8;
        border: 1px solid rgba(139, 100, 72, 0.20);
    }

    .icon-box {
        width: 58px;
        min-width: 58px;
        height: 58px;
        border-radius: 20px;
        background: #f8eadc;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .icon-img {
        width: 45px;
        height: 45px;
        object-fit: contain;
    }

    .emoji-icon {
        font-size: 2rem;
        line-height: 1;
    }

    .nav-text {
        flex: 1;
        min-width: 0;
    }

    .nav-title {
        font-size: 1.03rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 4px;
    }

    .nav-desc {
        font-size: 0.82rem;
        color: #8a7465;
        line-height: 1.45;
    }

    .arrow {
        color: #b28b6c;
        font-size: 1.35rem;
        font-weight: 800;
        padding-left: 2px;
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
        margin-top: 12px;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-title {
            font-size: 1.5rem;
        }

        .top-card {
            padding: 20px 17px;
        }

        .nav-card {
            min-height: 88px;
            padding: 14px 13px;
        }

        .icon-box {
            width: 52px;
            min-width: 52px;
            height: 52px;
        }

        .icon-img {
            width: 40px;
            height: 40px;
        }

        .nav-title {
            font-size: 0.98rem;
        }

        .nav-desc {
            font-size: 0.79rem;
        }
    }
</style>
""",
    unsafe_allow_html=True
)


# =========================
# 表示用関数
# =========================
def render_top_visual():
    top_img = load_asset("top_visual.png")

    if top_img:
        st.markdown(
            f"""
<div class="top-visual-wrap">
    <img class="top-visual" src="{top_img}" alt="ShufuMateトップ画像">
</div>
""",
            unsafe_allow_html=True
        )


def render_nav_card(title, desc, icon_file, emoji, href):
    icon_src = load_home_icon(icon_file)

    safe_title = html.escape(title)
    safe_desc = html.escape(desc)
    safe_href = html.escape(href)

    if icon_src:
        icon_html = f'<img class="icon-img" src="{icon_src}" alt="{safe_title}">'
    else:
        icon_html = f'<div class="emoji-icon">{html.escape(emoji)}</div>'

    st.markdown(
        f"""
<a class="nav-card" href="{safe_href}" target="_self">
    <div class="icon-box">
        {icon_html}
    </div>
    <div class="nav-text">
        <div class="nav-title">{safe_title}</div>
        <div class="nav-desc">{safe_desc}</div>
    </div>
    <div class="arrow">›</div>
</a>
""",
        unsafe_allow_html=True
    )


# =========================
# トップページ本体
# =========================
render_top_visual()

login_user = get_login_user()
user_text = f"{login_user} さん、" if login_user else ""

st.markdown(
    f"""
<div class="top-card">
    <div class="date-pill">{japanese_date()}</div>
    <div class="main-title">🌿 ShufuMate</div>
    <div class="main-message">
        {html.escape(user_text)}{greeting()}。<br>
        今日の食事・運動・記録・相談を、ここからまとめて始められます。
    </div>
</div>
""",
    unsafe_allow_html=True
)


st.markdown(
    """
<div class="recommend-box">
    <div class="recommend-title">🌸 今日のおすすめ</div>
    <div class="recommend-text">
        まずは「記録する」から今日の体調や食事を残してみましょう。<br>
        無理に完璧を目指さなくて大丈夫。続けられることが一番です。
    </div>
</div>
""",
    unsafe_allow_html=True
)


st.markdown('<div class="section-title">メニュー</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">使いたいメニューを選んでください。</div>',
    unsafe_allow_html=True
)


# =========================
# カードメニュー
# =========================
cards = [
    {
        "title": "記録する",
        "desc": "体重・体脂肪・食事・体調を記録します",
        "icon": "note.png",
        "emoji": "📝",
        "href": page_url("2_記録する"),
    },
    {
        "title": "写真で記録",
        "desc": "食事写真からかんたんに記録します",
        "icon": "camera.png",
        "emoji": "📷",
        "href": page_url("4_写真で記録"),
    },
    {
        "title": "相談する",
        "desc": "今日の食事・運動・体調を相談できます",
        "icon": "chat.png",
        "emoji": "💬",
        "href": page_url("3_相談する"),
    },
    {
        "title": "設定",
        "desc": "目標体重・体質・生活スタイルを設定します",
        "icon": "settings.png",
        "emoji": "⚙️",
        "href": page_url("1_設定"),
    },
    {
        "title": "献立",
        "desc": "家族も満足する献立を考えます",
        "icon": "food.png",
        "emoji": "🍽️",
        "href": page_url("3_相談する"),
    },
    {
        "title": "買い物",
        "desc": "献立に合わせた買い物メモを作ります",
        "icon": "cart.png",
        "emoji": "🛒",
        "href": page_url("3_相談する"),
    },
    {
        "title": "運動",
        "desc": "ヨガ・ピラティス・ストレッチを提案します",
        "icon": "exercise.png",
        "emoji": "🏃‍♀️",
        "href": page_url("3_相談する"),
    },
    {
        "title": "ホーム",
        "desc": "トップページに戻ります",
        "icon": "home.png",
        "emoji": "💻",
        "href": page_url("home"),
    },
]


cols = st.columns(2)

for i, card in enumerate(cards):
    with cols[i % 2]:
        render_nav_card(
            title=card["title"],
            desc=card["desc"],
            icon_file=card["icon"],
            emoji=card["emoji"],
            href=card["href"],
        )


st.markdown(
    """
<div class="bottom-message">
    今日できることを1つだけ選べば大丈夫です。<br>
    記録だけでも、相談だけでも、ShufuMateが少しずつ整えていきます。
</div>
""",
    unsafe_allow_html=True
)
