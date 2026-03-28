import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials

# --- 設定 ---
st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")
USER_ID = "nao513"

# --- Google Sheets 連携関連 ---
@st.cache_resource
def get_gspread_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google認証エラー: {e}")
        st.stop()

def get_sheet(tab_name: str):
    gc = get_gspread_client()
    sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
    return sh.worksheet(tab_name)

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# --- データ読み書き ---
def load_user_settings():
    try:
        ws = get_sheet("Settings")
        values = ws.get_all_values()
        if len(values) < 2: return None
        header = values[0]
        for row in values[1:]:
            row_dict = dict(zip(header, row))
            if row_dict.get("user_id") == USER_ID:
                return {
                    "common_age": int(safe_float(row_dict.get("age", 49))),
                    "common_height": safe_float(row_dict.get("height_cm", 160.0)),
                    "common_weight": safe_float(row_dict.get("start_weight", 55.0)),
                    "common_target_weight": safe_float(row_dict.get("target_weight", 50.0)),
                    "common_body_fat": safe_float(row_dict.get("start_body_fat", 25.0)),
                    "common_target_body_fat": safe_float(row_dict.get("target_body_fat", 20.0)),
                }
    except: return None
    return None

def save_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    # セッションから最新値を取得
    data = [
        USER_ID, st.session_state.common_age, st.session_state.common_height,
        st.session_state.common_weight, st.session_state.common_target_weight,
        st.session_state.common_body_fat, st.session_state.common_target_body_fat
    ]
    row_idx = next((i for i, r in enumerate(values) if r and r[0] == USER_ID), None)
    if row_idx:
        ws.update(values=[data], range_name=f"A{row_idx+1}:G{row_idx+1}")
    else:
        ws.append_row(data)

# --- セッションステート初期化 (重要: ウィジェット表示前に実行) ---
if "initialized" not in st.session_state:
    # 1. デフォルト値のセット
    st.session_state.common_age = 49
    st.session_state.common_height = 160.0
    st.session_state.common_weight = 55.0
    st.session_state.common_target_weight = 50.0
    st.session_state.common_body_fat = 25.0
    st.session_state.common_target_body_fat = 20.0
    st.session_state.dosha_type = ""
    
    # 2. クラウドからデータがあれば上書き
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v
    st.session_state.initialized = True

# --- メインロジック ---
st.title("🍀 ShufuMate｜主婦の味方アプリ")
mode = st.sidebar.radio("メニュー", ["今日のおすすめ", "ダイエット管理", "設定"])

if mode == "今日のおすすめ":
    st.header("🏠 今日のおすすめ")
    st.metric("現在の体重", f"{st.session_state.common_weight} kg")
    if st.session_state.dosha_type:
        st.info(f"あなたの体質: {st.session_state.dosha_type}")

elif mode == "ダイエット管理":
    st.header("📝 ダイエット記録")
    # keyを指定することで st.session_state.common_age 等と連動
    st.number_input("年齢", key="common_age")
    st.number_input("身長 (cm)", key="common_height")
    st.number_input("体重 (kg)", key="common_weight")
    st.number_input("体脂肪率 (%)", key="common_body_fat")
    
    if st.button("現在の状態を保存"):
        save_user_settings()
        st.success("クラウドへ保存しました！")

elif mode == "設定":
    st.header("⚙️ 設定")
    st.subheader("目標設定")
    st.number_input("目標体重 (kg)", key="common_target_weight")
    st.number_input("目標体脂肪率 (%)", key="common_target_body_fat")
    
    if st.button("設定をクラウドに同期"):
        save_user_settings()
        st.success("同期完了")
