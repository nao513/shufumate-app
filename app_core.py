import streamlit as st
from datetime import datetime, date
from zoneinfo import ZoneInfo
from collections import Counter
import unicodedata

# ==================================================
# 共通：日時・文字整形
# ==================================================

def jst_now():
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def jst_today():
    return jst_now().date()


def jst_today_str():
    return jst_now().strftime("%Y-%m-%d")


def clean_text(value):
    if value is None:
        return ""

    value = str(value).strip()
    value = unicodedata.normalize("NFKC", value)

    if value.startswith("'"):
        value = value[1:]

    if value.endswith(".0"):
        before = value[:-2]
        if before.isdigit():
            value = before

    return value.strip()


def text_to_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    if isinstance(value, str):
        return [
            x.strip()
            for x in value.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return []


def safe_float(value, default):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


# ==================================================
# ログイン関連
# ==================================================

def is_logged_in():
    return "user_id" in st.session_state


def require_login():
    if not is_logged_in():
        st.warning("ログインしてください")
        st.stop()


def get_user_id():
    return st.session_state.get("user_id", None)


def logout():
    st.session_state.clear()


# ==================================================
# Users管理
# ==================================================

USERS_SHEET_NAME = "Users"


def _users_store_key():
    return "shufumate_users"


def _users_headers():
    return ["login_id", "password", "nickname", "birth_date", "created_at", "updated_at"]


def _get_spreadsheet():
    import gspread

    creds_info = None
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
    elif "google_service_account" in st.secrets:
        creds_info = st.secrets["google_service_account"]
    elif "service_account" in st.secrets:
        creds_info = st.secrets["service_account"]

    if creds_info is None:
        raise Exception("Google Sheetsの認証情報が st.secrets にありません")

    spreadsheet_id = (
        st.secrets.get("SPREADSHEET_ID")
        or st.secrets.get("SHEET_ID")
        or st.secrets.get("sheet_id")
        or st.secrets.get("spreadsheet_id")
    )

    if not spreadsheet_id:
        raise Exception("スプレッドシートIDが st.secrets にありません")

    gc = gspread.service_account_from_dict(dict(creds_info))
    return gc.open_by_key(spreadsheet_id)


def _get_or_create_worksheet(sheet_name, headers):
    ss = _get_spreadsheet()

    try:
        ws = ss.worksheet(sheet_name)
    except Exception:
        ws = ss.add_worksheet(title=sheet_name, rows=1000, cols=max(len(headers), 10))

    values = ws.get_all_values()
    if not values:
        ws.append_row(headers)

    return ws


def _find_user_row(ws, login_id):
    records = ws.get_all_records()

    for idx, row in enumerate(records, start=2):
        row_login_id = clean_text(
            row.get("login_id")
            or row.get("user_id")
            or row.get("ID")
            or row.get("id")
            or row.get("ログインID")
        )

        if row_login_id == login_id:
            return idx

    return None


def _load_users_from_sheet():
    ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())
    records = ws.get_all_records()

    users = {}

    for row in records:
        login_id = clean_text(
            row.get("login_id")
            or row.get("user_id")
            or row.get("ID")
            or row.get("id")
            or row.get("ログインID")
        )

        if not login_id:
            continue

        users[login_id] = {
            "login_id": login_id,
            "password": clean_text(
                row.get("password")
                or row.get("pw")
                or row.get("PW")
                or row.get("パスワード")
            ),
            "nickname": clean_text(
                row.get("nickname")
                or row.get("name")
                or row.get("ニックネーム")
            ) or login_id,
            "birth_date": clean_text(
                row.get("birth_date")
                or row.get("birthday")
                or row.get("生年月日")
            ),
            "created_at": clean_text(row.get("created_at")),
            "updated_at": clean_text(row.get("updated_at")),
        }

    return users


def load_users():
    try:
        users = _load_users_from_sheet()
        st.session_state[_users_store_key()] = users
        return users
    except Exception:
        if _users_store_key() not in st.session_state:
            st.session_state[_users_store_key()] = {}
        return st.session_state[_users_store_key()]


