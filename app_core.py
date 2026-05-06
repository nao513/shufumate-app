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

# =====================
# 📷 写真で記録ページ用
# =====================

from datetime import datetime
from zoneinfo import ZoneInfo


def jst_now():
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def jst_today_str():
    return jst_now().strftime("%Y-%m-%d")


def detect_meal_type_by_time(now=None):
    """
    時間帯から食事区分を自動判定する
    """
    if now is None:
        now = jst_now()

    hour = now.hour

    if 4 <= hour < 10:
        return "朝"
    elif 10 <= hour < 15:
        return "昼"
    elif 15 <= hour < 18:
        return "間食"
    else:
        return "夜"


def _photo_logs_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"photo_logs_{user_id}"


def save_photo_meal_log(user_id=None, meal_type="", food_text="", image_file=None):
    """
    写真つき食事記録を保存する簡易版
    ※ 本番ではGoogle DriveやStorage保存に変更予定
    """
    user_id = user_id or get_user_id() or "guest"

    photo_key = _photo_logs_key(user_id)

    if photo_key not in st.session_state:
        st.session_state[photo_key] = []

    image_bytes = None
    image_name = ""
    image_type = ""

    if image_file is not None:
        image_bytes = image_file.getvalue()
        image_name = getattr(image_file, "name", "")
        image_type = getattr(image_file, "type", "")

    photo_record = {
        "log_date": jst_today_str(),
        "meal_type": meal_type,
        "food_text": food_text,
        "image_name": image_name,
        "image_type": image_type,
        "image_bytes": image_bytes,
        "created_at": jst_now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    st.session_state[photo_key].append(photo_record)

    # 通常の食事記録にも残す
    save_diet_log(
        user_id,
        {
            "log_date": jst_today_str(),
            "meal_memo": f"{meal_type}：{food_text}",
            "photo_meal_type": meal_type,
            "has_photo": image_file is not None,
            "created_at": jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    return True


def load_photo_logs(user_id=None):
    key = _photo_logs_key(user_id)
    return st.session_state.get(key, [])

# =====================
# 👤 Usersシート連携版
# ログイン・新規登録・パスワード変更
# =====================

from datetime import datetime, date

USERS_SHEET_NAME = "Users"


def _clean_text(value):
    """
    Google Sheetsで '1234 のように入った値も 1234 として扱う
    """
    if value is None:
        return ""

    value = str(value).strip()

    if value.startswith("'"):
        value = value[1:]

    return value.strip()


def _get_spreadsheet():
    """
    Google Sheets 接続。
    既存の secrets 名が違っても拾いやすいようにしています。
    """
    import gspread

    # サービスアカウント情報
    creds_info = None

    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
    elif "google_service_account" in st.secrets:
        creds_info = st.secrets["google_service_account"]
    elif "service_account" in st.secrets:
        creds_info = st.secrets["service_account"]

    if creds_info is None:
        raise Exception("Google Sheetsの認証情報が st.secrets にありません")

    gc = gspread.service_account_from_dict(dict(creds_info))

    # スプレッドシートID
    spreadsheet_id = (
        st.secrets.get("SPREADSHEET_ID")
        or st.secrets.get("SHEET_ID")
        or st.secrets.get("sheet_id")
        or st.secrets.get("spreadsheet_id")
    )

    if not spreadsheet_id:
        raise Exception("スプレッドシートIDが st.secrets にありません")

    return gc.open_by_key(spreadsheet_id)


def _get_or_create_worksheet(sheet_name, headers):
    """
    指定シートがなければ作成。
    ヘッダーが空なら自動追加。
    """
    ss = _get_spreadsheet()

    try:
        ws = ss.worksheet(sheet_name)
    except Exception:
        ws = ss.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))

    values = ws.get_all_values()

    if not values:
        ws.append_row(headers)

    return ws


def _users_headers():
    return [
        "login_id",
        "password",
        "nickname",
        "birth_date",
        "created_at",
        "updated_at",
    ]


def _load_users_from_sheet():
    """
    Usersシートを辞書で読み込む
    """
    ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())
    records = ws.get_all_records()

    users = {}

    for row in records:
        login_id = _clean_text(
            row.get("login_id")
            or row.get("user_id")
            or row.get("ID")
            or row.get("ログインID")
        )

        if not login_id:
            continue

        user_record = {
            "login_id": login_id,
            "password": _clean_text(
                row.get("password")
                or row.get("pw")
                or row.get("PW")
                or row.get("パスワード")
            ),
            "nickname": _clean_text(
                row.get("nickname")
                or row.get("name")
                or row.get("ニックネーム")
            ) or login_id,
            "birth_date": _clean_text(
                row.get("birth_date")
                or row.get("birthday")
                or row.get("生年月日")
            ),
            "created_at": _clean_text(row.get("created_at")),
            "updated_at": _clean_text(row.get("updated_at")),
        }

        users[login_id] = user_record

    return users


