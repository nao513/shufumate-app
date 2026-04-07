import base64
import io
import re
import calendar
import streamlit.components.v1 as components
from datetime import datetime, timedelta

import gspread
import pandas as pd
import streamlit as st
from openai import OpenAI
from PIL import Image
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

UI_TEXT = {
    "update": "更新する",
    "save": "保存する",
    "delete": "削除",
    "upload": "写真を追加",
    "settings": "設定",
    "notice": "お知らせ",
}


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


def rewrite_sheet_with_header(ws, expected_header):
    values = ws.get_all_values()

    if not values:
        ws.clear()
        ws.append_row(expected_header)
        return

    current_header = values[0]
    data_rows = values[1:]

    if current_header == expected_header:
        return

    migrated_rows = []
    for row in data_rows:
        row = row + [""] * (len(current_header) - len(row))
        row_dict = dict(zip(current_header, row))
        migrated_rows.append([row_dict.get(col, "") for col in expected_header])

    ws.clear()
    ws.append_row(expected_header)
    if migrated_rows:
        ws.append_rows(migrated_rows)


def ensure_headers():
    sh = get_spreadsheet()

    settings_ws = get_or_create_worksheet(sh, "Settings")
    diet_ws = get_or_create_worksheet(sh, "DietLogs")
    plans_ws = get_or_create_worksheet(sh, "TodayPlans")

    settings_header = [
    "user_id", "gender", "age", "height_cm", "start_weight",
    "target_weight", "start_body_fat", "target_body_fat",
    "meal_style", "ease_level", "staple_preference",
    "fridge_items", "avoid_foods", "favorite_meals",
    "favorite_protein_onigiri", "favorite_misodama_soup",
    "plan_type", "lunch_style",
    "real_mode", "daily_flow", "workout_today", "body_goal"
    ]
    diet_header = [
        "user_id", "date", "gender", "age", "height_cm", "weight",
        "target_weight", "body_fat", "target_body_fat",
        "bmi", "goal_calories"
    ]
    plan_header = ["user_id", "date", "plan_text"]

    rewrite_sheet_with_header(settings_ws, settings_header)
    rewrite_sheet_with_header(diet_ws, diet_header)
    rewrite_sheet_with_header(plans_ws, plan_header)


def get_current_user_id():
    return st.session_state.get("user_name_input", "").strip()
    
def reload_user_data_if_needed():
    current_user_id = get_current_user_id()

    if not current_user_id:
        return

    if st.session_state.get("last_loaded_user_id") != current_user_id:
        saved = load_user_settings()
        if saved:
            for k, v in saved.items():
                st.session_state[k] = v

        st.session_state["diet_logs"] = load_diet_logs()
        sync_common_from_latest_diet_log()

        saved_plan_date, saved_plan_text = load_today_plan()
        if saved_plan_date and saved_plan_text:
            st.session_state["today_plan_date"] = saved_plan_date
            st.session_state["today_plan_text"] = saved_plan_text

        st.session_state["last_loaded_user_id"] = current_user_id
        st.session_state["settings_snapshot"] = get_settings_snapshot()
        

def load_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2:
        return None

    header = values[0]
    data_rows = values[1:]

    for row in data_rows:
        if not row:
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))

        if row_dict.get("user_id") == current_user_id:
            return {
                "common_gender": row_dict.get("gender", "未選択") or "未選択",
                "common_age": int(float(row_dict["age"])) if row_dict.get("age") else 40,
                "common_height": float(row_dict["height_cm"]) if row_dict.get("height_cm") else 160.0,
                "common_weight": float(row_dict["start_weight"]) if row_dict.get("start_weight") else 50.0,
                "common_target_weight": float(row_dict["target_weight"]) if row_dict.get("target_weight") else 48.0,
                "common_body_fat": float(row_dict["start_body_fat"]) if row_dict.get("start_body_fat") else 28.0,
                "common_target_body_fat": float(row_dict["target_body_fat"]) if row_dict.get("target_body_fat") else 24.0,
                "meal_style": row_dict.get("meal_style", "和食中心") or "和食中心",
                "ease_level": row_dict.get("ease_level", "超かんたん") or "超かんたん",
                "staple_preference": row_dict.get("staple_preference", "ごはん派") or "ごはん派",
                "fridge_items": row_dict.get("fridge_items", "") or "",
                "avoid_foods": row_dict.get("avoid_foods", "") or "",
                "favorite_meals": row_dict.get("favorite_meals", "") or "",
                "favorite_protein_onigiri": row_dict.get("favorite_protein_onigiri", "") or "",
                "favorite_misodama_soup": row_dict.get("favorite_misodama_soup", "") or "",
                "avoid_foods": row_dict.get("avoid_foods", "") or "",
                "favorite_meals": row_dict.get("favorite_meals", "") or "",
                "favorite_protein_onigiri": row_dict.get("favorite_protein_onigiri", "") or "",
                "favorite_misodama_soup": row_dict.get("favorite_misodama_soup", "") or "",
                "plan_type": row_dict.get("plan_type", "通常") or "通常",
                "lunch_style": row_dict.get("lunch_style", "指定なし") or "指定なし",
                "real_mode": str(row_dict.get("real_mode", "True")).lower() == "true",
                "daily_flow": row_dict.get("daily_flow", "普通") or "普通",
                "workout_today": str(row_dict.get("workout_today", "False")).lower() == "true",
                "body_goal": row_dict.get("body_goal", "バランス") or "バランス",
            }
    return None


def save_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    row_values = [
        current_user_id,
        st.session_state["common_gender"],
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
        st.session_state.get("avoid_foods", ""),
        st.session_state.get("favorite_meals", ""),
        st.session_state.get("favorite_protein_onigiri", ""),
        st.session_state.get("favorite_misodama_soup", ""),
        st.session_state["plan_type"],
        st.session_state["lunch_style"],
        str(st.session_state["real_mode"]),
        st.session_state["daily_flow"],
        str(st.session_state["workout_today"]),
        st.session_state["body_goal"],
    ]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == current_user_id:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:V{row_index}", [row_values])
    else:
        ws.append_row(row_values)