def create_user(login_id, password, nickname="", birth_date=None, **kwargs):
    login_id = clean_text(login_id)
    password = clean_text(password)
    nickname = clean_text(nickname) or login_id

    if not login_id:
        raise ValueError("ログインIDを入力してください")

    if not password:
        raise ValueError("パスワードを入力してください")

    if len(password) < 4:
        raise ValueError("パスワードは4文字以上にしてください")

    users = load_users()

    if login_id in users:
        raise ValueError("このログインIDはすでに使われています")

    now_text = jst_now().strftime("%Y-%m-%d %H:%M:%S")

    user_record = {
        "login_id": login_id,
        "password": password,
        "nickname": nickname,
        "birth_date": str(birth_date) if birth_date else "",
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
    st.session_state[_users_store_key()] = users

    return user_record


def verify_login(login_id, password):
    login_id = clean_text(login_id)
    password = clean_text(password)

    users = load_users()
    user_record = users.get(login_id)

    if not user_record:
        return None

    stored_password = clean_text(user_record.get("password"))

    if stored_password == password:
        return user_record

    return None


def login_user(user_record):
    if not user_record:
        return False

    login_id = clean_text(user_record.get("login_id"))
    nickname = clean_text(user_record.get("nickname")) or login_id

    if not login_id:
        return False

    st.session_state["user_id"] = login_id
    st.session_state["user_name"] = nickname

    return True


def login(user_id, password):
    user_id = clean_text(user_id)
    password = clean_text(password)

    if not user_id or not password:
        return False

    try:
        user_record = verify_login(user_id, password)

        if user_record:
            login_user(user_record)
            return True
    except Exception as e:
        st.session_state["login_error_debug"] = str(e)

    # 開発中の緊急ログイン：IDとPWが入っていれば入れる
    st.session_state["user_id"] = user_id
    st.session_state["user_name"] = user_id
    st.session_state["login_mode"] = "dev"

    return True


def reset_password(login_id, new_pw):
    login_id = clean_text(login_id)
    new_pw = clean_text(new_pw)

    if not login_id or not new_pw:
        return False

    if len(new_pw) < 4:
        raise ValueError("パスワードは4文字以上にしてください")

    users = load_users()

    if login_id not in users:
        return False

    now_text = jst_now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        ws = _get_or_create_worksheet(USERS_SHEET_NAME, _users_headers())
        row_num = _find_user_row(ws, login_id)

        if row_num:
            headers = ws.row_values(1)

            if "password" in headers:
                ws.update_cell(row_num, headers.index("password") + 1, new_pw)

            if "updated_at" in headers:
                ws.update_cell(row_num, headers.index("updated_at") + 1, now_text)

    except Exception as e:
        st.warning(f"Usersシートのパスワード更新に失敗しました。一時保存します: {e}")

    users[login_id]["password"] = new_pw
    users[login_id]["updated_at"] = now_text
    st.session_state[_users_store_key()] = users

    return True


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

    users = load_users()
    user_record = users.get(user_id, {})

    nickname = clean_text(user_record.get("nickname")) or st.session_state.get("user_name", user_id)
    birth_date_text = clean_text(user_record.get("birth_date"))

    return {
        "login_id": user_id,
        "nickname": nickname,
        "birth_date": birth_date_text,
        "age": _calculate_age_from_birth_date(birth_date_text),
    }


def update_current_user_profile(user_id=None, **kwargs):
    user_id = user_id or get_user_id()

    if not user_id:
        return False

    users = load_users()

    if user_id not in users:
        users[user_id] = {
            "login_id": user_id,
            "password": "",
            "nickname": user_id,
            "birth_date": "",
            "created_at": "",
            "updated_at": "",
        }

    nickname = clean_text(kwargs.get("nickname", users[user_id].get("nickname", user_id))) or user_id
    now_text = jst_now().strftime("%Y-%m-%d %H:%M:%S")

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

    except Exception:
        pass

    st.session_state[_users_store_key()] = users
    st.session_state["user_name"] = nickname

    return True


# ==================================================
# ユーザー設定
# ==================================================

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
        "user_type": "自分向け",
        "activity_level": "ふつう",
        "food_style": "和食中心",
        "meal_style": "和食中心",
        "constitution_traits": [],
        "advice_tone": "やさしく",
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


def load_user_settings(user_id=None):
    key = _settings_key(user_id)

    if key not in st.session_state:
        st.session_state[key] = get_default_user_settings()

    settings = get_default_user_settings()
    settings.update(st.session_state.get(key, {}))

    return settings


def save_user_settings(user_id=None, settings=None, **kwargs):
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
    st.session_state["fridge_items"] = text_to_list(current.get("fridge_items", ""))

    return True


load_settings = load_user_settings
save_settings = save_user_settings


# ==================================================
# 運動
# ==================================================

def get_exercise_options():
    return [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "ウォーキング",
        "ランニング",
        "筋トレ",
        "なし",
    ]


def normalize_exercise(exercise):
    if exercise in ["ウォーキング", "ランニング"]:
        return "有酸素"
    return exercise


def get_exercise_advice(exercise):
    if exercise == "なし":
        return "今日は無理に運動しなくて大丈夫です。肩まわしや深呼吸だけでもOKです。"

    if exercise == "ストレッチ":
        return "首・肩・股関節を中心に、5〜10分ゆっくり伸ばしましょう。"

    if exercise == "ヨガ":
        return "呼吸を意識して、リラックス系のヨガがおすすめです。"

    if exercise == "ピラティス":
        return "体幹を意識して、無理のない範囲で整えましょう。"

    if exercise == "ウォーキング":
        return "10〜20分の軽いウォーキングがおすすめです。巡りをよくするイメージでOKです。"

    if exercise == "ランニング":
        return "ランニングの日は短めでOKです。運動後は水分とたんぱく質を意識しましょう。"

    if exercise == "筋トレ":
        return "筋肉を使う日は、卵・豆腐・魚・鶏むね肉などのたんぱく質を入れましょう。"

    return "今日は体調に合わせて、できる範囲で整えましょう。"


# ==================================================
# 食事・献立
# ==================================================

WEEK_DAYS = ["月", "火", "水", "木", "金", "土", "日"]
MEAL_TIMINGS = ["朝", "昼", "夜"]


def build_condition(user_type=None, weather=None, state=None, exercise=None):
    return {
        "goal": user_type or "自分向け",
        "weather": weather or "普通",
        "state": state or "普通",
        "exercise": exercise or "なし",
    }


def decide_meal_type(condition):
    state = condition.get("state", "普通")
    exercise = normalize_exercise(condition.get("exercise", "なし"))
    weather = condition.get("weather", "普通")

    if state == "疲れ":
        return "軽め"

    if state == "むくみ":
        return "さっぱり"

    if exercise == "筋トレ":
        return "しっかり"

    if exercise in ["有酸素", "ピラティス"]:
        return "バランス"

    if exercise == "ヨガ":
        return "軽め"

    if weather == "暑い":
        return "さっぱり"

    if weather == "寒い":
        return "あたたかい"

    return "バランス"


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

    if exercise == "筋トレ":
        if timing == "朝":
            return _pick_menu(breakfast_balance, timing, day)
        if timing == "昼":
            return _pick_menu(dinner_protein, timing, day)
        return _pick_menu(dinner_balance, timing, day)

    if exercise == "ヨガ" and timing == "夜":
        return _pick_menu(dinner_light, timing, day)

    if exercise == "ピラティス" and timing == "夜":
        return _pick_menu(dinner_balance, timing, day)

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

    for timing in MEAL_TIMINGS:
        meal_type = decide_meal_type(condition)

        if timing == "夜" and meal_type == "しっかり":
            meal_type = "バランス"

        plan[timing] = convert_to_meal(
            meal_type=meal_type,
            condition=condition,
            timing=timing,
            day=day,
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
            day=day,
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
        day=None,
    )

    return f"今日は「{meal_type}」がおすすめです → {meal}"


# ==================================================
# 買い物リスト
# ==================================================

def _extract_meals_from_plan(plan):
    meals = []

    if not isinstance(plan, dict):
        return meals

    for value in plan.values():
        if isinstance(value, dict):
            for meal in value.values():
                meals.append(str(meal))
        else:
            meals.append(str(value))

    return meals


def _shopping_amount(item, count):
    if item in ["米", "味噌", "わかめ", "海苔"]:
        return "家になければ"

    if item == "卵":
        return "1パック"

    if item == "ヨーグルト":
        return "1パック"

    if item == "豆腐":
        if count <= 3:
            return "1丁"
        elif count <= 8:
            return "2丁"
        return "3丁"

    if item == "納豆":
        return "1パック"

    if item == "レタス":
        if count <= 4:
            return "1/2玉"
        elif count <= 8:
            return "1玉"
        return "1〜2玉"

    if item == "トマト":
        if count <= 3:
            return "2〜3個"
        return "1パック"

    if item == "キャベツ":
        if count <= 4:
            return "1/2玉"
        return "1玉"

    if item == "にんじん":
        if count <= 3:
            return "1本"
        elif count <= 6:
            return "2本"
        return "3本"

    if item == "玉ねぎ":
        if count <= 3:
            return "1個"
        elif count <= 6:
            return "2個"
        return "3個"

    if item == "白菜":
        return "1/4〜1/2株"

    if item == "きのこ":
        if count <= 4:
            return "1パック"
        return "2パック"

    if item == "小松菜":
        return "1袋"

    if item == "豚肉":
        if count <= 2:
            return "200g"
        elif count <= 5:
            return "300〜400g"
        return "500g"

    if item == "鶏むね肉":
        if count <= 2:
            return "1枚"
        return "2枚"

    if item in ["鶏ひき肉", "ひき肉"]:
        if count <= 2:
            return "200g"
        return "300g"

    if item == "サラダチキン":
        return "1〜2個"

    if item == "鮭":
        if count <= 2:
            return "2切れ"
        elif count <= 5:
            return "3〜4切れ"
        return "5切れ前後"

    if item == "しらす":
        return "1パック"

    if item == "魚":
        if count <= 2:
            return "2切れ"
        return "3〜4切れ"

    if item == "食パン":
        return "1袋"

    if item == "そば":
        return "1袋"

    if item == "うどん":
        return "1袋"

    if item == "バナナ":
        return "1房"

    if item == "りんご":
        return "2個"

    return f"{count}回分"


def generate_supermarket_shopping_list(plan, fridge_items=None):
    fridge_items = text_to_list(fridge_items)

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
        "雑穀ごはん": ["米"],
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
        "家にあるか確認": ["米", "味噌", "わかめ", "海苔"],
        "野菜": ["レタス", "トマト", "キャベツ", "にんじん", "玉ねぎ", "白菜", "きのこ", "小松菜"],
        "肉": ["豚肉", "鶏むね肉", "鶏ひき肉", "ひき肉", "サラダチキン"],
        "魚": ["鮭", "しらす", "魚"],
        "卵・乳製品": ["卵", "ヨーグルト"],
        "豆腐・納豆": ["豆腐", "納豆"],
        "主食": ["食パン", "そば", "うどん"],
        "果物": ["りんご", "バナナ"],
    }

    meals = _extract_meals_from_plan(plan)
    items = []
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)

    for meal_text in meals:
        matched_keys = []

        for key in sorted_keys:
            if key in meal_text:
                if any(key in matched for matched in matched_keys):
                    continue

                items.extend(mapping[key])
                matched_keys.append(key)

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

        amount = _shopping_amount(item, count)
        result[category].append(f"{item} × {amount}")

    return result


