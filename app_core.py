import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from uuid import uuid4
import hashlib
import secrets

# =========================
# タイムゾーン
# =========================
JST = ZoneInfo("Asia/Tokyo")


def jst_now():
    return datetime.now(JST)


def jst_today():
    return jst_now().date()


def jst_today_str():
    return jst_now().strftime("%Y-%m-%d")


# =========================
# 定数
# =========================
USERS_HEADERS = [
    "user_id",
    "login_id",
    "password_hash",
    "password_salt",
    "nickname",
    "birth_date",
    "created_at",
    "updated_at",
    "is_active",
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
    "lunch_style",
    "user_type",
    "advice_tone",
    "constitution_traits",
    "updated_at",
]

DIETLOG_HEADERS = [
    "user_id",
    "log_date",
    "weight",
    "body_fat",
    "meal_memo",
    "exercise_memo",
    "condition_note",
    "mood_note",
    "today_conditions",
    "created_at",
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

LUNCH_STYLE_OPTIONS = [
    "指定なし",
    "お弁当",
    "外食",
    "コンビニ",
    "自宅",
]

ADVICE_TONE_OPTIONS = [
    "やさしく",
    "しっかり",
    "淡々と",
]

CONSTITUTION_TRAIT_OPTIONS = [
    "冷えやすい",
    "むくみやすい",
    "疲れやすい",
    "便通が乱れやすい",
    "胃腸がゆらぎやすい",
    "甘いものに流れやすい",
    "食べすぎやすい",
]

TODAY_CONDITION_OPTIONS = [
    "寝不足",
    "だるい",
    "むくみあり",
    "食べすぎた",
    "外食あり",
    "時間がない",
    "気分が落ち気味",
    "運動できそう",
]

CATEGORY_OPTIONS = [
    "食事",
    "運動",
    "体調",
    "外食調整",
]

WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]


# =========================
# 共通変換
# =========================
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


def parse_multi_value(v) -> list[str]:
    if v is None:
        return []

    if isinstance(v, str):
        raw = v.strip()
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    if isinstance(v, (list, tuple, set)):
        return [to_str(item).strip() for item in v if to_str(item).strip()]

    return []


def normalize_multi_value(v, allowed_options: list[str]) -> list[str]:
    items = parse_multi_value(v)
    return [item for item in items if item in allowed_options]


def join_multi_value(items) -> str:
    normalized = parse_multi_value(items)
    if not normalized:
        return ""
    return ",".join(normalized)


# =========================
# 年齢計算
# =========================
def calculate_age_from_birth_date(birth_date_str: str) -> int | None:
    try:
        birth = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    except Exception:
        return None

    today = jst_today()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


# =========================
# パスワード
# =========================
def generate_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    )
    return hashed.hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return hash_password(password, salt) == password_hash


# =========================
# Google Sheets接続
# =========================
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


def get_or_create_sheet(title: str, headers: list[str], rows: int = 200):
    ss = get_spreadsheet()
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows=rows, cols=max(len(headers), 20))
        ws.append_row(headers)

    ensure_headers(ws, headers)
    return ws


def get_users_sheet():
    return get_or_create_sheet("Users", USERS_HEADERS, rows=300)


def get_settings_sheet():
    return get_or_create_sheet("Settings", SETTINGS_HEADERS, rows=300)


def get_dietlogs_sheet():
    return get_or_create_sheet("DietLogs", DIETLOG_HEADERS, rows=3000)


# =========================
# 読み取りキャッシュ
# =========================
@st.cache_data(ttl=30, show_spinner=False)
def read_users_records():
    return get_users_sheet().get_all_records()


@st.cache_data(ttl=30, show_spinner=False)
def read_settings_records():
    ws = get_settings_sheet()
    data = ws.get_all_values()

    if len(data) < 2:
        return []

    headers = data[0]
    records = []

    for row in data[1:]:
        if len(row) != len(headers):
            continue  # ← 壊れた行スキップ

        record = dict(zip(headers, row))
        records.append(record)

    return records


@st.cache_data(ttl=30, show_spinner=False)
def read_dietlog_records():
    return get_dietlogs_sheet().get_all_records()


def clear_sheet_caches():
    read_users_records.clear()
    read_settings_records.clear()
    read_dietlog_records.clear()


# =========================
# セッション管理
# =========================
def login_user(user_record: dict):
    st.session_state["is_logged_in"] = True
    st.session_state["auth_user_id"] = to_str(user_record.get("user_id", ""))
    st.session_state["auth_login_id"] = to_str(user_record.get("login_id", ""))
    st.session_state["auth_nickname"] = to_str(user_record.get("nickname", ""))


def logout_user():
    for key in ["is_logged_in", "auth_user_id", "auth_login_id", "auth_nickname"]:
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in() -> bool:
    return bool(st.session_state.get("is_logged_in", False))


def get_current_user_id() -> str | None:
    if not is_logged_in():
        return None
    return to_str(st.session_state.get("auth_user_id", "")) or None


def require_login():
    if not is_logged_in():
        st.switch_page("pages/0_ログイン.py")
        st.stop()


def get_user_id() -> str:
    user_id = get_current_user_id()
    if not user_id:
        raise RuntimeError("ログインが必要です。")
    return user_id


# =========================
# 行検索
# =========================
def find_row_by_user_id(ws, user_id: str):
    values = ws.get_all_values()
    if len(values) <= 1:
        return None

    for row_idx, row in enumerate(values[1:], start=2):
        if len(row) > 0 and row[0] == user_id:
            return row_idx
    return None


# =========================
# Users
# =========================
def find_user_by_login_id(login_id: str) -> dict | None:
    login_id = login_id.strip()
    if not login_id:
        return None

    for record in read_users_records():
        if (
            to_str(record.get("login_id", "")).strip() == login_id
            and to_str(record.get("is_active", "1")).strip() != "0"
        ):
            return record
    return None


def find_user_by_user_id(user_id: str) -> dict | None:
    for record in read_users_records():
        if (
            to_str(record.get("user_id", "")) == user_id
            and to_str(record.get("is_active", "1")).strip() != "0"
        ):
            return record
    return None


def create_user(login_id: str, password: str, nickname: str, birth_date: date | str):
    login_id = login_id.strip()
    nickname = nickname.strip()

    if not login_id:
        raise ValueError("ログインIDを入力してください。")
    if not password:
        raise ValueError("パスワードを入力してください。")
    if len(password) < 4:
        raise ValueError("パスワードは4文字以上にしてください。")
    if not nickname:
        raise ValueError("ニックネームを入力してください。")

    birth_date_str = birth_date.strftime("%Y-%m-%d") if isinstance(birth_date, date) else to_str(birth_date).strip()
    if not birth_date_str:
        raise ValueError("生年月日を入力してください。")

    if find_user_by_login_id(login_id):
        raise ValueError("そのログインIDは既に使われています。")

    user_id = uuid4().hex
    salt = generate_salt()
    password_hash = hash_password(password, salt)
    now_str = jst_now().strftime("%Y-%m-%d %H:%M:%S")
    age = calculate_age_from_birth_date(birth_date_str)

    get_users_sheet().append_row(
        [
            user_id,
            login_id,
            password_hash,
            salt,
            nickname,
            birth_date_str,
            now_str,
            now_str,
            "1",
        ]
    )

    get_settings_sheet().append_row(
        [
            user_id,
            nickname,
            age if age is not None else "",
            160.0,
            50.0,
            48.0,
            30.0,
            28.0,
            "ふつう",
            "バランス重視",
            "指定なし",
            "自分だけ向け",
            "やさしく",
            "",
            now_str,
        ]
    )

    clear_sheet_caches()

    return {
        "user_id": user_id,
        "login_id": login_id,
        "nickname": nickname,
        "birth_date": birth_date_str,
    }


def verify_login(login_id: str, password: str) -> dict | None:
    user_record = find_user_by_login_id(login_id)
    if not user_record:
        return None

    salt = to_str(user_record.get("password_salt", ""))
    password_hash = to_str(user_record.get("password_hash", ""))

    if not salt or not password_hash:
        return None

    return user_record if verify_password(password, salt, password_hash) else None


def load_current_user_profile() -> dict | None:
    user_id = get_current_user_id()
    if not user_id:
        return None

    record = find_user_by_user_id(user_id)
    if not record:
        return None

    age = calculate_age_from_birth_date(to_str(record.get("birth_date", "")))

    return {
        "user_id": to_str(record.get("user_id", "")),
        "login_id": to_str(record.get("login_id", "")),
        "nickname": to_str(record.get("nickname", "")),
        "birth_date": to_str(record.get("birth_date", "")),
        "age": age,
    }


