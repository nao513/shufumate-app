import streamlit as st
import pandas as pd
from app_core import *

from pathlib import Path
import base64
import html
from urllib.parse import quote


# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered"
)


# -----------------
# 画像読み込み
# -----------------
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


def load_top_visual():
    root = Path(__file__).resolve().parent
    cwd = Path.cwd()

    candidates = [
        root / "assets" / "home_icons" / "top" / "top_visual.png",
        root / "assets" / "top_visual.png",
        cwd / "assets" / "home_icons" / "top" / "top_visual.png",
        cwd / "assets" / "top_visual.png",

        # フォルダごと二重に入ってしまった時の保険
        root / "assets" / "home_icons" / "top" / "assets" / "home_icons" / "top" / "top_visual.png",
        cwd / "assets" / "home_icons" / "top" / "assets" / "home_icons" / "top" / "top_visual.png",
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


def load_icon(filename):
    if not filename:
        return None

    root = Path(__file__).resolve().parent
    cwd = Path.cwd()

    candidates = [
        root / "assets" / "icons" / filename,
        cwd / "assets" / "icons" / filename,
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


def page_url(page_name):
    if page_name == "home":
        return "/"
    return "/" + quote(page_name)


def safe_text(value):
    return html.escape(str(value))


def safe_html_with_br(value):
    return html.escape(str(value)).replace("\n", "<br>")


# -----------------
# CSS
# -----------------
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fffaf4 0%, #fff4e8 45%, #fffaf4 100%);
    }

    .block-container {
        max-width: 760px;
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
    }

    .top-visual-wrap {
        width: calc(100% + 160px);
        margin-left: -80px;
        background: #ffffff;
        border-radius: 30px;
        padding: 12px;
        box-shadow: 0 10px 28px rgba(96, 65, 45, 0.12);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 20px;
    }

    .top-visual {
        width: 100%;
        border-radius: 24px;
        display: block;
    }

    .top-card {
        background: #ffffff;
        border-radius: 26px;
        padding: 22px 20px;
        box-shadow: 0 8px 24px rgba(96, 65, 45, 0.10);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 16px;
    }

    .date-pill {
        display: inline-block;
        background: #f4e5d6;
        color: #6b4c3b;
        border-radius: 999px;
        padding: 7px 14px;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 14px;
    }

    .main-message {
        font-size: 1.02rem;
        color: #7b6658;
        line-height: 1.8;
        font-weight: 600;
    }

    .status-card {
        background: #fff8ef;
        border-radius: 22px;
        padding: 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        box-shadow: 0 5px 16px rgba(96, 65, 45, 0.07);
        margin-bottom: 18px;
    }

    .status-title {
        font-size: 1.03rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 6px;
    }

    .status-text {
        font-size: 0.9rem;
        color: #7b6658;
        line-height: 1.65;
    }

    .section-subtitle {
        font-size: 0.9rem;
        color: #8a7465;
        margin-bottom: 12px;
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
        width: 38px;
        height: 38px;
        object-fit: contain;
    }

    .section-icon-state img {
        width: 44px;
        height: 44px;
    }

    .section-icon-exercise img {
        width: 40px;
        height: 40px;
    }

    .section-icon-cart img {
        width: 42px;
        height: 42px;
    }

    .section-icon-calendar img {
        width: 52px;
        height: 52px;
        transform: scale(1.6);
    }

    .section-icon-food img {
        width: 42px;
        height: 42px;
    }

    .section-icon-home img {
        width: 40px;
        height: 40px;
    }

    .section-head-emoji {
        font-size: 1.35rem;
        line-height: 1;
    }

    .section-head-title {
        font-size: 1.22rem;
        font-weight: 900;
        color: #5c4033;
        line-height: 1.2;
    }

    .sub-expander-note {
        font-size: 0.84rem;
        color: #8a7465;
        margin: -2px 0 10px 64px;
    }

    .advice-card {
        background: #eef8ef;
        border-radius: 18px;
        padding: 15px 16px;
        border: 1px solid rgba(78, 140, 82, 0.14);
        color: #316c37;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.7;
        margin-bottom: 18px;
    }

    .hint-card {
        background: #fffdf8;
        border-radius: 18px;
        padding: 15px 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        color: #6b4c3b;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.06);
    }

    .plan-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 14px 15px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.06);
        margin-bottom: 10px;
        color: #5c4033;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .small-menu-card {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #ffffff;
        border-radius: 20px;
        padding: 12px 12px;
        margin-bottom: 12px;
        min-height: 78px;
        text-decoration: none !important;
        color: inherit !important;
        box-shadow: 0 5px 15px rgba(96, 65, 45, 0.09);
        border: 1px solid rgba(139, 100, 72, 0.12);
        transition: all 0.18s ease;
    }

    .small-menu-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(96, 65, 45, 0.14);
        background: #fffdf8;
    }

    .icon-box {
        width: 48px;
        min-width: 48px;
        height: 48px;
        border-radius: 16px;
        background: #f8eadc;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .icon-img {
        width: 36px;
        height: 36px;
        object-fit: contain;
    }

    .emoji-icon {
        font-size: 1.6rem;
        line-height: 1;
    }

    .menu-text {
        flex: 1;
        min-width: 0;
    }

    .menu-title {
        font-size: 0.92rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 3px;
    }

    .menu-desc {
        font-size: 0.72rem;
        color: #8a7465;
        line-height: 1.35;
    }

    .arrow {
        color: #b28b6c;
        font-size: 1.1rem;
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
        margin-top: 16px;
    }

    div[data-testid="stRadio"] label {
        color: #5c4033;
    }

    div[data-testid="stSelectbox"] label {
        color: #5c4033;
        font-weight: 700;
    }

    @media (max-width: 900px) {
        .top-visual-wrap {
            width: 100%;
            margin-left: 0;
            padding: 10px;
            border-radius: 24px;
        }

        .top-visual {
            border-radius: 18px;
        }
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .top-card {
            padding: 20px 17px;
        }

        .main-message {
            font-size: 0.95rem;
        }

        .section-head-icon {
            width: 46px;
            min-width: 46px;
            height: 46px;
            border-radius: 15px;
        }

        .section-head-icon img {
            width: 34px;
            height: 34px;
        }

        .section-icon-state img {
            width: 38px;
            height: 38px;
        }

        .section-icon-calendar img {
            width: 48px;
            height: 48px;
            transform: scale(1.3);
        }

        .section-head-title {
            font-size: 1.08rem;
        }

        .sub-expander-note {
            margin-left: 58px;
            font-size: 0.78rem;
        }

        .small-menu-card {
            min-height: 74px;
            padding: 11px;
        }

        .icon-box {
            width: 44px;
            min-width: 44px;
            height: 44px;
        }

        .icon-img {
            width: 34px;
            height: 34px;
        }

        .menu-title {
            font-size: 0.88rem;
        }

        .menu-desc {
            font-size: 0.7rem;
        }
    }