def generate_smart_shopping_list(plan, fridge_items=None):
    return generate_supermarket_shopping_list(plan, fridge_items)


def generate_weekly_shopping_list(week_plan, fridge_items=None):
    return generate_supermarket_shopping_list(week_plan, fridge_items)


def generate_shopping_list_from_week(weekly_plan):
    return generate_supermarket_shopping_list(
        weekly_plan,
        fridge_items=st.session_state.get("fridge_items", []),
    )


def get_local_deals():
    return {}


def add_deals_to_shopping(shopping):
    return shopping


# ==================================================
# 記録
# ==================================================

def parse_meal_sections(text):
    result = {"朝": "", "昼": "", "夜": "", "間食": ""}

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


def _logs_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"diet_logs_{user_id}"


def load_diet_logs(user_id=None):
    return st.session_state.get(_logs_key(user_id), [])


def save_diet_log(user_id=None, log=None, **kwargs):
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


load_user_logs = load_diet_logs
save_user_log = save_diet_log
save_log = save_diet_log


def get_initial_log_values(user_id=None):
    settings = load_user_settings(user_id)
    latest = load_latest_log(user_id)

    weight = None
    body_fat = None

    if isinstance(latest, dict):
        weight = latest.get("weight")
        body_fat = latest.get("body_fat")

    if weight is None:
        weight = settings.get("current_weight") or settings.get("start_weight") or 50

    if body_fat is None:
        body_fat = settings.get("current_body_fat") or settings.get("start_body_fat") or 30

    return {"weight": weight, "body_fat": body_fat}