def _update_user_row(user_id: str, row_data: list):
    ws = get_users_sheet()
    row_index = find_row_by_user_id(ws, user_id)
    if not row_index:
        raise ValueError("Usersシートの更新行が見つかりません。")

    end_col = chr(64 + len(USERS_HEADERS))
    ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])


def change_login_id(user_id: str, current_password: str, new_login_id: str):
    new_login_id = new_login_id.strip()

    if not current_password:
        raise ValueError("現在のパスワードを入力してください。")
    if not new_login_id:
        raise ValueError("新しいログインIDを入力してください。")

    current_user = find_user_by_user_id(user_id)
    if not current_user:
        raise ValueError("現在のユーザーが見つかりません。")

    current_login_id = to_str(current_user.get("login_id", "")).strip()
    if new_login_id == current_login_id:
        raise ValueError("新しいログインIDが現在のものと同じです。")

    existing = find_user_by_login_id(new_login_id)
    if existing and to_str(existing.get("user_id", "")) != user_id:
        raise ValueError("そのログインIDは既に使われています。")

    salt = to_str(current_user.get("password_salt", ""))
    password_hash = to_str(current_user.get("password_hash", ""))
    if not verify_password(current_password, salt, password_hash):
        raise ValueError("現在のパスワードが違います。")

    row_data = [
        user_id,
        new_login_id,
        password_hash,
        salt,
        to_str(current_user.get("nickname", "")),
        to_str(current_user.get("birth_date", "")),
        to_str(current_user.get("created_at", "")),
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        to_str(current_user.get("is_active", "1")) or "1",
    ]

    _update_user_row(user_id, row_data)
    st.session_state["auth_login_id"] = new_login_id
    clear_sheet_caches()


def change_password(user_id: str, current_password: str, new_password: str, new_password_confirm: str):
    if not current_password:
        raise ValueError("現在のパスワードを入力してください。")
    if not new_password:
        raise ValueError("新しいパスワードを入力してください。")
    if len(new_password) < 4:
        raise ValueError("新しいパスワードは4文字以上にしてください。")
    if new_password != new_password_confirm:
        raise ValueError("新しいパスワード確認が一致しません。")

    current_user = find_user_by_user_id(user_id)
    if not current_user:
        raise ValueError("現在のユーザーが見つかりません。")

    old_salt = to_str(current_user.get("password_salt", ""))
    old_password_hash = to_str(current_user.get("password_hash", ""))
    if not verify_password(current_password, old_salt, old_password_hash):
        raise ValueError("現在のパスワードが違います。")

    new_salt = generate_salt()
    new_password_hash = hash_password(new_password, new_salt)

    row_data = [
        user_id,
        to_str(current_user.get("login_id", "")).strip(),
        new_password_hash,
        new_salt,
        to_str(current_user.get("nickname", "")).strip(),
        to_str(current_user.get("birth_date", "")).strip(),
        to_str(current_user.get("created_at", "")).strip(),
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        to_str(current_user.get("is_active", "1")).strip() or "1",
    ]

    _update_user_row(user_id, row_data)
    clear_sheet_caches()


def change_birth_date(user_id: str, current_password: str, new_birth_date):
    current_user = find_user_by_user_id(user_id)
    if not current_user:
        raise ValueError("現在のユーザーが見つかりません。")

    password_salt = to_str(current_user.get("password_salt", ""))
    password_hash = to_str(current_user.get("password_hash", ""))
    if not verify_password(current_password, password_salt, password_hash):
        raise ValueError("現在のパスワードが違います。")

    birth_date_str = new_birth_date.strftime("%Y-%m-%d") if isinstance(new_birth_date, date) else to_str(new_birth_date).strip()
    if not birth_date_str:
        raise ValueError("生年月日を入力してください。")

    new_age = calculate_age_from_birth_date(birth_date_str)
    if new_age is None:
        raise ValueError("生年月日が正しくありません。")

    updated_user_row = [
        user_id,
        to_str(current_user.get("login_id", "")).strip(),
        password_hash,
        password_salt,
        to_str(current_user.get("nickname", "")).strip(),
        birth_date_str,
        to_str(current_user.get("created_at", "")).strip(),
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        to_str(current_user.get("is_active", "1")).strip() or "1",
    ]
    _update_user_row(user_id, updated_user_row)

    settings = load_user_settings(user_id)
    save_user_settings(
        user_id,
        {
            "nickname": settings["nickname"],
            "height_cm": settings["height_cm"],
            "current_weight": settings["current_weight"],
            "target_weight": settings["target_weight"],
            "current_body_fat": settings["current_body_fat"],
            "target_body_fat": settings["target_body_fat"],
            "activity_level": settings["activity_level"],
            "food_style": settings["food_style"],
            "lunch_style": settings["lunch_style"],
            "user_type": settings["user_type"],
            "advice_tone": settings["advice_tone"],
            "constitution_traits": settings["constitution_traits"],
        },
    )

    clear_sheet_caches()


# =========================
# Settings
# =========================
def load_user_settings(user_id: str) -> dict:
    profile = load_current_user_profile()
    profile_nickname = profile["nickname"] if profile else ""
    auto_age = profile["age"] if profile and profile.get("age") is not None else None

    for record in read_settings_records():
        if to_str(record.get("user_id", "")) == user_id:
            activity_level = to_str(record.get("activity_level", "ふつう")) or "ふつう"
            if activity_level not in ACTIVITY_LEVEL_OPTIONS:
                activity_level = "ふつう"

            food_style = to_str(record.get("food_style", "バランス重視")) or "バランス重視"
            if food_style not in FOOD_STYLE_OPTIONS:
                food_style = "バランス重視"

            lunch_style = to_str(record.get("lunch_style", "指定なし")) or "指定なし"
            if lunch_style not in LUNCH_STYLE_OPTIONS:
                lunch_style = "指定なし"

            user_type = to_str(record.get("user_type", "自分だけ向け")) or "自分だけ向け"
            if user_type not in USER_TYPE_OPTIONS:
                user_type = "自分だけ向け"

            advice_tone = to_str(record.get("advice_tone", "やさしく")) or "やさしく"
            if advice_tone not in ADVICE_TONE_OPTIONS:
                advice_tone = "やさしく"

            constitution_traits = normalize_multi_value(
                record.get("constitution_traits", ""),
                CONSTITUTION_TRAIT_OPTIONS,
            )

            return {
                "nickname": profile_nickname or to_str(record.get("nickname", "")),
                "age": auto_age if auto_age is not None else to_int(record.get("age", 49), 49),
                "height_cm": to_float(record.get("height_cm", 160.0), 160.0),
                "current_weight": to_float(record.get("current_weight", 50.0), 50.0),
                "target_weight": to_float(record.get("target_weight", 48.0), 48.0),
                "current_body_fat": to_float(record.get("current_body_fat", 30.0), 30.0),
                "target_body_fat": to_float(record.get("target_body_fat", 28.0), 28.0),
                "activity_level": activity_level,
                "food_style": food_style,
                "lunch_style": lunch_style,
                "user_type": user_type,
                "advice_tone": advice_tone,
                "constitution_traits": constitution_traits,
            }

    return {
        "nickname": profile_nickname,
        "age": auto_age if auto_age is not None else 49,
        "height_cm": 160.0,
        "current_weight": 50.0,
        "target_weight": 48.0,
        "current_body_fat": 30.0,
        "target_body_fat": 28.0,
        "activity_level": "ふつう",
        "food_style": "バランス重視",
        "lunch_style": "指定なし",
        "user_type": "自分だけ向け",
        "advice_tone": "やさしく",
        "constitution_traits": [],
    }


