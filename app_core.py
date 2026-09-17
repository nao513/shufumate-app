import streamlit as st
import pandas as pd

import hashlib
import secrets
import hmac
import base64
import html
import textwrap

from datetime import datetime, date
from zoneinfo import ZoneInfo
from pathlib import Path
from PIL import Image

import gspread
from google.oauth2.service_account import Credentials


# =========================================================
# 基本
# =========================================================
JST = ZoneInfo("Asia/Tokyo")

APP_ROOT = Path(__file__).resolve().parent
ICON_DIR = APP_ROOT / "assets" / "icons"
WATERCOLOR_ICON_DIR = ICON_DIR / "ShufuMate_home_icons_8"


# =========================================================
# 日本時間
# =========================================================
def jst_now():
    return datetime.now(JST)


def jst_today():
    return datetime.now(JST)


def jst_today_str():
    return datetime.now(JST).strftime("%Y-%m-%d")


def jst_datetime_str():
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# Google Sheets
# =========================================================
def get_spreadsheet():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )

    client = gspread.authorize(creds)

    return client.open_by_key(
        st.secrets["SPREADSHEET_ID"]
    )


def get_sheet(sheet_name):

    return get_spreadsheet().worksheet(
        sheet_name
    )


# =========================================================
# 共通文字処理
# =========================================================
def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


def safe_text(value):

    return html.escape(
        clean_text(value)
    )


def safe_html_with_br(value):

    return (
        html.escape(clean_text(value))
        .replace("\n", "<br>")
    )


# =========================================================
# パスワード
# =========================================================
def make_password_hash(password, salt=None):

    password = clean_text(password)

    if not password:
        return "", ""

    if not salt:
        salt = secrets.token_hex(16)

    salt = clean_text(salt)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()

    return password_hash, salt


def verify_password(
    password,
    stored_hash,
    stored_salt,
):

    password = clean_text(password)
    stored_hash = clean_text(stored_hash)
    stored_salt = clean_text(stored_salt)

    if not password:
        return False

    if not stored_hash:
        return False

    if not stored_salt:
        return False

    calculated_hash, _ = make_password_hash(
        password,
        stored_salt,
    )

    return hmac.compare_digest(
        calculated_hash.lower(),
        stored_hash.lower(),
    )


# =========================================================
# Users
# =========================================================
def load_users():

    sheet = get_sheet("Users")

    values = sheet.get_all_values()

    if not values:
        return []

    headers = [
        clean_text(v)
        for v in values[0]
    ]

    users = []

    for row in values[1:]:

        row = row + [""] * (
            len(headers) - len(row)
        )

        record = {}

        for i, header in enumerate(headers):

            if header:

                record[header] = clean_text(
                    row[i]
                )

        users.append(record)

    return users


def find_user_by_login_id(login_id):

    login_id = clean_text(login_id)

    if not login_id:
        return None

    for user in load_users():

        if clean_text(
            user.get("login_id")
        ) == login_id:

            return user

    return None


def find_user_by_user_id(user_id):

    user_id = clean_text(user_id)

    if not user_id:
        return None

    for user in load_users():

        if clean_text(
            user.get("user_id")
        ) == user_id:

            return user

    return None


def is_active_user(user_record):

    if not user_record:
        return False

    value = clean_text(
        user_record.get(
            "is_active",
            "TRUE",
        )
    ).lower()

    return value not in [
        "false",
        "0",
        "no",
        "off",
        "無効",
    ]


# =========================================================
# ログイン状態
# =========================================================
def is_logged_in():

    return bool(
        st.session_state.get(
            "logged_in",
            False,
        )
        and
        st.session_state.get(
            "user_id"
        )
    )


def get_user_id():

    if not is_logged_in():
        return None

    return st.session_state.get(
        "user_id"
    )


def get_login_id():

    if not is_logged_in():
        return None

    return st.session_state.get(
        "login_id"
    )


def get_nickname():

    if not is_logged_in():
        return None

    return st.session_state.get(
        "nickname"
    )