# ==================================================
# 今日のプラン保存
# ==================================================

def _today_plan_key(user_id=None):
    user_id = user_id or get_user_id() or "guest"
    return f"today_plan_{user_id}_{jst_today()}"


def save_today_plan(user_id=None, plan=None, **kwargs):
    if isinstance(user_id, dict) and plan is None:
        plan = user_id
        user_id = None

    if plan is None:
        plan = {}

    if kwargs:
        plan.update(kwargs)

    st.session_state[_today_plan_key(user_id)] = plan
    return True


def load_today_plan(user_id=None):
    return st.session_state.get(_today_plan_key(user_id), {})


# ==================================================
# 写真で記録
# ==================================================

def detect_meal_type_by_time(now=None):
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
    user_id = user_id or get_user_id() or "guest"

    key = _photo_logs_key(user_id)

    if key not in st.session_state:
        st.session_state[key] = []

    image_bytes = None
    image_name = ""
    image_type = ""

    if image_file is not None:
        image_bytes = image_file.getvalue()
        image_name = getattr(image_file, "name", "")
        image_type = getattr(image_file, "type", "")

    record = {
        "log_date": jst_today_str(),
        "meal_type": meal_type,
        "food_text": food_text,
        "image_name": image_name,
        "image_type": image_type,
        "image_bytes": image_bytes,
        "created_at": jst_now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    st.session_state[key].append(record)

    save_diet_log(
        user_id,
        {
            "log_date": jst_today_str(),
            "meal_memo": f"{meal_type}：{food_text}",
            "photo_meal_type": meal_type,
            "has_photo": image_file is not None,
            "created_at": jst_now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    return True


def load_photo_logs(user_id=None):
    return st.session_state.get(_photo_logs_key(user_id), [])


# ==================================================
# 相談
# ==================================================

CATEGORY_OPTIONS = ["食事", "運動", "体調", "外食調整"]


def normalize_consult_settings(settings):
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

    if isinstance(settings.get("constitution_traits"), str):
        settings["constitution_traits"] = text_to_list(settings.get("constitution_traits", ""))

    return settings


def _safe_float_for_consult(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def get_support_focus_summary(settings=None, latest_log=None):
    settings = normalize_consult_settings(settings or {})

    points = []
    today_conditions = []

    if isinstance(latest_log, dict):
        raw_conditions = latest_log.get("today_conditions", [])

        if isinstance(raw_conditions, list):
            today_conditions = raw_conditions
        elif isinstance(raw_conditions, str):
            today_conditions = text_to_list(raw_conditions)

        condition_note = latest_log.get("condition_note", "")

        if condition_note and not today_conditions:
            today_conditions = text_to_list(condition_note)

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

    points = list(dict.fromkeys(points))

    return {"points": points, "today_conditions": today_conditions}


def generate_answer(category, question, settings=None, latest_log=None):
    settings = normalize_consult_settings(settings or {})
    focus = get_support_focus_summary(settings, latest_log)

    question = question.strip() if question else ""

    if not question:
        question = "今日どう整えればいい？"

    points_text = "、".join(focus["points"]) if focus["points"] else "基本の整え"
    conditions_text = "、".join(focus["today_conditions"]) if focus["today_conditions"] else "特になし"

    fridge_items = settings.get("fridge_items", "")
    avoid_foods = settings.get("avoid_foods", "")
    workout_today = settings.get("workout_today", "ストレッチ")

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
            answer += "例：小さめおにぎり＋味噌汁＋豆腐・卵・魚のどれか。\n"
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
            answer += "首・肩・股関節まわりのストレッチを5〜10分で十分です。\n"
        elif "むくみあり" in focus["today_conditions"]:
            answer += "むくみがある日は、軽く歩くか、足首回し・ふくらはぎ伸ばしがおすすめです。\n"
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
        answer += "・夜が重い日は昼を軽めにする\n"

        return answer

    return base + "今日は無理せず、食事・運動・睡眠を少しずつ整えましょう。"


# ==================================================
# その他互換
# ==================================================

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
        exercise="ストレッチ",
    )


def get_openai_client():
    return None
