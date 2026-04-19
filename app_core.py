import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, date
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
    "user_type",
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
        ws = ss.add_worksheet(title=title, rows=rows, cols=len(headers))
        ws.append_row(headers)

    ensure_headers(ws, headers)
    return ws


def get_users_sheet():
    return get_or_create_sheet("Users", USERS_HEADERS, rows=300)


def get_settings_sheet():
    return get_or_create_sheet("Settings", SETTINGS_HEADERS, rows=300)


def get_dietlogs_sheet():
    return get_or_create_sheet("DietLogs", DIETLOG_HEADERS, rows=2000)


# =========================
# 読み取りキャッシュ
# =========================
@st.cache_data(ttl=30, show_spinner=False)
def read_users_records():
    ws = get_users_sheet()
    return ws.get_all_records()


@st.cache_data(ttl=30, show_spinner=False)
def read_settings_records():
    ws = get_settings_sheet()
    return ws.get_all_records()


@st.cache_data(ttl=30, show_spinner=False)
def read_dietlog_records():
    ws = get_dietlogs_sheet()
    return ws.get_all_records()


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


# 既存ページ互換用
def get_user_id() -> str:
    user_id = get_current_user_id()
    if not user_id:
        raise RuntimeError("ログインが必要です。")
    return user_id


# =========================
# 共通行検索
# =========================
def find_user_row_by_user_id(ws, user_id: str):
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

    records = read_users_records()
    for record in records:
        if (
            to_str(record.get("login_id", "")).strip() == login_id
            and to_str(record.get("is_active", "1")).strip() != "0"
        ):
            return record
    return None


def find_user_by_user_id(user_id: str) -> dict | None:
    records = read_users_records()
    for record in records:
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

    if isinstance(birth_date, date):
        birth_date_str = birth_date.strftime("%Y-%m-%d")
    else:
        birth_date_str = to_str(birth_date).strip()

    if not birth_date_str:
        raise ValueError("生年月日を入力してください。")

    if find_user_by_login_id(login_id):
        raise ValueError("そのログインIDは既に使われています。")

    user_id = uuid4().hex
    salt = generate_salt()
    password_hash = hash_password(password, salt)
    now_str = jst_now().strftime("%Y-%m-%d %H:%M:%S")
    age = calculate_age_from_birth_date(birth_date_str)

    users_ws = get_users_sheet()
    users_ws.append_row(
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

    settings_ws = get_settings_sheet()
    settings_ws.append_row(
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
            "自分だけ向け",
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

    if verify_password(password, salt, password_hash):
        return user_record

    return None


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


def change_login_id(user_id: str, current_password: str, new_login_id: str):
    new_login_id = new_login_id.strip()

    if not user_id:
        raise ValueError("ユーザー情報が見つかりません。")
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

    ws = get_users_sheet()
    row_index = find_user_row_by_user_id(ws, user_id)
    if not row_index:
        raise ValueError("Usersシートの更新行が見つかりません。")

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

    end_col = chr(64 + len(USERS_HEADERS))
    ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])

    st.session_state["auth_login_id"] = new_login_id
    clear_sheet_caches()


def change_password(user_id: str, current_password: str, new_password: str, new_password_confirm: str):
    if not user_id:
        raise ValueError("ユーザー情報が見つかりません。")
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

    ws = get_users_sheet()
    row_index = find_user_row_by_user_id(ws, user_id)
    if not row_index:
        raise ValueError("Usersシートの更新行が見つかりません。")

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

    end_col = chr(64 + len(USERS_HEADERS))
    ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])

    clear_sheet_caches()