</style>
""",
    unsafe_allow_html=True
)


# -----------------
# 表示用関数
# -----------------
def render_top_visual():
    top_img = load_top_visual()

    if top_img:
        st.markdown(
            f"""
<div class="top-visual-wrap">
    <img class="top-visual" src="{top_img}" alt="ShufuMateトップ画像">
</div>
""",
            unsafe_allow_html=True
        )
    else:
        st.warning("トップ画像が見つかりません。assets/home_icons/top/top_visual.png を確認してください。")


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


def render_menu_card(title, desc, icon_file, emoji, href):
    icon_src = load_icon(icon_file)

    safe_title = safe_text(title)
    safe_desc = safe_text(desc)
    safe_href = safe_text(href)

    if icon_src:
        icon_html = f'<img class="icon-img" src="{icon_src}" alt="{safe_title}">'
    else:
        icon_html = f'<div class="emoji-icon">{safe_text(emoji)}</div>'

    st.markdown(
        f"""
<a class="small-menu-card" href="{safe_href}" target="_self">
    <div class="icon-box">
        {icon_html}
    </div>
    <div class="menu-text">
        <div class="menu-title">{safe_title}</div>
        <div class="menu-desc">{safe_desc}</div>
    </div>
    <div class="arrow">›</div>
</a>
""",
        unsafe_allow_html=True
    )


def render_status_message(weight_goal_status):
    if weight_goal_status == "減量優先":
        return "今は目標体重に向けて、夜を少し軽めに整える提案にしています。"
    elif weight_goal_status == "落としすぎ注意":
        return "今は落としすぎに注意して、軽くしすぎない提案にしています。"
    elif weight_goal_status == "維持":
        return "今は目標体重付近なので、維持しながら整える提案にしています。"
    else:
        return "今は基本の整え提案にしています。"


def render_advice_card(text):
    st.markdown(
        f"""
<div class="advice-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


