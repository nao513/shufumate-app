import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

# -----------------------------
# Google Sheets 保存
# -----------------------------
USER_ID = "nao513"

def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def get_sheet(tab_name: str):
    gc = get_gspread_client()
    sh = gc.open_by_key(st.secrets["GOOGLE_SHEET_ID"])
    return sh.worksheet(tab_name)

def ensure_headers():
    settings_ws = get_sheet("Settings")
    diet_ws = get_sheet("DietLogs")

    settings_header = [
        "user_id", "age", "height_cm", "start_weight",
        "target_weight", "start_body_fat", "target_body_fat"
    ]
    diet_header = [
        "user_id", "date", "age", "height_cm", "weight",
        "target_weight", "body_fat", "target_body_fat",
        "bmi", "goal_calories"
    ]

    settings_values = settings_ws.get_all_values()
    diet_values = diet_ws.get_all_values()

    if not settings_values:
        settings_ws.append_row(settings_header)
    elif settings_values[0] != settings_header:
        settings_ws.clear()
        settings_ws.append_row(settings_header)

    if not diet_values:
        diet_ws.append_row(diet_header)
    elif diet_values[0] != diet_header:
        diet_ws.clear()
        diet_ws.append_row(diet_header)

def load_user_settings():
    ensure_headers()
    ws = get_sheet("Settings")
    values = ws.get_all_values()

    if len(values) < 2:
        return None

    header = values[0]
    data_rows = values[1:]

    for row in data_rows:
        if not row or len(row) < len(header):
            continue

        row_dict = dict(zip(header, row))
        if row_dict.get("user_id") == USER_ID:
            return {
                "common_age": int(float(row_dict["age"])),
                "common_height": float(row_dict["height_cm"]),
                "common_weight": float(row_dict["start_weight"]),
                "common_target_weight": float(row_dict["target_weight"]),
                "common_body_fat": float(row_dict["start_body_fat"]),
                "common_target_body_fat": float(row_dict["target_body_fat"]),
            }
    return None

def save_user_settings():
    ensure_headers()
    ws = get_sheet("Settings")
    values = ws.get_all_values()

    header = [
        "user_id", "age", "height_cm", "start_weight",
        "target_weight", "start_body_fat", "target_body_fat"
    ]

    if not values:
        ws.append_row(header)
        values = [header]

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
        if row and len(row) > 0 and row[0] == USER_ID:
            row_index = i
            break

    if row_index:
        ws.update(f"A{row_index}:G{row_index}", [values_to_save])
    else:
        ws.append_row(values_to_save)

def reset_user_settings():
    st.session_state["common_age"] = 40
    st.session_state["common_height"] = 160.0
    st.session_state["common_weight"] = 40.0
    st.session_state["common_target_weight"] = 45.0
    st.session_state["common_body_fat"] = 15.0
    st.session_state["common_target_body_fat"] = 22.0

def load_diet_logs():
    ensure_headers()
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
    ensure_headers()
    ws = get_sheet("DietLogs")
    values = ws.get_all_values()

    header = [
        "user_id", "date", "age", "height_cm", "weight",
        "target_weight", "body_fat", "target_body_fat",
        "bmi", "goal_calories"
    ]

    if not values:
        ws.append_row(header)
        values = [header]

    row_index = None
    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2 and row[0] == USER_ID and row[1] == log_dict["日付"]:
            row_index = i
            break

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

    if row_index:
        ws.update(f"A{row_index}:J{row_index}", [row_values])
    else:
        ws.append_row(row_values)

# -----------------------------
# 共通データ初期値
# -----------------------------
if "common_age" not in st.session_state:
    st.session_state["common_age"] = 40

if "common_height" not in st.session_state:
    st.session_state["common_height"] = 160.0

if "common_weight" not in st.session_state:
    st.session_state["common_weight"] = 40.0

if "common_target_weight" not in st.session_state:
    st.session_state["common_target_weight"] = 45.0

if "common_body_fat" not in st.session_state:
    st.session_state["common_body_fat"] = 15.0