def change_birth_date(user_id: str, current_password: str, new_birth_date):
    if not user_id:
        raise ValueError("ユーザー情報が見つかりません。")
    if not current_password:
        raise ValueError("現在のパスワードを入力してください。")

    current_user = find_user_by_user_id(user_id)
    if not current_user:
        raise ValueError("現在のユーザーが見つかりません。")

    password_salt = to_str(current_user.get("password_salt", ""))
    password_hash = to_str(current_user.get("password_hash", ""))

    if not verify_password(current_password, password_salt, password_hash):
        raise ValueError("現在のパスワードが違います。")

    if isinstance(new_birth_date, date):
        birth_date_str = new_birth_date.strftime("%Y-%m-%d")
    else:
        birth_date_str = to_str(new_birth_date).strip()

    if not birth_date_str:
        raise ValueError("生年月日を入力してください。")

    new_age = calculate_age_from_birth_date(birth_date_str)
    if new_age is None:
        raise ValueError("生年月日が正しくありません。")

    users_ws = get_users_sheet()
    user_row_index = find_user_row_by_user_id(users_ws, user_id)
    if not user_row_index:
        raise ValueError("Usersシートの更新行が見つかりません。")

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

    users_end_col = chr(64 + len(USERS_HEADERS))
    users_ws.update(f"A{user_row_index}:{users_end_col}{user_row_index}", [updated_user_row])

    settings_ws = get_settings_sheet()
    settings_row_index = find_user_row_by_user_id(settings_ws, user_id)

    if settings_row_index:
        current_settings = load_user_settings(user_id)

        updated_settings_row = [
            user_id,
            to_str(current_settings.get("nickname", "")).strip(),
            new_age,
            current_settings.get("height_cm", 160.0),
            current_settings.get("current_weight", 50.0),
            current_settings.get("target_weight", 48.0),
            current_settings.get("current_body_fat", 30.0),
            current_settings.get("target_body_fat", 28.0),
            to_str(current_settings.get("activity_level", "ふつう")) or "ふつう",
            to_str(current_settings.get("food_style", "バランス重視")) or "バランス重視",
            to_str(current_settings.get("user_type", "自分だけ向け")) or "自分だけ向け",
            jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        ]

        settings_end_col = chr(64 + len(SETTINGS_HEADERS))
        settings_ws.update(
            f"A{settings_row_index}:{settings_end_col}{settings_row_index}",
            [updated_settings_row],
        )

    clear_sheet_caches()


# =========================
# Settings保存・読込
# =========================
def load_user_settings(user_id: str) -> dict:
    records = read_settings_records()
    profile = load_current_user_profile()
    profile_nickname = profile["nickname"] if profile else ""
    auto_age = profile["age"] if profile and profile.get("age") is not None else None

    for record in records:
        if str(record.get("user_id", "")) == user_id:
            fallback_age = to_int(record.get("age", 49), 49)

            return {
                "nickname": profile_nickname or to_str(record.get("nickname", "")),
                "age": auto_age if auto_age is not None else fallback_age,
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
        "nickname": profile_nickname,
        "age": auto_age if auto_age is not None else 49,
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
    ws = get_settings_sheet()
    profile = load_current_user_profile()
    current_user = find_user_by_user_id(user_id)

    age = None
    if profile and profile.get("user_id") == user_id:
        age = profile.get("age")

    row_data = [
        user_id,
        data["nickname"],
        age if age is not None else "",
        data["height_cm"],
        data["current_weight"],
        data["target_weight"],
        data["current_body_fat"],
        data["target_body_fat"],
        data["activity_level"],
        data["food_style"],
        data["user_type"],
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
    ]

    row_index = find_user_row_by_user_id(ws, user_id)

    if row_index:
        end_col = chr(64 + len(SETTINGS_HEADERS))
        ws.update(f"A{row_index}:{end_col}{row_index}", [row_data])
    else:
        ws.append_row(row_data)

    # Users.nickname も同期
    if current_user:
        users_ws = get_users_sheet()
        user_row_index = find_user_row_by_user_id(users_ws, user_id)
        if user_row_index:
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
            users_end_col = chr(64 + len(USERS_HEADERS))
            users_ws.update(
                f"A{user_row_index}:{users_end_col}{user_row_index}",
                [updated_user_row],
            )
            st.session_state["auth_nickname"] = data["nickname"]

    clear_sheet_caches()


# =========================
# DietLogs保存・読込
# =========================
def save_diet_log(user_id: str, data: dict):
    ws = get_dietlogs_sheet()
    row_data = [
        user_id,
        data["log_date"],
        data["weight"],
        data["body_fat"],
        data["meal_memo"],
        data["exercise_memo"],
        data["condition_note"],
        data["mood_note"],
        jst_now().strftime("%Y-%m-%d %H:%M:%S"),
    ]
    ws.append_row(row_data)
    clear_sheet_caches()


def load_latest_log(user_id: str) -> dict | None:
    records = read_dietlog_records()

    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]
    if not user_logs:
        return None

    def sort_key(x):
        created_at = to_str(x.get("created_at", ""))
        log_date = to_str(x.get("log_date", ""))
        return (log_date, created_at)

    user_logs.sort(key=sort_key, reverse=True)
    return user_logs[0]


