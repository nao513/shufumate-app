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

# =====================
# 🆕 新規登録・ユーザー管理 互換用
# =====================

def _users_store_key():
    return "shufumate_users"


def load_users():
    if _users_store_key() not in st.session_state:
        st.session_state[_users_store_key()] = {}
    return st.session_state[_users_store_key()]


def create_user(login_id, password, nickname="", birth_date=None, **kwargs):
    login_id = str(login_id).strip()
    password = str(password).strip()
    nickname = str(nickname).strip()

    if not login_id:
        raise ValueError("ログインIDを入力してください")

    if not password:
        raise ValueError("パスワードを入力してください")

    if len(password) < 4:
        raise ValueError("パスワードは4文字以上にしてください")

    users = load_users()

    if login_id in users:
        raise ValueError("このログインIDはすでに使われています")

    user_record = {
        "login_id": login_id,
        "password": password,
        "nickname": nickname or login_id,
        "birth_date": str(birth_date) if birth_date else "",
    }

    users[login_id] = user_record
    st.session_state[_users_store_key()] = users

    return user_record


def login_user(user_record):
    if not user_record:
        return False

    login_id = user_record.get("login_id", "")
    nickname = user_record.get("nickname", login_id)

    if not login_id:
        return False

    st.session_state["user_id"] = login_id
    st.session_state["user_name"] = nickname

    return True


def verify_login(login_id, password):
    login_id = str(login_id).strip()
    password = str(password).strip()

    users = load_users()

    user_record = users.get(login_id)

    if user_record and user_record.get("password") == password:
        return user_record

    return None

# =====================
# 👤 現在ユーザープロフィール取得
# =====================

def _calculate_age_from_birth_date(birth_date_text):
    try:
        bd = datetime.strptime(str(birth_date_text), "%Y-%m-%d").date()
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return None


def load_current_user_profile(user_id=None):
    user_id = user_id or get_user_id()

    if not user_id:
        return {}

    users = st.session_state.get("shufumate_users", {})
    user_record = users.get(user_id, {})

    profile = {
        "login_id": user_id,
        "nickname": st.session_state.get("user_name", user_id),
        "birth_date": "",
        "age": None,
    }

    if isinstance(user_record, dict):
        profile.update(user_record)

    birth_date_text = profile.get("birth_date", "")
    profile["age"] = _calculate_age_from_birth_date(birth_date_text)

    return profile


def update_current_user_profile(user_id=None, **kwargs):
    user_id = user_id or get_user_id()

    if not user_id:
        return False

    users = st.session_state.get("shufumate_users", {})

    if user_id not in users:
        users[user_id] = {
            "login_id": user_id,
            "password": "",
            "nickname": user_id,
            "birth_date": "",
        }

    users[user_id].update(kwargs)

    if "nickname" in kwargs:
        st.session_state["user_name"] = kwargs["nickname"]

    st.session_state["shufumate_users"] = users

    return True

# =====================
# 📝 記録画面 初期値取得
# =====================

def get_initial_log_values(user_id=None):
    settings = load_user_settings(user_id)
    latest = load_latest_log(user_id)

    def safe_value(value, default):
        try:
            if value is None or value == "":
                return default
            return value
        except Exception:
            return default

    weight = None
    body_fat = None

    if isinstance(latest, dict):
        weight = latest.get("weight")
        body_fat = latest.get("body_fat")

    if weight is None:
        weight = (
            settings.get("current_weight")
            or settings.get("start_weight")
            or 50
        )

    if body_fat is None:
        body_fat = (
            settings.get("current_body_fat")
            or settings.get("start_body_fat")
            or 30
        )

    return {
        "weight": safe_value(weight, 50),
        "body_fat": safe_value(body_fat, 30),
    }

# =====================
# 💬 相談ページ用 互換・簡易AI
# =====================

CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]