def save_user_settings(user_id: str, data: dict):
    ws = get_settings_sheet()
    profile = load_current_user_profile()
    current_user = find_user_by_user_id(user_id)

    age = profile.get("age") if profile and profile.get("user_id") == user_id else ""

    activity_level = data.get("activity_level", "ふつう")
    if activity_level not in ACTIVITY_LEVEL_OPTIONS:
        activity_level = "ふつう"

    food_style = data.get("food_style", "バランス重視")
    if food_style not in FOOD_STYLE_OPTIONS:
        food_style = "バランス重視"

    lunch_style = data.get("lunch_style", "指定なし")
    if lunch_style not in LUNCH_STYLE_OPTIONS:
        lunch_style = "指定なし"

    user_type = data.get("user_type", "自分だけ向け")
    if user_type not in USER_TYPE_OPTIONS:
        user_type = "自分だけ向け"

    advice_tone = data.get("advice_tone", "やさしく")
    if advice_tone not in ADVICE_TONE_OPTIONS:
        advice_tone = "やさしく"

    constitution_traits = normalize_multi_value(
        data.get("constitution_traits", []),
        CONSTITUTION_TRAIT_OPTIONS,
    )

    row_data = [
        user_id,
        data["nickname"],
        age,
        data["height_cm"],
        data["current_weight"],
        data["target_weight"],
        data["current_body_fat"],
        data["target_body_fat"],
        activity_level,
        food_style,
        lunch_style,
        user_type,
        advice_tone,
        join_multi_value(constitution_traits),
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
    ]

    row_index = find_row_by_user_id(ws, user_id)
    if row_index:
        end_col = chr(64 + len(SETTINGS_HEADERS))
        ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])
    else:
        ws.append_row(row_data)

    if current_user:
        updated_user_row = [
            user_id,
            to_str(current_user.get("login_id", "")).strip(),
            to_str(current_user.get("password_hash", "")).strip(),
            to_str(current_user.get("password_salt", "")).strip(),
            data["nickname"],
            to_str(current_user.get("birth_date", "")).strip(),
            to_str(current_user.get("created_at", "")).strip(),
            jst_now().strftime("%Y-%m-%d %H:%M:%S"),
            to_str(current_user.get("is_active", "1")).strip() or "1",
        ]
        _update_user_row(user_id, updated_user_row)
        st.session_state["auth_nickname"] = data["nickname"]

    clear_sheet_caches()


# =========================
# DietLogs
# =========================
def save_diet_log(user_id: str, data: dict):
    today_conditions = normalize_multi_value(
        data.get("today_conditions", []),
        TODAY_CONDITION_OPTIONS,
    )

    get_dietlogs_sheet().append_row(
        [
            user_id,
            data["log_date"],
            data["weight"],
            data["body_fat"],
            data["meal_memo"],
            data["exercise_memo"],
            data["condition_note"],
            data["mood_note"],
            join_multi_value(today_conditions),
            jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
    )
    clear_sheet_caches()


def load_latest_log(user_id: str) -> dict | None:
    user_logs = [r for r in read_dietlog_records() if to_str(r.get("user_id", "")) == user_id]
    if not user_logs:
        return None

    user_logs.sort(
        key=lambda x: (to_str(x.get("log_date", "")), to_str(x.get("created_at", ""))),
        reverse=True,
    )
    latest = user_logs[0]
    latest["today_conditions"] = normalize_multi_value(
        latest.get("today_conditions", ""),
        TODAY_CONDITION_OPTIONS,
    )
    return latest


def get_initial_log_values(user_id: str) -> dict:
    latest = load_latest_log(user_id)
    if latest:
        return {
            "weight": to_float(latest.get("weight", 50.0), 50.0),
            "body_fat": to_float(latest.get("body_fat", 30.0), 30.0),
            "today_conditions": normalize_multi_value(
                latest.get("today_conditions", []),
                TODAY_CONDITION_OPTIONS,
            ),
        }

    settings = load_user_settings(user_id)
    return {
        "weight": settings["current_weight"],
        "body_fat": settings["current_body_fat"],
        "today_conditions": [],
    }


def load_recent_logs(user_id: str, limit: int = 10) -> pd.DataFrame:
    user_logs = [r for r in read_dietlog_records() if to_str(r.get("user_id", "")) == user_id]
    if not user_logs:
        return pd.DataFrame()

    df = pd.DataFrame(user_logs)
    df["log_date_sort"] = pd.to_datetime(df.get("log_date"), errors="coerce")
    df["created_at_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")

    if "today_conditions" in df.columns:
        df["today_conditions"] = df["today_conditions"].fillna("").astype(str).str.replace(",", " / ")

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
            "today_conditions": "今日の状態",
            "meal_memo": "食事メモ",
            "exercise_memo": "運動メモ",
            "condition_note": "体調メモ",
            "mood_note": "気分メモ",
        }
    )

    show_cols = ["日付", "体重(kg)", "体脂肪(%)", "今日の状態", "食事メモ", "運動メモ", "体調メモ", "気分メモ"]
    show_cols = [c for c in show_cols if c in df.columns]

    return df[show_cols].head(limit)


