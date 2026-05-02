import random
from collections import Counter

import streamlit as st

# -----------------
# 🔐 ログイン状態チェック
# -----------------
def is_logged_in():
    return "user_id" in st.session_state


# -----------------
# 🔐 ログイン必須
# -----------------
def require_login():
    if not is_logged_in():
        st.warning("ログインしてください")
        st.stop()


# -----------------
# 🔐 ログイン処理
# -----------------
def login(user_id, password):

    # 仮ログイン（あとでGoogle Sheets連携）
    if password == "1234":
        st.session_state["user_id"] = user_id
        return True

    return False


# -----------------
# 🔐 ログアウト
# -----------------
def logout():
    st.session_state.clear()

# -----------------
# 🧠 状態まとめ
# -----------------
def build_condition(user_type=None, weather=None, state=None, exercise=None):
    return {
        "goal": user_type or "バランス",
        "weather": weather or "普通",
        "state": state or "普通",
        "exercise": exercise or "なし"
    }

# -----------------
# 🧭 食事タイプ決定
# -----------------
def decide_meal_type(condition):

    if condition["state"] == "疲れ":
        return "軽め"

    if condition["state"] == "むくみ":
        return "さっぱり"

    if condition["exercise"] == "筋トレ":
        return "しっかり"

    if condition["exercise"] == "有酸素":
        return "バランス"

    if condition["weather"] == "暑い":
        return "さっぱり"

    if condition["weather"] == "寒い":
        return "あたたかい"

    return "バランス"

# -----------------
# 🍽 メニュー生成
# -----------------
def convert_to_meal(meal_type, condition):

    if meal_type == "軽め":
        if condition["state"] == "疲れ":
            return "おにぎり＋味噌汁＋温かいお茶"
        return random.choice([
            "タンパク質おにぎり＋味噌玉の味噌汁",
            "ヨーグルト＋フルーツ＋ナッツ",
            "トースト＋ゆで卵＋スープ"
        ])

    elif meal_type == "しっかり":
        if condition["exercise"] == "筋トレ":
            return "ごはん＋鶏むね肉＋サラダ＋味噌汁"
        return random.choice([
            "豚しゃぶ＋ごはん＋副菜",
            "ハンバーグ＋サラダ＋スープ"
        ])

    elif meal_type == "さっぱり":
        return random.choice([
            "冷しゃぶサラダ＋スープ",
            "そば＋温泉卵",
            "冷やしうどん＋副菜"
        ])

    elif meal_type == "あたたかい":
        return random.choice([
            "雑炊＋味噌汁",
            "鍋風スープ＋ごはん",
            "うどん＋野菜たっぷり"
        ])

    else:
        return random.choice([
            "鮭おにぎり＋具だくさん味噌汁",
            "ごはん＋焼き魚＋副菜",
            "パスタ＋サラダ＋スープ"
        ])

# -----------------
# 🌿 かんたんモード
# -----------------
def generate_simple_advice(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)
    meal_type = decide_meal_type(condition)
    meal = convert_to_meal(meal_type, condition)

    return f"今日は「{meal_type}」がおすすめです\n→ {meal}"

# -----------------
# 💪 しっかりモード（朝昼夜）
# -----------------
def generate_full_plan(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)

    plan = {}

    for timing in ["朝", "昼", "夜"]:

        meal_type = decide_meal_type(condition)

        # 夜は軽めに寄せる
        if timing == "夜" and meal_type == "しっかり":
            meal_type = "軽め"

        plan[timing] = convert_to_meal(meal_type, condition)

    return plan

# -----------------
# 📅 1週間プラン
# -----------------
def generate_weekly_plan(user_type=None, weather=None, state=None, exercise=None):

    week_plan = {}

    for day in ["月", "火", "水", "木", "金", "土", "日"]:
        week_plan[day] = generate_full_plan(user_type, weather, state, exercise)

    return week_plan

# -----------------
# 🛒 スーパー用買い物リスト
# -----------------
def generate_smart_shopping_list(plan, fridge_items=None):

    if fridge_items is None:
        fridge_items = []

    mapping = {
        "おにぎり": ["ごはん", "鮭"],
        "味噌汁": ["味噌", "豆腐", "わかめ"],
        "鶏むね肉": ["鶏むね肉"],
        "サラダ": ["レタス", "トマト"],
        "卵": ["卵"],
        "ヨーグルト": ["ヨーグルト"],
        "フルーツ": ["バナナ"],
        "そば": ["そば"],
        "うどん": ["うどん"],
        "豚しゃぶ": ["豚肉"],
        "ハンバーグ": ["ひき肉"]
    }

    category_map = {
        "野菜": ["レタス", "トマト", "バナナ"],
        "肉": ["鶏むね肉", "豚肉", "ひき肉"],
        "魚": ["鮭"],
        "卵": ["卵"],
        "乳製品": ["ヨーグルト"],
        "主食": ["ごはん", "そば", "うどん"],
        "調味料": ["味噌"],
        "その他": ["豆腐", "わかめ"]
    }

    items = []

    for meal in plan.values():
        for key, ing in mapping.items():
            if key in meal:
                items.extend(ing)

    # 冷蔵庫差分
    items = [i for i in items if i not in fridge_items]

    # 数量まとめ
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

# -----------------
# 📅 週間買い物
# -----------------
def generate_weekly_shopping_list(week_plan, fridge_items=None):

    all_meals = []

    for day_plan in week_plan.values():
        for meal in day_plan.values():
            all_meals.append(meal)

    temp_plan = {"まとめ": " ".join(all_meals)}

    return generate_smart_shopping_list(temp_plan, fridge_items)

# -----------------
# 🉐 特売情報（仮）
# -----------------
def get_local_deals():
    return {
        "鶏むね肉": "特売 100g 78円",
        "トマト": "特価 1パック 198円",
        "卵": "10個 198円"
    }

# -----------------
# 🉐 特売反映
# -----------------
def add_deals_to_shopping(shopping):

    deals = get_local_deals()

    result = {}

    for category, items in shopping.items():

        result[category] = []

        for item in items:

            name = item.split(" × ")[0]

            if name in deals:
                item = f"{item} 🉐 {deals[name]}"

            result[category].append(item)

    return result