def get_initial_log_values(user_id: str) -> dict:
    latest = load_latest_log(user_id)
    if latest:
        return {
            "weight": to_float(latest.get("weight", 50.0), 50.0),
            "body_fat": to_float(latest.get("body_fat", 30.0), 30.0),
        }

    settings = load_user_settings(user_id)
    return {
        "weight": settings["current_weight"],
        "body_fat": settings["current_body_fat"],
    }


def load_recent_logs(user_id: str, limit: int = 10) -> pd.DataFrame:
    records = read_dietlog_records()
    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]

    if not user_logs:
        return pd.DataFrame()

    df = pd.DataFrame(user_logs)

    df["log_date_sort"] = pd.to_datetime(df.get("log_date"), errors="coerce")
    df["created_at_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")

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


def load_log_chart_df(user_id: str) -> pd.DataFrame:
    records = read_dietlog_records()
    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]

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
    df = df.sort_values(
        by=["log_date_sort", "created_at_sort"],
        ascending=[True, True],
        na_position="last",
    )

    df = df.drop_duplicates(subset=["log_date"], keep="last")

    chart_df = pd.DataFrame(
        {
            "日付": df["log_date_sort"],
            "体重(kg)": df["weight_num"],
            "体脂肪(%)": df["body_fat_num"],
        }
    ).set_index("日付")

    return chart_df


def get_today_log_status(user_id: str) -> dict:
    today = jst_today_str()
    records = read_dietlog_records()

    today_logs = [
        r
        for r in records
        if str(r.get("user_id", "")) == user_id
        and to_str(r.get("log_date", "")) == today
    ]

    if not today_logs:
        return {
            "is_logged": False,
            "label": "今日はまだ未記録です",
            "detail": "体重・体脂肪・食事・運動を記録できます。",
        }

    def sort_key(x):
        return to_str(x.get("created_at", ""))

    today_logs.sort(key=sort_key, reverse=True)
    latest = today_logs[0]
    created_at = to_str(latest.get("created_at", ""))

    time_text = ""
    if len(created_at) >= 16:
        time_text = created_at[11:16]

    if time_text:
        detail = f"今日の記録は保存済みです（最終保存 {time_text}）"
    else:
        detail = "今日の記録は保存済みです。"

    return {
        "is_logged": True,
        "label": "今日は記録済みです",
        "detail": detail,
    }


# =========================
# ホーム用サマリー
# =========================
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
# ホーム提案
# =========================
def get_today_advice(settings: dict) -> dict:
    user_type = settings["user_type"]
    food_style = settings["food_style"]

    if user_type == "自分＋家族向け":
        return {
            "食事": f"家族も満足しやすく、自分は重くなりすぎない組み立てがおすすめです。食事スタイルは「{food_style}」を軸に考えます。",
            "運動": "すきま時間の軽い運動で十分です。家事の合間に5〜10分でもOKです。",
            "ひとこと": "全部を完璧にしなくて大丈夫です。",
        }
    if user_type == "節約重視":
        return {
            "食事": f"使い回ししやすい食材で組み立てる日がおすすめです。食事スタイルは「{food_style}」を軸に考えます。",
            "運動": "家でできる軽い運動を優先しましょう。お金をかけずに続ける形でOKです。",
            "ひとこと": "無理なく続けられる形がいちばん強いです。",
        }
    if user_type == "忙しい日向け":
        return {
            "食事": f"時短・洗い物少なめの献立がおすすめです。食事スタイルは「{food_style}」を軸に考えます。",
            "運動": "今日は5分だけでも十分です。ゼロにしないことを優先します。",
            "ひとこと": "今日は回すこと優先で大丈夫です。",
        }

    return {
        "食事": f"軽めに整えながら、無理のない食事がおすすめです。食事スタイルは「{food_style}」を軸に考えます。",
        "運動": "短時間でも、自分のための運動時間を少し取りましょう。",
        "ひとこと": "今日は自分優先で大丈夫です。",
    }


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


