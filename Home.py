import streamlit as st
from pathlib import Path
from app_core import (
    WEEKDAY_JP,
    require_login,
    get_user_id,
    logout_user,
    load_user_settings,
    load_current_user_profile,
    get_today_advice,
    get_week_menu,
    get_today_exercise,
    get_home_progress_summary,
    get_today_log_status,
    jst_now,
)

st.set_page_config(
    page_title="ShufuMate",
    page_icon="💻",
    layout="centered",
)

require_login()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 760px;
    }

    .sm-top-visual {
        margin: 0.25rem 0 1rem 0;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #e8ddd1;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }

    .sm-hero {
        background: linear-gradient(135deg, #faf6f1 0%, #fffdfa 100%);
        border: 1px solid #eadfd3;
        border-radius: 22px;
        padding: 16px 16px 13px 16px;
        margin-top: 0.4rem;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }

    .sm-hero-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        color: #3f3834;
    }

    .sm-hero-sub {
        color: #6d645d;
        font-size: 0.92rem;
    }

    .sm-card {
        background: #ffffff;
        border: 1px solid #ece4db;
        border-radius: 18px;
        padding: 16px 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .sm-card-soft {
        background: #fffdf9;
    }

    .sm-status-ok {
        background: #f7fbf8;
        border: 1px solid #d8eadb;
    }

    .sm-status-ng {
        background: #fffaf5;
        border: 1px solid #eedecd;
    }

    .sm-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.7rem;
        color: #3f3834;
    }

    .sm-sub {
        color: #6d645d;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
        line-height: 1.5;
    }

    .sm-text {
        line-height: 1.7;
        font-size: 0.95rem;
        color: #403935;
    }

    .sm-label {
        display: inline-block;
        background: #f7f1e9;
        border: 1px solid #eadfce;
        border-radius: 999px;
        padding: 4px 10px;
        margin: 2px 6px 2px 0;
        font-size: 0.82rem;
        color: #554d47;
    }

    .sm-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }

    .sm-mini-card {
        background: #fffdf9;
        border: 1px solid #eee5da;
        border-radius: 16px;
        padding: 14px 12px;
    }

    .sm-mini-title {
        font-size: 0.86rem;
        color: #6d645d;
        margin-bottom: 0.3rem;
    }

    .sm-mini-main {
        font-size: 1.18rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #3f3834;
    }

    .sm-mini-sub {
        font-size: 0.87rem;
        color: #6d645d;
        line-height: 1.5;
    }

    .sm-menu-row {
        padding: 8px 0;
        border-bottom: 1px dashed #eee5da;
        line-height: 1.6;
        color: #403935;
    }

    .sm-menu-row:last-child {
        border-bottom: none;
    }

    .sm-day {
        font-weight: 700;
        display: inline-block;
        width: 1.5rem;
    }

    .sm-use-card {
        background: #fffdf9;
        border: 1px solid #ece2d6;
        border-radius: 18px;
        padding: 14px 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        min-height: 100%;
    }

    .sm-use-icon {
        font-size: 1.55rem;
        text-align: center;
        margin-bottom: 0.4rem;
    }

    .sm-use-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
        color: #3f3834;
    }

    .sm-use-sub {
        font-size: 0.82rem;
        color: #6d645d;
        line-height: 1.45;
        text-align: center;
        min-height: 2.6em;
        margin-bottom: 0.55rem;
    }

    .sm-note {
        background: #fffaf4;
        border: 1px dashed #e7d5c0;
        border-radius: 14px;
        padding: 10px 11px;
        margin: 6px 0 12px 0;
        color: #6b6055;
        font-size: 0.84rem;
        line-height: 1.55;
    }

    .stButton > button {
        border-radius: 12px !important;
        min-height: 42px;
        border: 1px solid #e2d2c1 !important;
        width: 100%;
        font-size: 0.92rem !important;
        background: #fffdfa !important;
        color: #4a4039 !important;
    }

    .stButton > button:hover {
        border: 1px solid #d6c2ae !important;
        background: #faf5ef !important;
    }

    h3 {
        margin-top: 0.55rem !important;
        margin-bottom: 0.55rem !important;
        font-size: 1rem !important;
        color: #3f3834 !important;
    }

    @media (max-width: 640px) {
        .sm-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_logo():
    logo_candidates = [
        Path("assets/top/logo.png"),
        Path("assets/logo.png"),
    ]
    for logo_path in logo_candidates:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            return


def show_top_visual():
    visual_path = Path("assets/top/top_visual.png")
    if visual_path.exists():
        st.markdown('<div class="sm-top-visual">', unsafe_allow_html=True)
        st.image(str(visual_path), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_today_advice_card(advice: dict):
    st.markdown(
        f"""
        <div class="sm-card sm-card-soft">
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


def render_status_card(status: dict):
    card_class = "sm-status-ok" if status["is_logged"] else "sm-status-ng"
    icon = "✅" if status["is_logged"] else "🕒"

    st.markdown(
        f"""
        <div class="sm-card {card_class}">
            <div class="sm-title">{icon} 今日の記録状況</div>
            <div class="sm-text"><b>{status["label"]}</b></div>
            <div class="sm-sub" style="margin-top:8px;">{status["detail"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_card(summary: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">📊 最新の記録</div>
            <div class="sm-sub">最新記録日：{summary["latest_date"]}</div>
            <div class="sm-grid" style="margin-top:12px;">
                <div class="sm-mini-card">
                    <div class="sm-mini-title">体重</div>
                    <div class="sm-mini-main">{summary["latest_weight"]:.1f} kg</div>
                    <div class="sm-mini-sub">{summary["weight_text"]}</div>
                </div>
                <div class="sm-mini-card">
                    <div class="sm-mini-title">体脂肪</div>
                    <div class="sm-mini-main">{summary["latest_body_fat"]:.1f} %</div>
                    <div class="sm-mini-sub">{summary["body_fat_text"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_week_menu_card(menu_list: list[dict], now):
    today_idx = now.weekday()
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


def render_use_card(icon: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="sm-use-card">
            <div class="sm-use-icon">{icon}</div>
            <div class="sm-use-title">{title}</div>
            <div class="sm-use-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
    profile = load_current_user_profile()
    progress = get_home_progress_summary(user_id)
    today_status = get_today_log_status(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

now = jst_now()
nickname = profile["nickname"].strip() if profile else settings["nickname"].strip()
today_text = now.strftime("%Y年%m月%d日")
weekday_text = WEEKDAY_JP[now.weekday()]

advice = get_today_advice(settings)
week_menu = get_week_menu(settings)
exercise = get_today_exercise(settings)

top1, top2 = st.columns([3, 1])

with top1:
    show_logo()

with top2:
    if st.button("ログアウト", use_container_width=True):
        logout_user()
        st.switch_page("pages/0_ログイン.py")

show_top_visual()

st.markdown(
    f"""
    <div class="sm-hero">
        <div class="sm-hero-title">💻 ホーム</div>
        <div class="sm-hero-sub">{today_text}（{weekday_text}）</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if nickname:
    st.subheader(f"{nickname}さん、今日は何から始めますか？")
else:
    st.subheader("今日は何から始めますか？")

st.markdown(
    f"""
    <span class="sm-label">利用タイプ：{settings['user_type']}</span>
    <span class="sm-label">活動量：{settings['activity_level']}</span>
    <span class="sm-label">食事スタイル：{settings['food_style']}</span>
    """,
    unsafe_allow_html=True,
)

st.markdown("### つかう")

col1, col2 = st.columns(2)
with col1:
    render_use_card("📷", "写真で記録", "写真からサッと残す")
    if st.button("📷 写真で記録", use_container_width=True, key="go_photo"):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    render_use_card("📝", "記録する", "数値やメモを入力する")
    if st.button("📝 記録する", use_container_width=True, key="go_log"):
        st.switch_page("pages/2_記録する.py")

col3, col4 = st.columns(2)
with col3:
    render_use_card("💬", "相談する", "食事や運動を相談する")
    if st.button("💬 相談する", use_container_width=True, key="go_advice"):
        st.switch_page("pages/3_相談する.py")

with col4:
    render_use_card("⚙️ 設定", "設定", "体質や目標を整える")
    if st.button("⚙️ 設定", use_container_width=True, key="go_settings"):
        st.switch_page("pages/1_設定.py")

st.markdown(
    """
    <div class="sm-note">
    写真でサッと残したい時は「写真で記録」、
    しっかり入力したい時は「記録する」がおすすめです。
    </div>
    """,
    unsafe_allow_html=True,
)

render_status_card(today_status)
render_today_advice_card(advice)
render_progress_card(progress)
render_week_menu_card(week_menu, now)
render_exercise_card(exercise)