if "common_target_body_fat" not in st.session_state:
    st.session_state["common_target_body_fat"] = 22.0

if "diet_logs" not in st.session_state:
    st.session_state["diet_logs"] = []

if "today_plan_text" not in st.session_state:
    st.session_state["today_plan_text"] = ""

if "today_plan_date" not in st.session_state:
    st.session_state["today_plan_date"] = ""

if "expenses" not in st.session_state:
    st.session_state["expenses"] = []

if "schedules" not in st.session_state:
    st.session_state["schedules"] = []

# -----------------------------
# 初回ロード
# -----------------------------
if "settings_loaded" not in st.session_state:
    saved = load_user_settings()
    if saved:
        for k, v in saved.items():
            st.session_state[k] = v

    st.session_state["diet_logs"] = load_diet_logs()
    st.session_state["settings_loaded"] = True

# -----------------------------
# 共通関数
# -----------------------------
def get_openai_client():
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("Streamlit Secrets に OPENAI_API_KEY が設定されていません。")
        st.stop()

def create_plan_for_date(client, date_str, gender, age, height_cm, weight, body_fat, target_weight, target_body_fat):
    prompt = f"""
あなたは優秀な管理栄養士とトレーナーです。

条件:
- 性別: {gender}
- 年齢: {age}歳
- 身長: {height_cm}cm
- 体重: {weight}kg
- 体脂肪率: {body_fat}%
- 目標体重: {target_weight}kg
- 目標体脂肪率: {target_body_fat}%

{date_str}の1日の健康的なダイエットプランを作ってください。

以下の形式で日本語で分かりやすく出力してください。

■朝食：
■昼食：
■夕食：
■運動：
■買い物リスト：
- 食材名
- 食材名
- 食材名
"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content

def categorize_item(item: str) -> str:
    meat_egg = ["鶏", "豚", "牛", "ひき肉", "ささみ", "むね肉", "もも肉", "ベーコン", "ハム", "卵"]
    seafood = ["鮭", "さば", "サバ", "まぐろ", "ツナ", "ぶり", "たら", "エビ", "いか", "あさり", "魚"]
    vegetables = [
        "キャベツ", "レタス", "白菜", "ほうれん草", "小松菜", "ブロッコリー", "トマト", "きゅうり",
        "にんじん", "玉ねぎ", "ねぎ", "大根", "もやし", "ピーマン", "ナス", "じゃがいも", "さつまいも"
    ]
    mushroom_seaweed = ["しめじ", "えのき", "しいたけ", "まいたけ", "きのこ", "わかめ", "ひじき", "のり", "昆布"]
    staple = ["米", "ご飯", "玄米", "もち麦", "オートミール", "パン", "うどん", "そば", "パスタ"]
    dairy_soy = ["牛乳", "ヨーグルト", "チーズ", "豆腐", "納豆", "豆乳", "油揚げ", "厚揚げ"]
    seasoning_other = ["味噌", "しょうゆ", "醤油", "塩", "こしょう", "胡椒", "砂糖", "酢", "オリーブオイル", "ごま油", "ドレッシング", "キムチ"]

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
    for word in seasoning_other:
        if word in item:
            return "調味料・その他"
    return "その他"

def extract_shopping_items(plan_texts):
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

# -----------------------------
# ヘッダー
# -----------------------------
st.title("🍀 ShufuMate｜主婦の味方アプリ")
st.caption("ダイエット・家計・予定・教育・人生設計・お得情報を総合管理")

# -----------------------------
# サイドバー
# -----------------------------
mode = st.sidebar.radio("機能を選んでください", [
    "今日のおすすめ",
    "ダイエット管理",
    "献立・運動プラン",
    "家計簿",
    "スケジュール",
    "教育費・人生設計",
    "お得情報",
    "設定"
])

# -----------------------------
# 今日のおすすめ
# -----------------------------
if mode == "今日のおすすめ":
    st.header("👉 今日のおすすめ")

    today_str = datetime.today().strftime("%Y-%m-%d")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 今日のダイエット状況")
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
        if st.session_state["today_plan_text"] and st.session_state["today_plan_date"] == today_str:
            st.markdown(st.session_state["today_plan_text"])
        else:
            st.info("まだプランがありません")
            st.caption("👉『献立・運動プラン』で作成してください")

# -----------------------------
# ダイエット管理
# -----------------------------
elif mode == "ダイエット管理":
    st.header("📝 ダイエット管理")

    age = st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")

    height_cm = st.number_input(
        "身長（cm）",
        min_value=145.0,
        max_value=200.0,
        step=0.5,
        format="%.1f",
        key="common_height"
    )

    weight = st.number_input(
        "現在の体重（kg）",
        min_value=40.0,
        max_value=200.0,
        step=0.1,
        format="%.1f",
        key="common_weight"
    )

    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=40.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        key="common_target_weight"
    )

    body_fat = st.number_input(
        "体脂肪率（%）",
        min_value=15.0,
        max_value=60.0,
        step=0.1,
        format="%.1f",
        key="common_body_fat"
    )

    target_body_fat = st.number_input(
        "目標体脂肪率（%）",
        min_value=15.0,
        max_value=50.0,
        step=0.1,
        format="%.1f",
        key="common_target_body_fat"
    )

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
        st.success("今日の記録を保存しました✨")

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

# -----------------------------
# 献立・運動プラン
# -----------------------------
elif mode == "献立・運動プラン":
    st.header("🥗献立＆🏃運動プラン")

    gender = st.radio("性別", ["女性", "男性"], horizontal=True)

    age = st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    height_cm = st.number_input(
        "身長（cm）",
        min_value=145.0,
        max_value=200.0,
        step=0.5,
        format="%.1f",
        key="common_height"
    )
    weight = st.number_input(
        "現在の体重（kg）",
        min_value=40.0,
        max_value=200.0,
        step=0.1,
        format="%.1f",
        key="common_weight"
    )
    target_weight = st.number_input(
        "目標体重（kg）",
        min_value=40.0,
        max_value=100.0,
        step=0.1,
        format="%.1f",
        key="common_target_weight"
    )
    body_fat = st.number_input(
        "体脂肪率（%）",
        min_value=15.0,
        max_value=60.0,
        step=0.1,
        format="%.1f",
        key="common_body_fat"
    )
    target_body_fat = st.number_input(
        "目標体脂肪率（%）",
        min_value=15.0,
        max_value=60.0,
        step=0.1,
        format="%.1f",
        key="common_target_body_fat"
    )

    days = st.slider("まとめて何日分作りますか？", 1, 30, 7)
    client = get_openai_client()

    today_str = datetime.today().strftime("%Y-%m-%d")

    if st.button("📅 今日のプランを表示"):
        with st.spinner("生成中..."):
            plan = create_plan_for_date(
                client, today_str, gender, age, height_cm, weight, body_fat, target_weight, target_body_fat
            )

        st.session_state["today_plan_text"] = plan
        st.session_state["today_plan_date"] = today_str

        st.subheader(f"今日のプラン（{today_str}）")
        st.markdown(plan)

    st.divider()

    if st.button("複数日プラン作成"):
        results = []

        with st.spinner("AIが複数日プランを作成中..."):
            for i in range(days):
                date = (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")
                plan_text = create_plan_for_date(
                    client, date, gender, age, height_cm, weight, body_fat, target_weight, target_body_fat
                )
                results.append({
                    "日付": date,
                    "プラン": plan_text
                })

        df = pd.DataFrame(results)

        st.success("プラン完成✨")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 献立・運動プランCSVダウンロード",
            data=csv,
            file_name="plan.csv",
            mime="text/csv"
        )

        st.subheader("🛒 買い物リストまとめ")
        shopping_df = extract_shopping_items(df["プラン"].tolist())

        if not shopping_df.empty:
            st.dataframe(shopping_df, use_container_width=True)

            for category in shopping_df["カテゴリ"].unique():
                st.markdown(f"### {category}")
                for item in shopping_df[shopping_df["カテゴリ"] == category]["食材"]:
                    st.write(f"- {item}")

            shopping_csv = shopping_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 買い物リストCSVダウンロード",
                data=shopping_csv,
                file_name="shopping_list.csv",
                mime="text/csv"
            )
        else:
            st.info("買い物リストを抽出できませんでした。")

# -----------------------------
# 家計簿
# -----------------------------
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

        summary = df_exp.groupby("カテゴリ", as_index=False)["金額"].sum()
        st.subheader("カテゴリ別集計")
        st.dataframe(summary, use_container_width=True)
        st.bar_chart(summary.set_index("カテゴリ"))

        csv_exp = df_exp.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 家計簿CSVダウンロード", csv_exp, "kakeibo.csv", "text/csv")

# -----------------------------
# スケジュール
# -----------------------------
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

# -----------------------------
# 教育費・人生設計
# -----------------------------
elif mode == "教育費・人生設計":
    st.header("📘 教育費・人生プラン")

    num_children = st.number_input("子どもの人数", min_value=0, max_value=5, value=1)
    edu_type = st.selectbox(
        "教育方針",
        ["すべて公立", "中学から私立", "高校から私立", "大学から私立", "すべて私立"]
    )

    edu_costs = {
        "公立": {"小学校": 50, "中学校": 70, "高校": 100, "大学": 300},
        "私立": {"小学校": 150, "中学校": 200, "高校": 300, "大学": 600}
    }

    current_year = datetime.now().year
    total_cost = 0

    for i in range(num_children):
        age = st.slider(f"子ども{i+1}の現在の年齢", 0, 18, 6, key=f"child_age_{i}")
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
            y = current_year + (6 - age) + offsets[j]
            cost = edu_costs[plan[j]][level]
            st.write(f"{y}年 - {level}（{plan[j]}）: {cost}万円")
            total_cost += cost

    st.metric("想定教育費合計", f"{total_cost} 万円")

# -----------------------------
# お得情報
# -----------------------------
elif mode == "お得情報":
    st.header("📢 地域のお得情報")

    sheet_url = st.text_input(
        "スプレッドシートCSVリンク",
        value="https://docs.google.com/spreadsheets/d/1cLT1eqx7A-XpPvuUSqwxayfXpu5j0xy3YV3opDmcgfU/export?format=csv"
    )

    try:
        df_info = pd.read_csv(sheet_url)
        pref = st.selectbox("地域を選択", df_info["地域"].dropna().unique())
        category = st.selectbox("カテゴリを選択", df_info["カテゴリ"].dropna().unique())
        filtered = df_info[(df_info["地域"] == pref) & (df_info["カテゴリ"] == category)]

        if filtered.empty:
            st.info("該当する情報がありません。")
        else:
            for _, row in filtered.iterrows():
                st.markdown(f"- {row['情報内容']}（{row['備考']}）")

    except Exception:
        st.error("スプレッドシートの読み込みに失敗しました。")

# -----------------------------
# 設定
# -----------------------------
elif mode == "設定":
    st.header("⚙️ アプリ設定")

    st.subheader("📌 初期設定")
    st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
    st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
    st.number_input("スタート時の体重（kg）", min_value=40.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
    st.number_input("目標体重（kg）", min_value=40.0, max_value=100.0, step=0.1, format="%.1f", key="common_target_weight")
    st.number_input("スタート時の体脂肪率（%）", min_value=15.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
    st.number_input("目標体脂肪率（%）", min_value=10.0, max_value=50.0, step=0.1, format="%.1f", key="common_target_body_fat")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 初期設定を保存"):
            save_user_settings()
            st.success("初期設定を保存しました。次回もこの値が反映されます。")

    with col2:
        if st.button("↺ 初期設定をリセット"):
            reset_user_settings()
            save_user_settings()
            st.success("初期設定をリセットしました。")