def normalize_consult_settings(settings):
    """
    相談ページで使う設定項目を安全に補完する
    """
    if not isinstance(settings, dict):
        settings = {}

    defaults = {
        "nickname": "",
        "user_type": "自分向け",
        "activity_level": "ふつう",
        "food_style": settings.get("meal_style", "和食中心"),
        "constitution_traits": [],
        "advice_tone": "やさしく",
        "target_weight": settings.get("target_weight", ""),
        "current_weight": settings.get("current_weight", settings.get("start_weight", "")),
        "target_body_fat": settings.get("target_body_fat", ""),
        "current_body_fat": settings.get("current_body_fat", settings.get("start_body_fat", "")),
        "fridge_items": settings.get("fridge_items", ""),
        "avoid_foods": settings.get("avoid_foods", ""),
        "workout_today": settings.get("workout_today", "ストレッチ"),
        "body_goal": settings.get("body_goal", "無理なく整える"),
    }

    for k, v in defaults.items():
        settings.setdefault(k, v)

    # constitution_traits が文字列ならリストに変換
    if isinstance(settings.get("constitution_traits"), str):
        text = settings.get("constitution_traits", "")
        settings["constitution_traits"] = [
            x.strip()
            for x in text.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return settings


def _safe_float_for_consult(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def get_support_focus_summary(settings=None, latest_log=None):
    """
    今の設定・最新記録から、相談時に見るべきポイントを作る
    """
    settings = normalize_consult_settings(settings or {})

    points = []
    today_conditions = []

    if isinstance(latest_log, dict):
        raw_conditions = latest_log.get("today_conditions", [])

        if isinstance(raw_conditions, list):
            today_conditions = raw_conditions
        elif isinstance(raw_conditions, str) and raw_conditions:
            today_conditions = [
                x.strip()
                for x in raw_conditions.replace("、", ",").split(",")
                if x.strip()
            ]

        condition_note = latest_log.get("condition_note", "")
        if condition_note and not today_conditions:
            today_conditions = [
                x.strip()
                for x in str(condition_note).replace("、", ",").split(",")
                if x.strip()
            ]

    # 今日の状態から見るポイント
    if "寝不足" in today_conditions:
        points.append("睡眠リカバリー")

    if "だるい" in today_conditions:
        points.append("疲労回復")

    if "むくみあり" in today_conditions:
        points.append("むくみケア")

    if "食べすぎた" in today_conditions:
        points.append("胃腸リセット")

    if "外食あり" in today_conditions:
        points.append("外食調整")

    if "時間がない" in today_conditions:
        points.append("時短メニュー")

    # 体重・体脂肪から見るポイント
    current_weight = _safe_float_for_consult(settings.get("current_weight"))
    target_weight = _safe_float_for_consult(settings.get("target_weight"))

    if current_weight is not None and target_weight is not None:
        if current_weight > target_weight:
            points.append("脂肪を落とす")
        else:
            points.append("維持・整える")

    current_body_fat = _safe_float_for_consult(settings.get("current_body_fat"))
    target_body_fat = _safe_float_for_consult(settings.get("target_body_fat"))

    if current_body_fat is not None and target_body_fat is not None:
        if current_body_fat > target_body_fat:
            points.append("体脂肪ケア")

    # 重複削除
    points = list(dict.fromkeys(points))

    return {
        "points": points,
        "today_conditions": today_conditions,
    }


def generate_answer(category, question, settings=None, latest_log=None):
    """
    相談ページ用の簡易回答。
    OpenAI API未接続でも動く安全版。
    """
    settings = normalize_consult_settings(settings or {})
    focus = get_support_focus_summary(settings, latest_log)

    question = question.strip() if question else ""

    points_text = "、".join(focus["points"]) if focus["points"] else "基本の整え"
    conditions_text = "、".join(focus["today_conditions"]) if focus["today_conditions"] else "特になし"

    food_style = settings.get("food_style", "和食中心")
    workout_today = settings.get("workout_today", "ストレッチ")
    avoid_foods = settings.get("avoid_foods", "")
    fridge_items = settings.get("fridge_items", "")

    if not question:
        question = "今日どう整えればいい？"

    base = (
        f"今のポイントは「{points_text}」です。\n"
        f"今日の状態は「{conditions_text}」として考えます。\n\n"
    )

    if category == "食事":
        answer = base
        answer += "🍽 食事のおすすめ\n"
        answer += "今日は無理に減らすより、温かい汁物＋たんぱく質を入れるのがおすすめです。\n\n"

        if "食べすぎた" in focus["today_conditions"]:
            answer += "食べすぎた翌日は、抜くよりも「軽めに整える」が安全です。\n"
            answer += "例：おにぎり小さめ＋味噌汁＋豆腐・卵・魚のどれか。\n"
        elif "むくみあり" in focus["today_conditions"]:
            answer += "むくみがある日は、塩分を少し控えて、温かい汁物と水分を意識しましょう。\n"
            answer += "例：具だくさん味噌汁、豆腐、きのこ、海藻、鮭おにぎり。\n"
        elif "寝不足" in focus["today_conditions"] or "だるい" in focus["today_conditions"]:
            answer += "疲れている日は、消化が重すぎないものが向いています。\n"
            answer += "例：雑炊、味噌汁、おにぎり、ゆで卵、ヨーグルト。\n"
        else:
            answer += "基本は「主食＋たんぱく質＋汁物」で整えると続けやすいです。\n"
            answer += "例：鮭おにぎり＋味噌玉の味噌汁＋ゆで卵。\n"

        if fridge_items:
            answer += f"\n冷蔵庫にあるもの：{fridge_items}\n"
            answer += "この中から使えるものを優先すると、買い物も減らせます。\n"

        if avoid_foods:
            answer += f"\n避けたいもの：{avoid_foods}\n"
            answer += "これは無理に使わない前提で考えましょう。\n"

        return answer

    if category == "運動":
        answer = base
        answer += "🏃‍♀️ 運動のおすすめ\n"

        if "寝不足" in focus["today_conditions"] or "だるい" in focus["today_conditions"]:
            answer += "今日は追い込まなくて大丈夫です。\n"
            answer += "おすすめは、首・肩・股関節まわりのストレッチを5〜10分です。\n"
        elif "むくみあり" in focus["today_conditions"]:
            answer += "むくみがある日は、軽く歩くか、足首回し・ふくらはぎ伸ばしがおすすめです。\n"
            answer += "汗をかくより、巡りを良くするイメージでOKです。\n"
        elif workout_today in ["筋トレ", "ピラティス"]:
            answer += "筋肉を使う日は、運動後にたんぱく質を入れると整いやすいです。\n"
            answer += "例：卵、豆腐、魚、鶏むね肉、ヨーグルト。\n"
        else:
            answer += "今日はストレッチか軽いウォーキングで十分です。\n"
            answer += "続けることを優先しましょう。\n"

        return answer

    if category == "体調":
        answer = base
        answer += "🌿 体調を整える提案\n"

        if "寝不足" in focus["today_conditions"]:
            answer += "寝不足の日は、食事制限より回復優先です。\n"
            answer += "温かい飲み物、軽めの夕食、早めのお風呂がおすすめです。\n"
        elif "むくみあり" in focus["today_conditions"]:
            answer += "むくみがある日は、冷たいもの・塩分多めを控えめにしましょう。\n"
            answer += "足首回し、ふくらはぎストレッチ、温かい汁物が合います。\n"
        elif "だるい" in focus["today_conditions"]:
            answer += "だるい日は、頑張る日ではなく整える日です。\n"
            answer += "食事は軽すぎず、味噌汁や卵などで最低限の栄養を入れましょう。\n"
        else:
            answer += "今日は大きな崩れがなければ、いつものリズムを守るだけで十分です。\n"

        return answer

    if category == "外食調整":
        answer = base
        answer += "🍴 外食調整のおすすめ\n"
        answer += "外食の日は、全部我慢より「選び方」と「前後の調整」が大事です。\n\n"

        answer += "おすすめの選び方：\n"
        answer += "・たんぱく質があるものを選ぶ\n"
        answer += "・揚げ物だけにしない\n"
        answer += "・汁物やサラダを足す\n"
        answer += "・夜が重い日は昼を軽めにする\n\n"

        if "食べすぎた" in focus["today_conditions"]:
            answer += "すでに食べすぎ感がある日は、外食では量を少し控えめにして、翌朝に味噌汁や果物で整えましょう。\n"
        else:
            answer += "外食を楽しみながら、翌食で整えれば大丈夫です。\n"

        return answer

    return base + "今日は無理せず、食事・運動・睡眠を少しずつ整えましょう。"