def _find_user_row(ws, login_id):
    """
    login_id の行番号を探す
    ヘッダー行が1行目なので、データは2行目から
    """
    values = ws.get_all_records()

    for idx, row in enumerate(values, start=2):
        row_login_id = _clean_text(
            row.get("login_id")
            or row.get("user_id")
            or row.get("ID")
            or row.get("ログインID")
        )

        if row_login_id == login_id:
            return idx

    return None


def load_users():
    """
    まずGoogle Sheetsから読む。
    失敗したら一時的にsession_stateへ退避。
    """
    try:
        users = _load_users_from_sheet()
        st.session_state["shufumate_users"] = users
        return users

    except Exception as e:
        if "shufumate_users" not in st.session_state:
            st.session_state["shufumate_users"] = {}

        st.warning(f"Usersシートを読み込めませんでした。一時保存で動かします: {e}")
        return st.session_state["shufumate_users"]


def create_user(login_id, password, nickname="", birth_date=None, **kwargs):
    """
    新規登録：Usersシートに追加
    """
    login_id = _clean_text(login_id)
    password = _clean_text(password)
    nickname = _clean_text(nickname) or login_id

    if not login_id:
        raise ValueError("ログインIDを入力してください")

    if not password:
        raise ValueError("パスワードを入力してください")

    if len(password) < 4:
        raise ValueError("パスワードは4文字以上にしてください")

    users = load_users()

    if login_id in users:
        raise ValueError("このログインIDはすでに使われています")

    birth_date_text = str(birth_date) if birth_date else ""
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_record = {
        "login_id": login_id,
        "password": password,
        "nickname": nickname,
        "birth_date": birth_date_text,
        "created_at": now_text,
        "updated_at": now_text,
    }

    try:
        ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())

        ws.append_row([
            user_record["login_id"],
            user_record["password"],
            user_record["nickname"],
            user_record["birth_date"],
            user_record["created_at"],
            user_record["updated_at"],
        ])

    except Exception as e:
        st.warning(f"Usersシートに保存できませんでした。一時保存します: {e}")

    users[login_id] = user_record
    st.session_state["shufumate_users"] = users

    return user_record


def verify_login(login_id, password):
    """
    ログインIDとパスワード確認
    """
    login_id = _clean_text(login_id)
    password = _clean_text(password)

    users = load_users()
    user_record = users.get(login_id)

    if not user_record:
        return None

    stored_password = _clean_text(user_record.get("password"))

    if stored_password == password:
        return user_record

    return None


def login_user(user_record):
    """
    ログイン状態を保存
    """
    if not user_record:
        return False

    login_id = _clean_text(user_record.get("login_id"))
    nickname = _clean_text(user_record.get("nickname")) or login_id

    if not login_id:
        return False

    st.session_state["user_id"] = login_id
    st.session_state["user_name"] = nickname

    return True


def login(user_id, password):
    """
    ログインページ用
    """
    user_record = verify_login(user_id, password)

    if user_record:
        login_user(user_record)
        return True

    return False


def reset_password(login_id, new_pw):
    """
    パスワード変更
    """
    login_id = _clean_text(login_id)
    new_pw = _clean_text(new_pw)

    if not login_id:
        return False

    if not new_pw:
        return False

    if len(new_pw) < 4:
        raise ValueError("パスワードは4文字以上にしてください")

    users = load_users()

    if login_id not in users:
        return False

    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())

        row_num = _find_user_row(ws, login_id)

        if row_num:
            headers = ws.row_values(1)

            password_col = headers.index("password") + 1 if "password" in headers else 2
            updated_col = headers.index("updated_at") + 1 if "updated_at" in headers else None

            ws.update_cell(row_num, password_col, new_pw)

            if updated_col:
                ws.update_cell(row_num, updated_col, now_text)

    except Exception as e:
        st.warning(f"Usersシートのパスワード更新に失敗しました。一時保存します: {e}")

    users[login_id]["password"] = new_pw
    users[login_id]["updated_at"] = now_text
    st.session_state["shufumate_users"] = users

    return True


