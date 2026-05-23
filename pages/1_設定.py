import streamlit as st
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html


# =========================
# パス・アイコン設定
# =========================
THIS_FILE = Path(__file__).resolve()

if THIS_FILE.parent.name == "pages":
    APP_ROOT = THIS_FILE.parent.parent
else:
    APP_ROOT = THIS_FILE.parent

ICON_DIR = APP_ROOT / "assets" / "icons"


def get_page_icon(filename, fallback="⚙️"):
    path = ICON_DIR / filename
    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            return fallback
    return fallback


# -----------------
# ページ設定
# -----------------
st.set_page_config(
    page_title="設定｜ShufuMate",
    page_icon=get_page_icon("settings.png", "⚙️"),
    layout="centered"
)


# =========================
# 画像読み込み
# =========================
def file_to_base64(path):
    if not path.exists():
        return None

    suffix = path.suffix.lower()

    if suffix == ".png":
        mime = "image/png"
    elif suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def load_icon(filename):
    if not filename:
        return None

    candidates = [
        ICON_DIR / filename,
        APP_ROOT / "assets" / "icons" / filename,
    ]

    for path in candidates:
        if path.exists():
            return file_to_base64(path)

    return None


def safe_text(value):
    return html.escape(str(value))


def safe_html_with_br(value):
    return html.escape(str(value)).replace("\n", "<br>")


# -----------------
# 安全関数
# -----------------
def local_safe_float(value, default):
    try:
        if value is None or value == "":
            return float(default)

        value = str(value).replace(",", "").replace("'", "").strip()
        return float(value)
    except Exception:
        return float(default)


def local_safe_text(value, default=""):
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def local_safe_list(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            x.strip()
            for x in value.replace("、", ",").replace("\n", ",").split(",")
            if x.strip()
        ]

    return []


def option_index(options, value, default=0):
    if value in options:
        return options.index(value)
    return default


def call_optional(func_name, default, *args, **kwargs):
    func = globals().get(func_name)

    if callable(func):
        try:
            return func(*args, **kwargs)
        except Exception:
            return default

    return default


