import base64
import io
import re
import os
import tempfile
import cv2
import hashlib
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from openai import OpenAI
from PIL import Image
from google.oauth2.service_account import Credentials

UI_TEXT = {
    "update": "更新する",
    "save": "保存する",
    "delete": "削除",
    "upload": "写真を追加",
    "settings": "設定",
    "notice": "お知らせ",
}

# -----------------------------
# Session defaults
# -----------------------------
defaults = {
    "user_name_input": "",

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

    "home_prefecture": "",
    "home_area": "",
    "home_area_custom": "",

    "dosha_type": "",

    "diet_logs": [],
    "today_plan_date": "",
    "today_plan_text": "",

    "fridge_scan_images": [],
    "photo_fridge_items": "",
    "processed_fridge_upload_hashes": [],
    "fridge_photo_uploader_version": 0,

    "scale_scan_images": [],
    "selected_scale_index": 0,
    "photo_scale_result": "",
    "processed_scale_upload_hashes": [],
    "scale_photo_uploader_version": 0,
    "scale_video_uploader_version": 0,

    "receipt_result": "",
    "receipt_store": "",
    "receipt_date_text": "",
    "receipt_date_value": None,
    "receipt_amount": 0,
    "receipt_memo": "",
    "receipt_scan_images": [],
    "selected_receipt_index": 0,

    "expenses": [],
    "schedules": [],

    "body_check_comment": "",
    "body_scan_comment": "",
    "body_goal_scan": "バランス",
    "ideal_body_prompt_result": "",
    "ideal_body_image_bytes": None,
    "body_crop_top_percent": 15,
    "use_cropped_body": True,
    "ideal_face_mode": "顔は反映しない",
    "ideal_image_from_photo_result": "",

    "quick_advice_question": "",
    "quick_advice_result": "",
    "advice_category": "食事相談",
    "advice_area": "",
    "advice_logs": [],
    "site_hint": "syufuosusume.com",

    "meal_eval_result": "",

    "settings_snapshot": {},
    "last_loaded_user_id": "",
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


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
    sheet_id = str(st.secrets["GOOGLE_SHEET_ID"]).strip()
    return gc.open_by_key(sheet_id)


@st.cache_resource
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


@st.cache_resource
def ensure_headers():
    sh = get_spreadsheet()

    settings_ws = get_or_create_worksheet(sh, "Settings")
    diet_ws = get_or_create_worksheet(sh, "DietLogs")
    plans_ws = get_or_create_worksheet(sh, "TodayPlans")
    expenses_ws = get_or_create_worksheet(sh, "Expenses")
    advice_ws = get_or_create_worksheet(sh, "AdviceLogs")

    settings_header = [
        "user_id", "gender", "age", "height_cm", "start_weight",
        "target_weight", "start_body_fat", "target_body_fat",
        "meal_style", "ease_level", "staple_preference",
        "fridge_items", "avoid_foods", "favorite_meals",
        "favorite_protein_onigiri", "favorite_misodama_soup",
        "plan_type", "lunch_style",
        "real_mode", "daily_flow", "workout_today", "body_goal",
        "home_prefecture", "home_area"
    ]
    diet_header = [
        "user_id", "date", "gender", "age", "height_cm", "weight",
        "target_weight", "body_fat", "target_body_fat",
        "bmi", "goal_calories"
    ]
    plan_header = ["user_id", "date", "plan_text"]
    expenses_header = ["user_id", "date", "category", "store_name", "amount", "memo"]
    advice_header = ["user_id", "datetime", "category", "area", "question", "answer"]

    rewrite_sheet_with_header(settings_ws, settings_header)
    rewrite_sheet_with_header(diet_ws, diet_header)
    rewrite_sheet_with_header(plans_ws, plan_header)
    rewrite_sheet_with_header(expenses_ws, expenses_header)
    rewrite_sheet_with_header(advice_ws, advice_header)


def get_current_user_id():
    return st.session_state.get("user_name_input", "").strip()


def load_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2 or not current_user_id:
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
                "plan_type": row_dict.get("plan_type", "通常") or "通常",
                "lunch_style": row_dict.get("lunch_style", "指定なし") or "指定なし",
                "real_mode": str(row_dict.get("real_mode", "True")).lower() == "true",
                "daily_flow": row_dict.get("daily_flow", "普通") or "普通",
                "workout_today": str(row_dict.get("workout_today", "False")).lower() == "true",
                "body_goal": row_dict.get("body_goal", "バランス") or "バランス",
                "home_prefecture": row_dict.get("home_prefecture", "") or "",
                "home_area": row_dict.get("home_area", "") or "",
                "home_area_custom": "",
            }

    return None


