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
