import streamlit as st
from datetime import datetime
from app_core import (
    require_login,
    load_user_settings,
    load_current_user_profile,
    jst_now,
)

# 既存の保存関数が app_core にある場合はそれを使う
try:
    from app_core import load_diet_logs, upsert_diet_log
    HAS_DIET_LOG_API = True
except Exception:
    HAS_DIET_LOG_API = False


st.set_page_config(
    page_title="記録する | ShufuMate",
    page_icon="📝",
    layout="centered",
)

require_login()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 920px;
    }

    .page-hero {
        background: linear-gradient(135deg, #fff8f2 0%, #f7ede4 100%);
        border: 1px solid #ead8c8;
        border-radius: 24px;
        padding: 20px 18px 16px 18px;
        margin-bottom: 16px;
        box-shadow: 0 6px 18px rgba(120, 90, 60, 0.08);
    }

    .page-hero-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #5c4432;
        margin-bottom: 6px;
    }

    .page-hero-sub {
        color: #7a6250;
        line-height: 1.6;
    }

    .section-card {
        background: #fffaf6;
        border: 1px solid #ead8c8;
        border-radius: 18px;
        padding: 16px 14px;
        margin-top: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #5c4432;
        margin-bottom: 10px;
    }

    button[data-testid="stBaseButton-primary"] {
        background: #E49858 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 14px !important;
        min-height: 50px !important;
        box-shadow: 0 10px 20px rgba(228, 152, 88, 0.28) !important;
    }

    button[data-testid="stBaseButton-primary"]:hover {
        background: #DA8A47 !important;
        color: #ffffff !important;
    }

    .hint-box {
        background: #fffaf4;
        border: 1px dashed #e7d5c0;
        border-radius: 14px;
        padding: 10px 11px;
        color: #6b6055;
        font-size: 0.84rem;
        line-height: 1.55;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_common_state(settings: dict):
    defaults = {
        "common_gender": settings.get("common_gender", "未選択"),
        "common_age": int(settings.get("common_age", 40)),
        "common_height": float(settings.get("common_height", 160.0)),
        "common_weight": float(settings.get("common_weight", 50.0)),
        "common_target_weight": float(settings.get("common_target_weight", 48.0)),
        "common_body_fat": float(settings.get("common_body_fat", 28.0)),
        "common_target_body_fat": float(settings.get("common_target_body_fat", 24.0)),
        "common_muscle_mass": float(settings.get("common_muscle_mass", 35.0)),
        "common_target_muscle_mass": float(settings.get("common_target_muscle_mass", 38.0)),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "record_notes_by_date" not in st.session_state:
        st.session_state["record_notes_by_date"] = {}


def get_today_note_defaults(date_str: str):
    saved = st.session_state["record_notes_by_date"].get(date_str, {})

    food_default = saved.get("food_memo", "").strip()
    if not food_default:
        food_default = "朝：\n昼：\n夜：\n間食："

    return {
        "food_memo": food_default,
        "exercise_memo": saved.get("exercise_memo", ""),
        "condition_note": saved.get("condition_note", ""),
        "mood_note": saved.get("mood_note", ""),
    }


def save_today_notes(date_str: str, food_memo: str, exercise_memo: str, condition_note: str, mood_note: str):
    st.session_state["record_notes_by_date"][date_str] = {
        "food_memo": food_memo,
        "exercise_memo": exercise_memo,
        "condition_note": condition_note,
        "mood_note": mood_note,
    }


def render_body_inputs():
    gender = st.selectbox(
        "性別（任意）",
        ["未選択", "女性", "男性", "その他", "回答しない"],
        key="common_gender",
    )
    age = st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    height_cm = st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    weight = st.number_input("現在の体重（kg）", min_value=35.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    target_weight = st.number_input("目標体重（kg）", min_value=35.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
    body_fat = st.number_input("体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    target_body_fat = st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")
    muscle_mass = st.number_input("筋肉量（kg）", min_value=10.0, max_value=80.0, step=0.1, format="%.1f", key="common_muscle_mass")
    target_muscle_mass = st.number_input("目標筋肉量（kg）", min_value=10.0, max_value=80.0, step=0.1, format="%.1f", key="common_target_muscle_mass")
    return gender, age, height_cm, weight, target_weight, body_fat, target_body_fat, muscle_mass, target_muscle_mass


settings = load_user_settings() or {}
profile = load_current_user_profile() or {}
init_common_state(settings)

now = jst_now()
today_str = now.strftime("%Y-%m-%d")
today_jp = now.strftime("%Y年%m月%d日")
nickname = (profile.get("nickname") or settings.get("nickname") or "").strip()

notes_default = get_today_note_defaults(today_str)

st.markdown(
    f"""
    <div class="page-hero">
        <div class="page-hero-title">📝 記録する</div>
        <div class="page-hero-sub">
            {nickname + "さん、" if nickname else ""}今日はどんな1日でしたか？<br>
            数値とメモをまとめて残せます。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"対象日：{today_jp}")

with st.container():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📏 体の記録</div>', unsafe_allow_html=True)

    gender, age, height_cm, weight, target_weight, body_fat, target_body_fat, muscle_mass, target_muscle_mass = render_body_inputs()

    bmi = weight / ((height_cm / 100) ** 2)
    bmr = weight * 22 * 1.5
    goal_calories = round(bmr, 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("BMI", f"{bmi:.1f}")
    with c2:
        st.metric("基礎代謝", f"{bmr:.0f} kcal")
    with c3:
        st.metric("目標摂取", f"{goal_calories:.0f} kcal")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🍽 今日のメモ</div>', unsafe_allow_html=True)

food_memo = st.text_area(
    "食事メモ",
    value=notes_default["food_memo"],
    height=180,
    placeholder="例：\n朝：納豆ごはん\n昼：お弁当\n夜：鮭と味噌汁\n間食：ヨーグルト",
)

exercise_memo = st.text_area(
    "運動メモ",
    value=notes_default["exercise_memo"],
    height=120,
    placeholder="例：ウォーキング20分、ストレッチ10分",
)

condition_note = st.text_area(
    "体調メモ",
    value=notes_default["condition_note"],
    placeholder="例：少しむくみあり、よく眠れた",
)

mood_note = st.text_area(
    "気分メモ",
    value=notes_default["mood_note"],
    placeholder="例：朝はだるかったけど午後は元気",
)

st.markdown(
    """
    <div class="hint-box">
        食事メモは最初から<br>
        朝： / 昼： / 夜： / 間食：<br>
        が入っているので、そのまま追記できます。
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    if st.button("💾 メモだけ保存", use_container_width=True):
        save_today_notes(today_str, food_memo, exercise_memo, condition_note, mood_note)
        st.success("メモを保存しました。")

with col_b:
    if st.button("📌 今日のデータを記録", use_container_width=True, type="primary"):
        save_today_notes(today_str, food_memo, exercise_memo, condition_note, mood_note)

        log = {
            "日付": today_str,
            "性別": gender,
            "年齢": age,
            "身長(cm)": height_cm,
            "体重(kg)": weight,
            "目標体重(kg)": target_weight,
            "体脂肪率(%)": body_fat,
            "目標体脂肪率(%)": target_body_fat,
            "筋肉量(kg)": muscle_mass,
            "目標筋肉量(kg)": target_muscle_mass,
            "BMI": round(bmi, 1),
            "目標摂取カロリー": goal_calories,
        }

        if HAS_DIET_LOG_API:
            upsert_diet_log(log)
            st.success("今日の数値を保存しました。メモはこの画面内にも保存しています。")
        else:
            if "diet_logs_local" not in st.session_state:
                st.session_state["diet_logs_local"] = []
            st.session_state["diet_logs_local"] = [
                x for x in st.session_state["diet_logs_local"] if x["日付"] != today_str
            ]
            st.session_state["diet_logs_local"].append(log)
            st.success("今日の数値を保存しました。")
        st.rerun()

try:
    if HAS_DIET_LOG_API:
        logs = load_diet_logs()
    else:
        logs = st.session_state.get("diet_logs_local", [])
except Exception:
    logs = []

if logs:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📘 最近の記録</div>', unsafe_allow_html=True)

    latest = logs[-1]
    c1, c2 = st.columns(2)
    with c1:
        st.metric("体重", f'{latest.get("体重(kg)", 0):.1f} kg')
    with c2:
        st.metric("体脂肪率", f'{latest.get("体脂肪率(%)", 0):.1f} %')

    st.markdown('</div>', unsafe_allow_html=True)
