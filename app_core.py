import streamlit as st
import random
from collections import Counter

# =====================
# 🔐 ログイン関連
# =====================

def is_logged_in():
    return "user_id" in st.session_state


def require_login():
    if not is_logged_in():
        st.warning("ログインしてください")
        st.stop()


def login(user_id, password):
    # 開発用：何でもログインOK（あとでシート連携）
    if user_id and password:
        st.session_state["user_id"] = user_id
        return True
    return False


def logout():
    st.session_state.clear()


def get_user_id():
    return st.session_state.get("user_id", None)


def reset_password(user_id, new_pw):
    # 仮（後でシート連携）
    return True


# =====================
# 🧠 状態ロジック
# =====================

def build_condition(user_type=None, weather=None, state=None, exercise=None):
    return {
        "goal": user_type or "バランス",
        "weather": weather or "普通",
        "state": state or "普通",
        "exercise": exercise or "なし"
    }


def decide_meal_type(condition):

    if condition["state"] == "疲れ":
        return "軽め"

    if condition["state"] == "むくみ":
        return "さっぱり"

    if condition["exercise"] == "筋トレ":
        return "しっかり"

    if condition["weather"] == "暑い":
        return "さっぱり"

    if condition["weather"] == "寒い":
        return "あたたかい"

    return "バランス"


# =====================
# 🍽 メニュー生成
# =====================

def convert_to_meal(meal_type, condition):

    if meal_type == "軽め":
        return random.choice([
            "おにぎり＋味噌汁",
            "ヨーグルト＋フルーツ",
            "トースト＋ゆで卵"
        ])

    elif meal_type == "しっかり":
        return random.choice([
            "ごはん＋鶏むね肉＋サラダ",
            "豚しゃぶ＋ごはん",
            "ハンバーグ＋サラダ"
        ])

    elif meal_type == "さっぱり":
        return random.choice([
            "そば＋温泉卵",
            "冷しゃぶサラダ",
            "冷やしうどん"
        ])

    elif meal_type == "あたたかい":
        return random.choice([
            "雑炊",
            "うどん",
            "スープ＋ごはん"
        ])

    return "ごはん＋焼き魚＋味噌汁"


# =====================
# 🌿 かんたんモード
# =====================

def generate_simple_advice(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)
    meal_type = decide_meal_type(condition)
    meal = convert_to_meal(meal_type, condition)

    return f"今日は「{meal_type}」がおすすめです\n→ {meal}"


# =====================
# 💪 しっかりモード
# =====================

def generate_full_plan(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)

    plan = {}

    for timing in ["朝", "昼", "夜"]:

        meal_type = decide_meal_type(condition)

        if timing == "夜" and meal_type == "しっかり":
            meal_type = "軽め"

        plan[timing] = convert_to_meal(meal_type, condition)

    return plan


# =====================
# 📅 1週間プラン
# =====================

def generate_weekly_plan(user_type=None, weather=None, state=None, exercise=None):

    week = {}

    for day in ["月", "火", "水", "木", "金", "土", "日"]:
        week[day] = generate_full_plan(user_type, weather, state, exercise)

    return week


# =====================
# 🛒 買い物リスト
# =====================

def generate_smart_shopping_list(plan, fridge_items=None):

    if fridge_items is None:
        fridge_items = []

    mapping = {
        "おにぎり": ["ごはん"],
        "味噌汁": ["味噌", "豆腐"],
        "鶏むね肉": ["鶏むね肉"],
        "サラダ": ["レタス"],
        "卵": ["卵"],
        "ヨーグルト": ["ヨーグルト"],
        "そば": ["そば"],
        "うどん": ["うどん"],
        "豚しゃぶ": ["豚肉"],
        "ハンバーグ": ["ひき肉"]
    }

    items = []

    for meal in plan.values():
        for key, ing in mapping.items():
            if key in meal:
                items.extend(ing)

    # 冷蔵庫差分
    items = [i for i in items if i not in fridge_items]

    counted = Counter(items)

    result = {"食材": []}

    for item, count in counted.items():
        result["食材"].append(f"{item} × {count}")

    return result


# =====================
# 📅 週間買い物
# =====================

def generate_weekly_shopping_list(week_plan, fridge_items=None):

    meals = []

    for day in week_plan.values():
        for meal in day.values():
            meals.append(meal)

    temp = {"まとめ": " ".join(meals)}

    return generate_smart_shopping_list(temp, fridge_items)


# =====================
# 🉐 特売
# =====================

def get_local_deals():
    return {
        "鶏むね肉": "特売 100g 78円",
        "卵": "10個 198円"
    }


def add_deals_to_shopping(shopping):

    deals = get_local_deals()
    result = {}

    for cat, items in shopping.items():

        result[cat] = []

        for item in items:

            name = item.split(" × ")[0]

            if name in deals:
                item = f"{item} 🉐 {deals[name]}"

            result[cat].append(item)

    return result


from datetime import datetime, date
from zoneinfo import ZoneInfo

# =====================
# 🧩 旧ページ互換用：日時
# =====================

def jst_now():
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def jst_today():
    return jst_now().date()


# =====================
# ⚙️ ユーザー設定 初期値
# =====================

