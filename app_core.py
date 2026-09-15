import streamlit as st
import pandas as pd
import hashlib
import secrets
import hmac

from datetime import datetime, date
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials


# =========================================================
# 基本設定
# =========================================================
JST = ZoneInfo("Asia/Tokyo")


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
    return datetime.now(JST).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =========================================================
# Google Sheets 接続
# =========================================================
def get_sheet(sheet_name):

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        st.secrets["SPREADSHEET_ID"]
    )

    return spreadsheet.worksheet(
        sheet_name
    )


# =========================================================
# 共通：文字列化
# =========================================================
def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# パスワードをハッシュ化
# =========================================================
def make_password_hash(
    password,
    salt=None,
):

    password = clean_text(
        password
    )

    if not password:
        return "", ""

    if not salt:
        salt = secrets.token_hex(16)

    salt = clean_text(
        salt
    )

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()

    return password_hash, salt


# =========================================================
# パスワード確認
# =========================================================
def verify_password(
    password,
    stored_hash,
    stored_salt,
):

    password = clean_text(
        password
    )

    stored_hash = clean_text(
        stored_hash
    )

    stored_salt = clean_text(
        stored_salt
    )

    if not password:
        return False

    if not stored_hash:
        return False

    if not stored_salt:
        return False

    calculated_hash, _ = (
        make_password_hash(
            password=password,
            salt=stored_salt,
        )
    )

    return hmac.compare_digest(
        calculated_hash.lower(),
        stored_hash.lower(),
    )


# =========================================================
# Usersシート取得
#
# ID・salt・hashなどが数字として
# 自動変換されないよう、
# get_all_values() で文字列のまま取得
# =========================================================
def load_users():

    sheet = get_sheet(
        "Users"
    )

    values = sheet.get_all_values()

    if not values:
        return []

    headers = [
        clean_text(value)
        for value in values[0]
    ]

    users = []

    for row in values[1:]:

        row = row + [""] * (
            len(headers) - len(row)
        )

        record = {}

        for index, header in enumerate(
            headers
        ):

            if not header:
                continue

            record[header] = clean_text(
                row[index]
            )

        users.append(
            record
        )

    return users


# =========================================================
# login_idでユーザー検索
# =========================================================
def find_user_by_login_id(
    login_id
):

    login_id = clean_text(
        login_id
    )

    if not login_id:
        return None

    users = load_users()

    for user in users:

        saved_login_id = clean_text(
            user.get(
                "login_id"
            )
        )

        if saved_login_id == login_id:
            return user

    return None


# =========================================================
# user_idでユーザー検索
# =========================================================
def find_user_by_user_id(
    user_id
):

    user_id = clean_text(
        user_id
    )

    if not user_id:
        return None

    users = load_users()

    for user in users:

        saved_user_id = clean_text(
            user.get(
                "user_id"
            )
        )

        if saved_user_id == user_id:
            return user

    return None


# =========================================================
# 有効ユーザー判定
# =========================================================
def is_active_user(
    user_record
):

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


# =========================================================
# ログイン状態を保存
# =========================================================
def login_user(
    user_record
):

    if not user_record:
        return False

    if not is_active_user(
        user_record
    ):
        return False

    user_id = clean_text(
        user_record.get(
            "user_id"
        )
    )

    login_id = clean_text(
        user_record.get(
            "login_id"
        )
    )

    nickname = clean_text(
        user_record.get(
            "nickname"
        )
    )

    if not user_id:
        return False

    st.session_state[
        "logged_in"
    ] = True

    st.session_state[
        "user_id"
    ] = user_id

    st.session_state[
        "login_id"
    ] = login_id

    st.session_state[
        "nickname"
    ] = nickname

    return True


# =========================================================
# ログイン
# =========================================================
def login(
    login_id,
    password,
):

    login_id = clean_text(
        login_id
    )

    password = clean_text(
        password
    )

    if not login_id:
        return False

    if not password:
        return False

    user_record = (
        find_user_by_login_id(
            login_id
        )
    )

    if not user_record:
        return False

    if not is_active_user(
        user_record
    ):
        return False

    stored_hash = clean_text(
        user_record.get(
            "password_hash"
        )
    )

    stored_salt = clean_text(
        user_record.get(
            "password_salt"
        )
    )

    if not verify_password(
        password,
        stored_hash,
        stored_salt,
    ):
        return False

    return login_user(
        user_record
    )


# =========================================================
# ログアウト
# =========================================================
def logout():

    keys = [
        "logged_in",
        "user_id",
        "login_id",
        "nickname",
    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]


