import base64
import io
import re
from datetime import datetime, timedelta

import gspread
import pandas as pd
import streamlit as st
from openai import OpenAI
from PIL import Image
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

USER_ID = "nao513"

# -----------------------------
# Google Sheets
# -----------------------------
@st.cache_resource
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


@st.cache_resource
def get_spreadsheet():
    gc = get_gspread_client()
    return gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])


def get_sheet(tab_name: str):
    sh = get_spreadsheet()
    return sh.worksheet(tab_name)


def get_or_create_worksheet(sh, title, rows=1000, cols=30):
    try:
        return sh.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)


def ensure_headers():
    sh = get_spreadsheet()

    settings_ws = get_or_create_worksheet(sh, "Settings")
    diet_ws = get_or_create_worksheet(sh, "DietLogs")
    plans_ws = get_or_create_worksheet(sh, "TodayPlans")

    settings_header = [
        "user_id", "age", "height_cm", "start_weight",
        "target_weight", "start_body_fat", "target_body_fat",
        "meal_style", "ease_level", "staple_preference",
        "fridge_items", "plan_type",
        "real_mode", "daily_flow", "workout_today", "body_goal"
    ]
    diet_header = [
        "user_id", "date", "age", "height_cm", "weight",
        "target_weight", "body_fat", "target_body_fat",
        "bmi", "goal_calories"
    ]
    plan_header = ["user_id", "date", "plan_text"]

    settings_values = settings_ws.get_all_values()
    diet_values = diet_ws.get_all_values()
    plan_values = plans_ws.get_all_values()

    if not settings_values or settings_values[0] != settings_header:
        settings_ws.clear()
        settings_ws.append_row(settings_header)

    if not diet_values or diet_values[0] != diet_header:
        diet_ws.clear()
        diet_ws.append_row(diet_header)

    if not plan_values or plan_values[0] != plan_header:
        plans_ws.clear()
        plans_ws.append_row(plan_header)
        

def load_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()

    if len(values) < 2:
        return None

    header = values[0]
    data_rows = values[1:]

    for row in data_rows:
        if not row:
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))

        if row_dict.get("user_id") == USER_ID:
            return {
                "common_age": int(float(row_dict["age"])),
                "common_height": float(row_dict["height_cm"]),
                "common_weight": float(row_dict["start_weight"]),
                "common_target_weight": float(row_dict["target_weight"]),
                "common_body_fat": float(row_dict["start_body_fat"]),
                "common_target_body_fat": float(row_dict["target_body_fat"]),
                "meal_style": row_dict.get("meal_style", "和食中心") or "和食中心",
                "ease_level": row_dict.get("ease_level", "超かんたん") or "超かんたん",
                "staple_preference": row_dict.get("staple_preference", "ごはん派") or "ごはん派",
                "fridge_items": row_dict.get("fridge_items", "") or "",
                "plan_type": row_dict.get("plan_type", "通常") or "通常",
                "real_mode": str(row_dict.get("real_mode", "True")).lower() == "true",
                "daily_flow": row_dict.get("daily_flow", "普通") or "普通",
                "workout_today": str(row_dict.get("workout_today", "False")).lower() == "true",
                "body_goal": row_dict.get("body_goal", "バランス") or "バランス",
            }
    return None


def save_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()

    row_values = [
        USER_ID,
        st.session_state["common_age"],
        st.session_state["common_height"],
        st.session_state["common_weight"],
        st.session_state["common_target_weight"],
        st.session_state["common_body_fat"],
        st.session_state["common_target_body_fat"],
        st.session_state["meal_style"],
        st.session_state["ease_level"],
        st.session_state["staple_preference"],
        st.session_state["fridge_items"],
        st.session_state["plan_type"],
        str(st.session_state["real_mode"]),
        st.session_state["daily_flow"],
        str(st.session_state["workout_today"]),
        st.session_state["body_goal"],
    ]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == USER_ID:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:P{row_index}", [row_values])
    else:
        ws.append_row(row_values)


def reset_user_settings():
    st.session_state["common_age"] = 40
    st.session_state["common_height"] = 160.0
    st.session_state["common_weight"] = 40.0
    st.session_state["common_target_weight"] = 45.0
    st.session_state["common_body_fat"] = 15.0
    st.session_state["common_target_body_fat"] = 22.0
    st.session_state["meal_style"] = "和食中心"
    st.session_state["ease_level"] = "超かんたん"
    st.session_state["staple_preference"] = "ごはん派"
    st.session_state["fridge_items"] = ""
    st.session_state["plan_type"] = "通常"
    st.session_state["real_mode"] = True
    st.session_state["daily_flow"] = "普通"
    st.session_state["workout_today"] = False
    st.session_state["body_goal"] = "バランス"


def load_settings_into_session():
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v


def load_diet_logs():
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()

    if len(values) < 2:
        return []

    header = values[0]
    data_rows = values[1:]
    logs = []

    for row in data_rows:
        if not row or len(row) < len(header):
            continue

        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == USER_ID:
            logs.append({
                "日付": row_dict["date"],
                "年齢": float(row_dict["age"]),
                "身長(cm)": float(row_dict["height_cm"]),
                "体重(kg)": float(row_dict["weight"]),
                "目標体重(kg)": float(row_dict["target_weight"]),
                "体脂肪率(%)": float(row_dict["body_fat"]),
                "目標体脂肪率(%)": float(row_dict["target_body_fat"]),
                "BMI": float(row_dict["bmi"]),
                "目標摂取カロリー": float(row_dict["goal_calories"]),
            })

    return logs


def upsert_diet_log(log_dict):
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()

    row_values = [
        USER_ID,
        log_dict["日付"],
        log_dict["年齢"],
        log_dict["身長(cm)"],
        log_dict["体重(kg)"],
        log_dict["目標体重(kg)"],
        log_dict["体脂肪率(%)"],
        log_dict["目標体脂肪率(%)"],
        log_dict["BMI"],
        log_dict["目標摂取カロリー"],
    ]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2 and row[0] == USER_ID and row[1] == log_dict["日付"]:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:J{row_index}", [row_values])
    else:
        ws.append_row(row_values)


def load_today_plan():
    ws = get_sheet("TodayPlans")
    values = ws.get_all_values()

    if len(values) < 2:
        return None, None

    header = values[0]
    data_rows = values[1:]

    latest_date = None
    latest_text = None

    for row in data_rows:
        if not row or len(row) < len(header):
            continue

        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == USER_ID:
            row_date = row_dict.get("date", "")
            if latest_date is None or row_date >= latest_date:
                latest_date = row_date
                latest_text = row_dict.get("plan_text", "")

    return latest_date, latest_text


