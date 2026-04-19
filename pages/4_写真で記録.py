import streamlit as st
import base64
import json
from pathlib import Path
from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    jst_today_str,
    jst_today,
    jst_now,
    load_user_settings,
    load_latest_log,
    build_food_evaluation_from_text,
)

require_login()

st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon="📷",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .sm-hero {
        background: linear-gradient(135deg, #fff9f3 0%, #fffdf9 100%);
        border: 1px solid #f0e4d8;
        border-radius: 20px;
        padding: 14px 14px 11px 14px;
        margin-top: 0.2rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
    }
    .sm-hero-title {
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .sm-hero-sub {
        color: #6b6b6b;
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .sm-card {
        background: #ffffff;
        border: 1px solid #eee5db;
        border-radius: 18px;
        padding: 14px 13px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .sm-card-soft {
        background: #fffdf9;
    }
    .sm-title {
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .sm-sub {
        color: #6b6b6b;
        font-size: 0.86rem;
        line-height: 1.45;
    }
    .sm-note {
        background: #fffaf5;
        border: 1px dashed #ead7bf;
        border-radius: 14px;
        padding: 10px 11px;
        margin: 8px 0 10px 0;
        color: #6d6152;
        font-size: 0.84rem;
        line-height: 1.55;
    }
    .sm-balance {
        display:inline-block;
        padding: 6px 10px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        font-size: 0.84rem;
        border: 1px solid #e4ddd3;
        background: #faf8f5;
    }
    .sm-ok {
        background: #f0f7f0;
        border-color: #cfe3cf;
    }
    .sm-ng {
        background: #faf1f1;
        border-color: #e9caca;
    }
    .stButton > button {
        border-radius: 12px !important;
        min-height: 42px;
        border: 1px solid #e7d8c8 !important;
        width: 100%;
        font-size: 0.92rem !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #eee3d7;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 10px;
        background: #fffdf9;
    }
    h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.55rem !important;
        font-size: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user_id = get_user_id()
settings = load_user_settings(user_id)
latest_log = load_latest_log(user_id)
today_str = jst_today_str()


def show_saved_illustration(path_str: str, caption: str = ""):
    path = Path(path_str)
    if path.exists():
        st.image(str(path), caption=caption if caption else None, use_container_width=True)


def get_openai_client():
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError(
            "openai パッケージが見つかりません。requirements.txt に openai を追加してください。"
        ) from e

    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("Streamlit Secrets に OPENAI_API_KEY が設定されていません。")

    return OpenAI(api_key=api_key)


def uploaded_file_to_data_url(uploaded_file) -> str:
    mime_type = uploaded_file.type or "image/jpeg"
    file_bytes = uploaded_file.getvalue()
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def get_time_hint_label() -> str:
    hour = jst_now().hour
    if 4 <= hour <= 10:
        return "朝"
    if 11 <= hour <= 15:
        return "昼"
    if 16 <= hour <= 22:
        return "夜"
    return "間食"


def parse_meal_sections_from_text(meal_memo: str) -> dict:
    text = (meal_memo or "").strip()
    result = {"朝": "", "昼": "", "夜": "", "間食": ""}

    lines = text.splitlines()
    current_key = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("朝:"):
            current_key = "朝"
            result[current_key] = line.replace("朝:", "", 1).strip()
        elif line.startswith("昼:"):
            current_key = "昼"
            result[current_key] = line.replace("昼:", "", 1).strip()
        elif line.startswith("夜:"):
            current_key = "夜"
            result[current_key] = line.replace("夜:", "", 1).strip()
        elif line.startswith("間食:"):
            current_key = "間食"
            result[current_key] = line.replace("間食:", "", 1).strip()
        else:
            if current_key:
                if result[current_key]:
                    result[current_key] += " " + line
                else:
                    result[current_key] = line

    return result


def get_today_meal_history_hint(latest_log_dict: dict | None, today_date_str: str) -> str:
    if not latest_log_dict:
        return "今日の記録ヒント: まだ今日の食事記録はありません。"

    log_date = str(latest_log_dict.get("log_date", "")).strip()
    if log_date != today_date_str:
        return "今日の記録ヒント: まだ今日の食事記録はありません。"

    sections = parse_meal_sections_from_text(str(latest_log_dict.get("meal_memo", "")))
    parts = []

    for slot in ["朝", "昼", "夜", "間食"]:
        value = sections.get(slot, "").strip()
        if value:
            parts.append(f"{slot}は記録あり（{value}）")
        else:
            parts.append(f"{slot}は未記録")

    return " / ".join(parts)


def normalize_multi(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        raw = v.strip()
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]
    if isinstance(v, (list, tuple, set)):
        return [str(item).strip() for item in v if str(item).strip()]
    return []


def get_constitution_traits(settings_dict: dict) -> list[str]:
    return normalize_multi(settings_dict.get("constitution_traits", []))


def get_today_conditions_from_latest_log(latest_log_dict: dict | None) -> list[str]:
    if not latest_log_dict:
        return []
    return normalize_multi(latest_log_dict.get("today_conditions", []))


def read_meal_text_from_image(uploaded_file, meal_type_hint: str = "") -> str:
    client = get_openai_client()
    image_data_url = uploaded_file_to_data_url(uploaded_file)

    hint_text = f"参考の食事区分ヒント: {meal_type_hint}" if meal_type_hint else "食事区分ヒントなし"

    prompt = f"""
あなたは主婦向け食事記録アプリの補助AIです。
画像を見て、食事内容を日本語で短く下書きしてください。

条件:
- 推定でよいが、見えているもの中心
- 余計な説明は書かない
- 箇条書きではなく、読点「、」でつなぐ
- 分からないものは無理に断定しない
- 量や栄養評価は書かない
- 出力は食事内容の1行だけ
- {hint_text}

出力例:
しらすおにぎり、ゆで卵、わかめときのこの味噌汁、ブルーベリー
"""

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
    )
    return (response.output_text or "").strip()


def guess_meal_slot_from_image(uploaded_file, time_hint: str = "", history_hint: str = "") -> str:
    client = get_openai_client()
    image_data_url = uploaded_file_to_data_url(uploaded_file)

    prompt = f"""
あなたは主婦向け食事記録アプリの補助AIです。
画像を見て、次の4択から最も近い食事区分を1つだけ返してください。

選択肢:
朝
昼
夜
間食

追加情報:
- 現在時刻からの参考ヒント: {time_hint}
- 今日の記録状況: {history_hint}

判断ルール:
- 出力は上の4つのうち1語だけ
- 説明は不要
- 飲み物だけ、デザート、お菓子、軽食なら「間食」寄り
- 定食、お弁当、しっかりした1食なら「朝・昼・夜」から選ぶ
- 迷うときは画像内容を最優先
- 次に今日の記録状況を見る
- それでも迷うときは時間帯ヒントを参考にする
"""

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
    )

    slot = (response.output_text or "").strip()
    if slot not in ["朝", "昼", "夜", "間食"]:
        return time_hint if time_hint in ["朝", "昼", "夜", "間食"] else "夜"
    return slot


def analyze_meal_balance_from_image(uploaded_file) -> dict:
    client = get_openai_client()
    image_data_url = uploaded_file_to_data_url(uploaded_file)

    prompt = """
あなたは主婦向け食事記録アプリの補助AIです。
画像を見て、食事バランスの目安をJSONで返してください。

返すキーは必ず以下:
{
  "main_food": true,
  "protein": true,
  "vegetables": true,
  "soup": true,
  "heavy": false,
  "sweet": false,
  "fried": false,
  "comment": "20文字以内の短い一言"
}

ルール:
- main_food は ごはん、パン、麺、おにぎりなど
- protein は 卵、魚、肉、豆腐、納豆、ヨーグルトなど
- vegetables は サラダ、野菜、副菜、海藻、きのこなど
- soup は 味噌汁、スープ、汁物
- heavy は 全体的に重め・こってり・量が多そうな印象
- sweet は デザート、甘い飲み物、スイーツ中心
- fried は 揚げ物が目立つ
- comment は短く自然な日本語
- JSON以外は出力しない
"""

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
    )

    raw = (response.output_text or "").strip()

    try:
        data = json.loads(raw)
    except Exception:
        data = {
            "main_food": False,
            "protein": False,
            "vegetables": False,
            "soup": False,
            "heavy": False,
            "sweet": False,
            "fried": False,
            "comment": "写真から目安を見ました",
        }

    return {
        "main_food": bool(data.get("main_food", False)),
        "protein": bool(data.get("protein", False)),
        "vegetables": bool(data.get("vegetables", False)),
        "soup": bool(data.get("soup", False)),
        "heavy": bool(data.get("heavy", False)),
        "sweet": bool(data.get("sweet", False)),
        "fried": bool(data.get("fried", False)),
        "comment": str(data.get("comment", "写真から目安を見ました")).strip(),
    }


def suggest_buy_item(balance: dict, meal_type_hint: str = "", settings_dict: dict | None = None, latest_log_dict: dict | None = None) -> str:
    meal_type_hint = (meal_type_hint or "").strip()
    traits = get_constitution_traits(settings_dict or {})
    conditions = get_today_conditions_from_latest_log(latest_log_dict)

    if "むくみやすい" in traits or "むくみあり" in conditions:
        if not balance.get("vegetables", False):
            return "買うなら：カットサラダ or ミニトマト"
        if not balance.get("soup", False):
            return "買うなら：わかめスープ or 味噌汁"

    if "冷えやすい" in traits and not balance.get("soup", False):
        return "買うなら：味噌汁 or 温かいスープ"

    if ("疲れやすい" in traits or "寝不足" in conditions or "だるい" in conditions) and not balance.get("protein", False):
        return "買うなら：ヨーグルト or サラダチキン"

    if ("胃腸がゆらぎやすい" in traits or "食べすぎた" in conditions) and not balance.get("soup", False):
        return "買うなら：やさしいスープ or 味噌汁"

    if not balance.get("protein", False):
        if meal_type_hint == "朝ごはん":
            return "買うなら：ゆで卵 or ヨーグルト"
        return "買うなら：サラダチキン or 冷ややっこ"

    if not balance.get("vegetables", False):
        return "買うなら：カットサラダ or ミニトマト"

    if not balance.get("soup", False):
        return "買うなら：即席味噌汁 or スープ"

    if not balance.get("main_food", False) and meal_type_hint != "間食":
        return "買うなら：おにぎり or 小さいごはん"

    return "買い足しは今はなくても大丈夫です"


def suggest_home_item(balance: dict, meal_type_hint: str = "", settings_dict: dict | None = None, latest_log_dict: dict | None = None) -> str:
    traits = get_constitution_traits(settings_dict or {})
    conditions = get_today_conditions_from_latest_log(latest_log_dict)

    if "冷えやすい" in traits and not balance.get("soup", False):
        return "家にあれば：味噌汁 or 温かいお茶"

    if ("むくみやすい" in traits or "むくみあり" in conditions) and not balance.get("vegetables", False):
        return "家にあれば：トマト or 野菜を少し"

    if ("疲れやすい" in traits or "寝不足" in conditions) and not balance.get("protein", False):
        return "家にあれば：卵 or 豆腐を1つ"

    if ("胃腸がゆらぎやすい" in traits or "食べすぎた" in conditions) and not balance.get("soup", False):
        return "家にあれば：スープ or 味噌汁を1杯"

    if not balance.get("protein", False):
        return "家にあれば：卵 or 豆腐を1つ"

    if not balance.get("vegetables", False):
        return "家にあれば：野菜を少し"

    if not balance.get("soup", False):
        return "家にあれば：味噌汁 or スープ"

    if not balance.get("main_food", False) and meal_type_hint != "間食":
        return "家にあれば：ごはん少し"

    return "家にあるもので無理に足さなくてもOKです"


def suggest_one_reduction(balance: dict, meal_type_hint: str = "", settings_dict: dict | None = None, latest_log_dict: dict | None = None) -> str:
    traits = get_constitution_traits(settings_dict or {})
    conditions = get_today_conditions_from_latest_log(latest_log_dict)

    if ("むくみやすい" in traits or "むくみあり" in conditions) and balance.get("heavy", False):
        return "減らすなら：こってり系を少し"
    if ("胃腸がゆらぎやすい" in traits or "食べすぎた" in conditions) and balance.get("heavy", False):
        return "減らすなら：量を少し"
    if balance.get("fried", False):
        return "減らすなら：揚げ物を少し"
    if balance.get("sweet", False) and meal_type_hint == "間食":
        return "減らすなら：甘いものを少し"
    if balance.get("heavy", False):
        return "減らすなら：主食かこってり系を少し"
    return "今は無理に減らさなくてもOKです"


def build_personal_hint_text(settings_dict: dict | None = None, latest_log_dict: dict | None = None) -> str:
    traits = get_constitution_traits(settings_dict or {})
    conditions = get_today_conditions_from_latest_log(latest_log_dict)
    hints = []

    if "冷えやすい" in traits:
        hints.append("冷えやすい体質寄り")
    if "むくみやすい" in traits:
        hints.append("むくみやすい体質寄り")
    if "疲れやすい" in traits:
        hints.append("疲れやすい体質寄り")
    if "胃腸がゆらぎやすい" in traits:
        hints.append("胃腸にやさしい方が合いやすい")
    if "寝不足" in conditions:
        hints.append("今日は寝不足寄り")
    if "だるい" in conditions:
        hints.append("今日はだるさあり")
    if "むくみあり" in conditions:
        hints.append("今日はむくみあり")
    if "食べすぎた" in conditions:
        hints.append("今日は食べすぎ後の調整日")

    if not hints:
        return ""
    return " / ".join(hints[:3])


def render_balance_badges(balance: dict, meal_type_hint: str = "", settings_dict: dict | None = None, latest_log_dict: dict | None = None):
    labels = [
        ("主食", balance.get("main_food", False)),
        ("たんぱく質", balance.get("protein", False)),
        ("野菜", balance.get("vegetables", False)),
        ("汁物", balance.get("soup", False)),
    ]

    html = []
    for label, ok in labels:
        cls = "sm-ok" if ok else "sm-ng"
        mark = "あり" if ok else "なし"
        html.append(f'<span class="sm-balance {cls}">{label}: {mark}</span>')

    st.markdown("".join(html), unsafe_allow_html=True)

    comment = balance.get("comment", "").strip()
    if comment:
        st.caption(comment)

    personal_hint = build_personal_hint_text(settings_dict=settings_dict, latest_log_dict=latest_log_dict)
    if personal_hint:
        st.markdown(f'<div class="sm-note">反映中：{personal_hint}</div>', unsafe_allow_html=True)

    st.info(suggest_buy_item(balance, meal_type_hint, settings_dict, latest_log_dict))
    st.info(suggest_home_item(balance, meal_type_hint, settings_dict, latest_log_dict))
    st.warning(suggest_one_reduction(balance, meal_type_hint, settings_dict, latest_log_dict))


def preset_text_by_type(meal_type: str, meal_text: str) -> tuple[str, str, str, str]:
    breakfast = ""
    lunch = ""
    dinner = ""
    snack = ""

    if meal_type == "朝ごはん":
        breakfast = meal_text
    elif meal_type == "昼ごはん":
        lunch = meal_text
    elif meal_type == "夜ごはん":
        dinner = meal_text
    elif meal_type == "間食":
        snack = meal_text

    return breakfast, lunch, dinner, snack


def apply_draft_to_log_fields(target_slot: str, meal_draft: str):
    if target_slot == "朝":
        st.session_state["photo_log_breakfast"] = meal_draft
    elif target_slot == "昼":
        st.session_state["photo_log_lunch"] = meal_draft
    elif target_slot == "夜":
        st.session_state["photo_log_dinner"] = meal_draft
    elif target_slot == "間食":
        st.session_state["photo_log_snack"] = meal_draft


show_saved_illustration("assets/home_icons/photo.png")

st.markdown(
    """
    <div class="sm-hero">
        <div class="sm-hero-title">📷 写真で記録</div>
        <div class="sm-hero-sub">
            写真から下書きしたり、バランスを見たりしながら、
            食事や体重の記録をラクに残せます。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    ["🍽 この食事を評価", "📝 食べたものを記録", "⚖ 体重計を記録"]
)

with tab1:
    st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
    show_saved_illustration("assets/home_icons/advice.png")
    st.markdown('<div class="sm-title">この食事を評価</div>', unsafe_allow_html=True)
    st.markdown('<div class="sm-sub">写真から内容を下書きして、食事バランスを見られます。</div>', unsafe_allow_html=True)

    eval_meal_type = st.radio(
        "食事区分",
        ["朝ごはん", "昼ごはん", "夜ごはん", "間食"],
        horizontal=True,
        key="eval_meal_type",
    )

    eval_camera = st.camera_input("食事の写真を撮る", key="eval_camera_input")
    eval_upload = st.file_uploader(
        "食事写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="eval_photo_upload",
    )
    selected_eval_image = eval_camera if eval_camera is not None else eval_upload

    if selected_eval_image is not None:
        st.image(selected_eval_image, caption="評価したい食事", use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📷 写真から食事内容を読む", use_container_width=True, key="read_meal_from_photo"):
            if selected_eval_image is None:
                st.warning("先に写真を撮るか、アップロードしてください。")
            else:
                try:
                    with st.spinner("写真から食事内容を読み取っています..."):
                        st.session_state["eval_meal_text"] = read_meal_text_from_image(selected_eval_image, eval_meal_type)
                    st.success("写真から下書きを入れました")
                except Exception as e:
                    st.error(f"写真の読み取りに失敗しました: {e}")

    with col_b:
        if st.button("🥗 バランスを見る", use_container_width=True, key="analyze_eval_balance"):
            if selected_eval_image is None:
                st.warning("先に写真を撮るか、アップロードしてください。")
            else:
                try:
                    with st.spinner("バランスを見ています..."):
                        st.session_state["eval_balance_result"] = analyze_meal_balance_from_image(selected_eval_image)
                    st.success("写真から目安を出しました")
                except Exception as e:
                    st.error(f"バランス確認に失敗しました: {e}")

    if "eval_balance_result" in st.session_state:
        with st.expander("写真から見た目安を見る", expanded=True):
            render_balance_badges(
                st.session_state["eval_balance_result"],
                meal_type_hint=eval_meal_type,
                settings_dict=settings,
                latest_log_dict=latest_log,
            )

    eval_meal_text = st.text_area(
        "この食事の内容",
        placeholder="例：しらすおにぎり、ゆで卵、味噌汁、ブルーベリー",
        height=110,
        key="eval_meal_text",
    )

    with st.expander("朝・昼・夜・間食で整理して入力したい場合"):
        default_breakfast, default_lunch, default_dinner, default_snack = preset_text_by_type(
            eval_meal_type, eval_meal_text
        )
        st.text_area("朝", value=default_breakfast, height=70, key="eval_breakfast")
        st.text_area("昼", value=default_lunch, height=70, key="eval_lunch")
        st.text_area("夜", value=default_dinner, height=70, key="eval_dinner")
        st.text_area("間食", value=default_snack, height=70, key="eval_snack")

    with st.expander("補足メモを入れる"):
        eval_note = st.text_area(
            "補足メモ",
            placeholder="例：外食予定 / 軽めにしたい / ヨガ前 など",
            height=90,
            key="eval_note",
        )

    if st.button("この食事を評価する", use_container_width=True, key="run_meal_eval"):
        sections_text = "\n".join(
            [
                f"朝: {st.session_state.get('eval_breakfast', '').strip()}",
                f"昼: {st.session_state.get('eval_lunch', '').strip()}",
                f"夜: {st.session_state.get('eval_dinner', '').strip()}",
                f"間食: {st.session_state.get('eval_snack', '').strip()}",
            ]
        )
        base_text = eval_meal_text.strip()
        merged_note = st.session_state.get("eval_note", "").strip()
        has_section_input = sections_text.replace("朝: ", "").replace("昼: ", "").replace("夜: ", "").replace("間食: ", "").strip()

        if has_section_input:
            if merged_note:
                merged_note += "\n"
            merged_note += "食事の流れメモ:\n" + sections_text

        st.session_state["meal_eval_result"] = build_food_evaluation_from_text(
            meal_type=eval_meal_type,
            meal_text=base_text,
            settings=settings,
            latest_log=latest_log,
            note=merged_note,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if "meal_eval_result" in st.session_state:
        with st.expander("評価結果を見る", expanded=True):
            result = st.session_state["meal_eval_result"]
            st.info(result["title"])
            st.markdown(result["body"].replace("\n", "  \n"))

with tab2:
    st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
    show_saved_illustration("assets/home_icons/diet.png")
    st.markdown('<div class="sm-title">食べたものを記録</div>', unsafe_allow_html=True)
    st.markdown('<div class="sm-sub">写真から下書きして、朝・昼・夜・間食に記録します。</div>', unsafe_allow_html=True)

    log_camera = st.camera_input("食べたものを撮る", key="log_camera_input")
    log_upload = st.file_uploader(
        "食事写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="log_photo_upload",
    )
    selected_log_image = log_camera if log_camera is not None else log_upload

    if selected_log_image is not None:
        st.image(selected_log_image, caption="記録する食事写真", use_container_width=True)

    mode = st.radio(
        "下書きの入れ方",
        ["自分で選ぶ", "AIにまかせる"],
        horizontal=True,
        key="log_fill_mode",
    )

    if mode == "自分で選ぶ":
        log_target_slot = st.radio(
            "入れる場所",
            ["朝", "昼", "夜", "間食"],
            horizontal=True,
            index=2,
            key="log_target_slot",
        )
        log_hint_for_balance = log_target_slot
    else:
        time_hint = get_time_hint_label()
        history_hint = get_today_meal_history_hint(latest_log, today_str)
        st.markdown(
            f'<div class="sm-note">AIが写真＋時間帯ヒント（今は「{time_hint}」寄り）＋今日の記録状況で推定します。<br>{history_hint}</div>',
            unsafe_allow_html=True,
        )
        log_target_slot = None
        log_hint_for_balance = st.session_state.get("last_guessed_slot", "")

    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("📷 写真から下書きする", use_container_width=True, key="read_log_meal_from_photo"):
            if selected_log_image is None:
                st.warning("先に写真を撮るか、アップロードしてください。")
            else:
                try:
                    with st.spinner("写真から食事内容を読み取っています..."):
                        if mode == "AIにまかせる":
                            guessed_slot = guess_meal_slot_from_image(
                                selected_log_image,
                                time_hint=get_time_hint_label(),
                                history_hint=get_today_meal_history_hint(latest_log, today_str),
                            )
                            meal_draft = read_meal_text_from_image(selected_log_image, f"{guessed_slot}の記録")
                            apply_draft_to_log_fields(guessed_slot, meal_draft)
                            st.session_state["last_guessed_slot"] = guessed_slot
                            st.success(f"AIが「{guessed_slot}」と判断して下書きを入れました。")
                        else:
                            meal_draft = read_meal_text_from_image(selected_log_image, f"{log_target_slot}の記録")
                            apply_draft_to_log_fields(log_target_slot, meal_draft)
                            st.success(f"{log_target_slot}の欄に下書きを入れました。")
                except Exception as e:
                    st.error(f"写真の読み取りに失敗しました: {e}")

    with btn2:
        if st.button("🥗 バランスを見る", use_container_width=True, key="analyze_log_balance"):
            if selected_log_image is None:
                st.warning("先に写真を撮るか、アップロードしてください。")
            else:
                try:
                    with st.spinner("バランスを見ています..."):
                        st.session_state["log_balance_result"] = analyze_meal_balance_from_image(selected_log_image)
                    st.success("写真から目安を出しました")
                except Exception as e:
                    st.error(f"バランス確認に失敗しました: {e}")

    if "log_balance_result" in st.session_state:
        with st.expander("写真から見た目安を見る", expanded=True):
            balance_hint = st.session_state.get("last_guessed_slot", log_hint_for_balance)
            render_balance_badges(
                st.session_state["log_balance_result"],
                meal_type_hint=balance_hint,
                settings_dict=settings,
                latest_log_dict=latest_log,
            )

    with st.expander("朝・昼・夜・間食を入力する", expanded=True):
        breakfast_text = st.text_area("朝", placeholder="例：納豆ごはん、味噌汁", height=80, key="photo_log_breakfast")
        lunch_text = st.text_area("昼", placeholder="例：鮭おにぎり、味噌汁", height=80, key="photo_log_lunch")
        dinner_text = st.text_area("夜", placeholder="例：焼き魚、サラダ、ごはん少なめ", height=80, key="photo_log_dinner")
        snack_text = st.text_area("間食", placeholder="例：ヨーグルト、チョコ2個", height=80, key="photo_log_snack")

    with st.expander("補足メモを入れる"):
        log_note = st.text_area(
            "補足メモ",
            placeholder="例：外食 / 軽め / 運動前後 / 写真あり など",
            height=90,
            key="photo_log_note",
        )

    st.markdown(
        """
        <div class="sm-note">
        朝は起きてから2時間以内、間食は夕方まで、
        夜は寝る直前を避けると整えやすいです。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("食べたものを記録する", use_container_width=True, key="save_photo_meal_log"):
        lines = [
            f"朝: {st.session_state.get('photo_log_breakfast', '').strip()}",
            f"昼: {st.session_state.get('photo_log_lunch', '').strip()}",
            f"夜: {st.session_state.get('photo_log_dinner', '').strip()}",
            f"間食: {st.session_state.get('photo_log_snack', '').strip()}",
        ]

        log_note_text = st.session_state.get("photo_log_note", "").strip()
        if log_note_text:
            lines.append("")
            lines.append(f"補足: {log_note_text}")

        meal_memo = "\n".join(lines)

        save_data = {
            "log_date": jst_today_str(),
            "weight": 0.0,
            "body_fat": 0.0,
            "meal_memo": meal_memo,
            "exercise_memo": "",
            "condition_note": "",
            "mood_note": "",
            "today_conditions": [],
        }

        try:
            save_diet_log(user_id, save_data)
            st.success("食事記録を保存しました")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="sm-card sm-card-soft">', unsafe_allow_html=True)
    show_saved_illustration("assets/home_icons/settings.png")
    st.markdown('<div class="sm-title">体重計を記録</div>', unsafe_allow_html=True)
    st.markdown('<div class="sm-sub">体重計の写真と数値を使って、今日の記録に残します。</div>', unsafe_allow_html=True)

    scale_camera = st.camera_input("体重計を撮る", key="scale_camera_input")
    scale_upload = st.file_uploader(
        "体重計写真をアップロード",
        type=["jpg", "jpeg", "png"],
        key="scale_photo_upload",
    )
    selected_scale_image = scale_camera if scale_camera is not None else scale_upload

    if selected_scale_image is not None:
        st.image(selected_scale_image, caption="体重計写真", use_container_width=True)

    with st.expander("数値を入力する", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input(
                "体重(kg)",
                min_value=0.0,
                max_value=200.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                key="scale_weight_input",
            )
        with col2:
            body_fat = st.number_input(
                "体脂肪(%)",
                min_value=0.0,
                max_value=70.0,
                value=0.0,
                step=0.1,
                format="%.1f",
                key="scale_bodyfat_input",
            )

    with st.expander("補足メモを入れる"):
        scale_note = st.text_area(
            "補足メモ",
            placeholder="例：朝いち / 入浴後 / いつもの体重計と差がある など",
            height=100,
            key="scale_note_input",
        )

    if st.button("この数値で記録する", use_container_width=True, key="save_scale_log"):
        save_data = {
            "log_date": jst_today_str(),
            "weight": float(weight),
            "body_fat": float(body_fat),
            "meal_memo": "",
            "exercise_memo": "",
            "condition_note": st.session_state.get("scale_note_input", "").strip(),
            "mood_note": "",
            "today_conditions": [],
        }

        try:
            save_diet_log(user_id, save_data)
            st.success("体重・体脂肪の記録を保存しました")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"記録日：{jst_today().strftime('%Y/%m/%d')}")
