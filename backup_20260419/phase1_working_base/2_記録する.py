import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# =========================
# 基本設定
# =========================
DEFAULT_USER_ID = "default_user"

DIETLOG_HEADERS = [
    "user_id",
    "log_date",
    "weight",
    "body_fat",
    "meal_memo",
    "exercise_memo",
    "condition_note",
    "mood_note",
    "created_at",
]

SETTINGS_HEADERS = [
    "user_id",
    "nickname",
    "age",
    "height_cm",
    "current_weight",
    "target_weight",
    "current_body_fat",
    "target_body_fat",
    "activity_level",
    "food_style",
    "user_type",
    "updated_at",
]


# =========================
# 共通関数
# =========================
def get_user_id() -> str:
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = DEFAULT_USER_ID
    return st.session_state["user_id"]


def to_str(v) -> str:
    return "" if v is None else str(v)


def to_float(v, default=0.0) -> float:
    try:
        if v in [None, ""]:
            return default
        return float(v)
    except Exception:
        return default


@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    return gspread.authorize(credentials)


def get_spreadsheet():
    client = get_gspread_client()
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    return client.open_by_key(sheet_id)


def ensure_headers(ws, headers):
    current = ws.row_values(1)
    if current != headers:
        ws.update("A1", [headers])


def get_or_create_sheet(title: str, headers: list[str]):
    ss = get_spreadsheet()
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows=200, cols=len(headers))
        ws.append_row(headers)

    ensure_headers(ws, headers)
    return ws


def get_or_create_logs_sheet():
    return get_or_create_sheet("DietLogs", DIETLOG_HEADERS)


def get_or_create_settings_sheet():
    return get_or_create_sheet("Settings", SETTINGS_HEADERS)


def load_settings_defaults(user_id: str) -> dict:
    ws = get_or_create_settings_sheet()
    records = ws.get_all_records()

    for record in records:
        if str(record.get("user_id", "")) == user_id:
            return {
                "current_weight": to_float(record.get("current_weight", 50.0), 50.0),
                "current_body_fat": to_float(record.get("current_body_fat", 30.0), 30.0),
            }

    return {
        "current_weight": 50.0,
        "current_body_fat": 30.0,
    }


def load_latest_log(user_id: str) -> dict | None:
    ws = get_or_create_logs_sheet()
    records = ws.get_all_records()

    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]
    if not user_logs:
        return None

    def sort_key(x):
        created_at = to_str(x.get("created_at", ""))
        log_date = to_str(x.get("log_date", ""))
        return (log_date, created_at)

    user_logs.sort(key=sort_key, reverse=True)
    return user_logs[0]


def get_initial_values(user_id: str) -> dict:
    latest = load_latest_log(user_id)
    if latest:
        return {
            "weight": to_float(latest.get("weight", 50.0), 50.0),
            "body_fat": to_float(latest.get("body_fat", 30.0), 30.0),
        }

    defaults = load_settings_defaults(user_id)
    return {
        "weight": defaults["current_weight"],
        "body_fat": defaults["current_body_fat"],
    }


def save_diet_log(user_id: str, data: dict):
    ws = get_or_create_logs_sheet()
    row_data = [
        user_id,
        data["log_date"],
        data["weight"],
        data["body_fat"],
        data["meal_memo"],
        data["exercise_memo"],
        data["condition_note"],
        data["mood_note"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]
    ws.append_row(row_data)


def load_recent_logs(user_id: str, limit: int = 10) -> pd.DataFrame:
    ws = get_or_create_logs_sheet()
    records = ws.get_all_records()
    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]

    if not user_logs:
        return pd.DataFrame()

    df = pd.DataFrame(user_logs)

    if "log_date" in df.columns:
        df["log_date_sort"] = pd.to_datetime(df["log_date"], errors="coerce")
    else:
        df["log_date_sort"] = pd.NaT

    if "created_at" in df.columns:
        df["created_at_sort"] = pd.to_datetime(df["created_at"], errors="coerce")
    else:
        df["created_at_sort"] = pd.NaT

    df = df.sort_values(
        by=["log_date_sort", "created_at_sort"],
        ascending=[False, False],
        na_position="last",
    )

    df = df.rename(
        columns={
            "log_date": "日付",
            "weight": "体重(kg)",
            "body_fat": "体脂肪(%)",
            "meal_memo": "食事メモ",
            "exercise_memo": "運動メモ",
            "condition_note": "体調メモ",
            "mood_note": "気分メモ",
        }
    )

    show_cols = ["日付", "体重(kg)", "体脂肪(%)", "食事メモ", "運動メモ", "体調メモ", "気分メモ"]
    show_cols = [c for c in show_cols if c in df.columns]

    return df[show_cols].head(limit)


# =========================
# 画面
# =========================
st.title("📝 記録する")
st.caption("今日の体重・体脂肪・食事・運動を記録します")

user_id = get_user_id()

try:
    initial = get_initial_values(user_id)
except Exception as e:
    st.error(f"初期値の読込に失敗しました: {e}")
    st.stop()

with st.form("diet_log_form"):
    log_date = st.date_input("日付", value=date.today())

    weight = st.number_input(
        "体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(initial["weight"]),
        step=0.1,
        format="%.1f",
    )

    body_fat = st.number_input(
        "体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(initial["body_fat"]),
        step=0.1,
        format="%.1f",
    )

    meal_memo = st.text_area("食事メモ", placeholder="例：朝 納豆ごはん、昼 パスタ、夜 鮭と味噌汁")
    exercise_memo = st.text_area("運動メモ", placeholder="例：ヨガ30分、散歩20分")
    condition_note = st.text_area("体調メモ", placeholder="例：少しむくみあり、よく眠れた")
    mood_note = st.text_area("気分メモ", placeholder="例：疲れ気味、やる気あり")

    submitted = st.form_submit_button("今日の記録を保存", use_container_width=True)

if submitted:
    save_data = {
        "log_date": log_date.strftime("%Y-%m-%d"),
        "weight": float(weight),
        "body_fat": float(body_fat),
        "meal_memo": meal_memo.strip(),
        "exercise_memo": exercise_memo.strip(),
        "condition_note": condition_note.strip(),
        "mood_note": mood_note.strip(),
    }

    try:
        save_diet_log(user_id, save_data)
        st.success("今日の記録を保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")

st.divider()
st.subheader("最近の記録")

try:
    recent_logs = load_recent_logs(user_id, limit=10)
    if recent_logs.empty:
        st.info("まだ記録がありません")
    else:
        st.dataframe(recent_logs, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"記録一覧の読込に失敗しました: {e}")