def load_settings_into_session():
    saved = load_user_settings()
    if not saved:
        return
    for k, v in saved.items():
        st.session_state[k] = v


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
        st.session_state.get("home_prefecture", ""),
        st.session_state.get("home_area_custom", "").strip() or st.session_state.get("home_area", ""),
    ]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == current_user_id:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:X{row_index}", [row_values])
    else:
        ws.append_row(row_values)


def reset_user_settings():
    for k, v in defaults.items():
        if k in st.session_state:
            st.session_state[k] = v


def load_diet_logs():
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2 or not current_user_id:
        return []

    header = values[0]
    data_rows = values[1:]
    logs = []

    for row in data_rows:
        if not row:
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))

        if row_dict.get("user_id") == current_user_id:
            logs.append({
                "日付": row_dict.get("date", ""),
                "性別": row_dict.get("gender", "未選択"),
                "年齢": float(row_dict["age"]) if row_dict.get("age") else 0,
                "身長(cm)": float(row_dict["height_cm"]) if row_dict.get("height_cm") else 0,
                "体重(kg)": float(row_dict["weight"]) if row_dict.get("weight") else 0,
                "目標体重(kg)": float(row_dict["target_weight"]) if row_dict.get("target_weight") else 0,
                "体脂肪率(%)": float(row_dict["body_fat"]) if row_dict.get("body_fat") else 0,
                "目標体脂肪率(%)": float(row_dict["target_body_fat"]) if row_dict.get("target_body_fat") else 0,
                "BMI": float(row_dict["bmi"]) if row_dict.get("bmi") else 0,
                "目標摂取カロリー": float(row_dict["goal_calories"]) if row_dict.get("goal_calories") else 0,
            })

    return logs


def sync_common_from_latest_diet_log():
    logs = st.session_state.get("diet_logs", [])
    if not logs:
        return

    latest = logs[-1]
    if latest.get("性別") not in [None, ""]:
        st.session_state["common_gender"] = latest["性別"]
    if latest.get("年齢") not in [None, ""]:
        st.session_state["common_age"] = int(float(latest["年齢"]))
    if latest.get("身長(cm)") not in [None, ""]:
        st.session_state["common_height"] = float(latest["身長(cm)"])
    if latest.get("体重(kg)") not in [None, ""]:
        st.session_state["common_weight"] = float(latest["体重(kg)"])
    if latest.get("目標体重(kg)") not in [None, ""]:
        st.session_state["common_target_weight"] = float(latest["目標体重(kg)"])
    if latest.get("体脂肪率(%)") not in [None, ""]:
        st.session_state["common_body_fat"] = float(latest["体脂肪率(%)"])
    if latest.get("目標体脂肪率(%)") not in [None, ""]:
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


def load_expenses():
    ws = get_sheet("Expenses")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2 or not current_user_id:
        return []

    header = values[0]
    data_rows = values[1:]
    expenses = []

    for idx, row in enumerate(data_rows, start=2):
        if not row:
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))

        if row_dict.get("user_id") == current_user_id:
            expenses.append({
                "_sheet_row": idx,
                "日付": row_dict.get("date", ""),
                "カテゴリ": row_dict.get("category", ""),
                "店名": row_dict.get("store_name", ""),
                "金額": int(float(row_dict["amount"])) if row_dict.get("amount") else 0,
                "メモ": row_dict.get("memo", ""),
            })

    return expenses


def append_expense(expense_dict):
    ws = get_sheet("Expenses")
    current_user_id = get_current_user_id()

    row_values = [
        current_user_id,
        expense_dict["日付"],
        expense_dict["カテゴリ"],
        expense_dict["店名"],
        expense_dict["金額"],
        expense_dict["メモ"],
    ]
    ws.append_row(row_values)