def get_default_user_settings():
    return {
        "gender": "",
        "age": "",
        "height_cm": "",
        "start_weight": "",
        "target_weight": "",
        "start_body_fat": "",
        "target_body_fat": "",
        "meal_style": "和食中心",
        "ease_level": "かんたん",
        "staple_preference": "ごはん",
        "fridge_items": "",
        "avoid_foods": "",
        "favorite_meals": "",
        "favorite_protein_onigiri": "鮭・しらす・枝豆のおにぎり",
        "favorite_misodama_soup": "味噌玉の味噌汁",
        "plan_type": "バランス",
        "lunch_style": "家・弁当",
        "real_mode": "やさしめ",
        "daily_flow": "",
        "workout_today": "ストレッチ",
        "body_goal": "無理なく整える",
    }


def _settings_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"user_settings_{user_id}"


# =====================
# ⚙️ 設定読み込み
# =====================

def load_user_settings(user_id=None):
    key = _settings_key(user_id)

    if key not in st.session_state:
        st.session_state[key] = get_default_user_settings()

    settings = get_default_user_settings()
    settings.update(st.session_state.get(key, {}))

    return settings


# =====================
# ⚙️ 設定保存
# =====================

def save_user_settings(user_id=None, settings=None, **kwargs):
    # save_user_settings(settings) の形でも動くようにする
    if isinstance(user_id, dict) and settings is None:
        settings = user_id
        user_id = None

    key = _settings_key(user_id)

    current = load_user_settings(user_id)

    if settings:
        current.update(settings)

    if kwargs:
        current.update(kwargs)

    st.session_state[key] = current

    # 冷蔵庫リストを買い物リスト用に整える
    fridge_text = current.get("fridge_items", "")

    if isinstance(fridge_text, str):
        fridge_list = [
            x.strip()
            for x in fridge_text.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]
    elif isinstance(fridge_text, list):
        fridge_list = fridge_text
    else:
        fridge_list = []

    st.session_state["fridge_items"] = fridge_list

    return True


# 古い名前でも動くようにする
load_settings = load_user_settings
save_settings = save_user_settings


# =====================
# 📝 食事メモ解析
# =====================

def parse_meal_sections(text):
    result = {
        "朝": "",
        "昼": "",
        "夜": "",
        "間食": "",
    }

    if not text:
        return result

    current = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("朝"):
            current = "朝"
            result[current] += line.replace("朝：", "").replace("朝:", "").strip()
        elif line.startswith("昼"):
            current = "昼"
            result[current] += line.replace("昼：", "").replace("昼:", "").strip()
        elif line.startswith("夜"):
            current = "夜"
            result[current] += line.replace("夜：", "").replace("夜:", "").strip()
        elif line.startswith("間食"):
            current = "間食"
            result[current] += line.replace("間食：", "").replace("間食:", "").strip()
        elif current:
            result[current] += "\n" + line

    return result


# =====================
# 📝 記録保存・読み込み
# =====================

def _logs_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"diet_logs_{user_id}"


def load_diet_logs(user_id=None):
    key = _logs_key(user_id)
    return st.session_state.get(key, [])


def save_diet_log(user_id=None, log=None, **kwargs):
    # save_diet_log(log) の形でも動くようにする
    if isinstance(user_id, dict) and log is None:
        log = user_id
        user_id = None

    key = _logs_key(user_id)

    logs = st.session_state.get(key, [])

    if log is None:
        log = {}

    if kwargs:
        log.update(kwargs)

    log.setdefault("date", str(jst_today()))
    log.setdefault("created_at", jst_now().strftime("%Y-%m-%d %H:%M:%S"))

    logs.append(log)

    st.session_state[key] = logs

    return True


def load_latest_log(user_id=None):
    logs = load_diet_logs(user_id)
    if logs:
        return logs[-1]
    return None


# 古い名前対策
load_user_logs = load_diet_logs
save_user_log = save_diet_log
save_log = save_diet_log


# =====================
# 📅 今日のプラン保存・読み込み
# =====================

def _today_plan_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"today_plan_{user_id}_{jst_today()}"


def save_today_plan(user_id=None, plan=None, **kwargs):
    if isinstance(user_id, dict) and plan is None:
        plan = user_id
        user_id = None

    key = _today_plan_key(user_id)

    if plan is None:
        plan = {}

    if kwargs:
        plan.update(kwargs)

    st.session_state[key] = plan

    return True


def load_today_plan(user_id=None):
    key = _today_plan_key(user_id)
    return st.session_state.get(key, {})


# =====================
# 🌿 旧UI用：動的アドバイス互換
# =====================

def generate_dynamic_advice(main_meal=None, advice=None, user_type=None, weather=None):
    if isinstance(advice, dict):
        if main_meal in advice:
            return advice.get(main_meal)
        return "今日は無理せず、食事と運動を整えましょう。"

    if isinstance(advice, str):
        return advice

    return generate_simple_advice(
        user_type=user_type,
        weather=weather,
        state="普通",
        exercise="ストレッチ"
    )


# =====================
# 🛒 旧UI用：週間買い物リスト互換
# =====================

def generate_shopping_list_from_week(weekly_plan):
    if not weekly_plan:
        return {"食材": []}

    # 週間プラン形式ならそのまま処理
    if isinstance(weekly_plan, dict):
        try:
            return generate_weekly_shopping_list(
                weekly_plan,
                fridge_items=st.session_state.get("fridge_items", [])
            )
        except Exception:
            pass

    return {"食材": []}


# =====================
# 🤖 相談ページ用 仮関数
# =====================

def get_openai_client():
    # 今は未接続。後でOpenAI API接続時に差し替え。
    return None