def load_log_chart_df(user_id: str) -> pd.DataFrame:
    user_logs = [r for r in read_dietlog_records() if to_str(r.get("user_id", "")) == user_id]
    if not user_logs:
        return pd.DataFrame()

    df = pd.DataFrame(user_logs)
    if "log_date" not in df.columns:
        return pd.DataFrame()

    df["log_date_sort"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["created_at_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")
    df["weight_num"] = pd.to_numeric(df.get("weight"), errors="coerce")
    df["body_fat_num"] = pd.to_numeric(df.get("body_fat"), errors="coerce")

    df = df.dropna(subset=["log_date_sort"])
    df = df.sort_values(by=["log_date_sort", "created_at_sort"], ascending=[True, True], na_position="last")
    df = df.drop_duplicates(subset=["log_date"], keep="last")

    return pd.DataFrame(
        {
            "日付": df["log_date_sort"],
            "体重(kg)": df["weight_num"],
            "体脂肪(%)": df["body_fat_num"],
        }
    ).set_index("日付")


def get_today_log_status(user_id: str) -> dict:
    today = jst_today_str()
    today_logs = [
        r for r in read_dietlog_records()
        if to_str(r.get("user_id", "")) == user_id and to_str(r.get("log_date", "")) == today
    ]

    if not today_logs:
        return {
            "is_logged": False,
            "label": "今日はまだ未記録です",
            "detail": "体重・体脂肪・今日の状態を記録できます。",
        }

    today_logs.sort(key=lambda x: to_str(x.get("created_at", "")), reverse=True)
    created_at = to_str(today_logs[0].get("created_at", ""))
    time_text = created_at[11:16] if len(created_at) >= 16 else ""
    detail = f"今日の記録は保存済みです（最終保存 {time_text}）" if time_text else "今日の記録は保存済みです。"

    return {
        "is_logged": True,
        "label": "今日は記録済みです",
        "detail": detail,
    }


def get_home_progress_summary(user_id: str) -> dict:
    settings = load_user_settings(user_id)
    latest = load_latest_log(user_id)

    current_weight = settings["current_weight"]
    target_weight = settings["target_weight"]
    current_body_fat = settings["current_body_fat"]
    target_body_fat = settings["target_body_fat"]

    latest_date = "未記録"

    if latest:
        latest_date = to_str(latest.get("log_date", "未記録")) or "未記録"
        latest_weight = to_float(latest.get("weight", current_weight), current_weight)
        latest_body_fat = to_float(latest.get("body_fat", current_body_fat), current_body_fat)
    else:
        latest_weight = current_weight
        latest_body_fat = current_body_fat

    weight_diff = round(latest_weight - target_weight, 1)
    body_fat_diff = round(latest_body_fat - target_body_fat, 1)

    if weight_diff > 0:
        weight_text = f"目標まであと {weight_diff:.1f}kg"
    elif weight_diff < 0:
        weight_text = f"目標を {abs(weight_diff):.1f}kg 下回っています"
    else:
        weight_text = "体重は目標ぴったりです"

    if body_fat_diff > 0:
        body_fat_text = f"目標まであと {body_fat_diff:.1f}%"
    elif body_fat_diff < 0:
        body_fat_text = f"目標を {abs(body_fat_diff):.1f}% 下回っています"
    else:
        body_fat_text = "体脂肪は目標ぴったりです"

    return {
        "latest_date": latest_date,
        "latest_weight": latest_weight,
        "latest_body_fat": latest_body_fat,
        "weight_text": weight_text,
        "body_fat_text": body_fat_text,
    }


# =========================
# 整えポイント
# =========================
FOCUS_LABELS = {
    "protein": "たんぱく質",
    "vegetables": "野菜・食物繊維",
    "hydration": "水分",
    "rest": "休息",
    "activity": "軽い活動",
    "warm_care": "体を冷やしすぎないこと",
    "digestive_care": "胃腸にやさしい食事",
}

FOCUS_FOOD_TIPS = {
    "protein": "卵、豆腐、魚、鶏むね肉など、たんぱく質を少し入れるのがおすすめです。",
    "vegetables": "汁物や温野菜、きのこ、海藻を足すと整えやすいです。",
    "hydration": "冷たい物に偏らず、水分をこまめにとる意識がおすすめです。",
    "rest": "回復を優先し、消化しやすい食事で無理を減らす日がおすすめです。",
    "activity": "食後や家事の合間に少し動くと整いやすいです。",
    "warm_care": "温かい汁物や温野菜で、体を冷やしすぎない組み立てがおすすめです。",
    "digestive_care": "重たい物を重ねず、やわらかく温かい食事が合いやすいです。",
}

FOCUS_EXERCISE_TIPS = {
    "protein": "運動後は軽くたんぱく質をとれると整いやすいです。",
    "vegetables": "今日は強度より、食事バランスを意識する方が優先です。",
    "hydration": "長時間より、軽く動いて水分をこまめにとる形がおすすめです。",
    "rest": "今日は追い込まず、ストレッチや深呼吸中心で十分です。",
    "activity": "10分程度の散歩や軽いストレッチから始めるのがおすすめです。",
    "warm_care": "体を温めるような軽い散歩やストレッチが合いやすいです。",
    "digestive_care": "お腹に負担が少ない、やさしい動きから始めるのがおすすめです。",
}


def _extract_today_conditions(latest_like) -> list[str]:
    if latest_like is None:
        return []
    return normalize_multi_value(latest_like.get("today_conditions", []), TODAY_CONDITION_OPTIONS)


def _score_support_focus(settings: dict, today_conditions: list[str]) -> dict:
    scores = {key: 0 for key in FOCUS_LABELS.keys()}
    traits = normalize_multi_value(settings.get("constitution_traits", []), CONSTITUTION_TRAIT_OPTIONS)

    for trait in traits:
        if trait == "冷えやすい":
            scores["warm_care"] += 2
            scores["activity"] += 1
        elif trait == "むくみやすい":
            scores["hydration"] += 2
            scores["activity"] += 1
        elif trait == "疲れやすい":
            scores["rest"] += 2
            scores["protein"] += 1
        elif trait == "便通が乱れやすい":
            scores["vegetables"] += 2
            scores["hydration"] += 1
            scores["activity"] += 1
        elif trait == "胃腸がゆらぎやすい":
            scores["digestive_care"] += 2
        elif trait == "甘いものに流れやすい":
            scores["protein"] += 1
            scores["vegetables"] += 1
        elif trait == "食べすぎやすい":
            scores["vegetables"] += 1
            scores["hydration"] += 1
            scores["digestive_care"] += 1

    for cond in today_conditions:
        if cond == "寝不足":
            scores["rest"] += 2
            scores["protein"] += 1
        elif cond == "だるい":
            scores["rest"] += 1
            scores["hydration"] += 1
        elif cond == "むくみあり":
            scores["hydration"] += 2
            scores["activity"] += 1
        elif cond == "食べすぎた":
            scores["vegetables"] += 1
            scores["hydration"] += 1
            scores["digestive_care"] += 1
        elif cond == "外食あり":
            scores["vegetables"] += 1
            scores["hydration"] += 1
        elif cond == "時間がない":
            scores["protein"] += 1
        elif cond == "気分が落ち気味":
            scores["rest"] += 1
            scores["activity"] += 1
        elif cond == "運動できそう":
            scores["activity"] += 1
            scores["protein"] += 1

    if max(scores.values()) == 0:
        scores["protein"] = 1
        scores["hydration"] = 1
        scores["activity"] = 1

    return scores


def get_support_focus_summary(settings: dict, latest_like: dict | None = None) -> dict:
    today_conditions = _extract_today_conditions(latest_like)
    scores = _score_support_focus(settings, today_conditions)

    ordered = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    top_keys = [key for key, score in ordered if score > 0][:3]
    points = [FOCUS_LABELS[key] for key in top_keys]

    top_food = FOCUS_FOOD_TIPS[top_keys[0]] if top_keys else "汁物とたんぱく質を意識すると整えやすいです。"
    top_exercise = FOCUS_EXERCISE_TIPS[top_keys[0]] if top_keys else "軽いストレッチや散歩からで十分です。"

    body_lines = []
    if points:
        body_lines.append("今整えたいポイント： " + " / ".join(points))
    else:
        body_lines.append("今整えたいポイント： 基本の整え")

    if today_conditions:
        body_lines.append("今日の状態： " + " / ".join(today_conditions))
    else:
        body_lines.append("今日は基本の整えを意識する日です。")

    body_lines.append("食事の目安： " + top_food)
    body_lines.append("運動の目安： " + top_exercise)

    return {
        "points": points,
        "food_tip": top_food,
        "exercise_tip": top_exercise,
        "today_conditions": today_conditions,
        "body": "\n".join(body_lines),
    }


# =========================
# ホーム用
# =========================
def get_week_goal(settings: dict, summary: dict) -> dict:
    user_type = to_str(settings.get("user_type", "自分だけ向け")) or "自分だけ向け"
    tone = to_str(settings.get("advice_tone", "やさしく")) or "やさしく"
    weight_text = to_str(summary.get("weight_text", ""))
    body_fat_text = to_str(summary.get("body_fat_text", ""))

    if user_type == "忙しい日向け":
        body = "完璧を目指さず、まずは記録を続けることを優先しましょう。週3回、5分だけでも動けたら十分です。"
    elif user_type == "節約重視":
        body = "食材を使い切る意識で、無理なく整える1週間にしましょう。外食後も次の食事で戻せば大丈夫です。"
    elif user_type == "自分＋家族向け":
        body = "家族優先の中でも、自分の量と体調を意識する1週間にしましょう。まずは1日1回、自分のための選択ができれば十分です。"
    else:
        body = "体重や体脂肪だけでなく、記録を続けることそのものを目標にしましょう。小さく整える積み重ねがいちばん強いです。"

    if weight_text:
        body += f"\n\n体重の目安：{weight_text}"
    if body_fat_text:
        body += f"\n体脂肪の目安：{body_fat_text}"

    if tone == "しっかり":
        body += "\n\n今週も流れで過ごさず、1回ずつ整えていきましょう。"
    elif tone == "やさしく":
        body += "\n\n今週もあせらず、自分のペースで進めば大丈夫です。"

    return {
        "title": "今週の目標",
        "body": body,
    }


def get_log_streak_summary(user_id: str) -> dict:
    user_logs = [r for r in read_dietlog_records() if to_str(r.get("user_id", "")) == user_id]

    log_dates = set()
    for row in user_logs:
        log_date_str = to_str(row.get("log_date", "")).strip()
        if not log_date_str:
            continue
        try:
            log_dates.add(datetime.strptime(log_date_str, "%Y-%m-%d").date())
        except Exception:
            continue

    today = jst_today()
    yesterday = today - timedelta(days=1)

    if today in log_dates:
        days = 0
        cursor = today
        while cursor in log_dates:
            days += 1
            cursor -= timedelta(days=1)

        return {
            "days": days,
            "is_active": True,
            "label": f"今日で {days}日連続です",
            "detail": "このまま続けていきましょう。",
        }

    if yesterday in log_dates:
        days = 0
        cursor = yesterday
        while cursor in log_dates:
            days += 1
            cursor -= timedelta(days=1)

        return {
            "days": days,
            "is_active": False,
            "label": f"昨日まで {days}日連続でした",
            "detail": "今日も記録すると連続記録が続きます。",
        }

    return {
        "days": 0,
        "is_active": False,
        "label": "連続記録はまだありません",
        "detail": "まずは今日1回の記録からで大丈夫です。",
    }


def tone_short_message(text: str, tone: str) -> str:
    tone = to_str(tone).strip() or "やさしく"

    if tone == "しっかり":
        return f"{text} 今日は意識して整えましょう。"
    if tone == "淡々と":
        return text
    return f"{text} あせらず進めば大丈夫です。"


def parse_meal_sections(meal_memo: str) -> dict:
    text = (meal_memo or "").strip()
    result = {"朝": "", "昼": "", "夜": "", "間食": ""}

    current_key = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("朝:"):
            current_key = "朝"
            result["朝"] = line.replace("朝:", "", 1).strip()
        elif line.startswith("昼:"):
            current_key = "昼"
            result["昼"] = line.replace("昼:", "", 1).strip()
        elif line.startswith("夜:"):
            current_key = "夜"
            result["夜"] = line.replace("夜:", "", 1).strip()
        elif line.startswith("間食:"):
            current_key = "間食"
            result["間食"] = line.replace("間食:", "", 1).strip()
        else:
            if current_key:
                if result[current_key]:
                    result[current_key] += " " + line
                else:
                    result[current_key] = line

    return result


def _meal_style_hint(food_style: str) -> str:
    if food_style == "和食中心":
        return "ごはん・汁物・たんぱく質・野菜を意識すると整いやすいです。"
    if food_style == "バランス重視":
        return "主食・たんぱく質・野菜をそろえる形が基本です。"
    if food_style == "節約重視":
        return "卵、豆腐、鶏むね肉、納豆など使い回しやすい食材が向いています。"
    return "無理なく続けやすい形で整えるのがおすすめです。"


def _lunch_style_hint(settings: dict) -> str:
    lunch_style = str(settings.get("lunch_style", "指定なし"))

    if lunch_style == "お弁当":
        return "昼はお弁当前提で、冷めても食べやすいおかずがおすすめです。"
    if lunch_style == "外食":
        return "昼は外食前提で、定食・丼・麺なら野菜や汁物を足せる選び方がおすすめです。"
    if lunch_style == "コンビニ":
        return "昼はコンビニ前提で、おにぎり＋たんぱく質＋汁物の形にすると整えやすいです。"
    if lunch_style == "自宅":
        return "昼は家で食べる前提で、作りすぎない簡単ごはんがおすすめです。"
    return "昼はその日の予定に合わせて、重くなりすぎない形が向いています。"


def _support_points(settings: dict, latest_log: dict | None = None) -> list[str]:
    points = []
    traits = settings.get("constitution_traits", []) or []
    if isinstance(traits, str):
        traits = [x.strip() for x in traits.split(",") if x.strip()]

    conditions = []
    if latest_log:
        conditions = latest_log.get("today_conditions", []) or []
        if isinstance(conditions, str):
            conditions = [x.strip() for x in conditions.split(",") if x.strip()]

    if "冷えやすい" in traits:
        points.append("温かいもの")
    if "むくみやすい" in traits or "むくみあり" in conditions:
        points.append("塩分を重ねすぎないこと")
    if "疲れやすい" in traits or "だるい" in conditions:
        points.append("たんぱく質を抜かないこと")
    if "胃腸がゆらぎやすい" in traits or "食べすぎた" in conditions:
        points.append("やさしい味・軽め")
    if "寝不足" in conditions:
        points.append("甘いものだけで済ませないこと")

    return points[:3]


def get_today_advice(settings: dict, latest_log: dict | None = None) -> dict:
    user_type = str(settings.get("user_type", "自分だけ向け"))
    food_style = str(settings.get("food_style", "バランス重視"))
    lunch_style = str(settings.get("lunch_style", "指定なし"))
    advice_tone = str(settings.get("advice_tone", "やさしく"))

    meal_sections = parse_meal_sections(latest_log.get("meal_memo", "") if latest_log else "")
    support_points = _support_points(settings, latest_log)
    point_text = "・".join(support_points) if support_points else "主食・たんぱく質・野菜のバランス"

    style_hint = _meal_style_hint(food_style)
    lunch_hint = _lunch_style_hint(settings)

    if meal_sections["朝"]:
        breakfast = "朝はすでに記録ありなので、昼と夜で整えましょう。"
    else:
        breakfast = f"朝は軽くてもよいので、たんぱく質を入れる形がおすすめです。{style_hint}"

    if lunch_style == "お弁当":
        lunch = "昼はお弁当なら、ごはん＋卵・肉・魚のおかず＋野菜1品が基本です。"
    elif lunch_style == "外食":
        lunch = "昼が外食なら、定食・和食・丼＋汁物の形を優先し、揚げ物を重ねすぎないのがおすすめです。"
    elif lunch_style == "コンビニ":
        lunch = "昼がコンビニなら、おにぎり＋サラダチキン or ゆで卵＋汁物が整えやすいです。"
    elif lunch_style == "自宅":
        lunch = "昼が自宅なら、丼もの1品だけで終えず、汁物か野菜を少し足す形がおすすめです。"
    else:
        lunch = lunch_hint

    if meal_sections["夜"]:
        dinner = "夜はすでに記録ありなので、食べすぎ防止と寝る前の重さを避ける意識で十分です。"
    else:
        if user_type == "自分＋家族向け":
            dinner = "夜は家族も満足しつつ、自分は主食を少し控えめにして、主菜＋汁物＋野菜で整えるのがおすすめです。"
        elif user_type == "節約重視":
            dinner = "夜は卵・豆腐・鶏むね肉など使い回ししやすい食材で、簡単に整えるのがおすすめです。"
        elif user_type == "忙しい日向け":
            dinner = "夜は時短優先で、丼ものだけで終えず、汁物か野菜を1つ足す形がおすすめです。"
        else:
            dinner = f"夜は食べすぎず、{point_text} を意識して整えるのがおすすめです。"

    summary = f"今日は {point_text} を意識すると整いやすいです。"
    short_msg = tone_short_message("全部を完璧にしなくて大丈夫です。", advice_tone)

    return {
        "食事": summary,
        "朝": breakfast,
        "昼": lunch,
        "夜": dinner,
        "運動": get_today_exercise(settings, latest_log)["body"],
        "ひとこと": short_msg,
    }


def get_today_shopping_list(settings: dict, latest_log: dict | None = None) -> list[str]:
    meal_sections = parse_meal_sections(latest_log.get("meal_memo", "") if latest_log else "")
    lunch_style = str(settings.get("lunch_style", "指定なし"))
    items = []

    if not meal_sections["朝"]:
        items.extend(["卵", "ヨーグルト", "味噌汁"])
    if not meal_sections["昼"]:
        if lunch_style == "お弁当":
            items.extend(["おにぎり用ごはん", "卵", "冷めても食べやすいおかず"])
        elif lunch_style == "外食":
            items.extend(["外食時に足しやすいサラダ or 汁物"])
        elif lunch_style == "コンビニ":
            items.extend(["おにぎり", "サラダチキン", "ゆで卵", "スープ"])
        else:
            items.extend(["ごはん", "豆腐", "簡単な汁物"])
    if not meal_sections["夜"]:
        items.extend(["魚 or 肉", "野菜", "汁物用の材料"])

    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)

    return deduped