def delete_expense(sheet_row: int):
    ws = get_sheet("Expenses")
    ws.delete_rows(sheet_row)


def load_advice_logs():
    ws = get_sheet("AdviceLogs")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2 or not current_user_id:
        return []

    header = values[0]
    data_rows = values[1:]
    logs = []

    for row in data_rows:
        if not row:
            continue

        row = row + [""] * (len(header) - len(row))
        row_dict = dict(zip(header, row))

        if row_dict.get("user_id") == current_user_id:
            logs.append({
                "日時": row_dict.get("datetime", ""),
                "カテゴリ": row_dict.get("category", ""),
                "地域": row_dict.get("area", ""),
                "相談内容": row_dict.get("question", ""),
                "回答": row_dict.get("answer", ""),
            })

    logs.sort(key=lambda x: x["日時"], reverse=True)
    return logs


def append_advice_log(category, area, question, answer):
    ws = get_sheet("AdviceLogs")
    current_user_id = get_current_user_id()

    row_values = [
        current_user_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        category,
        area,
        question,
        answer,
    ]
    ws.append_row(row_values)


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
        st.session_state["expenses"] = load_expenses()
        st.session_state["advice_logs"] = load_advice_logs()
        sync_common_from_latest_diet_log()
        st.session_state["last_loaded_user_id"] = current_user_id


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
    image = Image.open(file).convert("RGB")
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


def uploaded_file_signature(uploaded_file):
    data = uploaded_file.getvalue()
    return hashlib.md5(data).hexdigest()


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