def login_user(user_record):

    if not user_record:
        return False

    if not is_active_user(user_record):
        return False

    user_id = clean_text(
        user_record.get("user_id")
    )

    if not user_id:
        return False

    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user_id
    st.session_state["login_id"] = clean_text(
        user_record.get("login_id")
    )
    st.session_state["nickname"] = clean_text(
        user_record.get("nickname")
    )

    return True


def login(login_id, password):

    login_id = clean_text(login_id)
    password = clean_text(password)

    if not login_id or not password:
        return False

    user = find_user_by_login_id(
        login_id
    )

    if not user:
        return False

    if not is_active_user(user):
        return False

    if not verify_password(
        password,
        user.get("password_hash"),
        user.get("password_salt"),
    ):
        return False

    return login_user(user)


def logout():

    for key in [
        "logged_in",
        "user_id",
        "login_id",
        "nickname",
    ]:

        st.session_state.pop(
            key,
            None,
        )


def require_login():

    if is_logged_in():
        return

    st.warning(
        "このページを利用するにはログインが必要です。"
    )

    if st.button(
        "ログイン画面へ",
        key="require_login_button",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/0_ログイン.py"
        )

    st.stop()


# =========================================================
# 新規ユーザー
# =========================================================
def create_user_id(login_id):

    base = clean_text(login_id)

    if not base:
        base = "user"

    existing = {
        clean_text(
            user.get("user_id")
        )
        for user in load_users()
    }

    if base not in existing:
        return base

    while True:

        candidate = (
            f"{base}_{secrets.token_hex(3)}"
        )

        if candidate not in existing:
            return candidate


def create_user(
    login_id,
    password,
    nickname="",
    birth_date=None,
):

    login_id = clean_text(login_id)
    password = clean_text(password)
    nickname = clean_text(nickname)

    if not login_id:
        return None

    if len(password) < 4:
        return None

    if find_user_by_login_id(login_id):
        return None

    user_id = create_user_id(
        login_id
    )

    password_hash, password_salt = (
        make_password_hash(password)
    )

    if isinstance(
        birth_date,
        (date, datetime),
    ):

        birth_text = birth_date.strftime(
            "%Y-%m-%d"
        )

    else:

        birth_text = clean_text(
            birth_date
        )

    now = jst_datetime_str()

    row = [
        user_id,
        login_id,
        password_hash,
        password_salt,
        nickname,
        birth_text,
        now,
        now,
        "TRUE",
    ]

    get_sheet("Users").append_row(
        row,
        value_input_option="RAW",
    )

    return {
        "user_id": user_id,
        "login_id": login_id,
        "password_hash": password_hash,
        "password_salt": password_salt,
        "nickname": nickname,
        "birth_date": birth_text,
        "created_at": now,
        "updated_at": now,
        "is_active": "TRUE",
    }


# =========================================================
# パスワード再設定
# =========================================================
def reset_password(
    login_id,
    new_password,
):

    login_id = clean_text(login_id)
    new_password = clean_text(new_password)

    if not login_id:
        return False

    if len(new_password) < 4:
        return False

    sheet = get_sheet("Users")

    values = sheet.get_all_values()

    if not values:
        return False

    headers = [
        clean_text(v)
        for v in values[0]
    ]

    required = [
        "login_id",
        "password_hash",
        "password_salt",
        "updated_at",
    ]

    if any(
        col not in headers
        for col in required
    ):
        return False

    login_col = (
        headers.index("login_id") + 1
    )

    hash_col = (
        headers.index("password_hash") + 1
    )

    salt_col = (
        headers.index("password_salt") + 1
    )

    updated_col = (
        headers.index("updated_at") + 1
    )

    target_row = None

    for row_no in range(
        2,
        len(values) + 1,
    ):

        row = values[
            row_no - 1
        ]

        current = ""

        if len(row) >= login_col:

            current = clean_text(
                row[login_col - 1]
            )

        if current == login_id:

            target_row = row_no
            break

    if target_row is None:
        return False

    new_hash, new_salt = (
        make_password_hash(
            new_password
        )
    )

    sheet.update_cell(
        target_row,
        hash_col,
        new_hash,
    )

    sheet.update_cell(
        target_row,
        salt_col,
        new_salt,
    )

    sheet.update_cell(
        target_row,
        updated_col,
        jst_datetime_str(),
    )

    return True