def get_today_exercise(settings: dict, latest_log: dict | None = None) -> dict:
    user_type = settings["user_type"]
    activity_level = settings["activity_level"]
    support = get_support_focus_summary(settings, latest_log)

    if user_type == "忙しい日向け":
        title = "5分ストレッチ"
    elif user_type == "節約重視":
        title = "家トレ"
    elif user_type == "自分＋家族向け":
        title = "散歩 or 軽い全身運動"
    else:
        title = "ヨガ or ピラティス基礎"

    body = support["exercise_tip"]

    if activity_level == "低い":
        level_text = "活動量は低め設定なので、今日は軽めで十分です。"
    elif activity_level == "高い":
        level_text = "活動量は高め設定なので、余裕があれば少しだけ負荷を上げても大丈夫です。"
    else:
        level_text = "活動量はふつう設定なので、軽め〜中くらいで整えるのがおすすめです。"

    return {
        "title": title,
        "body": body,
        "level_text": level_text,
    }

def detect_meal_type_by_time(now_dt) -> str:
    hour = now_dt.hour

    if 4 <= hour < 10:
        return "朝"
    elif 10 <= hour < 15:
        return "昼"
    elif 15 <= hour < 22:
        return "夜"
    else:
        return "間食"

def get_week_menu(settings: dict) -> list[dict]:
    user_type = settings["user_type"]

    if user_type == "節約重視":
        return [
            {"day": "月", "menu": "豆腐そぼろ丼＋味噌汁"},
            {"day": "火", "menu": "鶏むね肉とキャベツ炒め"},
            {"day": "水", "menu": "卵と野菜のあんかけ丼"},
            {"day": "木", "menu": "もやし入りハンバーグ"},
            {"day": "金", "menu": "焼きそば＋スープ"},
            {"day": "土", "menu": "カレーの残り活用"},
            {"day": "日", "menu": "作り置きおかず活用"},
        ]

    if user_type == "忙しい日向け":
        return [
            {"day": "月", "menu": "鶏むねレンジ蒸し＋サラダ"},
            {"day": "火", "menu": "鮭＋即席味噌汁＋ごはん"},
            {"day": "水", "menu": "丼もの＋カット野菜"},
            {"day": "木", "menu": "豆腐ハンバーグ"},
            {"day": "金", "menu": "パスタ＋スープ"},
            {"day": "土", "menu": "外食調整日"},
            {"day": "日", "menu": "冷蔵庫の残りで簡単ごはん"},
        ]

    if user_type == "自分＋家族向け":
        return [
            {"day": "月", "menu": "鶏むね肉と野菜炒め"},
            {"day": "火", "menu": "鮭と味噌汁"},
            {"day": "水", "menu": "親子丼＋サラダ"},
            {"day": "木", "menu": "豆腐ハンバーグ"},
            {"day": "金", "menu": "パスタ＋スープ"},
            {"day": "土", "menu": "外食調整日"},
            {"day": "日", "menu": "作り置き活用"},
        ]

    return [
        {"day": "月", "menu": "鶏むね肉と野菜炒め"},
        {"day": "火", "menu": "鮭と味噌汁"},
        {"day": "水", "menu": "丼もの＋サラダ"},
        {"day": "木", "menu": "豆腐ハンバーグ"},
        {"day": "金", "menu": "パスタ＋スープ"},
        {"day": "土", "menu": "外食調整日"},
        {"day": "日", "menu": "作り置き活用"},
    ]


