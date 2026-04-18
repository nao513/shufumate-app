import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =========================
# 基本設定
# =========================
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

USER_TYPE_OPTIONS = [
    "自分だけ向け",
    "自分＋家族向け",
    "節約重視",
    "忙しい日向け",
]

ACTIVITY_LEVEL_OPTIONS = [
    "低い",
    "ふつう",
    "高い",
]

FOOD_STYLE_OPTIONS = [
    "バランス重視",
    "和食中心",
    "たんぱく質重視",
    "節約重視",
    "時短重視",
]

DEFAULT_USER_ID = "default_user"


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


def to_int(v, default=0) -> int:
    try:
        if v in [None, ""]:
            return default
        return int(float(v))
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


def get_or_create_settings_sheet():
    ss = get_spreadsheet()
    try:
        ws = ss.worksheet("Settings")
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title="Settings", rows=100, cols=len(SETTINGS_HEADERS))
        ws.append_row(SETTINGS_HEADERS)

    ensure_headers(ws, SETTINGS_HEADERS)
    return ws


def ensure_headers(ws, headers):
    current = ws.row_values(1)
    if current != headers:
        ws.update("A1", [headers])


def find_user_row(ws, user_id: str):
    values = ws.get_all_values()
    if len(values) <= 1:
        return None

    for row_idx, row in enumerate(values[1:], start=2):
        if len(row) > 0 and row[0] == user_id:
            return row_idx
    return None


def load_user_settings(user_id: str) -> dict:
    ws = get_or_create_settings_sheet()
    records = ws.get_all_records()

    for record in records:
        if str(record.get("user_id", "")) == user_id:
            return {
                "nickname": to_str(record.get("nickname", "")),
                "age": to_int(record.get("age", 49), 49),
                "height_cm": to_float(record.get("height_cm", 160.0), 160.0),
                "current_weight": to_float(record.get("current_weight", 50.0), 50.0),
                "target_weight": to_float(record.get("target_weight", 48.0), 48.0),
                "current_body_fat": to_float(record.get("current_body_fat", 30.0), 30.0),
                "target_body_fat": to_float(record.get("target_body_fat", 28.0), 28.0),
                "activity_level": to_str(record.get("activity_level", "ふつう")) or "ふつう",
                "food_style": to_str(record.get("food_style", "バランス重視")) or "バランス重視",
                "user_type": to_str(record.get("user_type", "自分だけ向け")) or "自分だけ向け",
            }

    return {
        "nickname": "",
        "age": 49,
        "height_cm": 160.0,
        "current_weight": 50.0,
        "target_weight": 48.0,
        "current_body_fat": 30.0,
        "target_body_fat": 28.0,
        "activity_level": "ふつう",
        "food_style": "バランス重視",
        "user_type": "自分だけ向け",
    }


def save_user_settings(user_id: str, data: dict):
    ws = get_or_create_settings_sheet()
    row_data = [
        user_id,
        data["nickname"],
        data["age"],
        data["height_cm"],
        data["current_weight"],
        data["target_weight"],
        data["current_body_fat"],
        data["target_body_fat"],
        data["activity_level"],
        data["food_style"],
        data["user_type"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]

    row_index = find_user_row(ws, user_id)

    if row_index:
        end_col = chr(64 + len(SETTINGS_HEADERS))
        ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])
    else:
        ws.append_row(row_data)


# =========================
# 画面
# =========================
st.title("⚙️ 設定")
st.caption("提案に使う基本情報を保存します")

user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

with st.form("settings_form"):
    nickname = st.text_input("ニックネーム", value=settings["nickname"])

    age = st.number_input(
        "年齢",
        min_value=18,
        max_value=100,
        value=int(settings["age"]),
        step=1,
    )

    height_cm = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=220.0,
        value=float(settings["height_cm"]),
        step=0.5,
        format="%.1f",
    )

    current_weight = st.number_input(
        "現在体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(settings["current_weight"]),
        step=0.1,
        format="%.1f",
    )

    target_weight = st.number_input(
        "目標体重(kg)",
        min_value=20.0,
        max_value=200.0,
        value=float(settings["target_weight"]),
        step=0.1,
        format="%.1f",
    )

    current_body_fat = st.number_input(
        "現在体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(settings["current_body_fat"]),
        step=0.1,
        format="%.1f",
    )

    target_body_fat = st.number_input(
        "目標体脂肪(%)",
        min_value=0.0,
        max_value=70.0,
        value=float(settings["target_body_fat"]),
        step=0.1,
        format="%.1f",
    )

    activity_level = st.selectbox(
        "活動量",
        ACTIVITY_LEVEL_OPTIONS,
        index=ACTIVITY_LEVEL_OPTIONS.index(settings["activity_level"])
        if settings["activity_level"] in ACTIVITY_LEVEL_OPTIONS
        else 1,
    )

    food_style = st.selectbox(
        "食事スタイル",
        FOOD_STYLE_OPTIONS,
        index=FOOD_STYLE_OPTIONS.index(settings["food_style"])
        if settings["food_style"] in FOOD_STYLE_OPTIONS
        else 0,
    )

    user_type = st.selectbox(
        "利用タイプ",
        USER_TYPE_OPTIONS,
        index=USER_TYPE_OPTIONS.index(settings["user_type"])
        if settings["user_type"] in USER_TYPE_OPTIONS
        else 0,
    )

    submitted = st.form_submit_button("保存", use_container_width=True)

if submitted:
    save_data = {
        "nickname": nickname.strip(),
        "age": int(age),
        "height_cm": float(height_cm),
        "current_weight": float(current_weight),
        "target_weight": float(target_weight),
        "current_body_fat": float(current_body_fat),
        "target_body_fat": float(target_body_fat),
        "activity_level": activity_level,
        "food_style": food_style,
        "user_type": user_type,
    }

    try:
        save_user_settings(user_id, save_data)
        st.success("設定を保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")