def render_hint_card(text):
    st.markdown(
        f"""
<div class="hint-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True
    )


def render_plan_card(title, body):
    st.markdown(
        f"""
<div class="plan-card">
    <strong>{safe_text(title)}</strong><br>
    {safe_html_with_br(body)}
</div>
""",
        unsafe_allow_html=True
    )


# -----------------
# ログインチェック
# -----------------
require_login()
user_id = get_user_id()


# -----------------
# 設定読み込み
# -----------------
try:
    settings = load_user_settings(user_id)
except Exception:
    settings = {}

if not isinstance(settings, dict):
    settings = {}


# -----------------
# 目標体重との距離を判定
# -----------------
def get_weight_goal_status(settings):
    try:
        current_weight = float(
            settings.get("current_weight")
            or settings.get("start_weight")
            or 0
        )
        target_weight = float(settings.get("target_weight") or 0)
    except Exception:
        return "整える"

    if current_weight <= 0 or target_weight <= 0:
        return "整える"

    diff = current_weight - target_weight

    if diff >= 1.0:
        return "減量優先"

    if diff <= -1.0:
        return "落としすぎ注意"

    return "維持"


weight_goal_status = get_weight_goal_status(settings)
user_type_for_plan = f"{settings.get('user_type', '自分向け')}｜{weight_goal_status}"


# -----------------
# 日付
# -----------------
weekday_jp = ["月", "火", "水", "木", "金", "土", "日"]
now = jst_now()
today_text = now.strftime("%Y年%m月%d日")
weekday_text = weekday_jp[now.weekday()]


# -----------------
# トップ画像
# -----------------
render_top_visual()


# -----------------
# ヘッダーカード
# -----------------
st.markdown(
    f"""
<div class="top-card">
    <div class="date-pill">📅 {today_text}（{weekday_text}）</div>
    <div class="main-message">
        こんにちは、<strong>{safe_text(user_id)} さん</strong> 😊<br>
        食事も、暮らしも、ちょうどよく。<br>
        今日の記録・相談・献立・運動をここから始められます。
    </div>
</div>
""",
    unsafe_allow_html=True
)


# -----------------
# 今日の整え方カード
# -----------------
st.markdown(
    f"""
<div class="status-card">
    <div class="status-title">今日の整え方</div>
    <div class="status-text">{safe_text(render_status_message(weight_goal_status))}</div>
</div>
""",
    unsafe_allow_html=True
)


# -----------------
# 今日の状態
# -----------------
render_section_header("今日の状態", icon_file="state.png", emoji="🌿")

mode = st.radio(
    "表示モード",
    ["かんたん", "しっかり"],
    horizontal=True,
    key="home_mode"
)

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox(
        "体調",
        ["普通", "疲れ", "むくみ"],
        key="home_state"
    )

with col2:
    weather_label = st.selectbox(
        "今日の体感",
        ["普通", "暑く感じる", "寒く感じる"],
        key="home_weather_label"
    )

weather_map = {
    "普通": "普通",
    "暑く感じる": "暑い",
    "寒く感じる": "寒い",
}
weather_value = weather_map.get(weather_label, "普通")


# -----------------
# 運動予定
# -----------------
exercise_options = [
    "ストレッチ",
    "ヨガ",
    "ピラティス",
    "ウォーキング",
    "ランニング",
    "筋トレ",
    "なし",
]

default_exercise = settings.get("workout_today", "ストレッチ")

if default_exercise == "有酸素":
    default_exercise = "ウォーキング"

if default_exercise not in exercise_options:
    default_exercise = "ストレッチ"

exercise = st.selectbox(
    "運動予定",
    exercise_options,
    index=exercise_options.index(default_exercise),
    key="home_exercise"
)


# -----------------
# 今日のプランを作成
# -----------------
try:
    today_plan = generate_full_plan(
        user_type=user_type_for_plan,
        weather=weather_value,
        state=state,
        exercise=exercise
    )
except Exception:
    today_plan = {}


# =====================
# 🌿 かんたんモード
# =====================
if mode == "かんたん":

    render_section_header("今日のおすすめ", icon_file="food.png", emoji="🌿")

    try:
        text = generate_simple_advice(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )
        render_advice_card(text)
    except Exception:
        st.warning("今日のおすすめを作成できませんでした。時間をおいてもう一度お試しください。")

    render_section_header("今日の運動ヒント", icon_file="exercise.png", emoji="🏃‍♀️")

    try:
        exercise_text = get_exercise_advice(exercise)
        render_hint_card(exercise_text)
    except Exception:
        render_hint_card("今日は無理のない範囲で、少し体を動かしましょう。")


# =====================
# 💪 しっかりモード
# =====================
else:

    render_section_header("今日のプラン", icon_file="food.png", emoji="🍽")

    st.markdown("### 🍽 食事")

    if today_plan:
        for meal_time, menu in today_plan.items():
            if meal_time == "朝":
                icon = "🌅"
            elif meal_time == "昼":
                icon = "☀️"
            elif meal_time == "夜":
                icon = "🌙"
            else:
                icon = "🍽"

            render_plan_card(f"{icon} {meal_time}", menu)
    else:
        st.info("今日の食事プランはまだありません。")

    render_section_header("今日の運動ヒント", icon_file="exercise.png", emoji="🏃‍♀️")

    try:
        exercise_text = get_exercise_advice(exercise)
        render_hint_card(exercise_text)
    except Exception:
        render_hint_card("今日は体調に合わせて、できる範囲で整えましょう。")


# -----------------
# 🛒 買い物リスト
# -----------------
st.markdown("---")

render_section_header("買い物リスト", icon_file="cart.png", emoji="🛒")
st.markdown(
    '<div class="sub-expander-note">必要なものを確認できます。</div>',
    unsafe_allow_html=True
)

with st.expander("買い物リストを開く"):

    try:
        shopping_week_plan = generate_weekly_plan(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )

        fridge_items = settings.get("fridge_items", "")

        shopping = generate_supermarket_shopping_list(
            shopping_week_plan,
            fridge_items=fridge_items
        )

        try:
            shopping = add_deals_to_shopping(shopping)
        except Exception:
            pass

        if shopping:
            shopping_rows = []

            for category, items in shopping.items():
                if items:
                    st.markdown(f"**{category}**")

                    for item in items:
                        st.checkbox(
                            item,
                            key=f"home_week_shopping_{category}_{item}"
                        )
                        shopping_rows.append({
                            "カテゴリ": category,
                            "商品": item,
                        })

            if shopping_rows:
                df = pd.DataFrame(shopping_rows)
                csv = df.to_csv(index=False).encode("utf-8-sig")

                st.download_button(
                    "📥 買い物リストCSVをダウンロード",
                    data=csv,
                    file_name="shopping_list_week.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("買い物リストはありません")

    except Exception:
        st.warning("買い物リストを作成できませんでした。時間をおいてもう一度お試しください。")


# -----------------
# 📅 1週間プラン
# -----------------
render_section_header("1週間プラン", icon_file="calendar.png", emoji="📅")
st.markdown(
    '<div class="sub-expander-note">1週間の食事プランを確認できます。</div>',
    unsafe_allow_html=True
)

with st.expander("1週間プランを開く"):

    try:
        week_plan = generate_weekly_plan(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )

        for day, day_plan in week_plan.items():
            st.markdown(f"### {day}")
            st.write(f"朝：{day_plan.get('朝', '')}")
            st.write(f"昼：{day_plan.get('昼', '')}")
            st.write(f"夜：{day_plan.get('夜', '')}")

    except Exception:
        st.warning("1週間プランを作成できませんでした。時間をおいてもう一度お試しください。")


# -----------------
# 下部メニュー
# -----------------
render_section_header("メニュー", icon_file="home.png", emoji="💻")
st.markdown(
    '<div class="section-subtitle">よく使うページへ移動できます。</div>',
    unsafe_allow_html=True
)

cards = [
    {
        "title": "記録する",
        "desc": "体重・食事・体調を記録",
        "icon": "note.png",
        "emoji": "📝",
        "href": page_url("2_記録する"),
    },
    {
        "title": "相談する",
        "desc": "食事・運動・体調を相談",
        "icon": "chat.png",
        "emoji": "💬",
        "href": page_url("3_相談する"),
    },
    {
        "title": "写真で記録",
        "desc": "食事写真から記録",
        "icon": "camera.png",
        "emoji": "📷",
        "href": page_url("4_写真で記録"),
    },
    {
        "title": "設定",
        "desc": "目標・体質を設定",
        "icon": "settings.png",
        "emoji": "⚙️",
        "href": page_url("1_設定"),
    },
]

cols = st.columns(2)

for i, card in enumerate(cards):
    with cols[i % 2]:
        render_menu_card(
            title=card["title"],
            desc=card["desc"],
            icon_file=card["icon"],
            emoji=card["emoji"],
            href=card["href"],
        )


# -----------------
# 下部メッセージ
# -----------------
st.markdown(
    """
<div class="bottom-message">
    今日できることを1つだけ選べば大丈夫です。<br>
    記録だけでも、相談だけでも、ShufuMateが少しずつ整えていきます。
</div>
""",
    unsafe_allow_html=True
)


# -----------------
# ログアウト
# -----------------
st.markdown("---")

if st.button("ログアウト", use_container_width=True):
    logout()
    st.rerun()