# =========================
# CSS
# =========================
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #fffaf4 0%, #fff4e8 45%, #fffaf4 100%);
    }

    .block-container {
        max-width: 820px;
        padding-top: 3.8rem;
        padding-bottom: 2.5rem;
    }

    .top-card {
        background: #ffffff;
        border-radius: 26px;
        padding: 22px 20px;
        box-shadow: 0 8px 24px rgba(96, 65, 45, 0.10);
        border: 1px solid rgba(139, 100, 72, 0.12);
        margin-bottom: 18px;
    }

    .page-head {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .page-head-icon {
        width: 74px;
        min-width: 74px;
        height: 74px;
        border-radius: 22px;
        background: #fff8ef;
        border: 1px solid rgba(139, 100, 72, 0.12);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.09);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .page-head-icon img {
        width: 58px;
        height: 58px;
        object-fit: contain;
    }

    .page-title {
        font-size: 1.75rem;
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 5px;
    }

    .page-subtitle {
        font-size: 0.95rem;
        color: #7b6658;
        line-height: 1.7;
        font-weight: 600;
    }

    .card {
        background: #ffffff;
        border-radius: 24px;
        padding: 20px 18px;
        box-shadow: 0 6px 18px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
    }

    .section-head {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 26px 0 10px 0;
    }

    .section-head-icon {
        width: 52px;
        min-width: 52px;
        height: 52px;
        border-radius: 17px;
        background: #ffffff;
        border: 1px solid rgba(139, 100, 72, 0.12);
        box-shadow: 0 4px 12px rgba(96, 65, 45, 0.09);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .section-head-icon img {
        width: 40px;
        height: 40px;
        object-fit: contain;
    }

    .section-icon-settings img {
        width: 42px;
        height: 42px;
    }

    .section-icon-state img {
        width: 42px;
        height: 42px;
    }

    .section-icon-food img {
        width: 42px;
        height: 42px;
    }

    .section-icon-exercise img {
        width: 42px;
        height: 42px;
    }

    .section-head-emoji {
        font-size: 1.45rem;
        line-height: 1;
    }

    .section-head-title {
        font-size: 1.2rem;
        font-weight: 900;
        color: #5c4033;
        line-height: 1.2;
    }

    .soft-card {
        background: #fffdf8;
        border-radius: 20px;
        padding: 16px;
        border: 1px solid rgba(139, 100, 72, 0.10);
        color: #6b4c3b;
        font-size: 0.92rem;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .account-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 20px 18px;
        box-shadow: 0 6px 18px rgba(96, 65, 45, 0.08);
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-bottom: 18px;
    }

    .note-card {
        background: #fff8ef;
        border-radius: 20px;
        padding: 14px 16px;
        color: #7b6658;
        font-size: 0.88rem;
        line-height: 1.7;
        border: 1px solid rgba(139, 100, 72, 0.10);
        margin-top: 14px;
        margin-bottom: 18px;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #8d6e63;
        color: #ffffff;
        border: none;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 800;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #76594f;
        color: #ffffff;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        color: #5c4033;
        font-weight: 700;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.2rem;
        }

        .top-card {
            padding: 18px 16px;
        }

        .page-head-icon {
            width: 62px;
            min-width: 62px;
            height: 62px;
            border-radius: 19px;
        }

        .page-head-icon img {
            width: 48px;
            height: 48px;
        }

        .page-title {
            font-size: 1.45rem;
        }

        .page-subtitle {
            font-size: 0.88rem;
        }

        .section-head-icon {
            width: 46px;
            min-width: 46px;
            height: 46px;
            border-radius: 15px;
        }

        .section-head-icon img {
            width: 35px;
            height: 35px;
        }

        .section-head-title {
            font-size: 1.08rem;
        }
    }
</style>
""",
    unsafe_allow_html=True
)


# =========================
# 表示用関数
# =========================
def render_page_header(title, subtitle, icon_file="settings.png"):
    icon_src = load_icon(icon_file)

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = '<div class="section-head-emoji">⚙️</div>'

    st.markdown(
        f"""
<div class="top-card">
    <div class="page-head">
        <div class="page-head-icon">
            {icon_html}
        </div>
        <div>
            <div class="page-title">{safe_text(title)}</div>
            <div class="page-subtitle">{safe_html_with_br(subtitle)}</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_header(title, icon_file=None, emoji=""):
    icon_src = load_icon(icon_file) if icon_file else None

    icon_class = ""
    if icon_file:
        icon_name = Path(icon_file).stem
        icon_class = f"section-icon-{icon_name}"

    if icon_src:
        icon_html = f'<img src="{icon_src}" alt="{safe_text(title)}">'
    else:
        icon_html = f'<div class="section-head-emoji">{safe_text(emoji)}</div>'

    st.markdown(
        f"""
<div class="section-head">
    <div class="section-head-icon {icon_class}">
        {icon_html}
    </div>
    <div class="section-head-title">{safe_text(title)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_note(text):
    st.markdown(
        f"""
<div class="note-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


# =========================
# ログインチェック
# =========================
require_login()
user_id = get_user_id()


# =========================
# データ読み込み
# =========================
try:
    settings = load_user_settings(user_id)
except Exception:
    st.warning("設定の読み込みに失敗しました。初期値で表示します。")
    settings = {}

profile = call_optional("load_current_user_profile", {}, user_id)

if not isinstance(settings, dict):
    settings = {}

if not isinstance(profile, dict):
    profile = {}

nickname_default = (
    profile.get("nickname")
    or settings.get("nickname")
    or user_id
)

login_id_text = profile.get("login_id") or user_id
birth_date_text = profile.get("birth_date") or "未設定"

age_val = profile.get("age")
age_text = f"{age_val}歳" if age_val is not None else "未設定"


# =========================
# ヘッダー
# =========================
render_page_header(
    title="設定",
    subtitle="基本設定・相談の好み・アカウント情報を管理します。",
    icon_file="settings.png",
)


render_note(
    "ここで設定した内容は、HOMEの今日のおすすめ・相談する・献立や運動の提案に使われます。"
)


# =====================
# 基本設定フォーム
# =====================
with st.form("settings_form"):

    render_section_header("基本設定", icon_file="settings.png", emoji="⚙️")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    nickname = st.text_input(
        "ニックネーム",
        value=local_safe_text(nickname_default, user_id)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "生年月日",
            value=local_safe_text(birth_date_text, "未設定"),
            disabled=True
        )

    with col2:
        st.text_input(
            "年齢",
            value=age_text,
            disabled=True
        )

    height_cm = st.number_input(
        "身長(cm)",
        min_value=100.0,
        max_value=220.0,
        value=local_safe_float(settings.get("height_cm"), 155),
        step=0.1
    )

    col3, col4 = st.columns(2)

    with col3:
        current_weight = st.number_input(
            "現在体重(kg)",
            min_value=20.0,
            max_value=150.0,
            value=local_safe_float(
                settings.get("current_weight")
                or settings.get("start_weight"),
                50
            ),
            step=0.1
        )

    with col4:
        target_weight = st.number_input(
            "目標体重(kg)",
            min_value=20.0,
            max_value=150.0,
            value=local_safe_float(settings.get("target_weight"), 48),
            step=0.1
        )

    col5, col6 = st.columns(2)

    with col5:
        current_body_fat = st.number_input(
            "現在体脂肪(%)",
            min_value=5.0,
            max_value=60.0,
            value=local_safe_float(
                settings.get("current_body_fat")
                or settings.get("start_body_fat"),
                30
            ),
            step=0.1
        )

    with col6:
        target_body_fat = st.number_input(
            "目標体脂肪(%)",
            min_value=5.0,
            max_value=60.0,
            value=local_safe_float(settings.get("target_body_fat"), 28),
            step=0.1
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # -----------------
    # 相談・提案の設定
    # -----------------
    render_section_header("相談・提案の設定", icon_file="state.png", emoji="🌿")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    user_type_options = [
        "自分向け",
        "自分＋家族向け",
        "子ども優先",
        "夫も満足",
        "ダイエット重視",
        "節約重視",
        "忙しい日向け",
    ]

    user_type = st.selectbox(
        "利用タイプ",
        user_type_options,
        index=option_index(
            user_type_options,
            settings.get("user_type", "自分向け")
        )
    )

    activity_options = [
        "少なめ",
        "ふつう",
        "多め",
        "ヨガ・ピラティスあり",
        "ウォーキングあり",
        "ランニングあり",
        "筋トレあり",
        "外出多め",
    ]

    activity_level = st.selectbox(
        "活動量",
        activity_options,
        index=option_index(
            activity_options,
            settings.get("activity_level", "ふつう")
        )
    )

    food_style_options = [
        "和食中心",
        "洋食もOK",
        "家族向け",
        "ダイエット重視",
        "節約重視",
        "外食あり",
        "コンビニ活用",
    ]

    food_style = st.selectbox(
        "食事スタイル",
        food_style_options,
        index=option_index(
            food_style_options,
            settings.get("food_style")
            or settings.get("meal_style", "和食中心")
        )
    )

    constitution_options = [
        "冷えやすい",
        "むくみやすい",
        "疲れやすい",
        "寝不足になりやすい",
        "肩こり",
        "便秘気味",
        "胃腸が弱い",
        "甘いものが欲しくなる",
        "外食が多い",
        "運動不足",
    ]

    constitution_traits = st.multiselect(
        "体質・傾向",
        constitution_options,
        default=[
            x for x in local_safe_list(settings.get("constitution_traits"))
            if x in constitution_options
        ]
    )

    advice_tone_options = [
        "やさしく",
        "具体的に",
        "短く",
        "励ましてほしい",
        "はっきり言ってほしい",
    ]

    advice_tone = st.selectbox(
        "アドバイスの言い方",
        advice_tone_options,
        index=option_index(
            advice_tone_options,
            settings.get("advice_tone", "やさしく")
        )
    )

    st.markdown("</div>", unsafe_allow_html=True)


    # -----------------
    # 運動設定
    # -----------------
    render_section_header("運動設定", icon_file="exercise.png", emoji="🏃‍♀️")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    workout_today_options = [
        "ストレッチ",
        "ヨガ",
        "ピラティス",
        "ウォーキング",
        "ランニング",
        "筋トレ",
        "なし",
    ]

    current_workout = settings.get("workout_today", "ストレッチ")

    if current_workout == "有酸素":
        current_workout = "ウォーキング"

    if current_workout not in workout_today_options:
        current_workout = "ストレッチ"

    workout_today = st.selectbox(
        "よくする運動",
        workout_today_options,
        index=workout_today_options.index(current_workout)
    )

    st.markdown("</div>", unsafe_allow_html=True)


    # -----------------
    # 食材・冷蔵庫
    # -----------------
    render_section_header("食材・冷蔵庫", icon_file="food.png", emoji="🍽")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    fridge_items = st.text_area(
        "冷蔵庫にあるもの",
        value=local_safe_text(settings.get("fridge_items"), ""),
        placeholder="例：卵、豆腐、納豆、キャベツ、鮭",
        height=100
    )

    avoid_foods = st.text_area(
        "避けたい食材",
        value=local_safe_text(settings.get("avoid_foods"), ""),
        placeholder="例：辛いもの、揚げ物、牛乳",
        height=80
    )

    favorite_meals = st.text_area(
        "好きな定番メニュー",
        value=local_safe_text(settings.get("favorite_meals"), ""),
        placeholder="例：鮭おにぎり、味噌玉の味噌汁、納豆ごはん",
        height=80
    )

    st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "保存する",
        use_container_width=True
    )


# =====================
# 保存処理
# =====================
if submitted:

    try:
        save_user_settings(
            user_id,
            {
                "nickname": nickname,
                "height_cm": height_cm,
                "current_weight": current_weight,
                "start_weight": settings.get("start_weight") or current_weight,
                "target_weight": target_weight,
                "current_body_fat": current_body_fat,
                "start_body_fat": settings.get("start_body_fat") or current_body_fat,
                "target_body_fat": target_body_fat,
                "user_type": user_type,
                "activity_level": activity_level,
                "food_style": food_style,
                "meal_style": food_style,
                "constitution_traits": constitution_traits,
                "advice_tone": advice_tone,
                "workout_today": workout_today,
                "fridge_items": fridge_items,
                "avoid_foods": avoid_foods,
                "favorite_meals": favorite_meals,
            }
        )

        update_func = globals().get("update_current_user_profile")

        if callable(update_func):
            try:
                update_func(
                    user_id,
                    nickname=nickname
                )
            except Exception:
                pass

        st.success("保存しました")
        st.rerun()

    except Exception:
        st.error("保存に失敗しました。時間をおいてもう一度お試しください。")


# =====================
# アカウント情報
# =====================
render_section_header("アカウント", icon_file="settings.png", emoji="👤")

st.markdown("<div class='account-card'>", unsafe_allow_html=True)

st.text_input(
    "ログインID",
    value=local_safe_text(login_id_text, user_id),
    disabled=True
)

st.markdown("</div>", unsafe_allow_html=True)


# =====================
# パスワード変更
# =====================
render_section_header("パスワード変更", icon_file=None, emoji="🔑")

st.markdown("<div class='account-card'>", unsafe_allow_html=True)

render_note(
    "数字だけのパスワードも使えますが、4文字以上にしてください。"
)

new_pw = st.text_input(
    "新しいパスワード",
    type="password"
)

new_pw2 = st.text_input(
    "確認",
    type="password"
)

if st.button("変更する", use_container_width=True):

    if not new_pw:
        st.warning("パスワードを入力してください")

    elif new_pw != new_pw2:
        st.error("パスワードが一致しません")

    elif len(new_pw) < 4:
        st.warning("パスワードは4文字以上にしてください")

    else:
        try:
            reset_func = globals().get("reset_password")

            if callable(reset_func):
                reset_func(login_id_text, new_pw)
                st.success("パスワードを変更しました")
            else:
                st.error("パスワード変更機能が見つかりません")

        except Exception:
            st.error("パスワード変更に失敗しました。時間をおいてもう一度お試しください。")

st.markdown("</div>", unsafe_allow_html=True)


# =====================
# ログアウト
# =====================
st.markdown("---")

if st.button("ログアウト", use_container_width=True):
    logout()

    try:
        st.switch_page("pages/0_ログイン.py")
    except Exception:
        st.rerun()
