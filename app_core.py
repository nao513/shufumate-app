import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime
from uuid import uuid4

# =========================
# 定数
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
# ユーザーID
# =========================
def get_user_id() -> str:
    if "user_id" in st.session_state:
        return st.session_state["user_id"]

    uid = st.query_params.get("uid", "")
    if isinstance(uid, list):
        uid = uid[0] if uid else ""

    uid = str(uid).strip()

    if not uid:
        uid = uuid4().hex
        st.query_params["uid"] = uid

    st.session_state["user_id"] = uid
    return uid


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


def get_settings_sheet():
    return get_or_create_sheet("Settings", SETTINGS_HEADERS, rows=200)


def get_dietlogs_sheet():
    return get_or_create_sheet("DietLogs", DIETLOG_HEADERS, rows=1000)


# =========================
# Settings保存・読込
# =========================
def find_user_row(ws, user_id: str):
    values = ws.get_all_values()
    if len(values) <= 1:
        return None

    for row_idx, row in enumerate(values[1:], start=2):
        if len(row) > 0 and row[0] == user_id:
            return row_idx
    return None


def load_user_settings(user_id: str) -> dict:
    ws = get_settings_sheet()
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
    ws = get_settings_sheet()
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
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ]
    ws.append_row(row_data)


def load_latest_log(user_id: str) -> dict | None:
    ws = get_dietlogs_sheet()
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
    ws = get_dietlogs_sheet()
    records = ws.get_all_records()
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


def build_food_answer(question: str, settings: dict) -> str:
    q = question.lower()
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["朝", "あさ", "morning"]):
        answer = "朝は、たんぱく質＋炭水化物を少し入れるのがおすすめです。例：納豆ごはん、ゆで卵とトースト、ヨーグルトとバナナ。"
    elif any(k in q for k in ["昼", "ひる", "lunch"]):
        answer = "昼は、主食を抜きすぎず、たんぱく質を入れると午後に崩れにくいです。例：おにぎり＋味噌汁＋サラダチキン。"
    elif any(k in q for k in ["夜", "よる", "夕飯", "夕食", "dinner"]):
        answer = "夜は、脂っこい物を重ねすぎず、主菜＋汁物＋野菜を意識すると整えやすいです。"
    elif any(k in q for k in ["食べすぎ", "食べ過ぎ", "食べてしま", "食べた後"]):
        answer = "食べすぎた日は、次の食事で極端に抜かず、汁物・たんぱく質・野菜で整えるのが安全です。翌日に軽く戻す意識で十分です。"
    elif any(k in q for k in ["甘い", "おやつ", "間食", "スイーツ"]):
        answer = "間食するなら、量を決めて早めの時間に。ヨーグルト、ナッツ少量、チーズ、ゆで卵などに置き換えると整えやすいです。"
    else:
        answer = "食事は、主食を極端に抜かず、たんぱく質を毎食少し入れると安定しやすいです。迷ったら『汁物＋たんぱく質＋主食少し＋野菜』で考えると組みやすいです。"

    style = f"食事スタイルは「{settings['food_style']}」で考えます。"
    return f"{base}\n\n{style}\n\n{answer}"


def build_exercise_answer(question: str, settings: dict) -> str:
    q = question.lower()
    level = settings["activity_level"]
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["5分", "短時間", "忙しい", "時間がない"]):
        answer = "今日は5分で十分です。肩回し1分、前もも伸ばし1分、股関節まわし1分、軽いスクワット1分、深呼吸1分でOKです。"
    elif any(k in q for k in ["朝", "あさ"]):
        answer = "朝は、背伸び・肩回し・股関節ほぐしなど、起こす系の動きがおすすめです。"
    elif any(k in q for k in ["夜", "よる"]):
        answer = "夜は、がんばる運動より、ストレッチ・呼吸・やさしいヨガの方が整いやすいです。"
    elif any(k in q for k in ["歩く", "ウォーキング", "散歩"]):
        answer = "歩く日は、10〜20分でも十分です。少し腕を振って歩くと体が温まりやすいです。"
    elif any(k in q for k in ["筋トレ", "筋肉", "引き締め"]):
        answer = "引き締め目的なら、スクワット・壁腕立て・ヒップリフトなど、自宅でできる基本種目を少しずつ続けるのがおすすめです。"
    else:
        answer = "迷った日は『ストレッチ→軽い全身運動→深呼吸』の順で短く動くと続けやすいです。"

    if level == "低い":
        level_text = "活動量は低め設定なので、今日は無理せず軽めで十分です。"
    elif level == "高い":
        level_text = "活動量は高め設定なので、余裕があれば少し負荷を上げても大丈夫です。"
    else:
        level_text = "活動量はふつう設定なので、軽め〜中くらいで整えるのがおすすめです。"

    return f"{base}\n\n{level_text}\n\n{answer}"


