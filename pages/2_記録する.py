import streamlit as st
import pandas as pd
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html
from datetime import date


# =========================
# パス・アイコン設定
# =========================
THIS_FILE = Path(__file__).resolve()

if THIS_FILE.parent.name == "pages":
    APP_ROOT = THIS_FILE.parent.parent
else:
    APP_ROOT = THIS_FILE.parent

ICON_DIR = APP_ROOT / "assets" / "icons"


def get_page_icon(filename, fallback="📝"):
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
    page_title="記録する｜ShufuMate",
    page_icon=get_page_icon("note.png", "📝"),
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


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(str(value).replace(",", "").replace("'", ""))
    except Exception:
        return float(default)


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

    .card {
        background: #ffffff;
        border-radius: 24px;
        padding: 20px 18px;
        box-shadow: 0 6px 18px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
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

    .metric-card {
        background: #fff8ef;
        border-radius: 18px;
        padding: 14px 15px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        color: #5c4033;
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 10px;
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

    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label,
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
def render_page_header(title, subtitle, icon_file="note.png"):
    icon_src = load_icon(icon_file)

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = '<div class="section-head-emoji">📝</div>'

    weekday_jp = ["月", "火", "水", "木", "金", "土", "日"]
    now = jst_now()
    today_text = now.strftime("%Y年%m月%d日")
    weekday_text = weekday_jp[now.weekday()]

    st.markdown(
        f"""
<div class="top-card">
    <div class="date-pill">📅 {today_text}（{weekday_text}）</div>
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


def render_metric_card(title, body):
    st.markdown(
        f"""
<div class="metric-card">
    <strong>{safe_text(title)}</strong><br>
    {safe_html_with_br(body)}
</div>
""",
        unsafe_allow_html=True,
    )


# =========================
# app_core関数の安全呼び出し
# =========================
def try_call_function(func_name, patterns):
    func = globals().get(func_name)

    if not callable(func):
        return False, None

    last_error = None

    for args, kwargs in patterns:
        try:
            return True, func(*args, **kwargs)
        except TypeError as e:
            last_error = e
            continue
        except Exception as e:
            return False, e

    return False, last_error


def load_record_logs(user_id):
    candidates = [
        "load_diet_logs",
        "load_daily_logs",
        "load_today_logs",
        "load_user_records",
        "load_record_logs",
    ]

    for name in candidates:
        ok, result = try_call_function(
            name,
            [
                ((user_id,), {}),
                ((), {}),
            ],
        )

        if ok:
            if isinstance(result, pd.DataFrame):
                logs = result.to_dict("records")
            elif isinstance(result, list):
                logs = result
            else:
                logs = []

            return logs

    return []


def save_record_log(user_id, log):
    candidates = [
        "save_diet_log",
        "save_daily_log",
        "save_today_log",
        "save_user_record",
        "save_record_log",
        "upsert_diet_log",
    ]

    for name in candidates:
        ok, result = try_call_function(
            name,
            [
                ((user_id, log), {}),
                ((log,), {}),
            ],
        )

        if ok:
            return True, result

    return False, None


def save_settings_safely(user_id, settings):
    candidates = [
        "save_user_settings",
        "upsert_user_settings",
    ]

    for name in candidates:
        ok, result = try_call_function(
            name,
            [
                ((user_id, settings), {}),
                ((settings,), {}),
            ],
        )

        if ok:
            return True

    return False


def filter_user_logs(logs, user_id):
    if not logs:
        return []

    user_keys = ["user_id", "ユーザーID", "ユーザー", "login_id"]

    has_user_key = any(
        any(key in log for key in user_keys)
        for log in logs
        if isinstance(log, dict)
    )

    if not has_user_key:
        return logs

    filtered = []

    for log in logs:
        if not isinstance(log, dict):
            continue

        for key in user_keys:
            if str(log.get(key, "")) == str(user_id):
                filtered.append(log)
                break

    return filtered


def get_latest_value(logs, keys, default=0.0):
    if not logs:
        return default

    latest = logs[-1]

    if not isinstance(latest, dict):
        return default

    for key in keys:
        value = latest.get(key)
        if value not in [None, ""]:
            return safe_float(value, default)

    return default


# =========================
# ログインチェック
# =========================
require_login()
user_id = get_user_id()


# =========================
# 設定読み込み
# =========================
try:
    settings = load_user_settings(user_id)
except Exception:
    settings = {}

if not isinstance(settings, dict):
    settings = {}


# =========================
# 既存ログ読み込み
# =========================
all_logs = load_record_logs(user_id)
user_logs = filter_user_logs(all_logs, user_id)


# =========================
# 初期値
# =========================
default_weight = safe_float(
    settings.get("current_weight")
    or settings.get("start_weight")
    or get_latest_value(user_logs, ["体重(kg)", "体重", "weight"], 50.0),
    50.0,
)

default_body_fat = safe_float(
    settings.get("current_body_fat")
    or settings.get("body_fat")
    or get_latest_value(user_logs, ["体脂肪率(%)", "体脂肪率", "body_fat"], 25.0),
    25.0,
)

default_target_weight = safe_float(
    settings.get("target_weight")
    or get_latest_value(user_logs, ["目標体重(kg)", "目標体重", "target_weight"], 50.0),
    50.0,
)

default_target_body_fat = safe_float(
    settings.get("target_body_fat")
    or get_latest_value(user_logs, ["目標体脂肪率(%)", "目標体脂肪率", "target_body_fat"], 23.0),
    23.0,
)

default_height = safe_float(
    settings.get("height_cm")
    or settings.get("height")
    or get_latest_value(user_logs, ["身長(cm)", "身長", "height_cm"], 155.0),
    155.0,
)

default_age = int(
    safe_float(
        settings.get("age")
        or get_latest_value(user_logs, ["年齢", "age"], 50),
        50,
    )
)


# =========================
# ヘッダー
# =========================
render_page_header(
    title="記録する",
    subtitle=f"{user_id} さんの今日の体重・体調・食事・運動を記録します。",
    icon_file="note.png",
)


# =========================
# 今日の体データ
# =========================
render_section_header("今日のわたし", icon_file="state.png", emoji="⚖️")


record_date = st.date_input(
    "記録日",
    value=jst_now().date(),
    key="record_date",
)

col1, col2 = st.columns(2)

with col1:
    weight = st.number_input(
        "体重（kg）",
        min_value=0.0,
        max_value=200.0,
        value=float(default_weight),
        step=0.1,
        format="%.1f",
        key="record_weight",
    )

with col2:
    body_fat = st.number_input(
        "体脂肪率（%）",
        min_value=0.0,
        max_value=80.0,
        value=float(default_body_fat),
        step=0.1,
        format="%.1f",
        key="record_body_fat",
    )

col3, col4 = st.columns(2)

with col3:
    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=0.0,
        max_value=200.0,
        value=float(default_target_weight),
        step=0.1,
        format="%.1f",
        key="record_target_weight",
    )

with col4:
    target_body_fat = st.number_input(
        "目標体脂肪率（%）",
        min_value=0.0,
        max_value=80.0,
        value=float(default_target_body_fat),
        step=0.1,
        format="%.1f",
        key="record_target_body_fat",
    )

height_cm = st.number_input(
    "身長（cm）",
    min_value=100.0,
    max_value=220.0,
    value=float(default_height),
    step=0.1,
    format="%.1f",
    key="record_height_cm",
)

if height_cm > 0 and weight > 0:
    bmi = weight / ((height_cm / 100) ** 2)
else:
    bmi = 0.0

diff_weight = weight - target_weight if target_weight > 0 else 0.0

if target_weight > 0:
    if diff_weight >= 1.0:
        goal_message = f"目標まであと {diff_weight:.1f}kg。今日は夜を少し軽めに整えるのがおすすめです。"
    elif diff_weight <= -1.0:
        goal_message = f"目標より {abs(diff_weight):.1f}kg 軽めです。落としすぎに注意して、たんぱく質を意識しましょう。"
    else:
        goal_message = "目標体重付近です。無理に減らすより、維持しながら整える日です。"
else:
    goal_message = "目標体重を設定すると、今日の整え方が出しやすくなります。"

col5, col6 = st.columns(2)

with col5:
    render_metric_card("BMI", f"{bmi:.1f}")

with col6:
    render_metric_card("今日の整え方", goal_message)



# =========================
# 今日の状態
# =========================
render_section_header("今日の状態", icon_file="state.png", emoji="🌿")

col1, col2 = st.columns(2)

with col1:
    condition = st.selectbox(
        "体調",
        ["普通", "疲れ", "むくみ", "冷え", "肩こり", "食べすぎ", "寝不足"],
        key="record_condition",
    )

with col2:
    mood = st.selectbox(
        "気分",
        ["普通", "元気", "少しだるい", "イライラ", "落ち込み気味", "すっきり"],
        key="record_mood",
    )

sleep_hours = st.number_input(
    "睡眠時間（時間）",
    min_value=0.0,
    max_value=24.0,
    value=safe_float(settings.get("sleep_hours"), 7.0),
    step=0.5,
    format="%.1f",
    key="record_sleep_hours",
)

body_memo = st.text_area(
    "体調メモ",
    placeholder="例：朝から少しむくみ。肩こりあり。体は軽い。",
    height=100,
    key="record_body_memo",
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 食事記録
# =========================
render_section_header("食事の記録", icon_file="food.png", emoji="🍽️")

breakfast = st.text_area(
    "朝ごはん",
    placeholder="例：白湯、納豆、ごはん、味噌汁、ブルーベリー",
    height=90,
    key="record_breakfast",
)

lunch = st.text_area(
    "昼ごはん",
    placeholder="例：鮭おにぎり、しらすおにぎり、味噌玉の味噌汁",
    height=90,
    key="record_lunch",
)

dinner = st.text_area(
    "夜ごはん",
    placeholder="例：鶏むね肉、サラダ、味噌汁、ごはん少なめ",
    height=90,
    key="record_dinner",
)

snack = st.text_area(
    "間食・飲み物",
    placeholder="例：豆乳、ナッツ、カフェラテ",
    height=80,
    key="record_snack",
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 運動記録
# =========================
render_section_header("運動の記録", icon_file="exercise.png", emoji="🏃‍♀️")

exercise_type = st.selectbox(
    "運動内容",
    [
        "なし",
        "ストレッチ",
        "ヨガ",
        "ホットヨガ",
        "ピラティス",
        "マシンピラティス",
        "ウォーキング",
        "ランニング",
        "筋トレ",
        "その他",
    ],
    index=1,
    key="record_exercise_type",
)

exercise_minutes = st.number_input(
    "運動時間（分）",
    min_value=0,
    max_value=300,
    value=30,
    step=5,
    key="record_exercise_minutes",
)

exercise_memo = st.text_area(
    "運動メモ",
    placeholder="例：リラックスヨガ。汗は少なめ。肩まわりが少し軽くなった。",
    height=100,
    key="record_exercise_memo",
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ひとことメモ
# =========================
render_section_header("ひとことメモ", icon_file="note.png", emoji="📝")

daily_memo = st.text_area(
    "今日のメモ",
    placeholder="例：今日は完璧じゃないけど、記録できたのでOK。",
    height=120,
    key="record_daily_memo",
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 保存
# =========================
st.markdown("---")

log = {
    "user_id": user_id,
    "ユーザーID": user_id,
    "日付": record_date.strftime("%Y-%m-%d") if hasattr(record_date, "strftime") else str(record_date),
    "年齢": default_age,
    "身長(cm)": round(height_cm, 1),
    "体重(kg)": round(weight, 1),
    "目標体重(kg)": round(target_weight, 1),
    "体脂肪率(%)": round(body_fat, 1),
    "目標体脂肪率(%)": round(target_body_fat, 1),
    "BMI": round(bmi, 1),
    "体調": condition,
    "気分": mood,
    "睡眠時間": round(sleep_hours, 1),
    "体調メモ": body_memo,
    "朝ごはん": breakfast,
    "昼ごはん": lunch,
    "夜ごはん": dinner,
    "間食": snack,
    "運動内容": exercise_type,
    "運動時間": exercise_minutes,
    "運動メモ": exercise_memo,
    "メモ": daily_memo,
}

if st.button("✅ 今日の記録を保存する", use_container_width=True):
    saved, result = save_record_log(user_id, log)

    if saved:
        try:
            settings["current_weight"] = str(round(weight, 1))
            settings["current_body_fat"] = str(round(body_fat, 1))
            settings["target_weight"] = str(round(target_weight, 1))
            settings["target_body_fat"] = str(round(target_body_fat, 1))
            settings["height_cm"] = str(round(height_cm, 1))
            settings["sleep_hours"] = str(round(sleep_hours, 1))
            save_settings_safely(user_id, settings)
        except Exception:
            pass

        st.success("今日の記録を保存しました✨")
        st.balloons()
        st.rerun()

    else:
        st.session_state.setdefault("local_record_logs", [])
        st.session_state["local_record_logs"].append(log)

        st.warning(
            "保存用の関数が見つからなかったため、今回は画面上だけに一時保存しました。"
            " app_core.py の保存関数名を確認してください。"
        )


# =========================
# 最新記録
# =========================
render_section_header("最新の記録", icon_file="calendar.png", emoji="📌")

with st.expander("最新の記録を確認する"):
    latest_logs = load_record_logs(user_id)
    latest_logs = filter_user_logs(latest_logs, user_id)

    if not latest_logs and st.session_state.get("local_record_logs"):
        latest_logs = st.session_state["local_record_logs"]

    if latest_logs:
        latest = latest_logs[-1]

        st.write(f"日付：{latest.get('日付', latest.get('date', ''))}")
        st.write(f"体重：{latest.get('体重(kg)', latest.get('体重', ''))} kg")
        st.write(f"体脂肪率：{latest.get('体脂肪率(%)', latest.get('体脂肪率', ''))} %")
        st.write(f"体調：{latest.get('体調', '')}")
        st.write(f"運動：{latest.get('運動内容', '')}")
        st.write(f"メモ：{latest.get('メモ', '')}")

    else:
        st.info("まだ記録がありません")


# =========================
# 記録一覧・グラフ
# =========================
with st.expander("記録一覧・グラフを見る"):
    logs_for_df = load_record_logs(user_id)
    logs_for_df = filter_user_logs(logs_for_df, user_id)

    if not logs_for_df and st.session_state.get("local_record_logs"):
        logs_for_df = st.session_state["local_record_logs"]

    if logs_for_df:
        df = pd.DataFrame(logs_for_df)

        if "日付" in df.columns:
            df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
            df = df.sort_values("日付")

        st.dataframe(df, use_container_width=True)

        if "日付" in df.columns and "体重(kg)" in df.columns:
            chart_df = df.dropna(subset=["日付"]).copy()
            chart_df["体重(kg)"] = pd.to_numeric(chart_df["体重(kg)"], errors="coerce")

            st.markdown("#### 体重推移")
            st.line_chart(chart_df.set_index("日付")["体重(kg)"])

        if "日付" in df.columns and "体脂肪率(%)" in df.columns:
            chart_df = df.dropna(subset=["日付"]).copy()
            chart_df["体脂肪率(%)"] = pd.to_numeric(chart_df["体脂肪率(%)"], errors="coerce")

            st.markdown("#### 体脂肪率推移")
            st.line_chart(chart_df.set_index("日付")["体脂肪率(%)"])

    else:
        st.info("まだ表示できる記録がありません")


# =========================
# 下部メッセージ
# =========================
st.markdown(
    """
<div class="bottom-message">
    完璧に書かなくても大丈夫です。<br>
    体重だけ、食事だけ、ひとことだけでも記録できれば十分です。
</div>
""",
    unsafe_allow_html=True,
)