# =========================
# 相談
# =========================
def get_user_type_advice(user_type: str) -> str:
    if user_type == "自分＋家族向け":
        return "家族も満足しつつ、自分は食べすぎない組み立てを優先します。"
    if user_type == "節約重視":
        return "使い回ししやすい食材と家でできる工夫を優先します。"
    if user_type == "忙しい日向け":
        return "時短・手間少なめ・続けやすさ優先で考えます。"
    return "まずは自分の体調を整えることを優先します。"


def normalize_question(text: str) -> str:
    return (
        text.lower()
        .replace("　", " ")
        .replace("？", "?")
        .replace("。", " ")
        .replace("、", " ")
        .replace("！", "!")
        .strip()
    )


def apply_advice_tone(text: str, tone: str) -> str:
    tone = to_str(tone).strip() or "やさしく"

    if tone == "しっかり":
        return f"今日は少し意識して整えましょう。\n\n{text}\n\n次の1回をきちんと整える意識で進めるのがおすすめです。"
    if tone == "淡々と":
        return text
    return f"大丈夫です。無理なく整えていきましょう。\n\n{text}\n\nできるところからで十分です。"


def format_meal_proposals(question: str, settings: dict, latest_log: dict | None = None) -> str:
    advice = get_today_advice(settings, latest_log)
    shopping_items = get_today_shopping_list(settings, latest_log)

    lines = [
        "今日の食事提案です。",
        "",
        "【朝】",
        advice["朝"],
        "",
        "【昼】",
        advice["昼"],
        "",
        "【夜】",
        advice["夜"],
    ]

    if shopping_items:
        lines.extend(
            [
                "",
                "【買い足し候補】",
                "・" + "\n・".join(shopping_items),
            ]
        )

    return "\n".join(lines)


def build_food_answer(question: str, settings: dict, latest_log: dict | None = None) -> str:
    q = normalize_question(question)
    base = get_user_type_advice(settings["user_type"])
    style = f"食事スタイルは「{settings['food_style']}」で考えます。"
    support = get_support_focus_summary(settings, latest_log)
    context = f"今整えたいポイント：{' / '.join(support['points'])}" if support["points"] else ""

    if any(k in q for k in ["提案", "メニュー", "献立", "何食べ", "何を食べ", "夕飯", "夕食", "朝ごはん", "昼ごはん", "ランチ"]):
        parts = [f"相談内容：{question}", base, style]
        if context:
            parts.append(context)
        parts.append(format_meal_proposals(question, settings, latest_log))
        return "\n\n".join(parts)

    answer = "食事は、主食を極端に抜かず、たんぱく質を毎食少し入れると安定しやすいです。迷ったら『汁物＋たんぱく質＋主食少し＋野菜』で考えると組みやすいです。"

    parts = [f"相談内容：{question}", base, style]
    if context:
        parts.append(context)
    parts.append("今日の目安：" + support["food_tip"])
    parts.append(answer)

    return "\n\n".join(parts)


def build_exercise_answer(question: str, settings: dict, latest_log: dict | None = None) -> str:
    q = normalize_question(question)
    level = settings["activity_level"]
    base = get_user_type_advice(settings["user_type"])
    support = get_support_focus_summary(settings, latest_log)
    context = f"今整えたいポイント：{' / '.join(support['points'])}" if support["points"] else ""

    if any(k in q for k in ["5分", "5ぷん", "短時間", "忙しい", "時間がない"]):
        answer = "今日は5分で十分です。肩回し1分、前もも伸ばし1分、股関節まわし1分、軽いスクワット1分、深呼吸1分でOKです。"
    elif any(k in q for k in ["疲れ", "だるい", "しんどい"]):
        answer = "疲れている日は、追い込むより、ストレッチ・肩回し・軽い散歩のような回復寄りの動きが合います。"
    else:
        answer = "迷った日は『ストレッチ→軽い全身運動→深呼吸』の順で短く動くと続けやすいです。"

    if level == "低い":
        level_text = "活動量は低め設定なので、今日は無理せず軽めで十分です。"
    elif level == "高い":
        level_text = "活動量は高め設定なので、余裕があれば少し負荷を上げても大丈夫です。"
    else:
        level_text = "活動量はふつう設定なので、軽め〜中くらいで整えるのがおすすめです。"

    parts = [f"相談内容：{question}", base, level_text]
    if context:
        parts.append(context)
    parts.append("今日の目安：" + support["exercise_tip"])
    parts.append(answer)

    return "\n\n".join(parts)


def build_condition_answer(question: str, settings: dict, latest_log: dict | None = None) -> str:
    q = normalize_question(question)
    base = get_user_type_advice(settings["user_type"])
    support = get_support_focus_summary(settings, latest_log)
    context = f"今整えたいポイント：{' / '.join(support['points'])}" if support["points"] else ""

    if any(k in q for k in ["むくみ", "だるい", "重い"]):
        answer = "むくみやだるさがある日は、冷たい物を重ねすぎず、水分をこまめに取り、足首を回したり軽く歩いたりすると整えやすいです。"
    elif any(k in q for k in ["疲れ", "つかれ", "しんどい"]):
        answer = "疲れが強い日は、無理に頑張る日ではなく回復優先でOKです。食事は抜かず、汁物・たんぱく質・炭水化物を少し入れてください。"
    else:
        answer = "体調が揺れている日は、食事を極端に減らさず、温かい物と軽い運動で整える考え方がおすすめです。"

    parts = [f"相談内容：{question}", base]
    if context:
        parts.append(context)
    parts.append("今日の目安：" + support["food_tip"])
    parts.append(answer)

    return "\n\n".join(parts)


def build_eating_out_answer(question: str, settings: dict, latest_log: dict | None = None) -> str:
    base = get_user_type_advice(settings["user_type"])
    support = get_support_focus_summary(settings, latest_log)
    context = f"今整えたいポイント：{' / '.join(support['points'])}" if support["points"] else ""
    answer = "外食は『主菜を決める → 汁物かサラダを足す → 主食を食べすぎない』で考えると整えやすいです。"

    parts = [f"相談内容：{question}", base]
    if context:
        parts.append(context)
    parts.append("今日の目安：" + support["food_tip"])
    parts.append(answer)

    return "\n\n".join(parts)


def generate_answer(category: str, question: str, settings: dict, latest_log: dict | None = None) -> str:
    question = question.strip()
    if not question:
        return "相談内容を入力してください。短くても大丈夫です。"

    if category == "食事":
        answer = build_food_answer(question, settings, latest_log)
    elif category == "運動":
        answer = build_exercise_answer(question, settings, latest_log)
    elif category == "体調":
        answer = build_condition_answer(question, settings, latest_log)
    elif category == "外食調整":
        answer = build_eating_out_answer(question, settings, latest_log)
    else:
        answer = f"相談内容：{question}\n\nカテゴリを選んで相談してください。"

    return apply_advice_tone(answer, settings.get("advice_tone", "やさしく"))