# =========================================================
# DietLogs
#
# A user_id
# B log_date
# C weight
# D body_fat
# E muscle_mass
# F meal_memo
# =========================================================
DIET_LOG_HEADERS = [
    "user_id",
    "log_date",
    "weight",
    "body_fat",
    "muscle_mass",
    "meal_memo",
]


def save_diet_log(
    user_id,
    log_data,
):

    user_id = clean_text(user_id)

    if not user_id:
        return False

    row = [
        user_id,
        clean_text(
            log_data.get(
                "log_date",
                jst_today_str(),
            )
        ),
        log_data.get(
            "weight",
            "",
        ),
        log_data.get(
            "body_fat",
            "",
        ),
        log_data.get(
            "muscle_mass",
            "",
        ),
        clean_text(
            log_data.get(
                "meal_memo",
                "",
            )
        ),
    ]

    get_sheet(
        "DietLogs"
    ).append_row(
        row,
        value_input_option="USER_ENTERED",
    )

    return True


def load_diet_logs(user_id=None):

    if user_id is None:
        user_id = get_user_id()

    user_id = clean_text(user_id)

    if not user_id:
        return []

    sheet = get_sheet(
        "DietLogs"
    )

    # get_all_values を使用して
    # 列位置を確実に保持
    values = sheet.get_all_values()

    if not values:
        return []

    headers = [
        clean_text(v)
        for v in values[0]
    ]

    logs = []

    for row in values[1:]:

        row = row + [""] * (
            len(headers) - len(row)
        )

        record = {}

        for i, header in enumerate(
            headers
        ):

            if header:

                record[header] = (
                    row[i]
                    if i < len(row)
                    else ""
                )

        # ---------------------------------------------
        # 標準ヘッダーがない古いシートにも対応
        # ---------------------------------------------
        if "user_id" not in record and len(row) >= 1:
            record["user_id"] = row[0]

        if "log_date" not in record and len(row) >= 2:
            record["log_date"] = row[1]

        if "weight" not in record and len(row) >= 3:
            record["weight"] = row[2]

        if "body_fat" not in record and len(row) >= 4:
            record["body_fat"] = row[3]

        if "muscle_mass" not in record and len(row) >= 5:
            record["muscle_mass"] = row[4]

        if "meal_memo" not in record and len(row) >= 6:
            record["meal_memo"] = row[5]

        if clean_text(
            record.get("user_id")
        ) != user_id:

            continue

        logs.append(
            {
                "user_id":
                    clean_text(
                        record.get("user_id")
                    ),

                "log_date":
                    clean_text(
                        record.get("log_date")
                    ),

                "weight":
                    clean_text(
                        record.get("weight")
                    ),

                "body_fat":
                    clean_text(
                        record.get("body_fat")
                    ),

                "muscle_mass":
                    clean_text(
                        record.get("muscle_mass")
                    ),

                "meal_memo":
                    clean_text(
                        record.get("meal_memo")
                    ),
            }
        )

    return logs


# =========================================================
# DietLogs DataFrame
# Home・記録ページ共通
# =========================================================
def load_diet_dataframe(user_id=None):

    logs = load_diet_logs(
        user_id
    )

    if not logs:
        return pd.DataFrame(
            columns=DIET_LOG_HEADERS
        )

    df = pd.DataFrame(
        logs
    )

    if "log_date" in df.columns:

        df["log_date"] = pd.to_datetime(
            df["log_date"],
            errors="coerce",
        )

    for column in [
        "weight",
        "body_fat",
        "muscle_mass",
    ]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            df.loc[
                df[column] <= 0,
                column
            ] = pd.NA

    df = df.dropna(
        subset=["log_date"]
    )

    df = (
        df
        .sort_values("log_date")
        .reset_index(drop=True)
    )

    return df