def upsert_today_plan(date_str, plan_text):
    ws = get_sheet("TodayPlans")
    values = ws.get_all_values()

    row_values = [USER_ID, date_str, plan_text]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2 and row[0] == USER_ID and row[1] == date_str:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:C{row_index}", [row_values])
    else:
        ws.append_row(row_values)


# -----------------------------
# OpenAI
# -----------------------------
def get_openai_client():
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("Streamlit Secrets に OPENAI_API_KEY が設定されていません。")
        st.stop()


# -----------------------------
# Image helpers
# -----------------------------
def resize_image(file, max_size=768):
    image = Image.open(file)
    image = image.convert("RGB")

    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        image = image.resize((int(w * ratio), int(h * ratio)))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer


def image_file_to_data_url(file_like):
    b64 = base64.b64encode(file_like.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def b64_to_bytes(b64_string: str) -> bytes:
    return base64.b64decode(b64_string)


def extract_foods_from_images(client, images):
    content = [{
        "type": "input_text",
        "text": """
この画像は冷蔵庫の中です。
見える食材を日本語でできるだけ具体的に列挙してください。

ルール:
- 一般的な食材名で出す
- 重複はまとめる
- 推測しすぎない
- 最後に「食材候補:」のあとにカンマ区切りで一覧を出す
"""
    }]

    for img in images:
        content.append({
            "type": "input_image",
            "image_url": image_file_to_data_url(img)
        })

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": content}]
    )
    return response.output_text


def extract_scale_values_from_image(client, resized_image):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": """
この画像は体組成計または体重計の表示です。
見えている数値を日本語で整理してください。

ルール:
- 読み取れたものだけ書く
- 推測しすぎない
- 次の形式にできるだけ合わせる
体重: xx.x
体脂肪率: xx.x
骨格筋率: xx.x
内臓脂肪: xx.x
皮下脂肪: xx.x
基礎代謝: xxxx
BMI: xx.x
メモ: 読み取りにくい項目があれば書く
"""
                },
                {
                    "type": "input_image",
                    "image_url": image_file_to_data_url(resized_image)
                }
            ]
        }]
    )
    return response.output_text

def evaluate_meal_day_from_images(client, breakfast_img, lunch_img, dinner_img):
    content = [
        {
            "type": "input_text",
            "text": """
この3枚は、朝食・昼食・夕食の写真です。
1日の食事内容を日本語でやさしく評価してください。

ルール:
- 写真から見える範囲で判断する
- 推測しすぎない
- 主婦向けにわかりやすく
- 厳しすぎない
- 点数だけでなく、良かった点も必ず書く
- 不足栄養は現実的な範囲で書く
- 夜の調整アドバイスはすぐできる内容にする

出力形式:
■朝食の印象:
■昼食の印象:
■夕食の印象:
■総合評価: 〇点 / 100点
■良かった点:
■改善ポイント:
■不足しやすい栄養:
■おすすめの調整:
■ひとこと:
"""
        },
        {
            "type": "input_text",
            "text": "1枚目が朝食です。"
        },
        {
            "type": "input_image",
            "image_url": image_file_to_data_url(breakfast_img)
        },
        {
            "type": "input_text",
            "text": "2枚目が昼食です。"
        },
        {
            "type": "input_image",
            "image_url": image_file_to_data_url(lunch_img)
        },
        {
            "type": "input_text",
            "text": "3枚目が夕食です。"
        },
        {
            "type": "input_image",
            "image_url": image_file_to_data_url(dinner_img)
        }
    ]

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{"role": "user", "content": content}]
    )
    return response.output_text

def generate_body_balance_comment(client, resized_image, body_goal="バランス"):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"""
この画像は全身写真です。
人物の体型やバランスについて、日本語でやさしくコメントしてください。

ルール:
- 顔の識別や人物特定はしない
- 骨格診断を断定しない
- 「見え方の傾向」として説明する
- 厳しい言い方をしない
- ダイエットや運動のモチベーションが上がる表現にする
- 目的は「{body_goal}」

出力形式:
■全体バランス:
■見え方の特徴:
■今がんばると変化しやすいポイント:
■おすすめ運動:
■ひとこと:
"""
                },
                {
                    "type": "input_image",
                    "image_url": image_file_to_data_url(resized_image)
                }
            ]
        }]
    )
    return response.output_text


def generate_ideal_body_prompt(client, body_comment, body_goal="バランス"):
    prompt = f"""
以下の体型コメントをもとに、
「理想の自分イメージ」を画像生成AIに渡しやすい日本語プロンプトへ整えてください。

ルール:
- 顔ははっきり作らない
- 同一人物らしさは残すが、個人特定できる表現は避ける
- 健康的で現実的な変化にする
- 過度に細すぎる表現は禁止
- モチベーションが上がる、やさしい表現
- アラフィフ女性向け
- 目的は「{body_goal}」

出力形式:
■理想イメージ説明:
■画像生成用プロンプト:
■意識したい変化ポイント:

体型コメント:
{body_comment}
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


def extract_image_prompt_only(ideal_prompt_text: str) -> str:
    match = re.search(r"■画像生成用プロンプト[:：]\s*(.*?)(?:\n■|\Z)", ideal_prompt_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ideal_prompt_text.strip()


def generate_ideal_body_image(client, ideal_prompt_text: str, size: str = "1024x1024") -> bytes | None:
    prompt = extract_image_prompt_only(ideal_prompt_text)
    if not prompt:
        return None

    result = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size=size,
        output_format="png"
    )

    if not result.data:
        return None

    image_b64 = result.data[0].b64_json
    if not image_b64:
        return None

    return b64_to_bytes(image_b64)

# -----------------------------
# Plan generation
# -----------------------------

def diagnose_dosha_advanced(answers: dict):
    scores = {"ヴァータ": 0, "ピッタ": 0, "カパ": 0}

    score_map = {
        "体型": {
            "痩せ型で食べても太らない": "ヴァータ",
            "中肉中背で平均的": "ピッタ",
            "子供の頃から太りやすい": "カパ",
        },
        "肌": {
            "乾燥している": "ヴァータ",
            "オイリーでシミやニキビができやすい": "ピッタ",
            "色白でもっちりしてる": "カパ",
        },
        "髪": {
            "硬く乾燥している": "ヴァータ",
            "柔らかくて細い": "ピッタ",
            "黒くて多い": "カパ",
        },
        "発汗": {
            "あまりかかない": "ヴァータ",
            "汗っかき": "ピッタ",
            "普通": "カパ",
        },
        "体温": {
            "手足が冷たい": "ヴァータ",
            "体が熱い": "ピッタ",
            "全体が冷たい": "カパ",
        },
        "食欲": {
            "ムラがある・不規則": "ヴァータ",
            "食欲旺盛・食事を抜くとイライラする": "ピッタ",
            "よく眠る・居眠りが多い": "カパ",
        },
        "排便": {
            "便秘気味・硬便": "ヴァータ",
            "下痢気味・軟便": "ピッタ",
            "中程度の硬さ・時間を要する": "カパ",
        },
    }

    for category, answer in answers.items():
        dosha = score_map.get(category, {}).get(answer)
        if dosha:
            scores[dosha] += 1

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    main_dosha = sorted_scores[0][0]
    second_dosha = sorted_scores[1][0]

    if sorted_scores[0][1] - sorted_scores[1][1] <= 1:
        result_type = f"{main_dosha}・{second_dosha}混合"
    else:
        result_type = main_dosha

    return result_type, scores