def get_today_exercise(settings: dict) -> dict:
    user_type = settings["user_type"]
    activity_level = settings["activity_level"]

    if user_type == "忙しい日向け":
        title = "5分ストレッチ"
        body = "肩回し、前もも伸ばし、股関節ほぐし、深呼吸でOKです。"
    elif user_type == "節約重視":
        title = "家トレ"
        body = "スクワット、肩回し、かかと上げを少しずつ。家でできる範囲で十分です。"
    elif user_type == "自分＋家族向け":
        title = "散歩 or 軽い全身運動"
        body = "10〜20分の散歩や、すきま時間の全身運動がおすすめです。"
    else:
        title = "ヨガ or ピラティス基礎"
        body = "短時間でも自分の体を整える時間を取るのがおすすめです。"

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


# =========================
# 相談ロジック
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


def build_food_answer(question: str, settings: dict) -> str:
    q = normalize_question(question)
    base = get_user_type_advice(settings["user_type"])
    style = f"食事スタイルは「{settings['food_style']}」で考えます。"

    if any(k in q for k in ["運動前", "トレーニング前", "ヨガ前", "ピラティス前"]):
        answer = "運動前は、食べすぎずにエネルギーになる物がおすすめです。おにぎり半分〜1個、バナナ、ヨーグルト、ゆで卵などが合わせやすいです。"
    elif any(k in q for k in ["運動後", "トレーニング後", "ヨガ後", "ピラティス後"]):
        answer = "運動後は、たんぱく質と炭水化物を少し入れると整えやすいです。例：味噌汁＋ごはん少し＋卵、サラダチキン＋おにぎりなど。"
    elif any(k in q for k in ["朝", "あさ", "朝ごはん", "朝食"]):
        answer = "朝は、たんぱく質＋炭水化物を少し入れるのがおすすめです。納豆ごはん、ゆで卵とトースト、ヨーグルトとバナナなどが組みやすいです。"
    elif any(k in q for k in ["昼", "ひる", "昼ごはん", "昼食", "ランチ"]):
        answer = "昼は、主食を抜きすぎず、たんぱく質を入れると午後に崩れにくいです。おにぎり＋味噌汁＋サラダチキンのような組み合わせが安定します。"
    elif any(k in q for k in ["夜", "よる", "夕飯", "夕食"]):
        answer = "夜は、脂っこい物を重ねすぎず、主菜＋汁物＋野菜を意識すると整えやすいです。ごはんは食べすぎない量で十分です。"
    elif any(k in q for k in ["食べすぎ", "食べ過ぎ", "食べてしま", "食べた後", "食べ過ぎた"]):
        answer = "食べすぎた日は、次の食事で極端に抜かず、汁物・たんぱく質・野菜で整えるのが安全です。翌日に軽く戻す意識で十分です。"
    elif any(k in q for k in ["甘い", "おやつ", "間食", "スイーツ"]):
        answer = "間食するなら、量を決めて早めの時間に。ヨーグルト、ナッツ少量, チーズ、ゆで卵などに置き換えると整えやすいです。"
    elif any(k in q for k in ["家族", "子ども", "夫", "みんな"]):
        answer = "家族向けなら、主菜をしっかり作って、自分は汁物や野菜を先に入れると調整しやすいです。取り分け前に自分の量を決めると崩れにくいです。"
    elif any(k in q for k in ["時短", "簡単", "すぐ", "忙しい"]):
        answer = "忙しい日は、丼もの＋汁物、鮭＋ごはん＋即席味噌汁、豆腐＋卵＋ごはんなどの時短型が続けやすいです。"
    else:
        answer = "食事は、主食を極端に抜かず、たんぱく質を毎食少し入れると安定しやすいです。迷ったら『汁物＋たんぱく質＋主食少し＋野菜』で考えると組みやすいです。"

    return f"相談内容：{question}\n\n{base}\n\n{style}\n\n{answer}"