def latest_valid_value(
    df,
    column,
):

    if (
        df is None
        or df.empty
        or "log_date" not in df.columns
        or column not in df.columns
    ):
        return None, None

    temp = df[
        ["log_date", column]
    ].copy()

    temp[column] = pd.to_numeric(
        temp[column],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[
            "log_date",
            column,
        ]
    )

    temp = temp[
        temp[column] > 0
    ]

    if temp.empty:
        return None, None

    temp = temp.sort_values(
        "log_date"
    )

    row = temp.iloc[-1]

    return (
        float(row[column]),
        row["log_date"],
    )


def previous_valid_difference(
    df,
    column,
):

    if (
        df is None
        or df.empty
        or "log_date" not in df.columns
        or column not in df.columns
    ):
        return None

    temp = df[
        ["log_date", column]
    ].copy()

    temp[column] = pd.to_numeric(
        temp[column],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[
            "log_date",
            column,
        ]
    )

    temp = temp[
        temp[column] > 0
    ]

    temp = temp.sort_values(
        "log_date"
    )

    if len(temp) < 2:
        return None

    return (
        float(temp.iloc[-1][column])
        -
        float(temp.iloc[-2][column])
    )


def load_latest_log(user_id=None):

    df = load_diet_dataframe(
        user_id
    )

    if df.empty:
        return None

    row = df.iloc[-1]

    return {
        "user_id":
            clean_text(
                row.get("user_id")
            ),

        "log_date":
            (
                row["log_date"].strftime(
                    "%Y-%m-%d"
                )
                if pd.notna(
                    row.get("log_date")
                )
                else ""
            ),

        "weight":
            row.get("weight"),

        "body_fat":
            row.get("body_fat"),

        "muscle_mass":
            row.get("muscle_mass"),

        "meal_memo":
            clean_text(
                row.get("meal_memo")
            ),
    }


# 旧ページ互換
load_user_logs = load_diet_logs
save_user_log = save_diet_log
save_log = save_diet_log
load_record_logs = load_diet_logs
save_record_log = save_diet_log
load_daily_logs = load_diet_logs
save_daily_log = save_diet_log
load_today_logs = load_diet_logs
save_today_log = save_diet_log
load_user_records = load_diet_logs
save_user_record = save_diet_log


# =========================================================
# UserSettings
# =========================================================
USER_SETTINGS_HEADERS = [
    "user_id",
    "nickname",
    "birth_date",
    "height",

    "current_weight",
    "target_weight",

    "current_body_fat",
    "target_body_fat",

    "current_muscle_mass",
    "target_muscle_mass",

    "user_type",
    "activity_level",
    "food_style",
    "constitution_traits",
    "advice_tone",
    "workout_today",
    "fridge_items",
    "avoid_foods",
    "favorite_meals",
    "updated_at",
]

# =========================================================
# UserSettings シート取得・不足列自動追加
# =========================================================
def get_or_create_user_settings_sheet():

    spreadsheet = get_spreadsheet()

    try:
        sheet = spreadsheet.worksheet(
            "UserSettings"
        )

    except gspread.WorksheetNotFound:

        sheet = spreadsheet.add_worksheet(
            title="UserSettings",
            rows=1000,
            cols=max(
                30,
                len(USER_SETTINGS_HEADERS),
            ),
        )

        sheet.append_row(
            USER_SETTINGS_HEADERS,
            value_input_option="RAW",
        )

        return sheet

    values = sheet.get_all_values()

    # -----------------------------------------
    # 完全に空のシート
    # -----------------------------------------
    if not values:

        sheet.append_row(
            USER_SETTINGS_HEADERS,
            value_input_option="RAW",
        )

        return sheet

    # -----------------------------------------
    # 現在のヘッダー
    # -----------------------------------------
    current_headers = [
        clean_text(value)
        for value in values[0]
    ]

    # -----------------------------------------
    # 不足列を右側へ追加
    # -----------------------------------------
    missing_headers = [
        header
        for header in USER_SETTINGS_HEADERS
        if header not in current_headers
    ]

    if missing_headers:

        start_col = (
            len(current_headers) + 1
        )

        end_col = (
            start_col
            + len(missing_headers)
            - 1
        )

        def column_letter(number):

            result = ""

            while number:

                number, remainder = divmod(
                    number - 1,
                    26,
                )

                result = (
                    chr(65 + remainder)
                    + result
                )

            return result

        start_letter = column_letter(
            start_col
        )

        end_letter = column_letter(
            end_col
        )

        sheet.update(
            range_name=(
                f"{start_letter}1:"
                f"{end_letter}1"
            ),
            values=[
                missing_headers
            ],
            value_input_option="RAW",
        )

    return sheet


