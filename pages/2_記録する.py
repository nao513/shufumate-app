import streamlit as st
import pandas as pd
from app_core import (
    require_login,
    get_user_id,
    load_user_settings,
    load_latest_log,
    get_initial_log_values,
    load_recent_logs,
    save_diet_log,
    jst_today_str,
    TODAY_CONDITION_OPTIONS,
)

st.set_page_config(
    page_title="記録する｜ShufuMate",
    page_icon="📝",
    layout="centered",
)

require_login()

user_id = get_user_id()

try:
    settings = load_user_settings(user_id) or {}
    latest_log = load_latest_log(user_id)
    initial_values = get_initial_log_values(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 760px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .sm-hero {
        background: linear-gradient(135deg, #faf6f1 0%, #fffdfa 100%);
        border: 1px solid #eadfd3;
        border-radius: 22px;
        padding: 10px 16px 8px 16px;
        margin-top: 0.3rem;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }

    .sm-hero-sub {
        color: #6d645d;
        font-size: 0.92rem;
        line-height: 1.5;
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

    .sm-note {
        background: #fffaf4;
        border: 1px dashed #e7d5c0;
        border-radius: 14px;
        padding: 10px 11px;
        margin: 8px 0 12px 0;
        color: #6b6055;
        font-size: 0.84rem;
        line-height: 1.55;
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

    .sm-mini-grid {
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

    div[data-testid="stExpander"] {
        border: 1px solid #eee3d7;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 10px;
        background: #fffdf9;
    }

    h3 {
        margin-top: 0.55rem !important;
        margin-bottom: 0.55rem !important;
        font-size: 1rem !important;
        color: #3f3834 !important;
    }

    @media (max-width: 640px) {
        .sm-mini-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nickname = (settings.get("nickname") or "").strip()
today_str = jst_today_str()

default_weight = float(initial_values.get("weight", settings.get("current_weight", 50.0)))
default_body_fat = float(initial_values.get("body_fat", settings.get("current_body_fat", 30.0)))
default_conditions = initial_values.get("today_conditions", [])

latest_date = "未記録"
if latest_log:
    latest_date = str(latest_log.get("log_date", "未記録")) or "未記録"

st.markdown(
    """
    <div class="sm-hero">
        <div class="sm-hero-sub">📝 数値やメモをまとめて記録します。写真でサッと残したい時は「写真で記録」、しっかり入力したい時はこちらがおすすめです。</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader(f"{nickname}さんの今日の記録" if nickname else "今日の記録")

st.markdown(
    f"""
    <span class="sm-label">日付：{today_str}</span>
    <span class="sm-label">最新記録日：{latest_date}</span>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="sm-card sm-card-soft">
        <div class="sm-title">基本情報</div>
        <div class="sm-sub">設定から読み込んだ内容です。今日の記録はこの情報をもとに保存されます。</div>
        <div class="sm-mini-grid" style="margin-top:10px;">
            <div class="sm-mini-card">
                <div class="sm-mini-title">身長</div>
                <div class="sm-mini-main">{float(settings.get("height_cm", 160.0)):.1f} cm</div>
            </div>
            <div class="sm-mini-card">
                <div class="sm-mini-title">目標</div>
                <div class="sm-mini-main">{float(settings.get("target_weight", 48.0)):.1f} kg / {float(settings.get("target_body_fat", 28.0)):.1f} %</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("daily_log_form"):
    st.markdown('<div class="sm-card">', unsafe_allow_html=True)
    st.markdown('<div class="sm-title">体重・体脂肪を記録</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(
            "体重(kg)",
            min_value=0.0,
            max_value=200.0,
            value=float(default_weight),
            step=0.1,
            format="%.1f",
        )
    with col2:
        body_fat = st.number_input(
            "体脂肪(%)",
            min_value=0.0,
            max_value=70.0,
            value=float(default_body_fat),
            step=0.1,
            format="%.1f",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
    st.markdown('<div class="sm-title">今日の状態</div>', unsafe_allow_html=True)
    today_conditions = st.multiselect(
        "当てはまるものを選ぶ",
        TODAY_CONDITION_OPTIONS,
        default=default_conditions,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sm-card">', unsafe_allow_html=True)
    st.markdown('<div class="sm-title">食事メモ</div>', unsafe_allow_html=True)
    meal_memo = st.text_area(
        "朝・昼・夜・間食など",
        placeholder="例：朝: 納豆ごはん、味噌汁\n昼: お弁当\n夜: 焼き魚、サラダ、ごはん少なめ\n間食: ヨーグルト",
        height=180,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("運動メモを入れる"):
        exercise_memo = st.text_area(
            "運動メモ",
            placeholder="例：散歩20分、ストレッチ10分、ヨガ45分",
            height=100,
        )

    with st.expander("体調・気分メモを入れる"):
        condition_note = st.text_area(
            "体調メモ",
            placeholder="例：むくみあり、少し疲れ気味、胃が重い",
            height=90,
        )
        mood_note = st.text_area(
            "気分メモ",
            placeholder="例：前向き、少しだるい、やる気が出にくい",
            height=90,
        )

    st.markdown(
        """
        <div class="sm-note">
        食事は完璧でなくても大丈夫です。朝・昼・夜・間食がざっくり分かるだけでも、次の提案につながりやすくなります。
        </div>
        """,
        unsafe_allow_html=True,
    )

    submitted = st.form_submit_button("📝 今日の記録を保存する", use_container_width=True)

if submitted:
    save_data = {
        "log_date": today_str,
        "weight": float(weight),
        "body_fat": float(body_fat),
        "meal_memo": meal_memo.strip(),
        "exercise_memo": exercise_memo.strip(),
        "condition_note": condition_note.strip(),
        "mood_note": mood_note.strip(),
        "today_conditions": today_conditions,
    }

    try:
        save_diet_log(user_id, save_data)
        st.success("今日の記録を保存しました。")
        st.rerun()
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")

st.markdown(
    """
    <div class="sm-note">
    朝は起きてから2時間以内、間食は夕方まで、夜は寝る直前を避けると整えやすいです。
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
st.markdown('<div class="sm-title">最近の記録</div>', unsafe_allow_html=True)

try:
    recent_df = load_recent_logs(user_id, limit=10)
except Exception:
    recent_df = pd.DataFrame()

if recent_df is not None and not recent_df.empty:
    st.dataframe(recent_df, use_container_width=True, hide_index=True)
else:
    st.caption("まだ記録はありません。")

st.markdown("</div>", unsafe_allow_html=True)