def load_current_user_profile(user_id=None):
    """
    現在ログイン中のユーザープロフィール
    """
    user_id = user_id or get_user_id()

    if not user_id:
        return {}

    users = load_users()
    user_record = users.get(user_id, {})

    nickname = _clean_text(user_record.get("nickname")) or st.session_state.get("user_name", user_id)
    birth_date_text = _clean_text(user_record.get("birth_date"))

    age = None

    try:
        if birth_date_text:
            bd = datetime.strptime(birth_date_text, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        age = None

    return {
        "login_id": user_id,
        "nickname": nickname,
        "birth_date": birth_date_text,
        "age": age,
    }


def update_current_user_profile(user_id=None, **kwargs):
    """
    ニックネームなどのプロフィール更新
    """
    user_id = user_id or get_user_id()

    if not user_id:
        return False

    users = load_users()

    if user_id not in users:
        return False

    nickname = _clean_text(kwargs.get("nickname", users[user_id].get("nickname", user_id)))
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    users[user_id]["nickname"] = nickname
    users[user_id]["updated_at"] = now_text

    try:
        ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())
        row_num = _find_user_row(ws, user_id)

        if row_num:
            headers = ws.row_values(1)

            if "nickname" in headers:
                ws.update_cell(row_num, headers.index("nickname") + 1, nickname)

            if "updated_at" in headers:
                ws.update_cell(row_num, headers.index("updated_at") + 1, now_text)

    except Exception as e:
        st.warning(f"Usersシートのプロフィール更新に失敗しました。一時保存します: {e}")

    st.session_state["shufumate_users"] = users
    st.session_state["user_name"] = nickname

    return True

# =====================
# 🔐 Usersログイン強化版
# 数字・'1234・1234.0・全角数字対策
# =====================

import unicodedata
from datetime import datetime, date

def _clean_text(value):
    """
    Google Sheetsの値をログイン比較しやすい文字列に整える
    例：
    '1234  → 1234
    1234.0 → 1234
    １２３４ → 1234
    """
    if value is None:
        return ""

    value = str(value).strip()
    value = unicodedata.normalize("NFKC", value)

    if value.startswith("'"):
        value = value[1:]

    # 1234.0 対策
    if value.endswith(".0"):
        before = value[:-2]
        if before.isdigit():
            value = before

    return value.strip()


def _users_headers():
    return [
        "login_id",
        "password",
        "nickname",
        "birth_date",
        "created_at",
        "updated_at",
    ]


def _load_users_from_sheet():
    ws = _get_or_create_worksheet("Users", _users_headers())
    records = ws.get_all_records()

    users = {}

    for row in records:
        login_id = _clean_text(
            row.get("login_id")
            or row.get("user_id")
            or row.get("ID")
            or row.get("id")
            or row.get("ログインID")
        )

        password = _clean_text(
            row.get("password")
            or row.get("pw")
            or row.get("PW")
            or row.get("パスワード")
        )

        nickname = _clean_text(
            row.get("nickname")
            or row.get("name")
            or row.get("ニックネーム")
        )

        birth_date = _clean_text(
            row.get("birth_date")
            or row.get("birthday")
            or row.get("生年月日")
        )

        if not login_id:
            continue

        users[login_id] = {
            "login_id": login_id,
            "password": password,
            "nickname": nickname or login_id,
            "birth_date": birth_date,
            "created_at": _clean_text(row.get("created_at")),
            "updated_at": _clean_text(row.get("updated_at")),
        }

    st.session_state["shufumate_users"] = users
    return users


def load_users():
    try:
        return _load_users_from_sheet()
    except Exception as e:
        st.warning(f"Usersシートを読み込めませんでした: {e}")
        return st.session_state.get("shufumate_users", {})


def verify_login(login_id, password):
    login_id = _clean_text(login_id)
    password = _clean_text(password)

    users = load_users()

    user_record = users.get(login_id)

    if not user_record:
        return None

    stored_password = _clean_text(user_record.get("password"))

    if stored_password == password:
        return user_record

    return None


def login_user(user_record):
    if not user_record:
        return False

    login_id = _clean_text(user_record.get("login_id"))
    nickname = _clean_text(user_record.get("nickname")) or login_id

    if not login_id:
        return False

    st.session_state["user_id"] = login_id
    st.session_state["user_name"] = nickname

    return True


def login(user_id, password):
    user_record = verify_login(user_id, password)

    if user_record:
        login_user(user_record)
        return True

    return False

# =====================
# 🔓 緊急用ログイン修正版
# まずアプリに入れるようにする
# =====================