# =========================================================
# UserSettings 読み込み
# =========================================================
def load_user_settings(
    user_id=None,
):

    if user_id is None:
        user_id = get_user_id()

    user_id = clean_text(
        user_id
    )

    if not user_id:
        return {}

    sheet = (
        get_or_create_user_settings_sheet()
    )

    values = sheet.get_all_values()

    if len(values) <= 1:
        return {}

    headers = [
        clean_text(value)
        for value in values[0]
    ]

    if "user_id" not in headers:
        return {}

    user_id_index = headers.index(
        "user_id"
    )

    for row in values[1:]:

        row = row + [""] * max(
            0,
            len(headers) - len(row),
        )

        if clean_text(
            row[user_id_index]
        ) != user_id:

            continue

        settings = {}

        for index, header in enumerate(
            headers
        ):

            if not header:
                continue

            value = (
                row[index]
                if index < len(row)
                else ""
            )

            # constitution_traits は
            # multiselect用にlistへ戻す
            if header == "constitution_traits":

                text = clean_text(
                    value
                )

                if text:

                    text = text.replace(
                        ",",
                        "、",
                    )

                    settings[header] = [
                        item.strip()
                        for item in text.split(
                            "、"
                        )
                        if item.strip()
                    ]

                else:

                    settings[header] = []

            else:

                settings[header] = (
                    clean_text(value)
                )

        return settings

    return {}


# =========================================================
# UserSettings 保存
# =========================================================
def save_user_settings(
    user_id,
    settings_data,
):

    user_id = clean_text(
        user_id
    )

    if not user_id:
        return False

    if settings_data is None:
        settings_data = {}

    sheet = (
        get_or_create_user_settings_sheet()
    )

    values = sheet.get_all_values()

    if not values:

        sheet.append_row(
            USER_SETTINGS_HEADERS,
            value_input_option="RAW",
        )

        values = sheet.get_all_values()

    headers = [
        clean_text(value)
        for value in values[0]
    ]

    # -----------------------------------------
    # 念のため不足列を再確認
    # -----------------------------------------
    for header in USER_SETTINGS_HEADERS:

        if header not in headers:

            headers.append(
                header
            )

            sheet.update_cell(
                1,
                len(headers),
                header,
            )

    # -----------------------------------------
    # 既存設定を読み込む
    # -----------------------------------------
    existing = load_user_settings(
        user_id
    )

    merged = {}

    if existing:
        merged.update(
            existing
        )

    merged.update(
        settings_data
    )

    merged["user_id"] = user_id
    merged["updated_at"] = (
        jst_datetime_str()
    )

    # -----------------------------------------
    # リストをSheets保存用文字列へ
    # -----------------------------------------
    row_values = []

    for header in headers:

        value = merged.get(
            header,
            "",
        )

        if isinstance(
            value,
            (list, tuple, set),
        ):

            value = "、".join(
                clean_text(item)
                for item in value
                if clean_text(item)
            )

        elif isinstance(
            value,
            datetime,
        ):

            value = value.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        elif isinstance(
            value,
            date,
        ):

            value = value.strftime(
                "%Y-%m-%d"
            )

        row_values.append(
            value
        )

    # -----------------------------------------
    # 同じuser_idの行を探す
    # -----------------------------------------
    user_id_col = (
        headers.index("user_id")
    )

    target_row = None

    current_values = (
        sheet.get_all_values()
    )

    for row_number, row in enumerate(
        current_values[1:],
        start=2,
    ):

        current_user_id = ""

        if len(row) > user_id_col:

            current_user_id = clean_text(
                row[user_id_col]
            )

        if current_user_id == user_id:

            target_row = row_number
            break

    # -----------------------------------------
    # 新規 or 更新
    # -----------------------------------------
    if target_row is None:

        sheet.append_row(
            row_values,
            value_input_option="USER_ENTERED",
        )

    else:

        def column_letter(number):

            result = ""

            while number:

                number, remainder = divmod(
                    number - 1,
                    26,
                )

                result = (
                    chr(65 + remainder)
                    + result
                )

            return result

        end_column = column_letter(
            len(headers)
        )

        sheet.update(
            range_name=(
                f"A{target_row}:"
                f"{end_column}{target_row}"
            ),
            values=[
                row_values
            ],
            value_input_option="USER_ENTERED",
        )

    # -----------------------------------------
    # nicknameは現在セッションにも反映
    # -----------------------------------------
    if (
        user_id == get_user_id()
        and "nickname" in settings_data
    ):

        st.session_state[
            "nickname"
        ] = clean_text(
            settings_data.get(
                "nickname"
            )
        )

    return True