def build_exercise_answer(question: str, settings: dict) -> str:
    q = normalize_question(question)
    level = settings["activity_level"]
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["5分", "5ぷん", "短時間", "忙しい", "時間がない"]):
        answer = "今日は5分で十分です。肩回し1分、前もも伸ばし1分、股関節まわし1分、軽いスクワット1分、深呼吸1分でOKです。"
    elif any(k in q for k in ["朝", "あさ"]):
        answer = "朝は、背伸び・肩回し・股関節ほぐしなど、起こす系の動きがおすすめです。"
    elif any(k in q for k in ["夜", "よる"]):
        answer = "夜は、がんばる運動より、ストレッチ・呼吸・やさしいヨガの方が整いやすいです。"
    elif any(k in q for k in ["歩く", "ウォーキング", "散歩"]):
        answer = "歩く日は、10〜20分でも十分です。少し腕を振って歩くと体が温まりやすいです。"
    elif any(k in q for k in ["筋トレ", "筋肉", "引き締め", "二の腕", "お腹", "脚"]):
        answer = "引き締め目的なら、スクワット・壁腕立て・ヒップリフト・膝つきプランクなど、自宅でできる基本種目を少しずつ続けるのがおすすめです。"
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

    return f"相談内容：{question}\n\n{base}\n\n{level_text}\n\n{answer}"


def build_condition_answer(question: str, settings: dict) -> str:
    q = normalize_question(question)
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["むくみ", "だるい", "重い"]):
        answer = "むくみやだるさがある日は、冷たい物を重ねすぎず、水分をこまめに取り、足首を回したり軽く歩いたりすると整えやすいです。"
    elif any(k in q for k in ["疲れ", "つかれ", "しんどい"]):
        answer = "疲れが強い日は、無理に頑張る日ではなく回復優先でOKです。食事は抜かず、汁物・たんぱく質・炭水化物を少し入れてください。"
    elif any(k in q for k in ["便秘", "お腹", "はら"]):
        answer = "お腹の調子が気になる日は、水分、温かい汁物、発酵食品、歩行や体をねじる軽い動きが合いやすいです。"
    elif any(k in q for k in ["眠い", "寝不足", "睡眠"]):
        answer = "寝不足の日は、激しい運動より、日中に軽く体を動かして夜に整える方がおすすめです。カフェインや甘い物のとりすぎに注意してください。"
    elif any(k in q for k in ["頭痛", "頭が痛い"]):
        answer = "頭痛がある日は、無理な運動は避けて、水分・休息・刺激を減らす方向で整えるのがおすすめです。つらい時は医療機関を優先してください。"
    else:
        answer = "体調が揺れている日は、食事を極端に減らさず、温かい物と軽い運動で整える考え方がおすすめです。"

    return f"相談内容：{question}\n\n{base}\n\n{answer}"


def build_eating_out_answer(question: str, settings: dict) -> str:
    q = normalize_question(question)
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["焼肉", "肉"]):
        answer = "焼肉なら、最初にサラダやスープを入れて、ごはんは食べすぎない量に。脂の多い肉ばかり重ねず、赤身や鶏も混ぜると整えやすいです。"
    elif any(k in q for k in ["パスタ", "イタリアン"]):
        answer = "パスタなら、クリーム系が続く日は避けて、サラダやスープを一緒に。取り分けできるなら量調整しやすいです。"
    elif any(k in q for k in ["ラーメン"]):
        answer = "ラーメンは、スープを全部飲まない、餃子やチャーハンを重ねすぎない、次の食事で野菜と汁物を意識、の3つで調整しやすいです。"
    elif any(k in q for k in ["寿司"]):
        answer = "寿司は比較的選びやすいです。揚げ物や甘い物を重ねすぎず、汁物を足すと整えやすいです。"
    elif any(k in q for k in ["居酒屋", "飲み会", "会食"]):
        answer = "居酒屋や会食では、最初にサラダ・枝豆・冷奴などを入れて、揚げ物と締めを重ねすぎないのが整えやすいです。"
    elif any(k in q for k in ["食べすぎ", "外食後"]):
        answer = "外食後は、翌日に極端に抜かず、朝か昼で汁物・たんぱく質・野菜を意識してください。軽く歩く程度で十分です。"
    else:
        answer = "外食は『主菜を決める → 汁物かサラダを足す → 主食を食べすぎない』で考えると整えやすいです。"

    return f"相談内容：{question}\n\n{base}\n\n{answer}"


def generate_answer(category: str, question: str, settings: dict) -> str:
    question = question.strip()

    if not question:
        return "相談内容を入力してください。短くても大丈夫です。"

    if category == "食事":
        return build_food_answer(question, settings)
    if category == "運動":
        return build_exercise_answer(question, settings)
    if category == "体調":
        return build_condition_answer(question, settings)
    if category == "外食調整":
        return build_eating_out_answer(question, settings)

    return f"相談内容：{question}\n\nカテゴリを選んで相談してください。"
