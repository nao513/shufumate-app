import streamlit as st
from app_core import (
    require_login,
    CATEGORY_OPTIONS,
    get_user_id,
    load_user_settings,
    generate_answer,
)

require_login()

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

CATEGORY_OPTIONS = [
    "食事",
    "運動",
    "体調",
    "外食調整",
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
# 画面
# =========================
st.title("💬 相談する")
st.caption("食事・運動・体調・外食の相談に答えます")

user_id = get_user_id()

try:
    settings = load_user_settings(user_id)
except Exception as e:
    st.error(f"設定の読込に失敗しました: {e}")
    st.stop()

nickname = settings["nickname"].strip()
if nickname:
    st.info(f"{nickname}さん向けに、現在の設定をもとに提案します。")
else:
    st.info("現在の設定をもとに提案します。")

category = st.radio(
    "相談カテゴリ",
    CATEGORY_OPTIONS,
    horizontal=True,
)

example_text = {
    "食事": "例：運動前に何を食べたらいい？ 今日は夜何を食べるのがおすすめ？",
    "運動": "例：今日は疲れてるけど何をしたらいい？ 5分だけ動くなら？",
    "体調": "例：むくみが気になる。だるい日はどうしたらいい？",
    "外食調整": "例：今日パスタ外食です。どう選べばいい？ 焼肉のときの調整は？",
}[category]

question = st.text_area(
    "相談内容",
    placeholder=example_text,
    height=140,
)

if st.button("相談する", use_container_width=True):
    answer = generate_answer(category, question, settings)
    st.session_state["last_answer"] = answer

if "last_answer" in st.session_state:
    st.subheader("回答")
    st.write(st.session_state["last_answer"])

st.divider()
st.subheader("いまの設定")
st.write(f"利用タイプ：{settings['user_type']}")
st.write(f"活動量：{settings['activity_level']}")
st.write(f"食事スタイル：{settings['food_style']}")

st.caption("※ この相談機能はフェーズ1の簡易版です。医療判断が必要な内容は医療機関に相談してください。")