# =========================================================
# UserSettings 互換名
# =========================================================
load_settings = load_user_settings
save_settings = save_user_settings
load_profile_settings = load_user_settings
save_profile_settings = save_user_settings
# =========================================================
# 写真記録
# =========================================================
def detect_meal_type_by_time(now=None):

    if now is None:
        now = jst_now()

    hour = now.hour

    if 4 <= hour < 10:
        return "朝"

    if 10 <= hour < 15:
        return "昼"

    if 15 <= hour < 18:
        return "間食"

    return "夜"


def _photo_logs_key(user_id=None):

    user_id = (
        user_id
        or get_user_id()
        or "guest"
    )

    return f"photo_logs_{user_id}"


def save_photo_meal_log(
    user_id=None,
    meal_type="",
    food_text="",
    image_file=None,
):

    user_id = (
        user_id
        or get_user_id()
        or "guest"
    )

    key = _photo_logs_key(
        user_id
    )

    if key not in st.session_state:

        st.session_state[key] = []

    image_name = ""

    if image_file is not None:

        image_name = clean_text(
            getattr(
                image_file,
                "name",
                "",
            )
        )

    record = {
        "user_id":
            user_id,

        "log_date":
            jst_today_str(),

        "created_at":
            jst_datetime_str(),

        "meal_type":
            clean_text(
                meal_type
            ),

        "food_text":
            clean_text(
                food_text
            ),

        "image_name":
            image_name,
    }

    st.session_state[
        key
    ].append(
        record
    )

    return True


def load_photo_logs(
    user_id=None
):

    user_id = (
        user_id
        or get_user_id()
        or "guest"
    )

    return st.session_state.get(
        _photo_logs_key(user_id),
        [],
    )


# =========================================================
# 食事判定
# =========================================================
PROTEIN_KEYWORDS = [
    "鶏",
    "豚",
    "牛",
    "魚",
    "鮭",
    "サバ",
    "さば",
    "ツナ",
    "卵",
    "たまご",
    "納豆",
    "豆腐",
    "豆乳",
    "ヨーグルト",
    "チーズ",
]


VEGETABLE_KEYWORDS = [
    "野菜",
    "サラダ",
    "人参",
    "にんじん",
    "キャベツ",
    "レタス",
    "トマト",
    "ほうれん草",
    "小松菜",
    "青菜",
    "きのこ",
    "しめじ",
    "わかめ",
    "海藻",
]