def build_log_feedback(user_id: str, save_data: dict) -> dict:
    settings = load_user_settings(user_id)
    tone = to_str(settings.get("advice_tone", "やさしく")) or "やさしく"

    weight = to_float(save_data.get("weight"), settings.get("current_weight", 0.0))
    body_fat = to_float(save_data.get("body_fat"), settings.get("current_body_fat", 0.0))
    target_weight = to_float(settings.get("target_weight", 0.0), 0.0)
    target_body_fat = to_float(settings.get("target_body_fat", 0.0), 0.0)

    meal_memo = to_str(save_data.get("meal_memo", "")).strip()
    exercise_memo = to_str(save_data.get("exercise_memo", "")).strip()
    condition_note = to_str(save_data.get("condition_note", "")).strip()
    mood_note = to_str(save_data.get("mood_note", "")).strip()

    support = get_support_focus_summary(settings, save_data)
    lines = []

    weight_diff = round(weight - target_weight, 1)
    if weight_diff <= 0:
        lines.append(f"体重は目標圏内です（{weight:.1f}kg）。")
    elif weight_diff <= 1.0:
        lines.append(f"体重は目標まであと {weight_diff:.1f}kg です。近い位置です。")
    else:
        lines.append(f"体重は目標まであと {weight_diff:.1f}kg です。")

    body_fat_diff = round(body_fat - target_body_fat, 1)
    if body_fat_diff <= 0:
        lines.append(f"体脂肪は目標圏内です（{body_fat:.1f}%）。")
    elif body_fat_diff <= 1.0:
        lines.append(f"体脂肪は目標まであと {body_fat_diff:.1f}% です。")
    else:
        lines.append(f"体脂肪は目標まであと {body_fat_diff:.1f}% です。")

    if meal_memo and exercise_memo:
        lines.append("食事と運動の両方を記録できています。振り返りやすい状態です。")
    elif meal_memo:
        lines.append("食事記録があります。運動も一言あると、あとで見返しやすくなります。")
    elif exercise_memo:
        lines.append("運動記録があります。食事も一言あると、流れが見やすくなります。")
    else:
        lines.append("今日は数値中心の記録です。食事か運動を一言残すと振り返りやすくなります。")

    if support["points"]:
        lines.append("今整えたいポイント： " + " / ".join(support["points"]))

    if condition_note or mood_note:
        lines.append("体調や気分も残せているので、変化を追いやすいです。")

    if tone == "しっかり":
        title = "記録完了"
        closing = "次回も数値だけでなく、内容まで整えていきましょう。"
    elif tone == "淡々と":
        title = "記録を保存しました"
        closing = ""
    else:
        title = "今日の記録を保存しました"
        closing = "この調子で少しずつ整えていけば大丈夫です。"

    body = "\n".join(lines)
    if closing:
        body += f"\n\n{closing}"

    return {
        "title": title,
        "body": body,
    }


# =========================
# 食事評価
# =========================
MEAL_TYPE_LABELS = {
    "朝ごはん": "朝ごはん",
    "昼ごはん": "昼ごはん",
    "夜ごはん": "夜ごはん",
    "間食": "間食",
    "朝": "朝ごはん",
    "昼": "昼ごはん",
    "夜": "夜ごはん",
}

PROTEIN_WORDS = [
    "卵", "ゆで卵", "豆腐", "納豆", "鮭", "しゃけ", "しらす", "鶏", "鶏肉",
    "豚", "豚肉", "牛", "牛肉", "魚", "さば", "サバ", "ツナ", "枝豆",
    "ヨーグルト", "豆乳", "サラダチキン", "チキン", "豆", "ハム", "チーズ",
]

VEGETABLE_WORDS = [
    "サラダ", "野菜", "ブロッコリー", "ほうれん草", "小松菜", "トマト", "キャベツ",
    "レタス", "きのこ", "えのき", "しいたけ", "椎茸", "しめじ", "わかめ",
    "青のり", "とろろ昆布", "昆布", "ごぼう", "大根", "にんじん", "玉ねぎ",
    "オクラ", "海藻", "乾燥野菜", "おひたし", "白菜", "もやし",
]

FRUIT_WORDS = [
    "ブルーベリー", "パイナップル", "キウイ", "いちご", "みかん", "バナナ",
    "りんご", "果物", "フルーツ", "オレンジ",
]

SOUP_WORDS = [
    "味噌汁", "みそ汁", "スープ", "豚汁", "鍋", "汁物",
]

CARB_WORDS = [
    "ごはん", "おにぎり", "パン", "トースト", "麺", "パスタ", "うどん",
    "そば", "ベーグル", "雑炊", "乾麺", "オートミール",
]

HEAVY_WORDS = [
    "揚げ", "揚げ物", "唐揚げ", "ラーメン", "カレー", "丼", "大盛り",
    "クリーム", "カルボナーラ", "ポテト", "チーズたっぷり", "こってり",
]

SALTY_WORDS = [
    "味噌", "みそ", "しらす", "鮭", "しゃけ", "サバ", "さば",
    "漬物", "昆布", "ポン酢", "味付き", "塩", "塩焼き",
]


def _count_hits(text: str, words: list[str]) -> int:
    count = 0
    for word in words:
        if word in text:
            count += 1
    return count


def parse_meal_sections_from_text(meal_memo: str) -> dict:
    text = to_str(meal_memo)
    result = {"朝": "", "昼": "", "夜": "", "間食": ""}

    lines = text.splitlines()
    current_key = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("朝:"):
            current_key = "朝"
            result[current_key] = line.replace("朝:", "", 1).strip()
        elif line.startswith("昼:"):
            current_key = "昼"
            result[current_key] = line.replace("昼:", "", 1).strip()
        elif line.startswith("夜:"):
            current_key = "夜"
            result[current_key] = line.replace("夜:", "", 1).strip()
        elif line.startswith("間食:"):
            current_key = "間食"
            result[current_key] = line.replace("間食:", "", 1).strip()
        else:
            if current_key:
                if result[current_key]:
                    result[current_key] += " " + line
                else:
                    result[current_key] = line

    return result


def get_meal_flow_context_text(meal_type: str, current_meal_text: str, latest_log: dict | None = None) -> str:
    meal_label = MEAL_TYPE_LABELS.get(meal_type, meal_type)
    if latest_log is None:
        return ""

    sections = parse_meal_sections_from_text(latest_log.get("meal_memo", ""))

    current_key_map = {
        "朝ごはん": "朝",
        "昼ごはん": "昼",
        "夜ごはん": "夜",
        "間食": "間食",
        "朝": "朝",
        "昼": "昼",
        "夜": "夜",
    }
    current_key = current_key_map.get(meal_type, "")

    if current_key:
        sections[current_key] = current_meal_text.strip()

    lines = []

    if meal_label == "朝ごはん":
        lines.append("朝はこの内容で見ます。")
        if not sections.get("昼"):
            lines.append("昼は、たんぱく質か汁物を少し足せると流れが整いやすいです。")
        if not sections.get("夜"):
            lines.append("夜は重くしすぎず、野菜や汁物を入れると1日がまとまりやすいです。")

    elif meal_label == "昼ごはん":
        if sections.get("朝"):
            lines.append("朝からの流れを見て、昼で不足を補う形で考えます。")
        if not sections.get("夜"):
            lines.append("夜は薄味・野菜多めにすると整いやすいです。")

    elif meal_label == "夜ごはん":
        if sections.get("朝") or sections.get("昼"):
            lines.append("朝昼の流れも見て、夜で1日を整える形で考えます。")
            day_text = " ".join([sections.get("朝", ""), sections.get("昼", "")])

            if _count_hits(day_text, SALTY_WORDS) >= 3:
                lines.append("今日は塩分が少したまりやすい流れなので、夜は薄味寄りが合いやすいです。")
            if _count_hits(day_text, PROTEIN_WORDS) == 0:
                lines.append("今日はここまでたんぱく質が少なめなので、夜で少し補えると良いです。")
            if _count_hits(day_text, VEGETABLE_WORDS) <= 1:
                lines.append("今日は野菜や食物繊維が少なめなので、夜で足すとまとまりやすいです。")

    elif meal_label == "間食":
        lines.append("間食は、次の食事に響きにくい量と内容にするのがポイントです。")

    return "\n".join(lines)