def reset_user_settings():
    st.session_state["common_gender"] = "未選択"
    st.session_state["common_age"] = 40
    st.session_state["common_height"] = 160.0
    st.session_state["common_weight"] = 50.0
    st.session_state["common_target_weight"] = 48.0
    st.session_state["common_body_fat"] = 28.0
    st.session_state["common_target_body_fat"] = 24.0
    st.session_state["meal_style"] = "和食中心"
    st.session_state["ease_level"] = "超かんたん"
    st.session_state["staple_preference"] = "ごはん派"
    st.session_state["fridge_items"] = ""
    st.session_state["avoid_foods"] = ""
    st.session_state["favorite_meals"] = ""
    st.session_state["favorite_protein_onigiri"] = ""
    st.session_state["favorite_misodama_soup"] = ""
    st.session_state["plan_type"] = "通常"
    st.session_state["lunch_style"] = "指定なし"
    st.session_state["real_mode"] = True
    st.session_state["daily_flow"] = "普通"
    st.session_state["workout_today"] = False
    st.session_state["body_goal"] = "バランス"
    st.session_state["avoid_foods"] = ""
    st.session_state["favorite_meals"] = ""
    st.session_state["favorite_protein_onigiri"] = ""
    st.session_state["favorite_misodama_soup"] = ""


def load_settings_into_session():
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v

def get_settings_snapshot():
    return {
        "common_gender": st.session_state.get("common_gender", "未選択"),
        "common_age": st.session_state.get("common_age", 40),
        "common_height": st.session_state.get("common_height", 160.0),
        "common_weight": st.session_state.get("common_weight", 50.0),
        "common_target_weight": st.session_state.get("common_target_weight", 48.0),
        "common_body_fat": st.session_state.get("common_body_fat", 28.0),
        "common_target_body_fat": st.session_state.get("common_target_body_fat", 24.0),
        "meal_style": st.session_state.get("meal_style", "和食中心"),
        "ease_level": st.session_state.get("ease_level", "超かんたん"),
        "staple_preference": st.session_state.get("staple_preference", "ごはん派"),
        "fridge_items": st.session_state.get("fridge_items", ""),
        "avoid_foods": st.session_state.get("avoid_foods", ""),
        "favorite_meals": st.session_state.get("favorite_meals", ""),
        "favorite_protein_onigiri": st.session_state.get("favorite_protein_onigiri", ""),
        "favorite_misodama_soup": st.session_state.get("favorite_misodama_soup", ""),
        "plan_type": st.session_state.get("plan_type", "通常"),
        "lunch_style": st.session_state.get("lunch_style", "指定なし"),
        "real_mode": st.session_state.get("real_mode", True),
        "daily_flow": st.session_state.get("daily_flow", "普通"),
        "workout_today": st.session_state.get("workout_today", False),
        "body_goal": st.session_state.get("body_goal", "バランス"),
    }


def autosave_settings_if_changed():
    current_snapshot = get_settings_snapshot()
    previous_snapshot = st.session_state.get("settings_snapshot", {})

    if previous_snapshot and current_snapshot != previous_snapshot:
        save_user_settings()

    st.session_state["settings_snapshot"] = current_snapshot


