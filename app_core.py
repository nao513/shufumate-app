import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# =========================
# Google Sheets接続
# =========================
def get_sheet(sheet_name):
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["SPREADSHEET_ID"]).worksheet(sheet_name)
    return sheet


# =========================
# ログイン（簡易版）
# =========================
import uuid
import streamlit as st

def require_login():
    if "user_id" not in st.session_state:

        # Cookie的な保持（簡易版）
        if "user_id_cookie" in st.session_state:
            st.session_state["user_id"] = st.session_state["user_id_cookie"]

        else:
            new_id = str(uuid.uuid4())[:8]

            st.session_state["user_id"] = new_id
            st.session_state["user_id_cookie"] = new_id

# =========================
# 記録保存
# =========================
def save_diet_log(user_id, log_data):
    sheet = get_sheet("DietLogs")

    row = [
        log_data.get("user_id"),
        log_data.get("log_date"),
        log_data.get("weight"),
        log_data.get("body_fat"),
        log_data.get("muscle_mass"),
        log_data.get("meal_memo"),
    ]

    sheet.append_row(row)


# =========================
# 記録取得
# =========================
def load_diet_logs(user_id):
    sheet = get_sheet("DietLogs")
    data = sheet.get_all_records()

    logs = []
    for row in data:
        if row.get("user_id") == user_id:
            logs.append(row)

    return logs


# =========================
# グラフ用データ
# =========================
def load_log_chart_df(user_id=None):
    user_id = user_id or get_user_id()

    logs = load_diet_logs(user_id)

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)

    # 日付
    df["log_date"] = pd.to_datetime(df["log_date"], errors="coerce")

    # 数値
    for col in ["weight", "body_fat", "muscle_mass"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["log_date"])
    df = df.sort_values("log_date")

    return df


# =========================
# 日付
# =========================
def jst_today():
    return datetime.now()


def jst_today_str():
    return datetime.now().strftime("%Y-%m-%d")


# =========================
# 食事評価ロジック
# =========================
PROTEIN = ["卵", "鶏", "魚", "納豆", "豆腐", "ヨーグルト"]
VEGETABLE = ["野菜", "サラダ", "きのこ", "海藻"]
CARB = ["ごはん", "パン", "麺", "おにぎり"]
HEAVY = ["揚げ物", "ラーメン", "丼", "カレー"]


def count_words(text, words):
    return sum([1 for w in words if w in text])


def build_food_evaluation_from_text(meal_type, meal_text):
    if not meal_text:
        return "内容が入力されていません"

    score = 75

    protein = count_words(meal_text, PROTEIN)
    veg = count_words(meal_text, VEGETABLE)
    carb = count_words(meal_text, CARB)
    heavy = count_words(meal_text, HEAVY)

    if protein:
        score += 5
    if veg:
        score += 5
    if heavy:
        score -= 5

    result = f"{meal_type}としては {score}点くらいです。\n\n"

    result += "良いところ\n"
    if protein:
        result += "・たんぱく質が取れています\n"
    if veg:
        result += "・野菜が入っています\n"

    result += "\n改善ポイント\n"
    if not protein:
        result += "・たんぱく質を追加すると良いです\n"
    if not veg:
        result += "・野菜を少し足すと良いです\n"
    if heavy:
        result += "・少し重い内容です\n"

    return result

# =========================
# 食事時間判定
# =========================
def jst_now():
    return datetime.now()


def detect_meal_type_by_time(now):
    hour = now.hour

    if 4 <= hour < 10:
        return "朝"
    elif 10 <= hour < 15:
        return "昼"
    elif 15 <= hour < 21:
        return "夜"
    else:
        return "間食"