CARB_KEYWORDS = [
    "ご飯",
    "ごはん",
    "米",
    "おにぎり",
    "パン",
    "うどん",
    "そば",
    "麺",
    "パスタ",
    "芋",
]


def contains_keyword(
    text,
    keywords,
):

    text = clean_text(text)

    return any(
        keyword in text
        for keyword in keywords
    )


def evaluate_meal_text(text):

    text = clean_text(text)

    if not text:
        return {
            "score": 0,
            "protein": False,
            "vegetable": False,
            "carb": False,
        }

    protein = contains_keyword(
        text,
        PROTEIN_KEYWORDS,
    )

    vegetable = contains_keyword(
        text,
        VEGETABLE_KEYWORDS,
    )

    carb = contains_keyword(
        text,
        CARB_KEYWORDS,
    )

    score = (
        int(protein)
        + int(vegetable)
        + int(carb)
    )

    return {
        "score": score,
        "protein": protein,
        "vegetable": vegetable,
        "carb": carb,
    }


# =========================================================
# アイコン
# =========================================================
def resolve_icon_path(filename):

    if not filename:
        return None

    filename = str(filename)

    candidates = [
        ICON_DIR / filename,
        WATERCOLOR_ICON_DIR / filename,
    ]

    for path in candidates:

        if path.exists():
            return path

    return None


def get_page_icon(
    filename,
    fallback="🌿",
):

    path = resolve_icon_path(
        filename
    )

    if path is None:
        return fallback

    try:

        return Image.open(path)

    except Exception:

        return fallback


def file_to_base64(path):

    if not path:
        return None

    path = Path(path)

    if not path.exists():
        return None

    suffix = path.suffix.lower()

    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(
        suffix,
        "image/png",
    )

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return (
        f"data:{mime};base64,{encoded}"
    )


def load_icon(filename):

    path = resolve_icon_path(
        filename
    )

    if path is None:
        return None

    return file_to_base64(
        path
    )


# =========================================================
# 共通CSS
# =========================================================
def inject_shufumate_css():

    st.markdown(
        textwrap.dedent(
            """
            <style>

            .stApp {
                background:
                    linear-gradient(
                        180deg,
                        #fffaf4 0%,
                        #fff4e8 48%,
                        #fffaf4 100%
                    );
            }

            .block-container {
                max-width: 820px;
                padding-top: 2.4rem !important;
                padding-bottom: 3rem;
            }

            .sm-top-card {
                background: rgba(255,255,255,.94);
                border-radius: 25px;
                padding: 22px;
                border: 1px solid rgba(139,100,72,.12);
                box-shadow:
                    0 7px 20px
                    rgba(96,65,45,.08);
                margin-bottom: 18px;
            }

            .sm-page-head {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .sm-page-head-icon {
                width: 70px;
                min-width: 70px;
                height: 70px;
                border-radius: 20px;
                background: #fff8ef;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }

            .sm-page-head-icon img {
                width: 58px;
                height: 58px;
                object-fit: contain;
            }

            .sm-page-emoji {
                font-size: 2rem;
            }

            .sm-page-title {
                color: #5c4033;
                font-size: 1.7rem;
                font-weight: 900;
            }

            .sm-page-subtitle {
                color: #7b6658;
                font-size: .92rem;
                line-height: 1.7;
                margin-top: 4px;
            }

            .sm-section-head {
                display: flex;
                align-items: center;
                gap: 11px;
                margin: 26px 0 13px;
            }

            .sm-section-icon {
                width: 52px;
                min-width: 52px;
                height: 52px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .sm-section-icon img {
                width: 48px;
                height: 48px;
                object-fit: contain;
            }

            .sm-section-emoji {
                font-size: 1.6rem;
            }

            .sm-section-title {
                color: #5c4033;
                font-size: 1.22rem;
                font-weight: 900;
            }

            .sm-note-card,
            .sm-card,
            .sm-focus-card,
            .sm-answer-card {
                border-radius: 19px;
                padding: 15px 17px;
                line-height: 1.75;
                margin: 10px 0 16px;
            }

            .sm-note-card {
                background: #fff8ef;
                color: #765b4b;
                border: 1px solid rgba(139,100,72,.10);
            }

            .sm-card {
                background: rgba(255,255,255,.92);
                color: #5c4033;
                border: 1px solid rgba(139,100,72,.10);
            }

            .sm-focus-card {
                background: #f4f8ef;
                color: #50644c;
                border: 1px solid rgba(92,130,83,.16);
            }

            .sm-answer-card {
                background: #fffdf9;
                color: #5c4033;
                border: 1px solid rgba(139,100,72,.12);
            }

            .sm-divider {
                height: 1px;
                background: #eadfce;
                margin: 2rem 0;
            }

            .stButton > button,
            .stFormSubmitButton > button {
                background: #8d6e63;
                color: #ffffff;
                border: none;
                border-radius: 14px;
                min-height: 45px;
                font-weight: 800;
            }

            .stButton > button:hover,
            .stFormSubmitButton > button:hover {
                background: #76594f;
                color: #ffffff;
                border: none;
            }

            div[data-testid="stMetric"] {
                background: rgba(255,255,255,.92);
                border: 1px solid rgba(168,126,88,.14);
                border-radius: 18px;
                padding: 14px 16px;
            }

            @media (max-width: 640px) {

                .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                    padding-top: 1.3rem !important;
                }

                .sm-page-head-icon {
                    width: 60px;
                    min-width: 60px;
                    height: 60px;
                }

                .sm-page-head-icon img {
                    width: 49px;
                    height: 49px;
                }

                .sm-page-title {
                    font-size: 1.45rem;
                }

                .sm-section-title {
                    font-size: 1.12rem;
                }
            }

            </style>
            """
        ).strip(),
        unsafe_allow_html=True,
    )