def build_food_evaluation_from_text(
    meal_type: str,
    meal_text: str,
    settings: dict,
    latest_log: dict | None = None,
    note: str = "",
) -> dict:
    meal_label = MEAL_TYPE_LABELS.get(meal_type, meal_type)
    text = to_str(meal_text).strip()
    note = to_str(note).strip()

    if not text:
        return {
            "title": f"{meal_label}の評価",
            "body": "食事内容がまだ入っていません。写真に写っている内容や食べたものを少し入れると、評価しやすくなります。",
            "score_text": "",
        }

    support = get_support_focus_summary(settings, latest_log)

    protein_count = _count_hits(text, PROTEIN_WORDS)
    vegetable_count = _count_hits(text, VEGETABLE_WORDS)
    fruit_count = _count_hits(text, FRUIT_WORDS)
    soup_count = _count_hits(text, SOUP_WORDS)
    carb_count = _count_hits(text, CARB_WORDS)
    heavy_count = _count_hits(text, HEAVY_WORDS)
    salty_count = _count_hits(text, SALTY_WORDS)

    score = 78

    if protein_count >= 1:
        score += 4
    if protein_count >= 2:
        score += 3
    if vegetable_count >= 1:
        score += 4
    if vegetable_count >= 3:
        score += 3
    if fruit_count >= 1:
        score += 2
    if soup_count >= 1:
        score += 3
    if carb_count >= 1:
        score += 2
    if heavy_count >= 1:
        score -= 4
    if heavy_count >= 2:
        score -= 3
    if salty_count >= 2:
        score -= 2
    if salty_count >= 4:
        score -= 2

    if meal_label == "朝ごはん":
        if protein_count >= 1 and carb_count >= 1:
            score += 2
        if fruit_count >= 1:
            score += 1

    if meal_label == "夜ごはん":
        if heavy_count >= 1:
            score -= 2
        if soup_count >= 1 or vegetable_count >= 2:
            score += 2

    score = max(55, min(score, 96))

    if score >= 90:
        score_text = "90〜95点"
    elif score >= 85:
        score_text = "85〜90点"
    elif score >= 80:
        score_text = "80〜85点"
    elif score >= 75:
        score_text = "75〜80点"
    else:
        score_text = "70〜75点"

    good_points = []
    concern_points = []
    improve_points = []

    if protein_count >= 1:
        good_points.append("たんぱく質が入っていて、満足感や回復につながりやすいです。")
    else:
        concern_points.append("たんぱく質が少なめなので、腹持ちや引き締め目線では少し弱めです。")
        improve_points.append("卵、豆腐、納豆、魚、鶏肉などを1つ足すと整いやすいです。")

    if vegetable_count >= 1:
        good_points.append("野菜・きのこ・海藻系が入っていて、バランスを取りやすいです。")
    else:
        concern_points.append("野菜や食物繊維が少なめです。")
        improve_points.append("味噌汁、温野菜、トマト、ブロッコリー、おひたしなどを少し足すと良いです。")

    if soup_count >= 1:
        good_points.append("汁物があるので、体を冷やしにくく、食事全体も整いやすいです。")

    if fruit_count >= 1:
        good_points.append("果物が入っていて、ビタミン面でもプラスです。")

    if salty_count >= 3:
        concern_points.append("塩分はやや重なりやすい組み合わせです。")
        improve_points.append("次の食事は薄味・水分・野菜を意識すると整いやすいです。")

    if heavy_count >= 1:
        concern_points.append("少し重めになりやすい内容です。")
        improve_points.append("量を少し控えるか、野菜や汁物を足すとバランスが取りやすいです。")

    if not good_points:
        good_points.append("大きく崩れているわけではなく、整え方しだいで十分良くできます。")

    if not concern_points:
        concern_points.append("大きな弱点はありません。今日はこのままでもかなり整っています。")

    if not improve_points:
        improve_points.append(support["food_tip"] if support["food_tip"] else "次の食事で汁物か野菜を少し足すと、さらにまとまりやすいです。")

    flow_text = get_meal_flow_context_text(meal_type=meal_type, current_meal_text=text, latest_log=latest_log)

    lines = [f"{meal_label}としては {score_text} くらいです。"]

    if flow_text:
        lines.append("")
        lines.append(flow_text)

    lines.append("")
    lines.append("良いところ")
    for item in good_points[:5]:
        lines.append(f"・{item}")

    lines.append("")
    lines.append("少し気になるところ")
    for item in concern_points[:4]:
        lines.append(f"・{item}")

    lines.append("")
    lines.append("さらに良くするなら")
    for item in improve_points[:4]:
        lines.append(f"・{item}")

    if support["points"]:
        lines.append("")
        lines.append("今整えたいポイント")
        lines.append("・" + " / ".join(support["points"]))

    if note:
        lines.append("")
        lines.append("補足メモ")
        lines.append(f"・{note}")

    return {
        "title": f"{meal_label}の評価",
        "body": "\n".join(lines),
        "score_text": score_text,
        "score_value": score,
    }

def simple_food_guess(meal_type: str) -> str:
    if meal_type == "朝":
        return "納豆、ごはん、味噌汁、ヨーグルト"
    elif meal_type == "昼":
        return "おにぎり、卵焼き、ブロッコリー"
    elif meal_type == "夜":
        return "鮭、サラダ、味噌汁、ごはん"
    else:
        return "ナッツ、ヨーグルト"

import random

def generate_weekly_plan(settings: dict, latest_log: dict | None = None) -> dict:
    import random

    user_type = settings.get("user_type", "自分だけ向け")
    food_style = settings.get("food_style", "バランス重視")
    activity = settings.get("activity_level", "ふつう")
    lunch_style = settings.get("lunch_style", "指定なし")

    # 体調
    conditions = []
    if latest_log:
        conditions = latest_log.get("today_conditions", []) or []
        if isinstance(conditions, str):
            conditions = [x.strip() for x in conditions.split(",")]

    # 体質
    traits = settings.get("constitution_traits", []) or []
    if isinstance(traits, str):
        traits = [x.strip() for x in traits.split(",")]

    # -----------------
    # 食材ベース
    # -----------------
    protein = ["鶏むね肉", "鮭", "豚肉", "卵", "豆腐"]
    veg = ["サラダ", "味噌汁", "野菜炒め"]
    carb = ["ごはん", "丼", "うどん", "パスタ"]

    # -----------------
    # 体質反映
    # -----------------
    if "むくみやすい" in traits:
        veg.append("きのこたっぷり味噌汁")
    if "冷えやすい" in traits:
        veg.append("温野菜＋スープ")

    # -----------------
    # 体調反映
    # -----------------
    if "疲れ" in str(conditions):
        protein.append("豚肉（疲労回復）")

    # -----------------
    # 活動量
    # -----------------
    if activity == "高い":
        carb.append("しっかりごはん")
    elif activity == "低い":
        carb = ["軽めごはん", "スープ"]

    # -----------------
    # 節約
    # -----------------
    if food_style == "節約重視":
        protein = ["卵", "豆腐", "鶏むね肉"]

    # -----------------
    # 家族向け
    # -----------------
    if user_type == "自分＋家族向け":
        protein.append("ハンバーグ")
        carb.append("カレー")

    # -----------------
    # 曜日生成
    # -----------------
    days = ["月", "火", "水", "木", "金", "土", "日"]
    plan = {}

    for d in days:
        if d == "土":
            plan[d] = "外食 or 調整日"
        elif d == "日":
            plan[d] = "作り置き・リセット日"
        else:
            plan[d] = f"{random.choice(protein)}＋{random.choice(veg)}＋{random.choice(carb)}"

    return plan

def get_week_key():
    today = jst_now()
    return f"{today.year}-{today.isocalendar()[1]}"

def generate_shopping_list_from_week(plan: dict) -> dict:

    categories = {
        "肉・魚": [],
        "野菜": [],
        "主食": [],
        "調味料": [],
        "その他": []
    }

    for meal in plan.values():

        if "鶏" in meal:
            categories["肉・魚"].append("鶏むね肉")
        if "鮭" in meal:
            categories["肉・魚"].append("鮭")
        if "豚" in meal:
            categories["肉・魚"].append("豚肉")

        if "サラダ" in meal or "野菜" in meal:
            categories["野菜"].extend(["キャベツ", "にんじん"])
        if "味噌汁" in meal:
            categories["野菜"].append("ねぎ")

        if "ごはん" in meal or "丼" in meal:
            categories["主食"].append("米")
        if "パスタ" in meal:
            categories["主食"].append("パスタ")

        if "味噌汁" in meal:
            categories["調味料"].extend(["味噌", "だし"])

    # 重複削除
    for k in categories:
        categories[k] = list(set(categories[k]))

    return categories