def get_ayurveda_foods(dosha_type):
    foods_map = {
        "ヴァータ": ["乳製品", "牛乳", "肉", "魚", "さつまいも", "オレンジ"],
        "ピッタ": ["キャベツ", "じゃがいも", "ブロッコリー", "そば", "乳製品"],
        "カパ": ["生のたまねぎ", "ニンニク", "カリフラワー", "ブロッコリー", "キャベツ", "ごぼう"],
    }

    if "・" in dosha_type:
        types = dosha_type.split("・")
        merged = []
        for t in types:
            base_t = t.replace("混合", "")
            if base_t in foods_map:
                merged.extend(foods_map[base_t])
        return sorted(set(merged))

    return foods_map.get(dosha_type, [])


def get_ayurveda_advice_advanced(dosha_type):
    base = {
        "ヴァータ": {
            "特徴": "乾燥しやすい、冷えやすい、食欲や体調にムラが出やすいタイプ",
            "食事": "温かいもの、やわらかいもの、汁物、根菜、たんぱく質を意識すると整いやすいです。",
            "生活": "冷え対策、睡眠確保、予定を詰め込みすぎないことが大切です。",
            "運動": "やさしいヨガ、ストレッチ、ゆったり散歩がおすすめです。",
            "ダイエット": "食事を抜かず、冷たいものを控えながら整えるのが向いています。"
        },
        "ピッタ": {
            "特徴": "熱がこもりやすい、食欲旺盛、がんばりすぎやすいタイプ",
            "食事": "刺激物や辛いものを控え、野菜、やさしい味付け、少しクールダウンできる食事がおすすめです。",
            "生活": "頑張りすぎを避けて、イライラをためないことがポイントです。",
            "運動": "中程度の運動、ウォーキング、ゆったりしたピラティスがおすすめです。",
            "ダイエット": "食べすぎ防止と熱をためない食べ方が向いています。"
        },
        "カパ": {
            "特徴": "ため込みやすい、むくみやすい、眠気や重だるさが出やすいタイプ",
            "食事": "重たい食事や甘いものを控え、野菜、香味野菜、軽めのたんぱく質を意識するとよいです。",
            "生活": "朝は早めに動き出し、こまめに体を動かすと整いやすいです。",
            "運動": "汗ばむ運動、ウォーキング、有酸素運動がおすすめです。",
            "ダイエット": "ため込みを減らす食事と、少ししっかり動く習慣が向いています。"
        },
    }

    if "・" in dosha_type:
        first = dosha_type.split("・")[0]
        return base.get(first, {})
    return base.get(dosha_type, {})


def create_plan_for_date(
    client,
    date_str,
    gender,
    age,
    height_cm,
    weight,
    body_fat,
    target_weight,
    target_body_fat,
    dosha_type="",
    meal_style="和食中心",
    ease_level="超かんたん",
    staple_preference="ごはん派",
    fridge_items="",
    plan_type="通常",
    real_mode=False,
    daily_flow="普通",
    workout_today=False,
    body_goal="バランス"
):
    dosha_rule = ""
    if dosha_type == "ヴァータ":
        dosha_rule = "温かい汁物、根菜、やわらかいごはん、消化にやさしい和食を優先してください。冷たいものや生野菜は控えめにしてください。"
    elif dosha_type == "ピッタ":
        dosha_rule = "刺激物や辛いものを控え、やさしい味付けの和食、野菜、豆腐、白身魚などを優先してください。"
    elif dosha_type == "カパ":
        dosha_rule = "脂っこいものや甘いものを控え、野菜多め、高たんぱく、温かく軽めの和食を優先してください。"

    fridge_rule = ""
    if fridge_items.strip():
        fridge_rule = f"冷蔵庫にある食材をできるだけ優先して使ってください: {fridge_items}"

    plan_type_rule = ""
    if plan_type == "外食":
        plan_type_rule = """
外食を前提にしてください。
・定食屋、和食屋、カフェなど現実的なお店を想定
・ダイエット向きのメニュー選びを提案
・揚げ物を避ける、タンパク質多めなど具体的に
"""
    elif plan_type == "コンビニ":
        plan_type_rule = """
コンビニ食（セブン・ファミマ・ローソン）で完結する内容にしてください。
・サラダチキン、おにぎり、ゆで卵、味噌汁、豆腐バー、サラダなど
・組み合わせで提案
・リアルに買いやすい内容にしてください
"""

    real_mode_rule = ""
    if real_mode:
        real_mode_rule = f"""
あなたは「アラフィフ主婦の現実的な食事判断」をする専門家です。

【今日の状況】
- 食事の流れ: {daily_flow}
- 運動: {"あり" if workout_today else "なし"}
- 目的: {body_goal}

以下を必ず守ってください：
・今日の流れを評価してから献立を決める
・「今日は90点前後」「今日は調整日」など評価をつける
・冷蔵庫の食材を優先して使う
・主婦がすぐ作れるレベルにする
・メニューは多すぎない（2〜4品）
・脚やせ、むくみ対策、回復など目的を理由に入れる

【出力に必ず含める】
①いちばんおすすめ
②2番目におすすめ
③3番目におすすめ
④今日のベスト献立
⑤今日1日の最終評価
⑥ひとことで

トーンは、やさしい主婦アドバイザー風にしてください。
"""

    prompt = f"""
あなたは優秀な管理栄養士・時短料理アドバイザー・主婦向け献立アドバイザーです。

【利用者情報】
- 性別: {gender}
- 年齢: {age}歳
- 身長: {height_cm}cm
- 体重: {weight}kg
- 体脂肪率: {body_fat}%
- 目標体重: {target_weight}kg
- 目標体脂肪率: {target_body_fat}%
- アーユルヴェーダ体質: {dosha_type if dosha_type else "未設定"}
- 食事スタイル: {meal_style}
- 調理レベル: {ease_level}
- 主食の好み: {staple_preference}
- プランタイプ: {plan_type}

【重要ルール】
- 日本の一般家庭で作りやすいメニューにしてください
- スーパーで買いやすい食材だけを使ってください
- 主婦向けに、手軽・簡単・現実的な献立にしてください
- 難しい横文字料理や、おしゃれすぎるカフェ料理は避けてください
- 朝食は特に手軽にしてください
- できれば節約・時短も意識してください
- たんぱく質をしっかり取れるようにしてください
- おにぎり、味噌汁、納豆、豆腐、卵、鶏むね肉、鮭、さば等も積極的に使ってよいです
- {dosha_rule}
- {fridge_rule}
- {plan_type_rule}
- {real_mode_rule}

【食事スタイルのルール】
- 和食中心: 味噌汁、おにぎり、焼き魚、納豆、卵、豆腐、煮物などを優先
- バランス: 和食中心だが洋風も少し可
- おしゃれカフェ風: 少しおしゃれでもよいが、家庭で作りやすい範囲

【調理レベルのルール】
- 超かんたん: 10〜15分程度、工程少なめ
- 普通: 20分程度
- しっかり: 少し手間をかけてもよい

【主食の好み】
- ごはん派なら、ごはん・おにぎり中心
- パン派なら、パン・トースト中心
- どちらもなら、バランスよく

{date_str}の1日の健康的なダイエットプランを作ってください。
"""
    res = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return res.output_text


