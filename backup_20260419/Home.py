import streamlit as st
from pathlib import Path
from app_core import (
    WEEKDAY_JP,
    require_login,
    logout_user,
    load_user_settings,
    load_current_user_profile,
    load_latest_log,
    get_today_advice,
    get_week_menu,
    get_today_exercise,
    get_home_progress_summary,
    get_today_log_status,
    get_week_goal,
    get_log_streak_summary,
    get_support_focus_summary,
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
        padding-bottom: 1.8rem;
        max-width: 760px;
    }
    .sm-top-visual {
        margin: 0.3rem 0 1rem 0;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #eadfd2;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }
    .sm-hero {
        background: linear-gradient(135deg, #fff9f3 0%, #fffdf9 100%);
        border: 1px solid #f0e4d8;
        border-radius: 20px;
        padding: 14px 14px 11px 14px;
        margin-top: 0.2rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
    }
    .sm-hero-title {
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .sm-hero-sub {
        color: #6b6b6b;
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .sm-card {
        background: #ffffff;
        border: 1px solid #eee5db;
        border-radius: 18px;
        padding: 14px 13px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .sm-card-soft {
        background: #fffdf9;
    }
    .sm-focus-card {
        background: #fffaf5;
        border: 1px solid #efdfcd;
    }
    .sm-goal-card {
        background: #fffaf5;
        border: 1px solid #efdfcd;
    }
    .sm-streak-on {
        background: #f5fbff;
        border: 1px solid #d9eaf5;
    }
    .sm-streak-off {
        background: #fcfbff;
        border: 1px solid #e8e2f2;
    }
    .sm-status-ok {
        background: #f6fcf7;
        border: 1px solid #d7eadc;
    }
    .sm-status-ng {
        background: #fffaf5;
        border: 1px solid #efdfcd;
    }
    .sm-title {
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .sm-sub {
        color: #6b6b6b;
        font-size: 0.86rem;
        line-height: 1.45;
    }
    .sm-text {
        line-height: 1.65;
        font-size: 0.92rem;
    }
    .sm-label {
        display: inline-block;
        background: #faf5ee;
        border: 1px solid #eadfd1;
        border-radius: 999px;
        padding: 4px 9px;
        margin: 2px 5px 2px 0;
        font-size: 0.78rem;
    }
    .sm-menu-row {
        padding: 7px 0;
        border-bottom: 1px dashed #eee7dd;
        line-height: 1.6;
        font-size: 0.92rem;
    }
    .sm-menu-row:last-child {
        border-bottom: none;
    }
    .sm-day {
        font-weight: 700;
        display: inline-block;
        width: 1.5rem;
    }
    .sm-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    .sm-mini-card {
        background: #fffdf9;
        border: 1px solid #eee7dc;
        border-radius: 14px;
        padding: 12px 11px;
    }
    .sm-mini-title {
        font-size: 0.8rem;
        color: #666666;
        margin-bottom: 0.25rem;
    }
    .sm-mini-main {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }
    .sm-mini-sub {
        font-size: 0.82rem;
        color: #666666;
        line-height: 1.4;
    }
    .sm-note {
        background: #fffaf5;
        border: 1px dashed #ead7bf;
        border-radius: 14px;
        padding: 10px 11px;
        margin: 8px 0 10px 0;
        color: #6d6152;
        font-size: 0.84rem;
        line-height: 1.55;
    }
    .sm-use-card {
        background: #fffdf9;
        border: 1px solid #eee3d7;
        border-radius: 18px;
        padding: 14px 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 10px;
        min-height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .sm-use-icon {
        font-size: 1.7rem;
        text-align: center;
        margin-top: 0.2rem;
        margin-bottom: 0.45rem;
    }
    .sm-use-title {
        font-size: 0.92rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.15rem;
    }
    .sm-use-sub {
        font-size: 0.8rem;
        color: #6f6f6f;
        line-height: 1.4;
        text-align: center;
        min-height: 2.8em;
        margin-bottom: 0.55rem;
    }
    .sm-compact-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
    }
    .sm-compact-box {
        background: #fffdf9;
        border: 1px solid #eee6da;
        border-radius: 12px;
        padding: 9px 10px;
    }
    .sm-compact-head {
        font-size: 0.78rem;
        color: #746a60;
        margin-bottom: 0.15rem;
    }
    .sm-compact-body {
        font-size: 0.84rem;
        line-height: 1.45;
    }
    .stButton > button {
        border-radius: 12px !important;
        min-height: 42px;
        border: 1px solid #e7d8c8 !important;
        width: 100%;
        font-size: 0.92rem !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #eee3d7;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 10px;
        background: #fffdf9;
    }
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.55rem !important;
        font-size: 1rem !important;
    }
    @media (max-width: 640px) {
        .sm-grid {
            grid-template-columns: 1fr;
        }
        .sm-compact-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_logo():
    for logo_path in [Path("assets/top/logo.png"), Path("assets/logo.png")]:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            return


def show_top_visual():
    visual_path = Path("assets/top/top_visual.png")
    if visual_path.exists():
        st.markdown('<div class="sm-top-visual">', unsafe_allow_html=True)
        st.image(str(visual_path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_status_card(status: dict):
    card_class = "sm-status-ok" if status["is_logged"] else "sm-status-ng"
    icon = "✅" if status["is_logged"] else "🕒"
    st.markdown(
        f"""
        <div class="sm-card {card_class}">
            <div class="sm-title">{icon} 今日の記録</div>
            <div class="sm-text"><b>{status["label"]}</b></div>
            <div class="sm-sub" style="margin-top:6px;">{status["detail"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_streak_card(streak: dict):
    card_class = "sm-streak-on" if streak["is_active"] else "sm-streak-off"
    icon = "🔥" if streak["is_active"] else "📝"
    st.markdown(
        f"""
        <div class="sm-card {card_class}">
            <div class="sm-title">{icon} 連続記録</div>
            <div class="sm-text"><b>{streak["label"]}</b></div>
            <div class="sm-sub" style="margin-top:6px;">{streak["detail"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_focus_card(focus: dict):
    st.markdown(
        f"""
        <div class="sm-card sm-focus-card">
            <div class="sm-title">🧭 今のポイント</div>
            <div class="sm-text">{focus["body"].replace(chr(10), "<br>")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_week_goal_card(goal: dict):
    st.markdown(
        f"""
        <div class="sm-card sm-goal-card">
            <div class="sm-title">🎯 今週の目標</div>
            <div class="sm-text">{goal["body"].replace(chr(10), "<br>")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_today_card(advice: dict, exercise: dict):
    st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
    st.markdown('<div class="sm-title">🌿 今日のおすすめ</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sm-compact-grid">
            <div class="sm-compact-box">
                <div class="sm-compact-head">食事</div>
                <div class="sm-compact-body">{advice["食事"]}</div>
            </div>
            <div class="sm-compact-box">
                <div class="sm-compact-head">運動</div>
                <div class="sm-compact-body">{exercise["title"]}</div>
            </div>
            <div class="sm-compact-box">
                <div class="sm-compact-head">ひとこと</div>
                <div class="sm-compact-body">{advice["ひとこと"]}</div>
            </div>
            <div class="sm-compact-box">
                <div class="sm-compact-head">強度</div>
                <div class="sm-compact-body">{exercise["level_text"]}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_progress_card(summary: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">📊 最新の記録</div>
            <div class="sm-sub">最新記録日：{summary["latest_date"]}</div>
            <div class="sm-grid" style="margin-top:10px;">
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
    rows = []
    today_idx = now.weekday()
    for idx, item in enumerate(menu_list):
        mark = " ← 今日" if idx == today_idx else ""
        rows.append(
            f'<div class="sm-menu-row"><span class="sm-day">{item["day"]}</span> {item["menu"]}{mark}</div>'
        )

    st.markdown(
        f"""
        <div class="sm-card sm-card-soft">
            <div class="sm-title">🍽 今週の献立</div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_nav_card(icon: str, title: str, subtitle: str):
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


profile = load_current_user_profile()
user_id = profile["user_id"] if profile else ""
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)
progress = get_home_progress_summary(user_id)
today_status = get_today_log_status(user_id)
streak = get_log_streak_summary(user_id)
week_goal = get_week_goal(settings, progress)
focus = get_support_focus_summary(settings, latest_log)

now = jst_now()
nickname = profile["nickname"].strip() if profile else settings["nickname"].strip()
today_text = now.strftime("%Y年%m月%d日")
weekday_text = WEEKDAY_JP[now.weekday()]

advice = get_today_advice(settings, latest_log)
week_menu = get_week_menu(settings)
exercise = get_today_exercise(settings, latest_log)

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

st.subheader(f"{nickname}さん、今日は何から始めますか？" if nickname else "今日は何から始めますか？")

st.markdown(
    f"""
    <span class="sm-label">利用タイプ：{settings['user_type']}</span>
    <span class="sm-label">活動量：{settings['activity_level']}</span>
    <span class="sm-label">食事：{settings['food_style']}</span>
    """,
    unsafe_allow_html=True,
)

st.markdown("### つかう")

col1, col2 = st.columns(2)
with col1:
    render_nav_card("📷", "写真で記録", "写真からサッと残す")
    if st.button("写真で記録", use_container_width=True, key="go_photo"):
        st.switch_page("pages/4_写真で記録.py")

with col2:
    render_nav_card("📝", "記録する", "数値やメモを入力する")
    if st.button("記録する", use_container_width=True, key="go_log"):
        st.switch_page("pages/2_記録する.py")

col3, col4 = st.columns(2)
with col3:
    render_nav_card("💬", "相談する", "食事や運動を相談する")
    if st.button("相談する", use_container_width=True, key="go_advice"):
        st.switch_page("pages/3_相談する.py")

with col4:
    render_nav_card("⚙️", "設定", "体質や目標を整える")
    if st.button("設定", use_container_width=True, key="go_settings"):
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

render_compact_today_card(advice, exercise)

with st.expander("今日の記録・流れを見る"):
    render_status_card(today_status)
    render_streak_card(streak)

with st.expander("今のポイント・今週の目標を見る"):
    render_focus_card(focus)
    render_week_goal_card(week_goal)

with st.expander("最新の記録・今週の献立を見る"):
    render_progress_card(progress)
    render_week_menu_card(week_menu, now)
