import streamlit as st
from datetime import datetime
from pathlib import Path
from app_core import (
    WEEKDAY_JP,
    get_user_id,
    load_user_settings,
    get_today_advice,
    get_week_menu,
    get_today_exercise,
)

st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered",
)

# =========================
# CSS
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 760px;
    }
    .sm-hero {
        background: linear-gradient(135deg, #fffaf5 0%, #fffefe 100%);
        border: 1px solid #f1e7dc;
        border-radius: 22px;
        padding: 18px 16px 14px 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }
    .sm-hero-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sm-hero-sub {
        color: #6b6b6b;
        font-size: 0.94rem;
    }
    .sm-card {
        background: #ffffff;
        border: 1px solid #ececec;
        border-radius: 18px;
        padding: 18px 16px;
        margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .sm-title {
        font-size: 1.02rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .sm-sub {
        color: #666666;
        font-size: 0.92rem;
        margin-bottom: 0.25rem;
    }
    .sm-text {
        line-height: 1.7;
        font-size: 0.96rem;
    }
    .sm-menu-row {
        padding: 8px 0;
        border-bottom: 1px dashed #eeeeee;
        line-height: 1.6;
    }
    .sm-menu-row:last-child {
        border-bottom: none;
    }
    .sm-day {
        font-weight: 700;
        display: inline-block;
        width: 1.5rem;
    }
    .sm-label {
        display: inline-block;
        background: #f7f2ec;
        border: 1px solid #eee2d4;
        border-radius: 999px;
        padding: 4px 10px;
        margin: 2px 6px 2px 0;
        font-size: 0.84rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 表示用関数
# =========================
def show_logo():
    logo_candidates = [
        Path("assets/top/logo.png"),
        Path("assets/logo.png"),
    ]
    for logo_path in logo_candidates:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            return


def render_today_advice_card(advice: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🌿 今日のおすすめ</div>
            <div class="sm-sub"><b>食事</b></div>
            <div class="sm-text">{advice["食事"]}</div>
            <br>
            <div class="sm-sub"><b>運動</b></div>
            <div class="sm-text">{advice["運動"]}</div>
            <br>
            <div class="sm-sub"><b>ひとこと</b></div>
            <div class="sm-text">{advice["ひとこと"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_week_menu_card(menu_list: list[dict]):
    today_idx = datetime.now().weekday()
    rows = []
    for idx, item in enumerate(menu_list):
        mark = " ← 今日" if idx == today_idx else ""
        rows.append(
            f'<div class="sm-menu-row"><span class="sm-day">{item["day"]}</span> {item["menu"]}{mark}</div>'
        )

    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🍽 今週の献立</div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exercise_card(exercise: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🏃 今日の運動</div>
            <div class="sm-sub"><b>{exercise["title"]}</b></div>
            <div class="sm-text">{exercise["body"]}</div>
            <br>
            <div class="sm-text">{exercise["level_text"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# データ読込
# =========================
user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

nickname = settings["nickname"].strip()
today_text = datetime.now().strftime("%Y年%m月%d日")
weekday_text = WEEKDAY_JP[datetime.now().weekday()]

advice = get_today_advice(settings)
week_menu = get_week_menu(settings)
exercise = get_today_exercise(settings)

# =========================
# 画面
# =========================
show_logo()

st.markdown(
    f"""
    <div class="sm-hero">
        <div class="sm-hero-title">🏠 ホーム</div>
        <div class="sm-hero-sub">{today_text}（{weekday_text}）</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if nickname:
    st.subheader(f"{nickname}さん、今日のおすすめです")
else:
    st.subheader("今日のおすすめです")

st.markdown(
    f"""
    <span class="sm-label">利用タイプ：{settings['user_type']}</span>
    <span class="sm-label">活動量：{settings['activity_level']}</span>
    <span class="sm-label">食事スタイル：{settings['food_style']}</span>
    """,
    unsafe_allow_html=True,
)

render_today_advice_card(advice)
render_week_menu_card(week_menu)
render_exercise_card(exercise)

st.markdown("### つかう")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

with col2:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

with col3:
    if st.button("⚙️ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")