def load_diet_logs():
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2:
        return []

    header = values[0]
    data_rows = values[1:]
    logs = []

    for row in data_rows:
        if not row or len(row) < len(header):
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == current_user_id:
            logs.append({
                "日付": row_dict["date"],
                "性別": row_dict.get("gender", "未選択"),
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

def sync_common_from_latest_diet_log():
    logs = st.session_state.get("diet_logs", [])
    if not logs:
        return

    latest = logs[-1]

    if "性別" in latest and latest["性別"] not in [None, ""]:
        st.session_state["common_gender"] = latest["性別"]
    if "年齢" in latest and latest["年齢"] not in [None, ""]:
        st.session_state["common_age"] = int(float(latest["年齢"]))
    if "身長(cm)" in latest and latest["身長(cm)"] not in [None, ""]:
        st.session_state["common_height"] = float(latest["身長(cm)"])
    if "体重(kg)" in latest and latest["体重(kg)"] not in [None, ""]:
        st.session_state["common_weight"] = float(latest["体重(kg)"])
    if "目標体重(kg)" in latest and latest["目標体重(kg)"] not in [None, ""]:
        st.session_state["common_target_weight"] = float(latest["目標体重(kg)"])
    if "体脂肪率(%)" in latest and latest["体脂肪率(%)"] not in [None, ""]:
        st.session_state["common_body_fat"] = float(latest["体脂肪率(%)"])
    if "目標体脂肪率(%)" in latest and latest["目標体脂肪率(%)"] not in [None, ""]:
        st.session_state["common_target_body_fat"] = float(latest["目標体脂肪率(%)"])

def upsert_diet_log(log_dict):
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    row_values = [
        current_user_id,
        log_dict["日付"],
        log_dict["性別"],
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
        if len(row) >= 2 and row[0] == current_user_id and row[1] == log_dict["日付"]:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:K{row_index}", [row_values])
    else:
        ws.append_row(row_values)


def load_today_plan():
    ws = get_sheet("TodayPlans")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2:
        return None, None

    header = values[0]
    data_rows = values[1:]

    latest_date = None
    latest_text = None

    for row in data_rows:
        if not row or len(row) < len(header):
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == current_user_id:
            row_date = row_dict.get("date", "")
            if latest_date is None or row_date >= latest_date:
                latest_date = row_date
                latest_text = row_dict.get("plan_text", "")

    return latest_date, latest_text


def upsert_today_plan(date_str, plan_text):
    ws = get_sheet("TodayPlans")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    row_values = [current_user_id, date_str, plan_text]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2 and row[0] == current_user_id and row[1] == date_str:
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


def delete_uploaded_state(upload_keys=None, stored_keys=None, success_message="削除しました。"):
    upload_keys = upload_keys or []
    stored_keys = stored_keys or []

    for key in upload_keys:
        st.session_state.pop(key, None)

    for key in stored_keys:
        if key.endswith("_list"):
            st.session_state[key] = []
        else:
            st.session_state[key] = None if "bytes" in key else ""

    st.success(success_message)
    st.rerun()


def photo_uploader_with_delete(label, upload_key, bytes_key):
    uploaded = st.file_uploader(label, type=["jpg", "jpeg", "png"], key=upload_key)

    if uploaded is not None:
        st.session_state[bytes_key] = uploaded.getvalue()

    if st.session_state.get(bytes_key):
        st.image(st.session_state[bytes_key], use_container_width=True)
        if st.button(f"🗑 {label}を削除", key=f"delete_{bytes_key}"):
            st.session_state.pop(bytes_key, None)
            st.session_state.pop(upload_key, None)
            st.rerun()


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
        {"type": "input_text", "text": "1枚目が朝食です。"},
        {"type": "input_image", "image_url": image_file_to_data_url(breakfast_img)},
        {"type": "input_text", "text": "2枚目が昼食です。"},
        {"type": "input_image", "image_url": image_file_to_data_url(lunch_img)},
        {"type": "input_text", "text": "3枚目が夕食です。"},
        {"type": "input_image", "image_url": image_file_to_data_url(dinner_img)},
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
# Ayurveda / state check
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
            "安定していて食べるのが好き": "カパ",
        },
        "排便": {
            "便秘気味・硬便": "ヴァータ",
            "下痢気味・軟便": "ピッタ",
            "中程度の硬さ・時間を要する": "カパ",
        },
        "睡眠": {
            "眠りが浅い・途中で起きやすい": "ヴァータ",
            "普通": "ピッタ",
            "よく眠る・居眠りが多い": "カパ",
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


def get_current_state_advice(
    sweet_craving,
    salty_craving,
    fatigue,
    irritable,
    sleepy_after_meal,
    swelling,
    coldness,
    constipation_now,
    dry_skin
):
    results = []

    if sweet_craving:
        results.append("甘いものが無性に食べたい時は、疲れ・ストレス・エネルギー不足、たんぱく質不足気味の可能性があります。まずは食事を抜かず、たんぱく質と温かい汁物を意識してみましょう。")
    if salty_craving:
        results.append("しょっぱいものが欲しい時は、疲労感やミネラル不足、水分バランスの乱れが関係していることがあります。")
    if fatigue:
        results.append("だるさが強い時は、カパの重さ、睡眠不足、栄養不足、動かなさすぎが重なっていることがあります。")
    if irritable:
        results.append("イライラしやすい時は、ピッタの乱れや空腹時間の長さが関係していることがあります。")
    if sleepy_after_meal:
        results.append("食後すぐ眠い時は、糖質に偏った食事や食べすぎ、血糖値変動の可能性があります。")
    if swelling:
        results.append("むくみやすい時は、水分代謝の低下やカパ寄りの乱れ、塩分過多が関係していることがあります。")
    if coldness:
        results.append("冷えやすい時は、ヴァータの乱れやエネルギー不足が関係していることがあります。")
    if constipation_now:
        results.append("便秘ぎみの時は、ヴァータの乱れ、水分不足、冷えが関係していることがあります。")
    if dry_skin:
        results.append("乾燥しやすい時は、ヴァータ寄りの乱れや水分・油分不足が関係していることがあります。")

    if not results:
        return "大きな乱れチェックは入っていません。今は比較的安定している可能性があります。"

    return "\n\n".join(results)


# -----------------------------
# Plan generation
# -----------------------------
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
    avoid_foods="",
    favorite_meals="",
    favorite_protein_onigiri="",
    favorite_misodama_soup="",
    plan_type="通常",
    lunch_style="指定なし",
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

    avoid_rule = ""
    if avoid_foods.strip():
        avoid_rule = f"次の食材・料理は献立に入れないでください: {avoid_foods}"

    favorite_rule = ""
    if favorite_meals.strip() or favorite_protein_onigiri.strip() or favorite_misodama_soup.strip():
        favorite_rule = f"""
ユーザーの定番・好きな食事:
- 定番食: {favorite_meals if favorite_meals else "未入力"}
- おすすめタンパク質おにぎり: {favorite_protein_onigiri if favorite_protein_onigiri else "未入力"}
- 味噌玉味噌汁: {favorite_misodama_soup if favorite_misodama_soup else "未入力"}

上記はできるだけ優先して提案に入れてください。
"""

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

    lunch_style_rule = ""
    if lunch_style == "お弁当":
        lunch_style_rule = """
昼食はお弁当向けにしてください。
・冷めても食べやすい
・汁気が少ない
・詰めやすい
・前日の夜や朝に準備しやすい
"""
    elif lunch_style == "コンビニ":
        lunch_style_rule = """
昼食はコンビニで買いやすい内容にしてください。
・おにぎり、味噌汁、サラダ、サラダチキン、ゆで卵など現実的な組み合わせ
"""
    elif lunch_style == "おすすめ定番":
        lunch_style_rule = f"""
昼食はユーザーのおすすめ定番を優先してください。
・タンパク質おにぎり: {favorite_protein_onigiri if favorite_protein_onigiri else "タンパク質おにぎり"}
・味噌玉の味噌汁: {favorite_misodama_soup if favorite_misodama_soup else "味噌玉味噌汁"}
・必要に応じて、ゆで卵、サラダ、豆腐、サラダチキンなどを組み合わせる
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
- 平日昼食スタイル: {lunch_style}

【重要ルール】
- 日本の一般家庭で作りやすいメニューにしてください
- スーパーで買いやすい食材だけを使ってください
- 主婦向けに、手軽・簡単・現実的な献立にしてください
- 難しい横文字料理や、おしゃれすぎるカフェ料理は避けてください
- 朝食は特に手軽にしてください
- 節約・時短を意識してください
- たんぱく質をしっかり取れるようにしてください
- おにぎり、味噌汁、納豆、豆腐、卵、鶏むね肉、鮭、さば等も積極的に使ってよいです
- {dosha_rule}
- {fridge_rule}
- {avoid_rule}
- {favorite_rule}
- {plan_type_rule}
- {lunch_style_rule}
- {real_mode_rule}

{date_str}の1日の健康的なダイエットプランを作ってください。
"""
    res = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return res.output_text


def ask_shufumate_advice(
    client,
    question,
    gender,
    age,
    height_cm,
    weight,
    body_fat,
    target_weight,
    target_body_fat,
    dosha_type,
    fridge_items,
    avoid_foods,
    favorite_meals,
    favorite_protein_onigiri,
    favorite_misodama_soup,
    daily_flow,
    workout_today,
    body_goal,
    lunch_style,
    category,
    area="",
    site_hint=""
):
    area_rule = ""
    if category == "外食相談" and area.strip():
        area_rule = f"""
【地域情報】
- 相談エリア: {area}

【外食相談ルール】
- 実在店を断定しすぎず、「こういう店・こういう選び方がよい」で答える
- エリアに合いそうな店のジャンルや選び方を優先する
- 運動前後なら食べ方のポイントも入れる
"""

    site_rule = ""
    if site_hint.strip():
        site_rule = f"""
【参考導線】
- 必要に応じて、ユーザーのおすすめ記事導線として次のサイト活用も提案してよい
- {site_hint}
"""

    prompt = f"""
あなたは、主婦向けのやさしい生活・食事・運動アドバイザーです。
質問者に寄り添って、日本語でわかりやすく答えてください。

【相談カテゴリ】
{category}

【質問】
{question}

【利用者情報】
- 性別: {gender}
- 年齢: {age}
- 身長: {height_cm} cm
- 体重: {weight} kg
- 体脂肪率: {body_fat} %
- 目標体重: {target_weight} kg
- 目標体脂肪率: {target_body_fat} %
- 体質傾向: {dosha_type if dosha_type else "未設定"}
- 冷蔵庫の食材: {fridge_items if fridge_items else "未入力"}
- 避けたい食材: {avoid_foods if avoid_foods else "未入力"}
- 定番食: {favorite_meals if favorite_meals else "未入力"}
- おすすめタンパク質おにぎり: {favorite_protein_onigiri if favorite_protein_onigiri else "未入力"}
- 味噌玉味噌汁: {favorite_misodama_soup if favorite_misodama_soup else "未入力"}
- 今日の食事バランス: {daily_flow}
- 今日の運動: {"あり" if workout_today else "なし"}
- 目的: {body_goal}
- 平日昼食スタイル: {lunch_style}

{area_rule}
{site_rule}

【回答ルール】
- 主婦がすぐ行動できる答えにする
- 厳しすぎず、やさしく現実的に答える
- 食事相談は、食べない方向だけでなく「どう調整するか」を含める
- 避けたい食材は提案に含めない
- 定番食やおすすめおにぎり・味噌汁は必要に応じて活用する
- 運動前後の相談は、タイミングとおすすめ食品を具体的に入れる
- 外食相談は、「こういう店・こういう選び方がよい」とわかる形にする
- 店名を無理に断定しない
- 医療判断はしない
- 断定表現を避け、「〜の可能性があります」「〜がおすすめです」と表現する
- 3〜6行程度で簡潔に
- 最後に「ひとことアドバイス」を1つ入れる

【出力形式】
■回答:
■ひとことアドバイス:
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


# -----------------------------
# Helpers
# -----------------------------
def get_common_profile():
    return {
        "gender": st.session_state.get("common_gender", "未選択"),
        "age": st.session_state.get("common_age", 40),
        "height": st.session_state.get("common_height", 160.0),
        "weight": st.session_state.get("common_weight", 50.0),
        "target_weight": st.session_state.get("common_target_weight", 48.0),
        "body_fat": st.session_state.get("common_body_fat", 28.0),
        "target_body_fat": st.session_state.get("common_target_body_fat", 24.0),
        "avoid_foods": st.session_state.get("avoid_foods", ""),
        "favorite_meals": st.session_state.get("favorite_meals", ""),
        "favorite_protein_onigiri": st.session_state.get("favorite_protein_onigiri", ""),
        "favorite_misodama_soup": st.session_state.get("favorite_misodama_soup", ""),
    }


def render_common_body_inputs():
    gender = st.selectbox(
        "性別（任意）",
        ["未選択", "女性", "男性", "その他", "回答しない"],
        key="common_gender"
    )
    age = st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    height_cm = st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    weight = st.number_input("現在の体重（kg）", min_value=39.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    target_weight = st.number_input("目標体重（kg）", min_value=39.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
    body_fat = st.number_input("体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    target_body_fat = st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")
    return gender, age, height_cm, weight, target_weight, body_fat, target_body_fat


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


def build_month_calendar(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdayscalendar(year, month)


def time_to_decimal(time_str: str) -> float:
    try:
        dt = datetime.strptime(time_str, "%H:%M")
        return dt.hour + dt.minute / 60
    except Exception:
        return 0.0


def build_daily_timeline_df(schedule_dict: dict):
    rows = []
    for label, time_str in schedule_dict.items():
        if label == "睡眠目安":
            continue
        rows.append({
            "項目": label,
            "時間": time_str,
            "時刻": time_to_decimal(time_str)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("時刻")
    return df


def render_daily_timeline_html(schedule_dict: dict):
    items = [
        ("起床", "#f59e0b"),
        ("朝食", "#10b981"),
        ("昼食", "#3b82f6"),
        ("夕食", "#8b5cf6"),
        ("入浴", "#f97316"),
        ("就寝", "#64748b"),
    ]

    html_parts = []
    html_parts.append("""
    <div style="border:1px solid #e5e7eb;border-radius:16px;padding:16px;background:#ffffff;">
      <div style="font-weight:700;font-size:18px;margin-bottom:12px;">1日の流れタイムライン</div>
      <div style="position:relative;height:56px;border-radius:12px;background:#f8fafc;border:1px solid #e5e7eb;margin-bottom:14px;">
    """)

    for hour in range(25):
        left = (hour / 24) * 100
        if hour < 24:
            html_parts.append(
                f"""
                <div style="position:absolute;left:{left}%;top:0;height:56px;width:1px;background:#e5e7eb;"></div>
                <div style="position:absolute;left:{left}%;top:36px;transform:translateX(-50%);font-size:11px;color:#64748b;">
                    {hour}
                </div>
                """
            )

    for label, color in items:
        time_str = schedule_dict.get(label, "")
        decimal_time = time_to_decimal(time_str)
        left = (decimal_time / 24) * 100

        html_parts.append(
            f"""
            <div title="{label} {time_str}"
                 style="
                    position:absolute;
                    left:calc({left}% - 10px);
                    top:8px;
                    width:20px;
                    height:20px;
                    border-radius:999px;
                    background:{color};
                    border:2px solid white;
                    box-shadow:0 1px 4px rgba(0,0,0,0.15);
                 ">
            </div>
            <div style="
                    position:absolute;
                    left:{left}%;
                    top:-2px;
                    transform:translateX(-50%);
                    font-size:11px;
                    font-weight:600;
                    color:#111827;
                    white-space:nowrap;
                 ">
                 {label}
            </div>
            """
        )

    html_parts.append("</div>")

    html_parts.append('<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">')
    for label, color in items:
        time_str = schedule_dict.get(label, "")
        html_parts.append(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
                padding:8px 10px;
                border:1px solid #e5e7eb;
                border-radius:12px;
                background:#fafafa;
            ">
                <span style="
                    display:inline-block;
                    width:12px;
                    height:12px;
                    border-radius:999px;
                    background:{color};
                "></span>
                <span style="font-size:13px;color:#374151;">{label}</span>
                <span style="margin-left:auto;font-weight:700;color:#111827;">{time_str}</span>
            </div>
            """
        )
    html_parts.append("</div></div>")

    components.html("".join(html_parts), height=220, scrolling=False)


def get_recommended_daily_schedule(wake_time_str: str):
    try:
        wake_dt = datetime.strptime(wake_time_str, "%H:%M")
    except Exception:
        wake_dt = datetime.strptime("06:30", "%H:%M")

    breakfast = wake_dt + timedelta(minutes=60)
    lunch = wake_dt + timedelta(hours=6)
    dinner = wake_dt + timedelta(hours=12)
    bath = wake_dt + timedelta(hours=14, minutes=30)
    sleep = wake_dt + timedelta(hours=15, minutes=30)

    return {
        "起床": wake_dt.strftime("%H:%M"),
        "朝食": breakfast.strftime("%H:%M"),
        "昼食": lunch.strftime("%H:%M"),
        "夕食": dinner.strftime("%H:%M"),
        "入浴": bath.strftime("%H:%M"),
        "就寝": sleep.strftime("%H:%M"),
        "睡眠目安": "7時間以上",
    }


# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "user_name_input": "",
    "last_loaded_user_id": "",
    "settings_snapshot": {},
    "common_gender": "未選択",
    "common_age": 40,
    "common_height": 160.0,
    "common_weight": 50.0,
    "common_target_weight": 48.0,
    "common_body_fat": 28.0,
    "common_target_body_fat": 24.0,
    "meal_style": "和食中心",
    "ease_level": "超かんたん",
    "staple_preference": "ごはん派",
    "fridge_items": "",
    "avoid_foods": "",
    "favorite_meals": "",
    "favorite_protein_onigiri": "",
    "favorite_misodama_soup": "",
    "plan_type": "通常",
    "lunch_style": "指定なし",
    "real_mode": True,
    "daily_flow": "普通",
    "workout_today": False,
    "body_goal": "バランス",
    "diet_logs": [],
    "today_plan_text": "",
    "today_plan_date": "",
    "expenses": [],
    "schedules": [],
    "selected_schedule_date": "",
    "wake_time_str": "06:30",
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
    "quick_advice_result": "",
    "quick_advice_question": "",
    "advice_area": "",
    "site_hint": "syufuosusume.com",
    "breakfast_img_bytes": None,
    "lunch_img_bytes": None,
    "dinner_img_bytes": None,
    "body_photo_bytes": None,
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
    sync_common_from_latest_diet_log()

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
st.text_input("お名前（ニックネーム）", key="user_name_input")

if not st.session_state["user_name_input"].strip():
    st.warning("最初にニックネームを入力してください。ご家族や知り合いとは別の名前を入れると、記録が分かれます。")
    st.stop()

reload_user_data_if_needed()

st.caption("※家族や身近な人と試す時は、ニックネームを変えると記録が分かれます。")
st.caption("※現在はお試し版です。食事・運動・生活の参考としてご利用ください。体調不良が強い場合や医療判断が必要な場合は、専門家へご相談ください。")

mode = st.sidebar.radio("機能を選んでください", [
    "今日のおすすめ",
    "ダイエット管理",
    "献立・運動プラン",
    "食事写真評価",
    "なんでも相談",
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
        advice = get_ayurveda_advice_advanced(st.session_state["dosha_type"])
        st.write(f"体質タイプ：**{st.session_state['dosha_type']}**")
        st.write(f"特徴：{advice.get('特徴', '')}")
        st.write(f"食事：{advice.get('食事', '')}")
        st.write(f"過ごし方：{advice.get('生活', '')}")
        st.write(f"運動：{advice.get('運動', '')}")
    else:
        st.info("まだアーユルヴェーダ体質チェックが未実施です。")

    st.divider()
    st.subheader("🧺 保存中の冷蔵庫食材")
    if st.session_state["fridge_items"]:
        st.write(st.session_state["fridge_items"])
    else:
        st.info("まだ冷蔵庫食材の登録がありません。")

    st.subheader("🚫 避けたい食材")
    if st.session_state["avoid_foods"]:
        st.write(st.session_state["avoid_foods"])
    else:
        st.caption("未設定")

    st.subheader("🍙 定番食")
    if st.session_state["favorite_meals"]:
        st.write(st.session_state["favorite_meals"])
    else:
        st.caption("未設定")

    if st.session_state["favorite_protein_onigiri"]:
        st.write(f"おすすめタンパク質おにぎり：{st.session_state['favorite_protein_onigiri']}")
    if st.session_state["favorite_misodama_soup"]:
        st.write(f"味噌玉味噌汁：{st.session_state['favorite_misodama_soup']}")

elif mode == "ダイエット管理":
    sync_settings_on_mode_enter(mode)
    st.session_state["diet_logs"] = load_diet_logs()
    st.header("📝 ダイエット管理")

    gender, age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()
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
            "性別": gender,
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
        sync_common_from_latest_diet_log()
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

    gender, age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()

    st.radio("食事スタイル", ["和食中心", "バランス", "おしゃれカフェ風"], horizontal=True, key="meal_style")
    st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
    st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")
    st.text_area(
        "冷蔵庫の食材（あるものを入力）",
        placeholder="例：卵、豆腐、納豆、鶏むね肉、にんじん、玉ねぎ、キャベツ",
        key="fridge_items"
    )
    st.text_area(
        "食べられないもの・避けたいもの",
        placeholder="例：えび、かに、牡蠣、辛いもの",
        key="avoid_foods"
    )
    st.text_area(
        "わたしの定番・好きな食事",
        placeholder="例：納豆、豆乳、ブルーベリー、タンパク質おにぎり",
        key="favorite_meals"
    )
    st.text_input(
        "おすすめタンパク質おにぎり",
        placeholder="例：鮭枝豆おにぎり",
        key="favorite_protein_onigiri"
    )
    st.text_input(
        "味噌玉味噌汁",
        placeholder="例：わかめ・豆腐・ねぎの味噌玉",
        key="favorite_misodama_soup"
    )
    st.radio("プランタイプ", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
    st.selectbox(
        "平日のお昼スタイル",
        ["指定なし", "お弁当", "コンビニ", "おすすめ定番", "外食", "自宅"],
        key="lunch_style"
    )
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
            st.session_state["avoid_foods"],
            st.session_state["favorite_meals"],
            st.session_state["favorite_protein_onigiri"],
            st.session_state["favorite_misodama_soup"],
            st.session_state["plan_type"],
            st.session_state["lunch_style"],
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
                st.session_state["avoid_foods"],
                st.session_state["favorite_meals"],
                st.session_state["favorite_protein_onigiri"],
                st.session_state["favorite_misodama_soup"],
                st.session_state["plan_type"],
                st.session_state["lunch_style"],
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
    breakfast_upload = st.file_uploader("または朝食写真をアップロード", type=["jpg", "jpeg", "png"], key="breakfast_upload")
    breakfast_source = breakfast_camera if breakfast_camera is not None else breakfast_upload
    breakfast_img = resize_image(breakfast_source, max_size=768) if breakfast_source is not None else None
    if breakfast_img is not None:
        st.image(breakfast_img, use_container_width=True)
        if st.button("🗑 朝食写真を削除"):
            delete_uploaded_state(
                upload_keys=["breakfast_camera", "breakfast_upload"],
                success_message="朝食写真を削除しました。"
            )

    st.divider()

    st.subheader("🍱 昼食")
    lunch_camera = st.camera_input("昼食を撮る", key="lunch_camera")
    lunch_upload = st.file_uploader("または昼食写真をアップロード", type=["jpg", "jpeg", "png"], key="lunch_upload")
    lunch_source = lunch_camera if lunch_camera is not None else lunch_upload
    lunch_img = resize_image(lunch_source, max_size=768) if lunch_source is not None else None
    if lunch_img is not None:
        st.image(lunch_img, use_container_width=True)
        if st.button("🗑 昼食写真を削除"):
            delete_uploaded_state(
                upload_keys=["lunch_camera", "lunch_upload"],
                success_message="昼食写真を削除しました。"
            )

    st.divider()

    st.subheader("🍽 夕食")
    dinner_camera = st.camera_input("夕食を撮る", key="dinner_camera")
    dinner_upload = st.file_uploader("または夕食写真をアップロード", type=["jpg", "jpeg", "png"], key="dinner_upload")
    dinner_source = dinner_camera if dinner_camera is not None else dinner_upload
    dinner_img = resize_image(dinner_source, max_size=768) if dinner_source is not None else None
    if dinner_img is not None:
        st.image(dinner_img, use_container_width=True)
        if st.button("🗑 夕食写真を削除"):
            delete_uploaded_state(
                upload_keys=["dinner_camera", "dinner_upload"],
                success_message="夕食写真を削除しました。"
            )

    st.divider()

    if st.button("📊 1日の食事を評価する"):
        if breakfast_img is None or lunch_img is None or dinner_img is None:
            st.warning("朝・昼・夜の3枚をそろえてください。")
        else:
            client = get_openai_client()
            with st.spinner("1日の食事バランスを分析中..."):
                result = evaluate_meal_day_from_images(client, breakfast_img, lunch_img, dinner_img)

            st.session_state["meal_eval_result"] = result
            st.success("1日の食事評価を作成しました。")
            st.rerun()

    st.text_area("評価結果", key="meal_eval_result", height=320)

    if st.session_state["meal_eval_result"]:
        st.download_button(
            "📥 評価結果をテキスト保存",
            data=st.session_state["meal_eval_result"],
            file_name="meal_day_evaluation.txt",
            mime="text/plain"
        )

elif mode == "なんでも相談":
    st.header("💬 なんでも相談")
    st.caption("食事・運動・外食・今日の困りごとを気軽に相談できます。")

    st.info(
        "ShufuMateは、主婦の毎日に寄り添う参考アプリとして作成中のお試し版です。\n"
        "毎日の食事・運動・暮らしのヒントとしてご活用ください。\n"
        "体調や状況には個人差があるため、無理のない範囲で参考にし、不安が強い場合は専門家へご相談ください。"
    )
    gender, age, height_cm, weight, target_weight, body_fat, target_body_fat = render_common_body_inputs()

    category = st.selectbox(
        "相談カテゴリ",
        ["食事相談", "運動相談", "外食相談", "体調・気分相談", "その他"],
        key="advice_category"
    )

    if category == "外食相談":
        st.text_input(
            "相談エリア",
            placeholder="例：長命ヶ丘、吉成、仙台駅周辺",
            key="advice_area"
        )

    st.text_area(
        "相談内容",
        placeholder="例：おにぎりを1個にした方がいい？\n例：運動前に何を食べたらいい？\n例：運動後、近所でどういう店を選べばいい？",
        key="quick_advice_question",
        height=140
    )

    if st.button("🪄 相談してみる"):
        question = st.session_state["quick_advice_question"].strip()
        area = st.session_state.get("advice_area", "").strip()

        if not question:
            st.warning("相談内容を入力してください。")
        else:
            client = get_openai_client()
            with st.spinner("相談内容を整理しています..."):
                result = ask_shufumate_advice(
                    client=client,
                    question=question,
                    gender=gender,
                    age=age,
                    height_cm=height_cm,
                    weight=weight,
                    body_fat=body_fat,
                    target_weight=target_weight,
                    target_body_fat=target_body_fat,
                    dosha_type=st.session_state["dosha_type"],
                    fridge_items=st.session_state["fridge_items"],
                    avoid_foods=st.session_state["avoid_foods"],
                    favorite_meals=st.session_state["favorite_meals"],
                    favorite_protein_onigiri=st.session_state["favorite_protein_onigiri"],
                    favorite_misodama_soup=st.session_state["favorite_misodama_soup"],
                    daily_flow=st.session_state["daily_flow"],
                    workout_today=st.session_state["workout_today"],
                    body_goal=st.session_state["body_goal"],
                    lunch_style=st.session_state["lunch_style"],
                    category=category,
                    area=area,
                    site_hint=st.session_state.get("site_hint", "syufuosusume.com")
                )
            st.session_state["quick_advice_result"] = result
            st.success("回答を作成しました。")

    st.text_area(
        "相談結果",
        key="quick_advice_result",
        height=220
    )

    st.info("※回答は参考用です。最終判断は、その日の体調・予定・空腹具合に合わせて無理なく調整してください。")

    st.subheader("💡 相談例")
    st.write("・おにぎりを1個にした方がいい？")
    st.write("・運動前に何を食べたらいい？")
    st.write("・運動後、長命ヶ丘でどういう店を選べばいい？")
    st.write("・夕飯前にお腹が空きすぎた時どうする？")

elif mode == "アーユルヴェーダ":
    st.header("🌿 アーユルヴェーダ体質チェック")
    st.write("8項目から体質傾向をチェックします。チェックが多い体質が今の自分に近い目です。")

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
        "安定していて食べるのが好き"
    ], key="ay_q6")

    q7 = st.radio("排便", [
        "便秘気味・硬便",
        "下痢気味・軟便",
        "中程度の硬さ・時間を要する"
    ], key="ay_q7")

    q8 = st.radio("睡眠", [
        "眠りが浅い・途中で起きやすい",
        "普通",
        "よく眠る・居眠りが多い"
    ], key="ay_q8")

    st.subheader("🍫 今の状態チェック")
    sweet_craving = st.checkbox("甘いものが無性に食べたい", key="state_sweet")
    salty_craving = st.checkbox("しょっぱいものが欲しい", key="state_salty")
    fatigue = st.checkbox("ずっとだるい・疲れやすい", key="state_fatigue")
    irritable = st.checkbox("イライラしやすい", key="state_irritable")
    sleepy_after_meal = st.checkbox("食後すぐ眠くなる", key="state_sleepy")
    swelling = st.checkbox("むくみやすい", key="state_swelling")
    coldness = st.checkbox("冷えやすい", key="state_cold")
    constipation_now = st.checkbox("最近便秘ぎみ", key="state_constipation")
    dry_skin = st.checkbox("肌や口が乾燥しやすい", key="state_dry")

    if st.button("🌿 体質をチェック"):
        answers = {
            "体型": q1,
            "肌": q2,
            "髪": q3,
            "発汗": q4,
            "体温": q5,
            "食欲": q6,
            "排便": q7,
            "睡眠": q8,
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

    if st.button("🪷 今の状態をみる"):
        current_state_text = get_current_state_advice(
            sweet_craving,
            salty_craving,
            fatigue,
            irritable,
            sleepy_after_meal,
            swelling,
            coldness,
            constipation_now,
            dry_skin
        )
        st.subheader("📝 今の乱れチェック")
        st.write(current_state_text)

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

                if st.button(f"🗑 この画像を削除 {i+1}", key=f"delete_fridge_{i}", use_container_width=True):
                    st.session_state["fridge_scan_images"].pop(i)
                    st.rerun()

            if st.button("🥬 スキャン画像から食材抽出"):
                client = get_openai_client()
                with st.spinner("AIが食材を読み取り中..."):
                    result = extract_foods_from_images(client, st.session_state["fridge_scan_images"])

                st.session_state["photo_fridge_items"] = result
                st.success("食材候補を抽出しました。")
                st.rerun()

                st.text_area("読み取った食材候補", key="photo_fridge_items", height=180)

        if st.button("🧹 読み取り結果をクリア", use_container_width=True):
            st.session_state["photo_fridge_items"] = ""
            st.rerun()

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

            if st.button("🗑 体重計写真を削除"):
                delete_uploaded_state(
                    upload_keys=["scale_photo_upload"],
                    success_message="体重計写真を削除しました。"
                )

                st.text_area(
            "読み取った数値候補メモ",
            placeholder="例：体重: 51.2\n体脂肪率: 25.6\n骨格筋率: 27.2",
            key="photo_scale_result",
            height=220
        )

        if st.button("🧹 数値候補をクリア", use_container_width=True):
            st.session_state["photo_scale_result"] = ""
            st.rerun()

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

        if st.button("🧹 数値候補をクリア", use_container_width=True):
            st.session_state["photo_scale_result"] = ""
            st.rerun()

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
    uploaded_body = st.file_uploader("または全身写真をアップロード", type=["jpg", "jpeg", "png"], key="body_photo_upload")

    source_body = body_camera if body_camera is not None else uploaded_body

    if source_body is not None:
        resized_body = resize_image(source_body, max_size=768)
        st.image(resized_body, caption="全身スキャン画像", use_container_width=True)

        if st.button("🗑 全身写真を削除"):
            delete_uploaded_state(
                upload_keys=["body_camera_scan", "body_photo_upload"],
                success_message="全身写真を削除しました。"
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🪄 体型コメントを自動生成"):
                client = get_openai_client()
                with st.spinner("体型バランスを分析中..."):
                    result = generate_body_balance_comment(client, resized_body, st.session_state["body_goal_scan"])
                st.session_state["body_scan_comment"] = result
                st.success("体型コメントを生成しました。")
                st.rerun()

        with col2:
            if st.button("✨ 理想イメージ用プロンプトを作成"):
                client = get_openai_client()
                source_comment = st.session_state["body_scan_comment"] or "まだ体型コメントなし"
                with st.spinner("理想イメージを整理中..."):
                    result = generate_ideal_body_prompt(client, source_comment, st.session_state["body_goal_scan"])
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

    st.text_area("体型バランスコメント", key="body_scan_comment", height=240)
    st.text_area("理想イメージ用プロンプト", key="ideal_body_prompt_result", height=240)

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
    st.header("🗓 スケジュール管理")

    today = datetime.today()
    col_y, col_m = st.columns(2)
    with col_y:
        view_year = st.number_input("年", min_value=2024, max_value=2100, value=today.year, step=1)
    with col_m:
        view_month = st.selectbox("月", list(range(1, 13)), index=today.month - 1)

    st.subheader(f"📅 {view_year}年 {view_month}月カレンダー")

    week_labels = ["日", "月", "火", "水", "木", "金", "土"]
    cols = st.columns(7)
    for i, label in enumerate(week_labels):
        cols[i].markdown(f"**{label}**")

    month_matrix = build_month_calendar(view_year, view_month)

    for week in month_matrix:
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                week_cols[i].write("")
            else:
                date_str = f"{view_year}-{view_month:02d}-{day:02d}"

                day_events = [
                    s for s in st.session_state["schedules"]
                    if s.get("日付") == date_str
                ]

                label = str(day)
                if day_events:
                    label += f" ✅{len(day_events)}"

                if week_cols[i].button(label, key=f"cal_{date_str}"):
                    st.session_state["selected_schedule_date"] = date_str

    selected_date = st.session_state.get("selected_schedule_date", "")
    if not selected_date:
        selected_date = today.strftime("%Y-%m-%d")

    st.divider()
    st.subheader("⏰ 生活リズム目安")

    st.text_input(
        "起きる時間（HH:MM）",
        key="wake_time_str"
    )

    recommended = get_recommended_daily_schedule(st.session_state["wake_time_str"])

    r1, r2, r3 = st.columns(3)
    r1.metric("起床", recommended["起床"])
    r2.metric("朝食", recommended["朝食"])
    r3.metric("昼食", recommended["昼食"])

    r4, r5, r6 = st.columns(3)
    r4.metric("夕食", recommended["夕食"])
    r5.metric("入浴", recommended["入浴"])
    r6.metric("就寝", recommended["就寝"])

    st.caption("※目安として、睡眠7時間以上・就寝1時間前までの入浴を意識します。")

    st.subheader("🕒 24時間タイムライン")

    timeline_df = build_daily_timeline_df(recommended)

    if not timeline_df.empty:
        st.dataframe(
            timeline_df[["項目", "時間"]],
            use_container_width=True,
            hide_index=True
        )

    render_daily_timeline_html(recommended)

    st.caption("※0〜24時の中で、起床・食事・入浴・就寝の目安時間を1日の流れとして見える化しています。")
    st.divider()
    st.subheader("➕ 選択日の予定を追加")
    st.write(f"選択中の日付: **{selected_date}**")

    with st.form("schedule_form"):
        event_type = st.selectbox(
            "種類",
            ["起床", "朝食", "昼食", "夕食", "入浴", "就寝", "運動", "買い物", "献立準備", "学校", "通院", "その他"]
        )
        event_time = st.text_input("時間（例 07:00）", "")
        event = st.text_input("予定内容")
        s_submitted = st.form_submit_button("追加する")

    if s_submitted:
        st.session_state["schedules"].append({
            "日付": selected_date,
            "種類": event_type,
            "時間": event_time,
            "内容": event
        })
        st.success("予定を登録しました。")
        st.rerun()

    st.divider()
    st.subheader("📋 選択日の予定一覧")

    selected_events = [
        s for s in st.session_state["schedules"]
        if s.get("日付") == selected_date
    ]

    if selected_events:
        df_sched = pd.DataFrame(selected_events)

        if "時間" in df_sched.columns:
            df_sched = df_sched.sort_values(by=["時間", "種類"], na_position="last")

        st.dataframe(df_sched, use_container_width=True)
    else:
        st.info("この日の予定はまだありません。")

    st.divider()
    st.subheader("🛏 睡眠・入浴チェック")

    sleep_time = recommended["就寝"]
    bath_time = recommended["入浴"]
    st.write(f"理想の目安：**入浴 {bath_time} → 就寝 {sleep_time}**")
    st.write("睡眠は **7時間以上確保** を目標にしましょう。")

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
    st.selectbox("性別（任意）", ["未選択", "女性", "男性", "その他", "回答しない"], key="common_gender")
    st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    st.number_input("スタート時の体重（kg）", min_value=39.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    st.number_input("目標体重（kg）", min_value=39.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
    st.number_input("スタート時の体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")

    st.subheader("🍽 献立の初期値")
    st.radio("食事スタイル", ["和食中心", "バランス", "おしゃれカフェ風"], horizontal=True, key="meal_style")
    st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
    st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")
    st.text_area("よくある冷蔵庫の食材", key="fridge_items")

    st.text_area(
        "食べられないもの・避けたいもの",
        key="avoid_foods",
        placeholder="例：えび、かに、牡蠣、辛いもの、牛乳 など"
    )

    st.text_area(
        "わたしの定番・好きな食事",
        key="favorite_meals",
        placeholder="例：納豆、豆乳、ブルーベリー、タンパク質おにぎり"
    )

    st.text_input(
        "おすすめタンパク質おにぎり",
        key="favorite_protein_onigiri",
        placeholder="例：鮭枝豆おにぎり"
    )

    st.text_input(
        "味噌玉味噌汁",
        key="favorite_misodama_soup",
        placeholder="例：わかめ・豆腐・ねぎの味噌玉"
    )

    st.radio("プランタイプ初期値", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
    st.selectbox("平日のお昼スタイル", ["指定なし", "お弁当", "コンビニ", "おすすめ定番", "外食", "自宅"], key="lunch_style")
    st.checkbox("主婦リアル提案モード初期値", key="real_mode")
    st.selectbox("食事の流れ初期値", ["普通", "朝しっかり・昼軽め", "食べすぎた", "あまり食べてない"], key="daily_flow")
    st.checkbox("運動あり初期値", key="workout_today")
    st.selectbox("目的初期値", ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"], key="body_goal")

    st.subheader("🪞 理想イメージの作り方")
    st.caption("年齢に寄せすぎず、若々しく上品で美しい雰囲気を優先したい場合の設定です。")

    st.checkbox("理想イメージは若々しく美しく生成する", key="ideal_image_youthful")
    st.checkbox("年齢感を強く出しすぎない", key="ideal_image_soft_age")
    st.checkbox("上品で清潔感のある雰囲気を優先する", key="ideal_image_elegant")
    st.checkbox("本人の雰囲気を少し残したい", key="ideal_image_keep_mood")

    st.text_area(
        "理想イメージでなりたい雰囲気",
        key="ideal_image_style_note",
        placeholder="例：若々しい、透明感、姿勢がよい、すっきりした印象、上品できれい"
    )

    st.subheader("📷 写真機能について")
    st.caption("今後追加したい機能メモとして保存用に使えます。")

    st.checkbox("ズーム機能がほしい", key="need_photo_zoom")
    st.checkbox("トリミング機能がほしい", key="need_photo_crop")
    st.checkbox("顔が映った時に上だけ切り取りたい", key="need_face_cut")
    st.checkbox("明るさなどの簡易編集がほしい", key="need_photo_edit")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("💾 初期設定を保存", use_container_width=True):
            save_user_settings()
            st.success("初期設定を保存しました。")

    with c2:
        if st.button("↺ 初期設定をリセット", use_container_width=True):
            reset_user_settings()
            save_user_settings()
            st.success("初期設定をリセットしました。")
            st.rerun()