# -----------------------------
# Helpers
# -----------------------------

def render_common_body_inputs():
    age = st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    height_cm = st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    weight = st.number_input("現在の体重（kg）", min_value=30.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    target_weight = st.number_input("目標体重（kg）", min_value=30.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
    body_fat = st.number_input("体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    target_body_fat = st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")
    return age, height_cm, weight, target_weight, body_fat, target_body_fat
    
def extract_shopping_items(plan_texts):
    
    def categorize_item(item: str) -> str:
        meat_egg = ["鶏", "豚", "牛", "ひき肉", "ささみ", "むね肉", "もも肉", "ベーコン", "ハム", "卵"]
        seafood = ["鮭", "さば", "サバ", "まぐろ", "ツナ", "ぶり", "たら", "エビ", "いか", "あさり", "魚"]
        vegetables = ["キャベツ", "レタス", "白菜", "ほうれん草", "小松菜", "ブロッコリー", "トマト", "きゅうり", "にんじん", "玉ねぎ", "ねぎ", "大根", "もやし", "ピーマン", "ナス", "じゃがいも", "さつまいも"]
        mushroom_seaweed = ["しめじ", "えのき", "しいたけ", "まいたけ", "きのこ", "わかめ", "ひじき", "のり", "昆布"]
        staple = ["米", "ご飯", "玄米", "もち麦", "オートミール", "パン", "うどん", "そば", "パスタ"]
        dairy_soy = ["牛乳", "ヨーグルト", "チーズ", "豆腐", "納豆", "豆乳", "油揚げ", "厚揚げ"]

        for word in meat_egg:
            if word in item:
                return "肉・卵"
        for word in seafood:
            if word in item:
                return "魚介"
        for word in vegetables:
            if word in item:
                return "野菜"
        for word in mushroom_seaweed:
            if word in item:
                return "きのこ・海藻"
        for word in staple:
            if word in item:
                return "主食"
        for word in dairy_soy:
            if word in item:
                return "乳製品・大豆"
        return "その他"

    shopping_items = []
    for plan in plan_texts:
        lines = plan.splitlines()
        in_shopping = False
        for line in lines:
            if "■買い物リスト" in line:
                in_shopping = True
                continue
            if in_shopping:
                if line.startswith("■"):
                    break
                item = line.replace("-", "").replace("・", "").strip()
                if item:
                    shopping_items.append(item)

    unique_items = sorted(set(shopping_items))
    categorized_rows = [{"カテゴリ": categorize_item(item), "食材": item} for item in unique_items]

    if categorized_rows:
        return pd.DataFrame(categorized_rows).sort_values(["カテゴリ", "食材"])
    return pd.DataFrame(columns=["カテゴリ", "食材"])


def sync_settings_on_mode_enter(current_mode: str):
    if st.session_state.get("last_mode") != current_mode:
        if current_mode in ["ダイエット管理", "献立・運動プラン", "設定"]:
            load_settings_into_session()
        st.session_state["last_mode"] = current_mode


# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "common_age": 40,
    "common_height": 160.0,
    "common_weight": 40.0,
    "common_target_weight": 45.0,
    "common_body_fat": 15.0,
    "common_target_body_fat": 22.0,
    "meal_style": "和食中心",
    "ease_level": "超かんたん",
    "staple_preference": "ごはん派",
    "fridge_items": "",
    "plan_type": "通常",
    "real_mode": True,
    "daily_flow": "普通",
    "workout_today": False,
    "body_goal": "バランス",
    "diet_logs": [],
    "today_plan_text": "",
    "today_plan_date": "",
    "expenses": [],
    "schedules": [],
    "dosha_type": "",
    "dosha_scores": {"ヴァータ": 0, "ピッタ": 0, "カパ": 0},
    "last_mode": "",
    "photo_fridge_items": "",
    "photo_scale_result": "",
    "body_check_comment": "",
    "body_scan_comment": "",
    "body_goal_scan": "バランス",
    "ideal_body_prompt_result": "",
"ideal_body_image_bytes": None,
"fridge_scan_images": [],
"meal_eval_result": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -----------------------------
# Initial load
# -----------------------------
if "settings_loaded" not in st.session_state:
    ensure_headers()
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v

    st.session_state["diet_logs"] = load_diet_logs()
    saved_plan_date, saved_plan_text = load_today_plan()
    if saved_plan_date and saved_plan_text:
        st.session_state["today_plan_date"] = saved_plan_date
        st.session_state["today_plan_text"] = saved_plan_text

    st.session_state["settings_loaded"] = True


# -----------------------------
# UI
# -----------------------------
st.title("🍀 ShufuMate｜主婦の味方アプリ")
st.caption("ダイエット・家計・予定・教育・人生設計・お得情報を総合管理")

mode = st.sidebar.radio("機能を選んでください", [
    "今日のおすすめ",
    "ダイエット管理",
    "献立・運動プラン",
    "食事写真評価",
    "アーユルヴェーダ",
    "写真で記録",
    "体型チェック",
    "家計簿",
    "スケジュール",
    "教育費・人生設計",
    "お得情報",
    "設定"
])

if mode == "今日のおすすめ":
    st.header("👉 今日のおすすめ")

    today_str = datetime.today().strftime("%Y-%m-%d")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 今日のダイエット状況")
        st.session_state["diet_logs"] = load_diet_logs()

        if st.session_state["diet_logs"]:
            latest = st.session_state["diet_logs"][-1]
            st.write(f"体重：{latest['体重(kg)']} kg")
            st.write(f"体脂肪率：{latest['体脂肪率(%)']} %")
            st.write(f"目標体重：{latest['目標体重(kg)']} kg")
            st.write(f"目標体脂肪率：{latest['目標体脂肪率(%)']} %")
            st.write(f"BMI：{latest['BMI']}")
            st.write(f"摂取目標：{latest['目標摂取カロリー']} kcal")
        else:
            st.info("まだ記録がありません")

    with col2:
        st.subheader("🥗 今日の献立＆運動")
        saved_plan_date, saved_plan_text = load_today_plan()
        if saved_plan_date and saved_plan_text:
            st.session_state["today_plan_date"] = saved_plan_date
            st.session_state["today_plan_text"] = saved_plan_text

        if st.session_state["today_plan_text"] and st.session_state["today_plan_date"] == today_str:
            st.markdown(st.session_state["today_plan_text"])
        else:
            st.info("まだプランがありません")
            st.caption("👉『献立・運動プラン』で作成してください")

    st.divider()
    st.subheader("🌿 今日の体質アドバイス")
    if st.session_state["dosha_type"]:
        advice = get_ayurveda_advice(st.session_state["dosha_type"])
        st.write(f"体質タイプ：**{st.session_state['dosha_type']}**")
        st.write(f"特徴：{advice['特徴']}")
        st.write(f"食事：{advice['食事']}")
        st.write(f"過ごし方：{advice['生活']}")
        st.write(f"運動：{advice['運動']}")
    else:
        st.info("まだアーユルヴェーダ体質チェックが未実施です。")

    st.divider()
    st.subheader("🧺 保存中の冷蔵庫食材")
    if st.session_state["fridge_items"]:
        st.write(st.session_state["fridge_items"])
    else:
        st.info("まだ冷蔵庫食材の登録がありません。")

elif mode == "ダイエット管理":
    sync_settings_on_mode_enter(mode)
    st.session_state["diet_logs"] = load_diet_logs()
    st.header("📝 ダイエット管理")

    age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()
    weeks = st.slider("目標達成までの期間（週）", 1, 52, 4)

    bmi = weight / ((height_cm / 100) ** 2)
    bmr = weight * 22 * 1.5
    cal_deficit = ((weight - target_weight) * 7200) / (weeks * 7)
    goal_calories = bmr - cal_deficit

    c1, c2, c3 = st.columns(3)
    c1.metric("BMI", f"{bmi:.1f}")
    c2.metric("基礎代謝", f"{bmr:.0f} kcal")
    c3.metric("目標摂取カロリー", f"{goal_calories:.0f} kcal/日")

    st.caption(f"現在体脂肪率: {body_fat:.1f}% / 目標体脂肪率: {target_body_fat:.1f}%")

    if st.button("📌 今日のデータを記録"):
        log = {
            "日付": datetime.today().strftime("%Y-%m-%d"),
            "年齢": age,
            "身長(cm)": height_cm,
            "体重(kg)": weight,
            "目標体重(kg)": target_weight,
            "体脂肪率(%)": body_fat,
            "目標体脂肪率(%)": target_body_fat,
            "BMI": round(bmi, 1),
            "目標摂取カロリー": round(goal_calories, 0),
        }

        updated = False
        for i, existing in enumerate(st.session_state["diet_logs"]):
            if existing["日付"] == log["日付"]:
                st.session_state["diet_logs"][i] = log
                updated = True
                break

        if not updated:
            st.session_state["diet_logs"].append(log)

        upsert_diet_log(log)
        st.session_state["diet_logs"] = load_diet_logs()
        st.success("今日の記録を保存しました✨")
        st.rerun()

    if st.session_state["diet_logs"]:
        st.subheader("📘 ダイエット履歴")
        df = pd.DataFrame(st.session_state["diet_logs"])
        st.dataframe(df, use_container_width=True)

        df["日付"] = pd.to_datetime(df["日付"])
        df = df.sort_values("日付")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📈 体重推移")
            st.line_chart(df.set_index("日付")["体重(kg)"])
        with col2:
            st.write("📉 体脂肪率推移")
            st.line_chart(df.set_index("日付")["体脂肪率(%)"])

elif mode == "献立・運動プラン":
    sync_settings_on_mode_enter(mode)
    st.session_state["diet_logs"] = load_diet_logs()
    st.header("🥗献立＆🏃運動プラン")

    gender = st.radio("性別", ["女性", "男性"], horizontal=True)
    age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()

    st.radio("食事スタイル", ["和食中心", "バランス", "おしゃれカフェ風"], horizontal=True, key="meal_style")
    st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
    st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")
    st.text_area(
        "冷蔵庫の食材（あるものを入力）",
        placeholder="例：卵、豆腐、納豆、鶏むね肉、にんじん、玉ねぎ、キャベツ",
        key="fridge_items"
    )
    st.radio("プランタイプ", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
    st.checkbox("👩 主婦リアル提案モード", key="real_mode")
    st.selectbox("今日の食事バランス", ["普通", "朝しっかり・昼軽め", "食べすぎた", "あまり食べてない"], key="daily_flow")
    st.checkbox("🏃‍♀️ 今日運動あり（ジム・ヨガなど）", key="workout_today")
    st.selectbox("目的", ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"], key="body_goal")

    if st.session_state["dosha_type"]:
        st.info(f"🌿 現在の体質設定：{st.session_state['dosha_type']}")

    days = st.slider("まとめて何日分作りますか？", 1, 30, 7)
    client = get_openai_client()
    today_str = datetime.today().strftime("%Y-%m-%d")

    if st.button("📅 今日のプランを表示"):
        with st.spinner("生成中..."):
            plan = create_plan_for_date(
                client,
                today_str,
                gender,
                age,
                height_cm,
                weight,
                body_fat,
                target_weight,
                target_body_fat,
                st.session_state["dosha_type"],
                st.session_state["meal_style"],
                st.session_state["ease_level"],
                st.session_state["staple_preference"],
                st.session_state["fridge_items"],
                st.session_state["plan_type"],
                st.session_state["real_mode"],
                st.session_state["daily_flow"],
                st.session_state["workout_today"],
                st.session_state["body_goal"]
            )

        st.session_state["today_plan_text"] = plan
        st.session_state["today_plan_date"] = today_str
        upsert_today_plan(today_str, plan)

        st.subheader(f"今日のプラン（{today_str}）")
        st.markdown(plan)

    st.divider()

    if st.button("複数日プラン作成"):
        results = []
        with st.spinner("AIが複数日プランを作成中..."):
            for i in range(days):
                date = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")
                plan_text = create_plan_for_date(
                    client,
                    date,
                    gender,
                    age,
                    height_cm,
                    weight,
                    body_fat,
                    target_weight,
                    target_body_fat,
                    st.session_state["dosha_type"],
                    st.session_state["meal_style"],
                    st.session_state["ease_level"],
                    st.session_state["staple_preference"],
                    st.session_state["fridge_items"],
                    st.session_state["plan_type"],
                    st.session_state["real_mode"],
                    st.session_state["daily_flow"],
                    st.session_state["workout_today"],
                    st.session_state["body_goal"]
                )
                results.append({"日付": date, "プラン": plan_text})

        df = pd.DataFrame(results)
        st.success("プラン完成✨")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 献立・運動プランCSVダウンロード", data=csv, file_name="plan.csv", mime="text/csv")

        st.subheader("🛒 買い物リストまとめ")
        shopping_df = extract_shopping_items(df["プラン"].tolist())
        if not shopping_df.empty:
            st.dataframe(shopping_df, use_container_width=True)
            shopping_csv = shopping_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 買い物リストCSVダウンロード", data=shopping_csv, file_name="shopping_list.csv", mime="text/csv")
        else:
            st.info("買い物リストを抽出できませんでした。")

elif mode == "食事写真評価":
    st.header("📸 食事写真で1日評価")
    st.caption("朝・昼・夜の写真から、1日の食事バランスをやさしくチェックします。")

    with st.expander("使い方を見る"):
        st.write("① 朝・昼・夜の写真を1枚ずつ入れます")
        st.write("② 『1日の食事を評価する』を押します")
        st.write("③ 良かった点・不足しやすい栄養・調整アドバイスを確認します")

    st.subheader("🍙 朝食")
    breakfast_camera = st.camera_input("朝食を撮る", key="breakfast_camera")
    breakfast_upload = st.file_uploader(
        "または朝食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="breakfast_upload"
    )
    breakfast_source = breakfast_camera if breakfast_camera is not None else breakfast_upload
    breakfast_img = resize_image(breakfast_source, max_size=768) if breakfast_source is not None else None

    if breakfast_img is not None:
        st.image(breakfast_img, use_container_width=True)

    st.divider()

    st.subheader("🍱 昼食")
    lunch_camera = st.camera_input("昼食を撮る", key="lunch_camera")
    lunch_upload = st.file_uploader(
        "または昼食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="lunch_upload"
    )
    lunch_source = lunch_camera if lunch_camera is not None else lunch_upload
    lunch_img = resize_image(lunch_source, max_size=768) if lunch_source is not None else None

    if lunch_img is not None:
        st.image(lunch_img, use_container_width=True)

    st.divider()

    st.subheader("🍽 夕食")
    dinner_camera = st.camera_input("夕食を撮る", key="dinner_camera")
    dinner_upload = st.file_uploader(
        "または夕食写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="dinner_upload"
    )
    dinner_source = dinner_camera if dinner_camera is not None else dinner_upload
    dinner_img = resize_image(dinner_source, max_size=768) if dinner_source is not None else None

    if dinner_img is not None:
        st.image(dinner_img, use_container_width=True)

    st.divider()

    if st.button("📊 1日の食事を評価する"):
        if breakfast_img is None or lunch_img is None or dinner_img is None:
            st.warning("朝・昼・夜の3枚をそろえてください。")
        else:
            client = get_openai_client()
            with st.spinner("1日の食事バランスを分析中..."):
                result = evaluate_meal_day_from_images(
                    client,
                    breakfast_img,
                    lunch_img,
                    dinner_img
                )

            st.session_state["meal_eval_result"] = result
            st.success("1日の食事評価を作成しました。")
            st.rerun()

    st.text_area(
        "評価結果",
        key="meal_eval_result",
        height=320
    )

    if st.session_state["meal_eval_result"]:
        st.download_button(
            "📥 評価結果をテキスト保存",
            data=st.session_state["meal_eval_result"],
            file_name="meal_day_evaluation.txt",
            mime="text/plain"
        )

elif mode == "アーユルヴェーダ":
    st.header("🌿 アーユルヴェーダ体質チェック")
    st.write("7項目から体質傾向をチェックします。チェックが多い体質が今の自分に近い目です。")

    q1 = st.radio("体型", [
        "痩せ型で食べても太らない",
        "中肉中背で平均的",
        "子供の頃から太りやすい"
    ], key="ay_q1")

    q2 = st.radio("肌", [
        "乾燥している",
        "オイリーでシミやニキビができやすい",
        "色白でもっちりしてる"
    ], key="ay_q2")

    q3 = st.radio("髪", [
        "硬く乾燥している",
        "柔らかくて細い",
        "黒くて多い"
    ], key="ay_q3")

    q4 = st.radio("発汗", [
        "あまりかかない",
        "汗っかき",
        "普通"
    ], key="ay_q4")

    q5 = st.radio("体温", [
        "手足が冷たい",
        "体が熱い",
        "全体が冷たい"
    ], key="ay_q5")

    q6 = st.radio("食欲", [
        "ムラがある・不規則",
        "食欲旺盛・食事を抜くとイライラする",
        "よく眠る・居眠りが多い"
    ], key="ay_q6")

    q7 = st.radio("排便", [
        "便秘気味・硬便",
        "下痢気味・軟便",
        "中程度の硬さ・時間を要する"
    ], key="ay_q7")

    if st.button("🌿 体質をチェック"):
        answers = {
            "体型": q1,
            "肌": q2,
            "髪": q3,
            "発汗": q4,
            "体温": q5,
            "食欲": q6,
            "排便": q7,
        }

        result_type, scores = diagnose_dosha_advanced(answers)
        advice = get_ayurveda_advice_advanced(result_type)
        foods = get_ayurveda_foods(result_type)

        st.session_state["dosha_type"] = result_type
        st.session_state["dosha_scores"] = scores

        st.success(f"あなたの体質傾向は **{result_type}** です。")

        c1, c2, c3 = st.columns(3)
        c1.metric("ヴァータ", scores["ヴァータ"])
        c2.metric("ピッタ", scores["ピッタ"])
        c3.metric("カパ", scores["カパ"])

        st.subheader("🌿 体質の特徴")
        st.write(advice.get("特徴", ""))

        st.subheader("🍽 食事アドバイス")
        st.write(advice.get("食事", ""))

        st.subheader("🛀 過ごし方")
        st.write(advice.get("生活", ""))

        st.subheader("🏃 おすすめ運動")
        st.write(advice.get("運動", ""))

        st.subheader("⚖ ダイエットのコツ")
        st.write(advice.get("ダイエット", ""))

        st.subheader("🥕 おすすめ食材")
        st.write("・" + "\n・".join(foods) if foods else "おすすめ食材は未設定です")

        if st.session_state["fridge_items"]:
            fridge_text = st.session_state["fridge_items"]
            match_foods = [f for f in foods if f in fridge_text]
            if match_foods:
                st.subheader("🧺 冷蔵庫にある相性食材")
                st.write("・" + "\n・".join(match_foods))
            else:
                st.subheader("🧺 冷蔵庫との相性")
                st.write("今の冷蔵庫食材との一致は少なめです。買い足し候補としておすすめ食材を活用できます。")

    if st.button("↺ 体質診断をリセット"):
        st.session_state["dosha_type"] = ""
        st.session_state["dosha_scores"] = {"ヴァータ": 0, "ピッタ": 0, "カパ": 0}
        st.success("体質診断をリセットしました。")

elif mode == "写真で記録":
    st.header("📷 写真で記録")

    tab1, tab2 = st.tabs(["冷蔵庫写真", "体重計写真"])

    with tab1:
        st.subheader("🥬 冷蔵庫スキャン")
        st.caption("スマホでは1枚ずつ撮って追加していく使い方がおすすめです。")

        fridge_camera = st.camera_input("冷蔵庫を撮る", key="fridge_camera_scan")

        col1, col2 = st.columns(2)

        with col1:
            if fridge_camera is not None and st.button("➕ この写真を追加"):
                resized = resize_image(fridge_camera, max_size=768)
                st.session_state["fridge_scan_images"].append(resized)
                st.success("冷蔵庫写真を追加しました。")
                st.rerun()

        with col2:
            if st.button("🧹 スキャン画像を全部クリア"):
                st.session_state["fridge_scan_images"] = []
                st.rerun()

        fridge_photos = st.file_uploader(
            "または冷蔵庫写真をアップロード（複数OK）",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="fridge_photo_upload"
        )

        if fridge_photos:
            for photo in fridge_photos:
                resized = resize_image(photo, max_size=768)
                st.session_state["fridge_scan_images"].append(resized)
            st.success("アップロード画像を追加しました。")
            st.rerun()

        if st.session_state["fridge_scan_images"]:
            st.write(f"保存中の画像: {len(st.session_state['fridge_scan_images'])}枚")
            for i, img in enumerate(st.session_state["fridge_scan_images"]):
                st.image(img, caption=f"冷蔵庫画像 {i+1}", use_container_width=True)

            if st.button("🥬 スキャン画像から食材抽出"):
                client = get_openai_client()
                with st.spinner("AIが食材を読み取り中..."):
                    result = extract_foods_from_images(client, st.session_state["fridge_scan_images"])

                st.session_state["photo_fridge_items"] = result
                st.success("食材候補を抽出しました。")
                st.rerun()

        st.text_area(
            "読み取った食材候補",
            key="photo_fridge_items",
            height=180
        )

        if st.button("➡ 冷蔵庫食材に反映"):
            text = st.session_state["photo_fridge_items"]
            if "食材候補:" in text:
                text = text.split("食材候補:")[-1].strip()
            st.session_state["fridge_items"] = text
            st.success("冷蔵庫の食材に反映しました。")

    with tab2:
        st.subheader("⚖ 体重計写真から記録候補を管理")

        scale_photo = st.file_uploader(
            "体重計の写真をアップロード",
            type=["jpg", "jpeg", "png"],
            key="scale_photo_upload"
        )

        resized_scale = None

        if scale_photo is not None:
            resized_scale = resize_image(scale_photo, max_size=768)
            st.image(resized_scale, caption="アップロードした体重計写真", use_container_width=True)

            if st.button("⚖ 数値を自動抽出"):
                client = get_openai_client()
                with st.spinner("AIが数値を読み取り中..."):
                    result = extract_scale_values_from_image(client, resized_scale)

                st.session_state["photo_scale_result"] = result
                st.success("数値候補を抽出しました✨")
                st.rerun()

        st.text_area(
            "読み取った数値候補メモ",
            placeholder="例：体重: 51.2\n体脂肪率: 25.6\n骨格筋率: 27.2",
            key="photo_scale_result",
            height=220
        )

        st.caption("内容を見ながら、ダイエット管理へ反映できます。")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("➡ 体重だけ反映"):
                text = st.session_state["photo_scale_result"]
                m = re.search(r"体重[:：]\s*([0-9]+(?:\.[0-9]+)?)", text)
                if m:
                    st.session_state["common_weight"] = float(m.group(1))
                    st.success("体重を反映しました。")
                else:
                    st.warning("体重が見つかりませんでした。")

        with col2:
            if st.button("➡ 体脂肪率だけ反映"):
                text = st.session_state["photo_scale_result"]
                m = re.search(r"体脂肪率[:：]\s*([0-9]+(?:\.[0-9]+)?)", text)
                if m:
                    st.session_state["common_body_fat"] = float(m.group(1))
                    st.success("体脂肪率を反映しました。")
                else:
                    st.warning("体脂肪率が見つかりませんでした。")

        if st.button("📌 体重・体脂肪率をまとめて反映"):
            text = st.session_state["photo_scale_result"]
            weight_match = re.search(r"体重[:：]\s*([0-9]+(?:\.[0-9]+)?)", text)
            fat_match = re.search(r"体脂肪率[:：]\s*([0-9]+(?:\.[0-9]+)?)", text)

            updated = False

            if weight_match:
                st.session_state["common_weight"] = float(weight_match.group(1))
                updated = True

            if fat_match:
                st.session_state["common_body_fat"] = float(fat_match.group(1))
                updated = True

            if updated:
                st.success("体重・体脂肪率を反映しました。")
            else:
                st.warning("反映できる数値が見つかりませんでした。")

elif mode == "体型チェック":
    st.header("🪞 体型チェック")
    st.caption("顔がはっきり写らない距離・角度での撮影がおすすめです。")

    st.selectbox(
        "今回の目的",
        ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"],
        key="body_goal_scan"
    )

    body_camera = st.camera_input("全身を撮る", key="body_camera_scan")

    uploaded_body = st.file_uploader(
        "または全身写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="body_photo_upload"
    )

    source_body = body_camera if body_camera is not None else uploaded_body
    resized_body = None

    if source_body is not None:
        resized_body = resize_image(source_body, max_size=768)
        st.image(resized_body, caption="全身スキャン画像", use_container_width=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🪄 体型コメントを自動生成"):
                client = get_openai_client()
                with st.spinner("体型バランスを分析中..."):
                    result = generate_body_balance_comment(
                        client,
                        resized_body,
                        st.session_state["body_goal_scan"]
                    )

                st.session_state["body_scan_comment"] = result
                st.success("体型コメントを生成しました。")
                st.rerun()

        with col2:
            if st.button("✨ 理想イメージ用プロンプトを作成"):
                client = get_openai_client()
                source_comment = st.session_state["body_scan_comment"] or "まだ体型コメントなし"
                with st.spinner("理想イメージを整理中..."):
                    result = generate_ideal_body_prompt(
                        client,
                        source_comment,
                        st.session_state["body_goal_scan"]
                    )

                st.session_state["ideal_body_prompt_result"] = result
                st.success("理想イメージ用プロンプトを作成しました。")
                st.rerun()

        with col3:
            if st.button("🖼 理想イメージを生成"):
                client = get_openai_client()
                prompt_text = st.session_state["ideal_body_prompt_result"]
                if not prompt_text.strip():
                    st.warning("先に理想イメージ用プロンプトを作成してください。")
                else:
                    with st.spinner("理想イメージを生成中..."):
                        image_bytes = generate_ideal_body_image(client, prompt_text, size="1024x1024")

                    if image_bytes:
                        st.session_state["ideal_body_image_bytes"] = image_bytes
                        st.success("理想イメージを生成しました。")
                        st.rerun()
                    else:
                        st.error("画像生成に失敗しました。")

    st.text_area(
        "体型バランスコメント",
        key="body_scan_comment",
        height=240
    )

    st.text_area(
        "理想イメージ用プロンプト",
        key="ideal_body_prompt_result",
        height=240
    )

    if st.session_state["ideal_body_image_bytes"]:
        st.subheader("🖼 理想イメージ")
        st.image(st.session_state["ideal_body_image_bytes"], use_container_width=True)

    st.text_area(
        "体型バランスメモ",
        placeholder="例：肩まわりがしっかり、下半身にボリューム、脚のむくみが気になる、背中をすっきりさせたい",
        key="body_check_comment",
        height=160
    )

    st.caption("骨格を断定するのではなく、見え方やバランス傾向として使うのがおすすめです。")
    st.caption("理想イメージはモチベーション用の参考として使う設計です。")

elif mode == "家計簿":
    st.header("💰 家計簿入力")
    with st.form("budget_form"):
        date = st.date_input("日付", datetime.today())
        category = st.selectbox("カテゴリ", ["食費", "日用品", "教育費", "交際費", "医療費", "その他"])
        amount = st.number_input("金額（円）", min_value=0, step=100)
        memo = st.text_input("メモ")
        submitted = st.form_submit_button("記録する")

    if submitted:
        st.session_state["expenses"].append({
            "日付": str(date),
            "カテゴリ": category,
            "金額": amount,
            "メモ": memo
        })
        st.success("家計簿を記録しました。")

    if st.session_state["expenses"]:
        df_exp = pd.DataFrame(st.session_state["expenses"])
        st.subheader("📊 記録一覧")
        st.dataframe(df_exp, use_container_width=True)

elif mode == "スケジュール":
    st.header("🗓 スケジュール登録")
    with st.form("schedule_form"):
        date = st.date_input("予定日", datetime.today())
        event_type = st.selectbox("種類", ["運動", "買い物", "献立準備", "学校", "通院", "その他"])
        event = st.text_input("予定内容")
        s_submitted = st.form_submit_button("追加する")

    if s_submitted:
        st.session_state["schedules"].append({
            "日付": str(date),
            "種類": event_type,
            "内容": event
        })
        st.success("予定を登録しました。")

    if st.session_state["schedules"]:
        df_sched = pd.DataFrame(st.session_state["schedules"])
        st.subheader("📅 予定一覧")
        st.dataframe(df_sched, use_container_width=True)

elif mode == "教育費・人生設計":
    st.header("📘 教育費・人生設計")

    num_children = st.number_input("子どもの人数", min_value=0, max_value=5, value=1)
    edu_type = st.selectbox("教育方針", ["すべて公立", "中学から私立", "高校から私立", "大学から私立", "すべて私立"])

    edu_costs = {
        "公立": {"小学校": 50, "中学校": 70, "高校": 100, "大学": 300},
        "私立": {"小学校": 150, "中学校": 200, "高校": 300, "大学": 600}
    }

    current_year = datetime.now().year
    total_cost = 0

    for i in range(num_children):
        child_age = st.slider(f"子ども{i+1}の現在の年齢", 0, 18, 6, key=f"child_age_{i}")
        plan = {
            "すべて公立": ["公立"] * 4,
            "中学から私立": ["公立", "私立", "私立", "私立"],
            "高校から私立": ["公立", "公立", "私立", "私立"],
            "大学から私立": ["公立"] * 3 + ["私立"],
            "すべて私立": ["私立"] * 4
        }[edu_type]

        levels = ["小学校", "中学校", "高校", "大学"]
        offsets = [0, 6, 9, 12]

        for j, level in enumerate(levels):
            y = current_year + (6 - child_age) + offsets[j]
            cost = edu_costs[plan[j]][level]
            st.write(f"{y}年 - {level}（{plan[j]}）: {cost}万円")
            total_cost += cost

    st.metric("想定教育費合計", f"{total_cost} 万円")


elif mode == "お得情報":
    st.header("📢 お得情報")
    st.info("ここは今後拡張できます。")


elif mode == "設定":
    st.header("⚙️ 設定")

    st.subheader("📌 初期設定")
    st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    st.number_input("スタート時の体重（kg）", min_value=30.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    st.number_input("目標体重（kg）", min_value=30.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
    st.number_input("スタート時の体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")

    st.subheader("🍽 献立の初期値")
    st.radio("食事スタイル", ["和食中心", "バランス", "おしゃれカフェ風"], horizontal=True, key="meal_style")
    st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
    st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")
    st.text_area("よくある冷蔵庫の食材", key="fridge_items")
    st.radio("プランタイプ初期値", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
    st.checkbox("主婦リアル提案モード初期値", key="real_mode")
    st.selectbox("食事の流れ初期値", ["普通", "朝しっかり・昼軽め", "食べすぎた", "あまり食べてない"], key="daily_flow")
    st.checkbox("運動あり初期値", key="workout_today")
    st.selectbox("目的初期値", ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"], key="body_goal")

    if st.button("💾 初期設定を保存"):
        save_user_settings()
        st.success("初期設定を保存しました。")

    if st.button("↺ 初期設定をリセット"):
        reset_user_settings()
        save_user_settings()
        st.success("初期設定をリセットしました。")