# =========================================================
# 共通UI
# =========================================================
def render_page_header(
    title,
    subtitle="",
    icon_file=None,
    emoji="🌿",
):

    icon_src = (
        load_icon(icon_file)
        if icon_file
        else None
    )

    if icon_src:

        icon_html = (
            f'<img src="{icon_src}" '
            f'alt="{safe_text(title)}">'
        )

    else:

        icon_html = (
            '<div class="sm-page-emoji">'
            f'{safe_text(emoji)}'
            '</div>'
        )

    markup = f"""
    <div class="sm-top-card">
        <div class="sm-page-head">
            <div class="sm-page-head-icon">
                {icon_html}
            </div>
            <div>
                <div class="sm-page-title">
                    {safe_text(title)}
                </div>
                <div class="sm-page-subtitle">
                    {safe_html_with_br(subtitle)}
                </div>
            </div>
        </div>
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_section_header(
    title,
    icon_file=None,
    emoji="🌿",
):

    icon_src = (
        load_icon(icon_file)
        if icon_file
        else None
    )

    if icon_src:

        icon_html = (
            f'<img src="{icon_src}" '
            f'alt="{safe_text(title)}">'
        )

    else:

        icon_html = (
            '<div class="sm-section-emoji">'
            f'{safe_text(emoji)}'
            '</div>'
        )

    markup = f"""
    <div class="sm-section-head">
        <div class="sm-section-icon">
            {icon_html}
        </div>
        <div class="sm-section-title">
            {safe_text(title)}
        </div>
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_note(text):

    markup = f"""
    <div class="sm-note-card">
        {safe_html_with_br(text)}
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_card(text):

    markup = f"""
    <div class="sm-card">
        {safe_html_with_br(text)}
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_focus_card(text):

    markup = f"""
    <div class="sm-focus-card">
        {safe_html_with_br(text)}
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_answer_card(text):

    markup = f"""
    <div class="sm-answer-card">
        {safe_html_with_br(text)}
    </div>
    """

    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def render_divider():

    st.markdown(
        '<div class="sm-divider"></div>',
        unsafe_allow_html=True,
    )