# =========================================================
# ログイン必須ページ
# =========================================================
def require_login():

    if is_logged_in():
        return

    st.warning(
        "このページを利用するには"
        "ログインが必要です。"
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
# user_id生成
# =========================================================
def create_user_id(
    login_id
):

    base = clean_text(
        login_id
    )

    if not base:
        base = "user"

    users = load_users()

    existing_ids = {
        clean_text(
            user.get(
                "user_id"
            )
        )
        for user in users
    }

    if base not in existing_ids:
        return base

    while True:

        suffix = secrets.token_hex(3)

        candidate = (
            f"{base}_{suffix}"
        )

        if candidate not in existing_ids:
            return candidate


# =========================================================
# 新規登録
# =========================================================
def create_user(
    login_id,
    password,
    nickname="",
    birth_date=None,
):

    login_id = clean_text(
        login_id
    )

    password = clean_text(
        password
    )

    nickname = clean_text(
        nickname
    )

    if not login_id:
        return None

    if not password:
        return None

    if len(password) < 4:
        return None

    # -------------------------
    # login_id 重複確認
    # -------------------------
    if find_user_by_login_id(
        login_id
    ):
        return None

    # -------------------------
    # user_id
    # -------------------------
    user_id = create_user_id(
        login_id
    )

    # -------------------------
    # パスワード
    # -------------------------
    password_hash, password_salt = (
        make_password_hash(
            password
        )
    )

    # -------------------------
    # 生年月日
    # -------------------------
    if isinstance(
        birth_date,
        (date, datetime),
    ):

        birth_date_text = (
            birth_date.strftime(
                "%Y-%m-%d"
            )
        )

    else:

        birth_date_text = clean_text(
            birth_date
        )

    now_text = (
        jst_datetime_str()
    )

    # -------------------------
    # Usersシート
    # -------------------------
    sheet = get_sheet(
        "Users"
    )

    row = [
        user_id,
        login_id,
        password_hash,
        password_salt,
        nickname,
        birth_date_text,
        now_text,
        now_text,
        "TRUE",
    ]

    # 文字列を崩さないようRAW保存
    sheet.append_row(
        row,
        value_input_option="RAW",
    )

    return {
        "user_id": user_id,
        "login_id": login_id,
        "password_hash": password_hash,
        "password_salt": password_salt,
        "nickname": nickname,
        "birth_date": birth_date_text,
        "created_at": now_text,
        "updated_at": now_text,
        "is_active": "TRUE",
    }


# =========================================================
# パスワード変更
# =========================================================
def reset_password(
    login_id,
    new_password,
):

    login_id = clean_text(
        login_id
    )

    new_password = clean_text(
        new_password
    )

    if not login_id:
        return False

    if len(new_password) < 4:
        return False

    sheet = get_sheet(
        "Users"
    )

    values = (
        sheet.get_all_values()
    )

    if not values:
        return False

    headers = [
        clean_text(value)
        for value in values[0]
    ]

    required_columns = [
        "login_id",
        "password_hash",
        "password_salt",
        "updated_at",
    ]

    for column in required_columns:

        if column not in headers:
            return False

    login_col = (
        headers.index(
            "login_id"
        ) + 1
    )

    hash_col = (
        headers.index(
            "password_hash"
        ) + 1
    )

    salt_col = (
        headers.index(
            "password_salt"
        ) + 1
    )

    updated_col = (
        headers.index(
            "updated_at"
        ) + 1
    )

    target_row = None

    for row_number in range(
        2,
        len(values) + 1,
    ):

        row = values[
            row_number - 1
        ]

        current_login = ""

        if len(row) >= login_col:

            current_login = (
                clean_text(
                    row[
                        login_col - 1
                    ]
                )
            )

        if current_login == login_id:

            target_row = row_number
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
# DietLogs 保存
# =========================================================
def save_diet_log(
    user_id,
    log_data,
):

    user_id = clean_text(
        user_id
    )

    if not user_id:
        return False

    sheet = get_sheet(
        "DietLogs"
    )

    row = [
        user_id,

        log_data.get(
            "log_date",
            jst_today_str(),
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

        log_data.get(
            "meal_memo",
            "",
        ),
    ]

    sheet.append_row(
        row,
        value_input_option="USER_ENTERED",
    )

    return True


# =========================================================
# DietLogs 取得
# =========================================================
def load_diet_logs(
    user_id=None
):

    if user_id is None:
        user_id = get_user_id()

    user_id = clean_text(
        user_id
    )

    if not user_id:
        return []

    sheet = get_sheet(
        "DietLogs"
    )

    data = sheet.get_all_records(
        default_blank=""
    )

    logs = []

    for row in data:

        row_user_id = clean_text(
            row.get(
                "user_id"
            )
        )

        if row_user_id == user_id:
            logs.append(row)

    return logs


# =========================================================
# グラフ用データ
# =========================================================
def load_log_chart_df(
    user_id=None
):

    if user_id is None:
        user_id = get_user_id()

    logs = load_diet_logs(
        user_id
    )

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(
        logs
    )

    if "log_date" not in df.columns:
        return pd.DataFrame()

    df["log_date"] = pd.to_datetime(
        df["log_date"],
        errors="coerce",
    )

    numeric_columns = [
        "weight",
        "body_fat",
        "muscle_mass",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    df = df.dropna(
        subset=[
            "log_date"
        ]
    )

    df = df.sort_values(
        "log_date"
    )

    return df


# =========================================================
# 最新記録
# =========================================================
def get_latest_diet_log(
    user_id=None
):

    df = load_log_chart_df(
        user_id
    )

    if df.empty:
        return None

    return (
        df.iloc[-1]
        .to_dict()
    )


# =========================================================
# 食事評価用ワード
# =========================================================
PROTEIN = [
    "卵",
    "たまご",
    "鶏",
    "鶏肉",
    "鶏むね",
    "魚",
    "鮭",
    "サバ",
    "まぐろ",
    "ツナ",
    "納豆",
    "豆腐",
    "ヨーグルト",
    "豆乳",
    "豚",
    "豚肉",
    "牛肉",
]


VEGETABLE = [
    "野菜",
    "サラダ",
    "きのこ",
    "しめじ",
    "えのき",
    "海藻",
    "わかめ",
    "ほうれん草",
    "小松菜",
    "キャベツ",
    "レタス",
    "トマト",
    "人参",
]


CARB = [
    "ごはん",
    "ご飯",
    "米",
    "パン",
    "麺",
    "うどん",
    "そば",
    "パスタ",
    "おにぎり",
]


HEAVY = [
    "揚げ物",
    "唐揚げ",
    "フライ",
    "ラーメン",
    "丼",
    "カレー",
]


# =========================================================
# 食事ワードカウント
# =========================================================
def count_words(
    text,
    words,
):

    text = clean_text(
        text
    )

    if not text:
        return 0

    return sum(
        1
        for word in words
        if word in text
    )


# =========================================================
# 食事評価
# =========================================================
def build_food_evaluation_from_text(
    meal_type,
    meal_text,
):

    meal_text = clean_text(
        meal_text
    )

    if not meal_text:
        return (
            "内容が入力されていません"
        )

    score = 75

    protein = count_words(
        meal_text,
        PROTEIN,
    )

    vegetable = count_words(
        meal_text,
        VEGETABLE,
    )

    carb = count_words(
        meal_text,
        CARB,
    )

    heavy = count_words(
        meal_text,
        HEAVY,
    )

    if protein:
        score += 8

    if vegetable:
        score += 8

    if carb:
        score += 4

    if heavy:
        score -= 5

    score = max(
        0,
        min(
            score,
            100,
        ),
    )

    result = (
        f"{meal_type}としては "
        f"{score}点くらいです。\n\n"
    )

    result += "良いところ\n"

    if protein:

        result += (
            "・たんぱく質が"
            "取れています\n"
        )

    if vegetable:

        result += (
            "・野菜や海藻・"
            "きのこ類が入っています\n"
        )

    if carb:

        result += (
            "・エネルギー源になる"
            "炭水化物も取れています\n"
        )

    if (
        not protein
        and not vegetable
        and not carb
    ):

        result += (
            "・食事内容をもう少し入力すると"
            "評価しやすくなります\n"
        )

    result += (
        "\n改善ポイント\n"
    )

    if not protein:

        result += (
            "・卵、魚、鶏肉、豆腐などの"
            "たんぱく質を追加すると良いです\n"
        )

    if not vegetable:

        result += (
            "・野菜、きのこ、海藻を"
            "少し足すと良いです\n"
        )

    if heavy:

        result += (
            "・少し重めの内容なので、"
            "野菜や汁物を組み合わせると"
            "整いやすいです\n"
        )

    if (
        protein
        and vegetable
        and carb
        and not heavy
    ):

        result += (
            "・全体のバランスは"
            "かなり良いです\n"
        )

    return result


# =========================================================
# 食事時間判定
# =========================================================
def detect_meal_type_by_time(
    now=None
):

    if now is None:
        now = jst_now()

    hour = now.hour

    if 4 <= hour < 10:
        return "朝"

    elif 10 <= hour < 15:
        return "昼"

    elif 15 <= hour < 21:
        return "夜"

    else:
        return "間食"
