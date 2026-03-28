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
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google認証に失敗しました。Secretsを確認してください: {e}")
        st.stop()

def get_sheet(tab_name: str):
    gc = get_gspread_client()
    try:
        sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
        return sh.worksheet(tab_name)
    except Exception as e:
        st.error(f"スプレッドシートの取得に失敗しました: {e}")
        st.stop()

def ensure_headers():
    """アプリ起動時に一度だけヘッダーをチェックし、API制限を回避する"""
    tabs = {
        "Settings": ["user_id", "age", "height_cm", "start_weight", "target_weight", "start_body_fat", "target_body_fat"],
        "DietLogs": ["user_id", "date", "age", "height_cm", "weight", "target_weight", "body_fat", "target_body_fat", "bmi", "goal_calories"],
        "TodayPlans": ["user_id", "date", "plan_text"]
    }
    
    for tab_name, header in tabs.items():
        ws = get_sheet(tab_name)
        values = ws.get_all_values()
        if not values or values[0] != header:
            ws.clear()
            ws.append_row(header)

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def load_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    if len(values) < 2:
        return None

    header = values[0]
    for row in values[1:]:
        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == USER_ID:
            return {
                "common_age": int(safe_float(row_dict.get("age", 40))),
                "common_height": safe_float(row_dict.get("height_cm", 160.0)),
                "common_weight": safe_float(row_dict.get("start_weight", 50.0)),
                "common_target_weight": safe_float(row_dict.get("target_weight", 45.0)),
                "common_body_fat": safe_float(row_dict.get("start_body_fat", 20.0)),
                "common_target_body_fat": safe_float(row_dict.get("target_body_fat", 18.0)),
            }
    return None

def save_user_settings():
    ws = get_sheet("Settings")
    values = ws.get_all_values()
    
    values_to_save = [
        USER_ID,
        st.session_state["common_age"],
        st.session_state["common_height"],
        st.session_state["common_weight"],
        st.session_state["common_target_weight"],
        st.session_state["common_body_fat"],
        st.session_state["common_target_body_fat"],
    ]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if row and row[0] == USER_ID:
            row_index = i
            break

    if row_index:
        # 最新のgspread(v6+)に対応した記述
        ws.update(values=[values_to_save], range_name=f"A{row_index}:G{row_index}")
    else:
        ws.append_row(values_to_save)

def upsert_diet_log(log_dict):
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2 and row[0] == USER_ID and row[1] == log_dict["日付"]:
            row_index = i
            break

    row_values = [
        USER_ID, log_dict["日付"], log_dict["年齢"], log_dict["身長(cm)"],
        log_dict["体重(kg)"], log_dict["目標体重(kg)"], log_dict["体脂肪率(%)"],
        log_dict["目標体脂肪率(%)"], log_dict["BMI"], log_dict["目標摂取カロリー"],
    ]

    if row_index:
        ws.update(values=[row_values], range_name=f"A{row_index}:J{row_index}")
    else:
        ws.append_row(row_values)

# --- セッションステート初期化 ---
defaults = {
    "common_age": 49,
    "common_height": 160.0,
    "common_weight": 55.0,
    "common_target_weight": 50.0,
    "common_body_fat": 25.0,
    "common_target_body_fat": 20.0,
    "diet_logs": [],
    "today_plan_text": "",
    "today_plan_date": "",
    "expenses": [],
    "schedules": [],
    "dosha_type": "",
    "dosha_scores": {"ヴァータ": 0, "ピッタ": 0, "カパ": 0}
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "settings_loaded" not in st.session_state:
    ensure_headers() # 初回のみ実行
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v
    st.session_state["settings_loaded"] = True

# --- ロジック関数 (診断・AI連携) ---
def get_ayurveda_advice(dosha):
    advice_map = {
        "ヴァータ": {"特徴": "冷え・乾燥・疲れやすい", "食事": "温かいスープ、根菜", "生活": "規則正しい睡眠、保温", "運動": "ヨガ、ストレッチ"},
        "ピッタ": {"特徴": "暑がり・イライラ・食欲旺盛", "食事": "生野菜、豆類、マイルドな味", "生活": "クールダウン、余裕を持つ", "運動": "ウォーキング、水泳"},
        "カパ": {"特徴": "むむくみ・重だるい・溜め込み", "食事": "温野菜、スパイス、低脂質", "生活": "早起き、活動的に動く", "運動": "ジョギング、有酸素運動"}
    }
    return advice_map.get(dosha, {})

def create_plan_for_date(client, date_str, age, height, weight, b_fat, t_weight, t_fat, dosha=""):
    prompt = f"年齢:{age},身長:{height},体重:{weight},体脂肪:{b_fat},目標:{t_weight}({t_fat}%),体質:{dosha}に基づき、{date_str}の献立・運動・買い物リストを作成してください。"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "管理栄養士として回答してください。"},{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

# --- UI (サイドバー & メイン) ---
mode = st.sidebar.radio("メニュー", ["今日のおすすめ", "ダイエット管理", "献立・運動プラン", "アーユルヴェーダ", "家計簿", "設定"])

if mode == "今日のおすすめ":
    st.header("🏠 今日のおすすめ")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 現在の状態")
        st.write(f"体重: {st.session_state.common_weight}kg / BMI: {round(st.session_state.common_weight/((st.session_state.common_height/100)**2),1)}")
    with c2:
        st.subheader("🌿 体質アドバイス")
        if st.session_state.dosha_type:
            adv = get_ayurveda_advice(st.session_state.dosha_type)
            st.info(f"タイプ: {st.session_state.dosha_type}\n\nおすすめ: {adv['食事']}")
        else:
            st.warning("診断がまだです")

elif mode == "ダイエット管理":
    st.header("📝 ダイエット記録")
    # 入力フォーム
    age = st.number_input("年齢", key="common_age")
    h = st.number_input("身長", key="common_height")
    w = st.number_input("体重", key="common_weight")
    bf = st.number_input("体脂肪率", key="common_body_fat")
    
    if st.button("記録を保存"):
        bmi = round(w / ((h / 100) ** 2), 1)
        log = {
            "日付": datetime.today().strftime("%Y-%m-%d"),
            "年齢": age, "身長(cm)": h, "体重(kg)": w,
            "目標体重(kg)": st.session_state.common_target_weight,
            "体脂肪率(%)": bf, "目標体脂肪率(%)": st.session_state.common_target_body_fat,
            "BMI": bmi, "目標摂取カロリー": 1500 # 簡易計算
        }
        upsert_diet_log(log)
        st.success("スプレッドシートに保存しました！")

elif mode == "設定":
    st.header("⚙️ アプリ設定")
    if st.button("クラウドから設定を再読み込み"):
        st.cache_resource.clear()
        st.rerun()
    if st.button("マスターデータを保存"):
        save_user_settings()
        st.success("設定を更新しました。")

# (他、献立、アーユルヴェーダ、家計簿などは元のロジックを流用可能ですが、API呼び出し部分は上記upsert関数に準じて書き換えてください)
