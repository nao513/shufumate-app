import base64
import io
import re
import calendar
import os
import tempfile
import cv2
import hashlib
from datetime import datetime, timedelta

import gspread
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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

defaults = {
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

@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"gspread接続エラー: {e}")
        raise


@st.cache_resource
def get_spreadsheet():
    try:
        gc = get_gspread_client()
        sheet_id = str(st.secrets["GOOGLE_SHEET_ID"]).strip()
        return gc.open_by_key(sheet_id)
    except Exception as e:
        st.error(f"スプレッドシート接続エラー: {e}")
        raise

def get_sheet(tab_name: str):
    sh = get_spreadsheet()
    return sh.worksheet(tab_name)


def get_or_create_worksheet(sh, title, rows=1000, cols=30):
    try:
        return sh.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)
    except Exception as e:
        st.error(f"ワークシート取得エラー（{title}）: {e}")
        raise

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

def load_advice_logs():
    ws = get_sheet("AdviceLogs")
    values = ws.get_all_values()
    current_user_id = get_current_user_id()

    if len(values) < 2:
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
def get_openai_client():
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("Streamlit Secrets に OPENAI_API_KEY が設定されていません。")
        st.stop()

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

