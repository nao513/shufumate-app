import streamlit as st
import pandas as pd
import uuid

from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials


# =========================
# 日本時間
# =========================
JST = ZoneInfo("Asia/Tokyo")


def jst_now():
    return datetime.now(JST)


def jst_today():
    return datetime.now(JST)


def jst_today_str():
    return datetime.now(JST).strftime("%Y-%m-%d")


# =========================
# Google Sheets接続
# =========================
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

    sheet = spreadsheet.worksheet(sheet_name)

    return sheet


# =========================
# ログイン（現在は簡易版）
# =========================
def require_login():

    # すでにログイン済み
    if "user_id" in st.session_state:
        return

    # 簡易的に保持しているIDがある場合
    if "user_id_cookie" in st.session_state:

        st.session_state["user_id"] = (
            st.session_state["user_id_cookie"]
        )

        return

    # 初回アクセス時
    new_id = str(uuid.uuid4())[:8]

    st.session_state["user_id"] = new_id
    st.session_state["user_id_cookie"] = new_id


# =========================
# ログイン中ユーザーID取得
# =========================
def get_user_id():

    return st.session_state.get(
        "user_id",
        None
    )


# =========================
# 記録保存
# =========================
def save_diet_log(user_id, log_data):

    sheet = get_sheet("DietLogs")

    row = [
        user_id,
        log_data.get("log_date", jst_today_str()),
        log_data.get("weight", ""),
        log_data.get("body_fat", ""),
        log_data.get("muscle_mass", ""),
        log_data.get("meal_memo", ""),
    ]

    sheet.append_row(
        row,
        value_input_option="USER_ENTERED"
    )


# =========================
# 記録取得
# =========================
def load_diet_logs(user_id):

    if not user_id:
        return []

    sheet = get_sheet("DietLogs")

    data = sheet.get_all_records()

    logs = []

    for row in data:

        row_user_id = str(
            row.get("user_id", "")
        ).strip()

        if row_user_id == str(user_id).strip():
            logs.append(row)

    return logs


# =========================
# グラフ用データ
# =========================
def load_log_chart_df(user_id=None):

    if user_id is None:
        user_id = get_user_id()

    logs = load_diet_logs(user_id)

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)

    # -------------------------
    # 日付
    # -------------------------
    if "log_date" not in df.columns:
        return pd.DataFrame()

    df["log_date"] = pd.to_datetime(
        df["log_date"],
        errors="coerce"
    )

    # -------------------------
    # 数値変換
    # -------------------------
    numeric_columns = [
        "weight",
        "body_fat",
        "muscle_mass",
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # -------------------------
    # 不正日付削除
    # -------------------------
    df = df.dropna(
        subset=["log_date"]
    )

    # -------------------------
    # 日付順
    # -------------------------
    df = df.sort_values(
        "log_date"
    )

    return df


# =========================
# 最新記録取得
# =========================
def get_latest_diet_log(user_id=None):

    if user_id is None:
        user_id = get_user_id()

    df = load_log_chart_df(user_id)

    if df.empty:
        return None

    latest = df.iloc[-1]

    return latest.to_dict()


# =========================
# 食事評価用ワード
# =========================
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


# =========================
# ワードカウント
# =========================
def count_words(text, words):

    if not text:
        return 0

    return sum(
        1
        for word in words
        if word in text
    )


# =========================
# 食事評価
# =========================
def build_food_evaluation_from_text(
    meal_type,
    meal_text
):

    if not meal_text:
        return "内容が入力されていません"

    score = 75

    protein = count_words(
        meal_text,
        PROTEIN
    )

    veg = count_words(
        meal_text,
        VEGETABLE
    )

    carb = count_words(
        meal_text,
        CARB
    )

    heavy = count_words(
        meal_text,
        HEAVY
    )

    # -------------------------
    # 点数調整
    # -------------------------
    if protein:
        score += 8

    if veg:
        score += 8

    if carb:
        score += 4

    if heavy:
        score -= 5

    # 最大100点
    score = min(
        score,
        100
    )

    # -------------------------
    # 評価文
    # -------------------------
    result = (
        f"{meal_type}としては "
        f"{score}点くらいです。\n\n"
    )

    result += "良いところ\n"

    if protein:
        result += (
            "・たんぱく質が取れています\n"
        )

    if veg:
        result += (
            "・野菜や海藻・きのこ類が入っています\n"
        )

    if carb:
        result += (
            "・エネルギー源になる炭水化物も取れています\n"
        )

    if not protein and not veg and not carb:
        result += (
            "・食事内容をもう少し入力すると評価しやすくなります\n"
        )

    result += "\n改善ポイント\n"

    if not protein:
        result += (
            "・卵、魚、鶏肉、豆腐などの"
            "たんぱく質を追加すると良いです\n"
        )

    if not veg:
        result += (
            "・野菜、きのこ、海藻を少し足すと良いです\n"
        )

    if heavy:
        result += (
            "・少し重めの内容なので、"
            "野菜や汁物を組み合わせると整いやすいです\n"
        )

    if protein and veg and carb and not heavy:
        result += (
            "・全体のバランスはかなり良いです\n"
        )

    return result


# =========================
# 食事時間判定
# =========================
def detect_meal_type_by_time(now=None):

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

    