def build_condition_answer(question: str, settings: dict) -> str:
    q = question.lower()
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["むくみ", "だるい", "重い"]):
        answer = "むくみやだるさがある日は、冷たい物を重ねすぎず、水分をこまめに取り、足首を回したり軽く歩いたりすると整えやすいです。"
    elif any(k in q for k in ["疲れ", "つかれ", "しんどい"]):
        answer = "疲れが強い日は、無理に頑張る日ではなく回復優先でOKです。食事は抜かず、汁物・たんぱく質・炭水化物を少し入れてください。"
    elif any(k in q for k in ["便秘", "お腹", "はら"]):
        answer = "お腹の調子が気になる日は、水分、温かい汁物、発酵食品、歩行や体をねじる軽い動きが合いやすいです。"
    elif any(k in q for k in ["眠い", "寝不足", "睡眠"]):
        answer = "寝不足の日は、激しい運動より、日中に軽く体を動かして夜に整える方がおすすめです。カフェインや甘い物のとりすぎに注意してください。"
    else:
        answer = "体調が揺れている日は、食事を極端に減らさず、温かい物と軽い運動で整える考え方がおすすめです。"

    return f"{base}\n\n{answer}"


def build_eating_out_answer(question: str, settings: dict) -> str:
    q = question.lower()
    base = get_user_type_advice(settings["user_type"])

    if any(k in q for k in ["焼肉", "肉"]):
        answer = "焼肉なら、最初にサラダやスープを入れて、ごはんは食べすぎない量に。脂の多い肉ばかり重ねず、赤身や鶏も混ぜると整えやすいです。"
    elif any(k in q for k in ["パスタ", "イタリアン"]):
        answer = "パスタなら、クリーム系が続く日は避けて、サラダやスープを一緒に。取り分けできるなら量調整しやすいです。"
    elif any(k in q for k in ["ラーメン"]):
        answer = "ラーメンは、スープを全部飲まない、餃子やチャーハンを重ねすぎない、次の食事で野菜と汁物を意識、の3つで調整しやすいです。"
    elif any(k in q for k in ["寿司"]):
        answer = "寿司は比較的選びやすいです。揚げ物や甘い物を重ねすぎず、汁物を足すと整えやすいです。"
    elif any(k in q for k in ["食べすぎ", "会食", "外食後"]):
        answer = "外食後は、翌日に極端に抜かず、朝か昼で汁物・たんぱく質・野菜を意識してください。軽く歩く程度で十分です。"
    else:
        answer = "外食は『主菜を決める → 汁物かサラダを足す → 主食を食べすぎない』で考えると整えやすいです。"

    return f"{base}\n\n{answer}"


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

    return "カテゴリを選んで相談してください。"


# =========================
# UI
# =========================
def inject_home_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 760px;
        }
        .sm-card {
            background: #ffffff;
            border: 1px solid #e9e9e9;
            border-radius: 18px;
            padding: 18px 16px;
            margin-bottom: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        .sm-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }
        .sm-sub {
            color: #666666;
            font-size: 0.92rem;
            margin-bottom: 0.3rem;
        }
        .sm-menu-row {
            padding: 8px 0;
            border-bottom: 1px dashed #eeeeee;
        }
        .sm-menu-row:last-child {
            border-bottom: none;
        }
        .sm-day {
            font-weight: 700;
            display: inline-block;
            width: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_today_advice_card(advice: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🌿 今日のおすすめ</div>
            <div class="sm-sub"><b>食事</b></div>
            <div>{advice["食事"]}</div>
            <br>
            <div class="sm-sub"><b>運動</b></div>
            <div>{advice["運動"]}</div>
            <br>
            <div class="sm-sub"><b>ひとこと</b></div>
            <div>{advice["ひとこと"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_week_menu_card(menu_list: list[dict]):
    today_idx = datetime.now().weekday()
    rows = []
    for idx, item in enumerate(menu_list):
        mark = " ← 今日" if idx == today_idx else ""
        rows.append(
            f'<div class="sm-menu-row"><span class="sm-day">{item["day"]}</span> {item["menu"]}{mark}</div>'
        )

    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🍽 今週の献立</div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exercise_card(exercise: dict):
    st.markdown(
        f"""
        <div class="sm-card">
            <div class="sm-title">🏃 今日の運動</div>
            <div class="sm-sub"><b>{exercise["title"]}</b></div>
            <div>{exercise["body"]}</div>
            <br>
            <div>{exercise["level_text"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    latest_weight = None
    latest_body_fat = None

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