def extract_scale_values_from_images(client, images):
    content = [{
        "type": "input_text",
        "text": """
これらは体組成計または体重計の複数画像です。
複数枚を見比べて、読み取りやすい数値を日本語で整理してください。

ルール:
- 複数枚のうち、最も読み取りやすい情報を優先する
- 同じ項目が複数画像で一致する場合は、その値を優先する
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


def extract_receipt_info(client, resized_image):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": """
この画像はレシートです。
家計簿に使いやすいように、日本語で整理してください。

ルール:
- 読み取れた内容だけを書く
- 推測しすぎない
- 合計金額が分かれば最優先で書く
- 店名、日付、合計金額、主な購入内容を整理する
- 購入内容は3～10件くらいまででよい
- 最後に家計簿登録しやすいように短くまとめる

出力形式:
■店名:
■日付:
■合計金額:
■主な購入内容:
- 〇〇
- 〇〇
- 〇〇
■家計簿メモ:
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


def parse_receipt_result(text: str):
    result = {
        "store": "",
        "date": "",
        "amount": 0,
        "memo": "",
    }

    store_match = re.search(r"■店名[:：]\s*(.*)", text)
    date_match = re.search(r"■日付[:：]\s*(.*)", text)
    amount_match = re.search(r"■合計金額[:：]\s*([0-9,]+)", text)
    memo_match = re.search(r"■家計簿メモ[:：]\s*(.*)", text)

    if store_match:
        result["store"] = store_match.group(1).strip()
    if date_match:
        result["date"] = date_match.group(1).strip()
    if amount_match:
        result["amount"] = int(amount_match.group(1).replace(",", "").strip())
    if memo_match:
        result["memo"] = memo_match.group(1).strip()

    return result


def parse_receipt_date_to_dateobj(date_text: str):
    if not date_text:
        return None

    text = str(date_text).strip()

    patterns = [
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            try:
                y, mth, d = map(int, m.groups())
                return datetime(y, mth, d).date()
            except Exception:
                return None

    return None


def extract_frames_from_video(uploaded_video, interval_sec=3.0, max_frames=8, max_size=768):
    frames = []

    suffix = ".mp4"
    if hasattr(uploaded_video, "name") and "." in uploaded_video.name:
        suffix = os.path.splitext(uploaded_video.name)[1] or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_video.getbuffer())
        temp_path = tmp.name

    try:
        cap = cv2.VideoCapture(temp_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 30

        frame_interval = max(1, int(fps * interval_sec))
        frame_count = 0
        saved_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb).convert("RGB")

                w, h = image.size
                if max(w, h) > max_size:
                    ratio = max_size / max(w, h)
                    image = image.resize((int(w * ratio), int(h * ratio)))

                buffer = io.BytesIO()
                image.save(buffer, format="JPEG", quality=85)
                buffer.seek(0)
                frames.append(buffer)

                saved_count += 1
                if saved_count >= max_frames:
                    break

            frame_count += 1

        cap.release()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return frames


def parse_scale_values(text: str):
    text = text or ""

    weight_match = re.search(r"体重\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?)", text)
    body_fat_match = re.search(r"体脂肪率?\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?)", text)

    return {
        "weight": float(weight_match.group(1)) if weight_match else None,
        "body_fat": float(body_fat_match.group(1)) if body_fat_match else None,
    }


def save_today_log_from_scale_result():
    parsed = parse_scale_values(st.session_state.get("photo_scale_result", ""))
    weight = parsed["weight"]
    body_fat = parsed["body_fat"]

    if weight is None and body_fat is None:
        return False, "保存できる数値が見つかりませんでした。"

    gender = st.session_state.get("common_gender", "未選択")
    age = st.session_state.get("common_age", 40)
    height_cm = st.session_state.get("common_height", 160.0)
    target_weight = st.session_state.get("common_target_weight", 48.0)
    target_body_fat = st.session_state.get("common_target_body_fat", 24.0)

    current_weight = weight if weight is not None else st.session_state.get("common_weight", 50.0)
    current_body_fat = body_fat if body_fat is not None else st.session_state.get("common_body_fat", 28.0)

    st.session_state["common_weight"] = current_weight
    st.session_state["common_body_fat"] = current_body_fat

    bmi = current_weight / ((height_cm / 100) ** 2)
    bmr = current_weight * 22 * 1.5
    goal_calories = round(bmr, 0)

    log = {
        "日付": datetime.today().strftime("%Y-%m-%d"),
        "性別": gender,
        "年齢": age,
        "身長(cm)": height_cm,
        "体重(kg)": current_weight,
        "目標体重(kg)": target_weight,
        "体脂肪率(%)": current_body_fat,
        "目標体脂肪率(%)": target_body_fat,
        "BMI": round(bmi, 1),
        "目標摂取カロリー": goal_calories,
    }

    upsert_diet_log(log)
    st.session_state["diet_logs"] = load_diet_logs()
    sync_common_from_latest_diet_log()

    return True, "読み取った数値で今日の記録を保存しました。"


# -----------------------------
# Advice
# -----------------------------
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
    dosha_type="",
    fridge_items="",
    avoid_foods="",
    favorite_meals="",
    favorite_protein_onigiri="",
    favorite_misodama_soup="",
    daily_flow="普通",
    workout_today=False,
    body_goal="バランス",
    lunch_style="指定なし",
    category="食事相談",
    area="",
    site_hint="syufuosusume.com"
):
    prompt = f"""
あなたは主婦向けのやさしい生活アドバイザーです。
食事・運動・外食・日常の困りごとに、日本語でわかりやすく答えてください。

【利用者情報】
- 性別: {gender}
- 年齢: {age}
- 身長: {height_cm}
- 体重: {weight}
- 体脂肪率: {body_fat}
- 目標体重: {target_weight}
- 目標体脂肪率: {target_body_fat}
- 体質: {dosha_type if dosha_type else "未設定"}
- 冷蔵庫の食材: {fridge_items}
- 避けたい食べ物: {avoid_foods}
- 定番・好きな食事: {favorite_meals}
- 食事の流れ: {daily_flow}
- 運動: {"あり" if workout_today else "なし"}
- 目的: {body_goal}
- 昼食スタイル: {lunch_style}
- 相談カテゴリ: {category}
- 相談エリア: {area if area else "未指定"}

【回答ルール】
- 主婦目線でやさしく、実用的に答える
- 難しすぎる言い方はしない
- すぐできる提案を優先する
- 外食相談なら、地域があればその地域で探す前提のアドバイスにする
- 必要なら選び方の基準も入れる
- 最後にひとことで背中を押す
- {site_hint} に合いそうな、暮らしに役立つ雰囲気で答える

【相談内容】
{question}

【出力形式】
■答え
■理由
■おすすめ行動
■ひとこと
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text
