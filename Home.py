import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered",
)

# =========================
# 基本設定
# =========================
DEFAULT_USER_ID = "default_user"

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

WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]


# =========================
# 共通関数
# =========================
def get_user_id() -> str:
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = DEFAULT_USER_ID
    return st.session_state["user_id"]


def to_str(v) -> str:
    return "" if v is None else str(v)


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


def get_or_create_settings_sheet():
    ss = get_spreadsheet()
    try:
        ws = ss.worksheet("Settings")
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title="Settings", rows=100, cols=len(SETTINGS_HEADERS))
        ws.append_row(SETTINGS_HEADERS)

    ensure_headers(ws, SETTINGS_HEADERS)
    return ws


def load_user_settings(user_id: str) -> dict:
    ws = get_or_create_settings_sheet()
    records = ws.get_all_records()

    for record in records:
        if str(record.get("user_id", "")) == user_id:
            return {
                "nickname": to_str(record.get("nickname", "")),
                "activity_level": to_str(record.get("activity_level", "ふつう")) or "ふつう",
                "food_style": to_str(record.get("food_style", "バランス重視")) or "バランス重視",
                "user_type": to_str(record.get("user_type", "自分だけ向け")) or "自分だけ向け",
            }

    return {
        "nickname": "",
        "activity_level": "ふつう",
        "food_style": "バランス重視",
        "user_type": "自分だけ向け",
    }


# =========================
# 提案ロジック
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
# UI
# =========================
def inject_css():
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
    today_idx = datetime.now().weekday()  # 月=0
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
# 画面
# =========================
inject_css()

user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

nickname = settings["nickname"].strip()
today_text = datetime.now().strftime("%Y年%m月%d日")
weekday_text = WEEKDAY_JP[datetime.now().weekday()]

st.title("🏠 ホーム")
st.caption(f"{today_text}（{weekday_text}）")

if nickname:
    st.subheader(f"{nickname}さん、今日のおすすめです")
else:
    st.subheader("今日のおすすめです")

advice = get_today_advice(settings)
week_menu = get_week_menu(settings)
exercise = get_today_exercise(settings)

render_today_advice_card(advice)
render_week_menu_card(week_menu)
render_exercise_card(exercise)

st.markdown("### つかう")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 記録する", use_container_width=True):
        st.switch_page("pages/2_記録する.py")

with col2:
    if st.button("💬 相談する", use_container_width=True):
        st.switch_page("pages/3_相談する.py")

with col3:
    if st.button("⚙️ 設定", use_container_width=True):
        st.switch_page("pages/1_設定.py")

st.divider()
st.write(f"利用タイプ：{settings['user_type']}")
st.write(f"活動量：{settings['activity_level']}")
st.write(f"食事スタイル：{settings['food_style']}")
