import random
from datetime import datetime

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

    # 体調優先
    if condition["state"] == "疲れ":
        return "軽め"

    if condition["state"] == "むくみ":
        return "さっぱり"

    # 運動
    if condition["exercise"] == "筋トレ":
        return "しっかり"

    if condition["exercise"] == "有酸素":
        return "バランス"

    # 天気
    if condition["weather"] == "暑い":
        return "さっぱり"

    if condition["weather"] == "寒い":
        return "あたたかい"

    return "バランス"

# -----------------
# 🍽 メニュー変換
# -----------------
def convert_to_meal(meal_type, condition):

    if meal_type == "軽め":
        options = [
            "タンパク質おにぎり＋味噌玉の味噌汁",
            "ヨーグルト＋フルーツ＋ナッツ",
            "トースト＋ゆで卵＋スープ"
        ]
        if condition["state"] == "疲れ":
            return "おにぎり＋味噌汁＋温かいお茶"
        return random.choice(options)

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
# 🌿 かんたん用
# -----------------
def generate_simple_advice(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)

    meal_type = decide_meal_type(condition)
    meal = convert_to_meal(meal_type, condition)

    return f"今日は「{meal_type}」がおすすめです。\n→ {meal}"

# -----------------
# 💪 しっかり用（朝昼夜）
# -----------------
def generate_full_plan(user_type=None, weather=None, state=None, exercise=None):

    condition = build_condition(user_type, weather, state, exercise)

    plan = {}

    for timing in ["朝", "昼", "夜"]:

        meal_type = decide_meal_type(condition)

        # 夜だけ調整（軽め寄せ）
        if timing == "夜" and meal_type == "しっかり":
            meal_type = "軽め"

        plan[timing] = convert_to_meal(meal_type, condition)

    return plan

# -----------------
# 🛒 買い物リスト生成
# -----------------
def generate_shopping_list_from_plan(plan):

    mapping = {
        "おにぎり": ["ごはん", "鮭"],
        "味噌汁": ["味噌", "豆腐", "わかめ"],
        "鶏むね肉": ["鶏むね肉"],
        "サラダ": ["レタス", "トマト"],
        "卵": ["卵"],
        "ヨーグルト": ["ヨーグルト"],
        "フルーツ": ["バナナ", "りんご"],
        "そば": ["そば"],
        "うどん": ["うどん"]
    }

    result = {}

    for timing, meal in plan.items():

        for key, items in mapping.items():
            if key in meal:

                category = "食材"

                if category not in result:
                    result[category] = []

                result[category].extend(items)

    # 重複削除
    result["食材"] = list(set(result["食材"]))

    return result

# -----------------
# 🛒 スーパー用買い物リスト（最強版）
# -----------------
from collections import Counter

def generate_smart_shopping_list(plan, fridge_items=None):

    if fridge_items is None:
        fridge_items = []

    # 食材マッピング（強化版）
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

    # 売り場分類
    category_map = {
        "野菜": ["レタス", "トマト", "バナナ"],
        "肉": ["鶏むね肉", "豚肉", "ひき肉"],
        "魚": ["鮭"],
        "乳製品": ["ヨーグルト"],
        "卵": ["卵"],
        "主食": ["ごはん", "そば", "うどん"],
        "調味料": ["味噌"],
        "その他": ["豆腐", "わかめ"]
    }

    items = []

    # -----------------
    # 食材抽出
    # -----------------
    for meal in plan.values():
        for key, ing in mapping.items():
            if key in meal:
                items.extend(ing)

    # -----------------
    # 冷蔵庫差分
    # -----------------
    items = [i for i in items if i not in fridge_items]

    # -----------------
    # 数量まとめ
    # -----------------
    counted = Counter(items)

    # -----------------
    # カテゴリ分け
    # -----------------
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