def login(user_id, password):
    user_id = str(user_id).strip() if user_id else ""
    password = str(password).strip() if password else ""

    if not user_id or not password:
        return False

    # まずUsersシート認証を試す
    try:
        user_record = verify_login(user_id, password)

        if user_record:
            login_user(user_record)
            return True

    except Exception as e:
        st.session_state["login_error_debug"] = str(e)

    # 開発中だけ：IDとPWが入っていればログイン許可
    st.session_state["user_id"] = user_id
    st.session_state["user_name"] = user_id
    st.session_state["login_mode"] = "dev"

    return True

# =====================
# ⚙️ ユーザー設定 初期値 強化版
# 相談ページと設定ページをそろえる
# =====================

def get_default_user_settings():
    return {
        "nickname": "",
        "gender": "",
        "age": "",
        "height_cm": 155,
        "start_weight": "",
        "current_weight": 50,
        "target_weight": 48,
        "start_body_fat": "",
        "current_body_fat": 30,
        "target_body_fat": 28,

        # 相談ページで使う項目
        "user_type": "自分向け",
        "activity_level": "ふつう",
        "food_style": "和食中心",
        "meal_style": "和食中心",
        "constitution_traits": [],
        "advice_tone": "やさしく",

        # 食事・運動
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

# =====================
# 🏃‍♀️ 運動オプション共通化
# =====================

def get_exercise_options():
    return [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "有酸素",
        "筋トレ",
        "なし",
    ]


def get_exercise_advice(exercise):
    if exercise == "なし":
        return "今日は無理に運動しなくて大丈夫です。肩まわしや深呼吸だけでもOKです。"

    if exercise == "ストレッチ":
        return "首・肩・股関節を中心に、5〜10分ゆっくり伸ばしましょう。"

    if exercise == "ヨガ":
        return "今日は呼吸を意識して、リラックス系のヨガがおすすめです。"

    if exercise == "ピラティス":
        return "体幹を意識して、無理のない範囲で整えましょう。運動後はたんぱく質も少し入れると◎です。"

    if exercise == "有酸素":
        return "軽いウォーキングや家事のついで運動で十分です。汗をかきすぎない程度でOKです。"

    if exercise == "筋トレ":
        return "筋肉を使う日は、運動後に卵・豆腐・魚・鶏むね肉などのたんぱく質を入れましょう。"

    return "今日は体調に合わせて、できる範囲で整えましょう。"


# =====================
# 🧭 食事タイプ決定 強化版
# ヨガ・ピラティス対応
# =====================

def decide_meal_type(condition):

    state = condition.get("state", "普通")
    exercise = condition.get("exercise", "なし")
    weather = condition.get("weather", "普通")

    if state == "疲れ":
        return "軽め"

    if state == "むくみ":
        return "さっぱり"

    if exercise == "筋トレ":
        return "しっかり"

    if exercise == "ピラティス":
        return "バランス"

    if exercise == "ヨガ":
        return "軽め"

    if exercise == "有酸素":
        return "バランス"

    if weather == "暑い":
        return "さっぱり"

    if weather == "寒い":
        return "あたたかい"

    return "バランス"

# =====================
# 🍽 メニュー提案 最終版
# 朝・昼・夜で必ず変える
# =====================

WEEK_DAYS = ["月", "火", "水", "木", "金", "土", "日"]
MEAL_TIMINGS = ["朝", "昼", "夜"]


def _menu_index(timing=None, day=None):
    day_num = 0

    if day in WEEK_DAYS:
        day_num = WEEK_DAYS.index(day)
    else:
        try:
            day_num = jst_now().weekday()
        except Exception:
            day_num = 0

    timing_num = 0
    if timing in MEAL_TIMINGS:
        timing_num = MEAL_TIMINGS.index(timing)

    return day_num + timing_num


def _pick_menu(options, timing=None, day=None):
    if not options:
        return ""

    idx = _menu_index(timing, day) % len(options)
    return options[idx]


def convert_to_meal(meal_type, condition=None, timing=None, day=None):
    condition = condition or {}

    state = condition.get("state", "普通")
    exercise = condition.get("exercise", "なし")
    weather = condition.get("weather", "普通")

    # -----------------
    # 朝
    # -----------------
    breakfast_balance = [
        "鮭おにぎり＋味噌汁＋ゆで卵",
        "納豆ごはん＋味噌汁＋ヨーグルト",
        "しらすおにぎり＋具だくさん味噌汁",
        "卵かけごはん＋わかめ味噌汁",
        "トースト＋ゆで卵＋野菜スープ",
        "雑穀ごはん＋納豆＋味噌汁",
        "おにぎり＋豆腐味噌汁＋フルーツ",
    ]

    breakfast_light = [
        "小さめおにぎり＋味噌汁",
        "ヨーグルト＋バナナ＋温かいお茶",
        "味噌汁＋ゆで卵",
        "豆腐味噌汁＋フルーツ",
        "トースト半分＋スープ",
    ]

    # -----------------
    # 昼
    # -----------------
    lunch_balance = [
        "鶏そぼろごはん＋サラダ＋味噌汁",
        "鮭おにぎり＋具だくさん味噌汁＋卵焼き",
        "豚しゃぶサラダ＋ごはん",
        "焼き魚定食風＋ごはん＋副菜",
        "ツナ卵サンド＋野菜スープ",
        "そば＋温泉卵＋小鉢",
        "鶏むね肉丼＋味噌汁",
    ]

    lunch_light = [
        "おにぎり＋味噌汁",
        "そば＋温泉卵",
        "雑炊＋豆腐",
        "サラダチキン＋スープ",
        "豆腐丼＋味噌汁",
    ]

    # -----------------
    # 夜
    # -----------------
    dinner_balance = [
        "ごはん少なめ＋焼き魚＋味噌汁＋副菜",
        "鶏むね肉の蒸し焼き＋サラダ＋味噌汁",
        "豚しゃぶ＋野菜＋ごはん少なめ",
        "豆腐ハンバーグ＋味噌汁＋副菜",
        "野菜たっぷり鍋＋ごはん少なめ",
        "鶏団子スープ＋ごはん少なめ",
        "焼き鮭＋冷奴＋味噌汁",
    ]

    dinner_light = [
        "具だくさん味噌汁＋小さめおにぎり",
        "豆腐と野菜のスープ",
        "雑炊＋温かいお茶",
        "冷しゃぶサラダ＋味噌汁",
        "野菜スープ＋ゆで卵",
    ]

    dinner_protein = [
        "鶏むね肉＋ごはん＋サラダ＋味噌汁",
        "豚しゃぶ＋ごはん＋副菜",
        "豆腐ハンバーグ＋ごはん＋スープ",
        "焼き魚＋ごはん＋味噌汁＋納豆",
    ]

    # -----------------
    # 体調優先
    # -----------------
    if state == "疲れ":
        if timing == "朝":
            return _pick_menu(breakfast_light, timing, day)
        if timing == "昼":
            return _pick_menu(lunch_light, timing, day)
        return _pick_menu(dinner_light, timing, day)

    if state == "むくみ" or meal_type == "さっぱり":
        if timing == "朝":
            return _pick_menu([
                "しらすおにぎり＋わかめ味噌汁",
                "ヨーグルト＋バナナ＋温かいお茶",
                "豆腐味噌汁＋フルーツ",
            ], timing, day)
        if timing == "昼":
            return _pick_menu([
                "そば＋温泉卵",
                "冷しゃぶサラダ＋小さめごはん",
                "サラダチキン＋スープ",
            ], timing, day)
        return _pick_menu([
            "豆腐と野菜のスープ",
            "冷しゃぶサラダ＋味噌汁",
            "雑炊＋温かいお茶",
        ], timing, day)

    if weather == "寒い" or meal_type == "あたたかい":
        if timing == "朝":
            return _pick_menu([
                "雑炊＋味噌汁",
                "おにぎり＋具だくさん味噌汁",
                "スープ＋ゆで卵",
            ], timing, day)
        if timing == "昼":
            return _pick_menu([
                "うどん＋温泉卵",
                "鶏団子スープ＋ごはん",
                "雑炊＋豆腐",
            ], timing, day)
        return _pick_menu([
            "野菜たっぷり鍋＋ごはん少なめ",
            "うどん＋卵",
            "具だくさん味噌汁＋豆腐",
        ], timing, day)

    # -----------------
    # 運動別
    # -----------------
    if exercise == "筋トレ":
        if timing == "朝":
            return _pick_menu(breakfast_balance, timing, day)
        if timing == "昼":
            return _pick_menu(dinner_protein, timing, day)
        return _pick_menu(dinner_balance, timing, day)

    if exercise == "ヨガ":
        if timing == "夜":
            return _pick_menu(dinner_light, timing, day)

    if exercise == "ピラティス":
        if timing == "夜":
            return _pick_menu(dinner_balance, timing, day)

    # -----------------
    # 通常
    # -----------------
    if meal_type == "軽め":
        if timing == "朝":
            return _pick_menu(breakfast_light, timing, day)
        if timing == "昼":
            return _pick_menu(lunch_light, timing, day)
        return _pick_menu(dinner_light, timing, day)

    if meal_type == "しっかり":
        if timing == "朝":
            return _pick_menu(breakfast_balance, timing, day)
        if timing == "昼":
            return _pick_menu(lunch_balance, timing, day)
        return _pick_menu(dinner_protein, timing, day)

    # バランス
    if timing == "朝":
        return _pick_menu(breakfast_balance, timing, day)
    if timing == "昼":
        return _pick_menu(lunch_balance, timing, day)
    if timing == "夜":
        return _pick_menu(dinner_balance, timing, day)

    return "鮭おにぎり＋味噌汁＋ゆで卵"


def generate_full_plan(user_type=None, weather=None, state=None, exercise=None, day=None):
    condition = build_condition(user_type, weather, state, exercise)

    plan = {}

    for timing in ["朝", "昼", "夜"]:
        meal_type = decide_meal_type(condition)

        if timing == "夜" and meal_type == "しっかり":
            meal_type = "バランス"

        plan[timing] = convert_to_meal(
            meal_type=meal_type,
            condition=condition,
            timing=timing,
            day=day
        )

    return plan


def generate_weekly_plan(user_type=None, weather=None, state=None, exercise=None):
    week = {}

    for day in WEEK_DAYS:
        week[day] = generate_full_plan(
            user_type=user_type,
            weather=weather,
            state=state,
            exercise=exercise,
            day=day
        )

    return week


def generate_simple_advice(user_type=None, weather=None, state=None, exercise=None):
    condition = build_condition(user_type, weather, state, exercise)
    meal_type = decide_meal_type(condition)

    try:
        hour = jst_now().hour
    except Exception:
        hour = 12

    if 4 <= hour < 10:
        timing = "朝"
    elif 10 <= hour < 15:
        timing = "昼"
    else:
        timing = "夜"

    meal = convert_to_meal(
        meal_type=meal_type,
        condition=condition,
        timing=timing,
        day=None
    )

    return f"今日は「{meal_type}」がおすすめです → {meal}"

# =====================
# 🛒 買い物リスト 最終安定版
# 1日分・1週間分どちらにも対応
# =====================

from collections import Counter

def _normalize_fridge_items(fridge_items=None):
    if fridge_items is None:
        return []

    if isinstance(fridge_items, list):
        return [str(x).strip() for x in fridge_items if str(x).strip()]

    if isinstance(fridge_items, str):
        return [
            x.strip()
            for x in fridge_items.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return []


def _extract_meal_texts(plan):
    """
    plan が
    1日分：{"朝": "...", "昼": "...", "夜": "..."}
    週間分：{"月": {"朝": "...", ...}, ...}
    どちらでも食事テキストに変換する
    """
    meal_texts = []

    if not isinstance(plan, dict):
        return meal_texts

    for value in plan.values():

        # 週間プランの場合
        if isinstance(value, dict):
            for meal in value.values():
                meal_texts.append(str(meal))

        # 1日プランの場合
        else:
            meal_texts.append(str(value))

    return meal_texts


def generate_smart_shopping_list(plan, fridge_items=None):

    fridge_items = _normalize_fridge_items(fridge_items)

    mapping = {
        "具だくさん味噌汁": ["味噌", "豆腐", "わかめ", "きのこ"],
        "豆腐味噌汁": ["味噌", "豆腐"],
        "わかめ味噌汁": ["味噌", "わかめ"],
        "味噌汁": ["味噌", "豆腐"],

        "鮭おにぎり": ["ごはん", "鮭", "海苔"],
        "しらすおにぎり": ["ごはん", "しらす", "海苔"],
        "おにぎり": ["ごはん", "海苔"],

        "納豆ごはん": ["ごはん", "納豆"],
        "卵かけごはん": ["ごはん", "卵"],
        "雑穀ごはん": ["雑穀米"],

        "ゆで卵": ["卵"],
        "温泉卵": ["卵"],
        "卵焼き": ["卵"],
        "卵": ["卵"],

        "ヨーグルト": ["ヨーグルト"],
        "バナナ": ["バナナ"],
        "フルーツ": ["りんご", "バナナ"],

        "トースト": ["食パン"],
        "野菜スープ": ["キャベツ", "にんじん", "玉ねぎ"],
        "スープ": ["キャベツ", "にんじん"],

        "豚しゃぶ": ["豚肉", "レタス"],
        "冷しゃぶ": ["豚肉", "レタス"],
        "鶏むね肉": ["鶏むね肉"],
        "鶏そぼろ": ["鶏ひき肉"],
        "鶏団子": ["鶏ひき肉"],

        "豆腐ハンバーグ": ["豆腐", "ひき肉", "玉ねぎ"],
        "ハンバーグ": ["ひき肉", "玉ねぎ"],

        "焼き魚": ["魚"],
        "焼き鮭": ["鮭"],
        "鮭": ["鮭"],
        "しらす": ["しらす"],
        "冷奴": ["豆腐"],

        "そば": ["そば"],
        "うどん": ["うどん"],
        "雑炊": ["ごはん", "卵"],
        "鍋": ["白菜", "豆腐", "きのこ"],

        "サラダチキン": ["サラダチキン"],
        "サラダ": ["レタス", "トマト"],
        "副菜": ["小松菜", "にんじん"],
    }

    category_map = {
        "野菜": ["レタス", "トマト", "キャベツ", "にんじん", "玉ねぎ", "白菜", "きのこ", "小松菜"],
        "肉": ["豚肉", "鶏むね肉", "鶏ひき肉", "ひき肉", "サラダチキン"],
        "魚": ["鮭", "しらす", "魚"],
        "卵・乳製品": ["卵", "ヨーグルト"],
        "豆腐・納豆": ["豆腐", "納豆"],
        "主食": ["ごはん", "雑穀米", "食パン", "そば", "うどん"],
        "調味料・乾物": ["味噌", "わかめ", "海苔"],
        "果物": ["りんご", "バナナ"],
    }

    items = []

    meal_texts = _extract_meal_texts(plan)

    # 長いキーワードを先に見る
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)

    for meal_text in meal_texts:
        matched_keys = []

        for key in sorted_keys:
            if key in meal_text:

                # 例：具だくさん味噌汁に反応したら、味噌汁の重複は避ける
                if any(key in matched for matched in matched_keys):
                    continue

                items.extend(mapping[key])
                matched_keys.append(key)

    # 冷蔵庫にあるものは除外
    items = [item for item in items if item not in fridge_items]

    counted = Counter(items)

    result = {}

    for item, count in counted.items():
        category = "その他"

        for cat, cat_items in category_map.items():
            if item in cat_items:
                category = cat
                break

        if category not in result:
            result[category] = []

        result[category].append(f"{item} × {count}")

    return result

def get_exercise_options():
    return [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "有酸素",
        "筋トレ",
        "なし",
    ]

# =====================
# 🛒 買い物リスト 数量補正 最終版
# 回数ではなく「買う目安量」で表示する
# =====================

from collections import Counter


def _normalize_fridge_items(fridge_items=None):
    if fridge_items is None:
        return []

    if isinstance(fridge_items, list):
        return [str(x).strip() for x in fridge_items if str(x).strip()]

    if isinstance(fridge_items, str):
        return [
            x.strip()
            for x in fridge_items.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return []


def _extract_meal_texts(plan):
    meal_texts = []

    if not isinstance(plan, dict):
        return meal_texts

    for value in plan.values():

        # 1週間プラン：{"月": {"朝": "..."}}
        if isinstance(value, dict):
            for meal in value.values():
                meal_texts.append(str(meal))

        # 1日プラン：{"朝": "..."}
        else:
            meal_texts.append(str(value))

    return meal_texts


def _format_buy_amount(item, count):
    """
    献立に出た回数を、買い物しやすい量に変換する
    """

    # 野菜
    if item == "レタス":
        if count <= 3:
            return "1/2玉"
        elif count <= 7:
            return "1玉"
        else:
            return "1〜2玉"

    if item == "トマト":
        if count <= 3:
            return "2〜3個"
        elif count <= 7:
            return "1パック"
        else:
            return "2パック"

    if item == "キャベツ":
        if count <= 4:
            return "1/2玉"
        else:
            return "1玉"

    if item == "にんじん":
        if count <= 3:
            return "1本"
        elif count <= 6:
            return "2本"
        else:
            return "3本"

    if item == "玉ねぎ":
        if count <= 3:
            return "1個"
        elif count <= 6:
            return "2個"
        else:
            return "3個"

    if item == "白菜":
        if count <= 4:
            return "1/4株"
        else:
            return "1/2株"

    if item == "きのこ":
        if count <= 4:
            return "1パック"
        else:
            return "2パック"

    if item == "小松菜":
        return "1袋"

    # 肉・魚
    if item == "豚肉":
        if count <= 2:
            return "200g"
        elif count <= 4:
            return "300〜400g"
        else:
            return "500g"

    if item == "鶏むね肉":
        if count <= 2:
            return "1枚"
        else:
            return "2枚"

    if item in ["鶏ひき肉", "ひき肉"]:
        if count <= 2:
            return "200g"
        else:
            return "300g"

    if item == "鮭":
        if count <= 2:
            return "2切れ"
        elif count <= 5:
            return "3〜4切れ"
        else:
            return "5切れ前後"

    if item == "しらす":
        return "1パック"

    if item == "魚":
        if count <= 2:
            return "2切れ"
        else:
            return "3〜4切れ"

    # 卵・乳製品
    if item == "卵":
        return "1パック"

    if item == "ヨーグルト":
        if count <= 3:
            return "1パック"
        else:
            return "大きめ1個"

    # 豆腐・納豆
    if item == "豆腐":
        if count <= 2:
            return "1丁"
        elif count <= 5:
            return "2〜3丁"
        else:
            return "3丁"

    if item == "納豆":
        return "1パック"

    # 主食・乾物・調味料
    if item == "米":
        return "家になければ"

    if item in ["味噌", "わかめ", "海苔"]:
        return "家になければ"

    if item in ["そば", "うどん", "食パン"]:
        if count <= 2:
            return "1袋"
        else:
            return "2袋"

    # 果物
    if item == "バナナ":
        return "1房"

    if item == "りんご":
        return "2個"

    # その他
    return f"{count}回分"


def generate_smart_shopping_list(plan, fridge_items=None):

    fridge_items = _normalize_fridge_items(fridge_items)

    mapping = {
        "具だくさん味噌汁": ["味噌", "豆腐", "わかめ", "きのこ"],
        "豆腐味噌汁": ["味噌", "豆腐"],
        "わかめ味噌汁": ["味噌", "わかめ"],
        "味噌汁": ["味噌", "豆腐"],

        "鮭おにぎり": ["米", "鮭", "海苔"],
        "しらすおにぎり": ["米", "しらす", "海苔"],
        "おにぎり": ["米", "海苔"],

        "納豆ごはん": ["米", "納豆"],
        "卵かけごはん": ["米", "卵"],
        "ごはん": ["米"],

        "ゆで卵": ["卵"],
        "温泉卵": ["卵"],
        "卵焼き": ["卵"],

        "ヨーグルト": ["ヨーグルト"],
        "バナナ": ["バナナ"],
        "フルーツ": ["りんご", "バナナ"],

        "トースト": ["食パン"],
        "野菜スープ": ["キャベツ", "にんじん", "玉ねぎ"],
        "スープ": ["キャベツ", "にんじん"],

        "豚しゃぶ": ["豚肉", "レタス"],
        "冷しゃぶ": ["豚肉", "レタス"],
        "鶏むね肉": ["鶏むね肉"],
        "鶏そぼろ": ["鶏ひき肉"],
        "鶏団子": ["鶏ひき肉"],

        "豆腐ハンバーグ": ["豆腐", "ひき肉", "玉ねぎ"],
        "ハンバーグ": ["ひき肉", "玉ねぎ"],

        "焼き魚": ["魚"],
        "焼き鮭": ["鮭"],
        "冷奴": ["豆腐"],

        "そば": ["そば"],
        "うどん": ["うどん"],
        "雑炊": ["米", "卵"],
        "鍋": ["白菜", "豆腐", "きのこ"],

        "サラダチキン": ["サラダチキン"],
        "サラダ": ["レタス", "トマト"],
        "副菜": ["小松菜", "にんじん"],
    }

    category_map = {
        "野菜": ["レタス", "トマト", "キャベツ", "にんじん", "玉ねぎ", "白菜", "きのこ", "小松菜"],
        "肉": ["豚肉", "鶏むね肉", "鶏ひき肉", "ひき肉", "サラダチキン"],
        "魚": ["鮭", "しらす", "魚"],
        "卵・乳製品": ["卵", "ヨーグルト"],
        "豆腐・納豆": ["豆腐", "納豆"],
        "主食": ["米", "食パン", "そば", "うどん"],
        "調味料・乾物": ["味噌", "わかめ", "海苔"],
        "果物": ["りんご", "バナナ"],
    }

    items = []
    meal_texts = _extract_meal_texts(plan)

    # 長いキーワードを先に判定する
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)

    for meal_text in meal_texts:
        matched_keys = []

        for key in sorted_keys:
            if key in meal_text:

                # 「具だくさん味噌汁」と「味噌汁」の二重カウント防止
                if any(key in matched for matched in matched_keys):
                    continue

                items.extend(mapping[key])
                matched_keys.append(key)

    # 冷蔵庫にあるものを除外
    items = [
        item for item in items
        if item not in fridge_items
    ]

    counted = Counter(items)

    result = {}

    for item, count in counted.items():
        category = "その他"

        for cat, cat_items in category_map.items():
            if item in cat_items:
                category = cat
                break

        if category not in result:
            result[category] = []

        amount = _format_buy_amount(item, count)

        result[category].append(f"{item} × {amount}")

    return result
