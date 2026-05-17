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


def page_url(page_name):
    if page_name == "home":
        return "/"
    return "/" + quote(page_name)


# -----------------
# CSS
# -----------------
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fffaf4 0%, #fff5eb 45%, #fffaf4 100%);
    }

    .block-container {
        max-width: 780px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
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

    .status-card {
        background: #fff8ef;
        border-radius: 22px;
        padding: 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        box-shadow: 0 5px 16px rgba(96, 65, 45, 0.07);
        margin-bottom: 18px;
    }

    .status-title {
        font-size: 1.05rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 6px;
    }

    .status-text {
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

    .soft-box {
        background: #ffffff;
        border-radius: 22px;
        padding: 16px;
        box-shadow: 0 5px 16px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 16px;
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


# -----------------
# 表示用関数
# -----------------
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


def render_status_message(weight_goal_status):
    if weight_goal_status == "減量優先":
        return "今は目標体重に向けて、夜を少し軽めに整える提案にしています。"
    elif weight_goal_status == "落としすぎ注意":
        return "今は落としすぎに注意して、軽くしすぎない提案にしています。"
    elif weight_goal_status == "維持":
        return "今は目標体重付近なので、維持しながら整える提案にしています。"
    else:
        return "今は基本の整え提案にしています。"


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
# ヘッダー
# -----------------
st.markdown(
    f"""
<div class="top-card">
    <div class="date-pill">{today_text}（{weekday_text}）</div>
    <div class="main-title">🌿 ShufuMate</div>
    <div class="main-message">
        こんにちは、<strong>{html.escape(str(user_id))} さん</strong> 😊<br>
        食事も、暮らしも、ちょうどよく。<br>
        今日の記録・相談・献立・運動をここから始められます。
    </div>
</div>
""",
    unsafe_allow_html=True
)


# -----------------
# 体重目標メッセージ
# -----------------
st.markdown(
    f"""
<div class="status-card">
    <div class="status-title">今日の整え方</div>
    <div class="status-text">{html.escape(render_status_message(weight_goal_status))}</div>
</div>
""",
    unsafe_allow_html=True
)


# -----------------
# カードメニュー
# -----------------
st.markdown('<div class="section-title">メニュー</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">使いたいメニューを選んでください。</div>',
    unsafe_allow_html=True
)

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
        "desc": "1週間分の買い物リストを確認します",
        "icon": "cart.png",
        "emoji": "🛒",
        "href": page_url("home"),
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


st.markdown("---")


# -----------------
# 表示モード
# -----------------
st.markdown("### 今日のおすすめ")

mode = st.radio(
    "表示モード",
    ["かんたん", "しっかり"],
    horizontal=True
)


# -----------------
# 今日の状態
# -----------------
st.markdown("### 🌿 今日の状態")

col1, col2 = st.columns(2)

with col1:
    state = st.selectbox(
        "体調",
        ["普通", "疲れ", "むくみ"]
    )

with col2:
    weather_label = st.selectbox(
        "今日の体感",
        ["普通", "暑く感じる", "寒く感じる"]
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
    index=exercise_options.index(default_exercise)
)

st.markdown("---")


# -----------------
# 今日のプランを先に作成
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

    st.subheader("🌿 今日のおすすめ")

    try:
        text = generate_simple_advice(
            user_type=user_type_for_plan,
            weather=weather_value,
            state=state,
            exercise=exercise
        )
        st.success(text)
    except Exception as e:
        st.warning(f"今日のおすすめを作成できませんでした: {e}")

    st.markdown("### 🏃‍♀️ 今日の運動ヒント")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は無理のない範囲で、少し体を動かしましょう。")


# =====================
# 💪 しっかりモード
# =====================
else:

    st.subheader("💪 今日のプラン")

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

            st.markdown(f"{icon} **{meal_time}：** {menu}")
    else:
        st.info("今日の食事プランはまだありません。")

    st.markdown("### 🏃‍♀️ 運動")

    try:
        st.write(get_exercise_advice(exercise))
    except Exception:
        st.write("今日は体調に合わせて、できる範囲で整えましょう。")


# -----------------
# 🛒 買い物リスト
# -----------------
st.markdown("---")

with st.expander("🛒 買い物リスト"):

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

    except Exception as e:
        st.warning(f"買い物リストを作成できませんでした: {e}")


# -----------------
# 📅 1週間プラン
# -----------------
with st.expander("📅 1週間プラン"):

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

    except Exception as e:
        st.warning(f"1週間プランを作成できませんでした: {e}")


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
