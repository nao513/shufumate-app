# =========================================================
# ShufuMate
# pages/4_写真で記録.py
# AI写真解析・DietLogs保存 完全版
# =========================================================

import base64
import hashlib
import html
import json
import re

import pandas as pd
import streamlit as st
from openai import OpenAI

from app_core import (
    require_login,
    get_user_id,
    get_page_icon,
    inject_shufumate_css,
    render_page_header,
    render_section_header,
    load_diet_dataframe,
    save_diet_log,
    clean_text,
    jst_today_str,
)


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/camera.png",
        "📷",
    ),
    layout="centered",
)


# =========================================================
# 共通
# =========================================================
inject_shufumate_css()
require_login()

user_id = get_user_id()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

.photo-intro {
    background: rgba(255,250,244,.95);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #6e584c;
    line-height: 1.85;
    margin-bottom: 18px;
}

.photo-step {
    background: rgba(255,255,255,.82);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 18px;
    padding: 15px 17px;
    margin: 8px 0 15px;
    color: #665044;
    line-height: 1.75;
}

.photo-result-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,250,243,.98),
            rgba(249,239,227,.98)
        );
    border: 1px solid rgba(139,100,72,.14);
    border-radius: 20px;
    padding: 16px 18px;
    color: #5d473b;
    line-height: 1.75;
    margin-top: 8px;
    margin-bottom: 10px;
}

.photo-result-title {
    color: #5c4033;
    font-weight: 900;
    font-size: 1.03rem;
    margin-bottom: 6px;
}

.photo-score {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: #9b7a69;
    color: white;
    font-size: 1.2rem;
    font-weight: 900;
    margin: 3px 0 9px;
}

.photo-small {
    color: #917b70;
    font-size: .85rem;
    line-height: 1.7;
    margin-top: 10px;
    margin-bottom: 18px;
}

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.60);
    border-radius: 18px;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 15px !important;
}

div[data-testid="stImage"] img {
    border-radius: 17px;
}

@media (max-width: 640px) {

    .photo-intro {
        padding: 15px 16px;
    }

    .photo-step {
        padding: 14px 15px;
    }

    .photo-result-card {
        padding: 17px 18px;
    }
}

    .photo-result-card {
        padding: 14px 16px;
        margin-bottom: 8px;
    }

    .photo-score {
        width: 66px;
        height: 66px;
        font-size: 1.1rem;
    }

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def safe_html(value):

    return html.escape(
        str(value or "")
    )


def safe_html_with_br(value):

    return safe_html(value).replace(
        "\n",
        "<br>"
    )


def uploaded_file_bytes(uploaded_file):

    if uploaded_file is None:
        return None

    return uploaded_file.getvalue()


def image_hash(image_bytes):

    if not image_bytes:
        return ""

    return hashlib.sha256(
        image_bytes
    ).hexdigest()


def image_to_data_url(
    image_bytes,
    mime_type,
):

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    mime_type = (
        mime_type
        or "image/jpeg"
    )

    return (
        f"data:{mime_type};"
        f"base64,{encoded}"
    )


def extract_json(text):

    text = clean_text(text)

    if not text:
        raise ValueError(
            "AIから解析結果を取得できませんでした。"
        )

    # ```json ... ``` 対応
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        return json.loads(text)

    except Exception:
        pass

    # 前後に文章が付いた場合
    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "AI解析結果の形式を読み取れませんでした。"
        )

    return json.loads(
        match.group(0)
    )


# =========================================================
# AI画像解析
# =========================================================
def analyze_meal_photo(
    image_bytes,
    mime_type,
):

    api_key = clean_text(
        st.secrets.get(
            "OPENAI_API_KEY",
            ""
        )
    )

    if not api_key:

        raise ValueError(
            "OPENAI_API_KEY が設定されていません。"
        )

    client = OpenAI(
        api_key=api_key
    )

    data_url = image_to_data_url(
        image_bytes,
        mime_type,
    )

    prompt = """
あなたは食事記録アプリ ShufuMate の食事写真解析AIです。

写真に実際に写っているものを中心に、日本語で食事内容を分析してください。

推測できない食材は断定しないでください。
量やカロリーを写真だけから無理に断定しないでください。

必ず次のJSONだけを返してください。
Markdownや説明文は付けないでください。

{
  "foods": "写真から確認できる料理・食品。修正しやすいよう簡潔に列挙",
  "balance": "主食・たんぱく質・野菜などのバランスについて短く評価",
  "improvement": "次の食事やこの食事に足すとよいものを具体的に短く提案",
  "score": 80
}

scoreは0～100の整数です。
写真だけで判断できない部分については控えめに評価してください。
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": "auto",
                    },
                ],
            }
        ],
    )

    result = extract_json(
        response.output_text
    )

    foods = clean_text(
        result.get(
            "foods",
            ""
        )
    )

    balance = clean_text(
        result.get(
            "balance",
            ""
        )
    )

    improvement = clean_text(
        result.get(
            "improvement",
            ""
        )
    )

    try:

        score = int(
            result.get(
                "score",
                0
            )
        )

    except Exception:

        score = 0

    score = max(
        0,
        min(
            100,
            score,
        )
    )

    if not foods:

        foods = (
            "写真だけでは食事内容を"
            "十分に判定できませんでした。"
        )

    return {
        "foods": foods,
        "balance": balance,
        "improvement": improvement,
        "score": score,
    }


# =========================================================
# 最新体組成
# =========================================================
def latest_body_values():

    try:

        df = load_diet_dataframe(
            user_id
        )

    except Exception:

        return None, None, None

    if (
        df is None
        or df.empty
    ):

        return None, None, None

    if "log_date" in df.columns:

        df = df.sort_values(
            "log_date"
        ).reset_index(
            drop=True
        )

    def get_latest(column):

        if column not in df.columns:
            return None

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        values = values.dropna()

        values = values[
            values > 0
        ]

        if values.empty:
            return None

        return float(
            values.iloc[-1]
        )

    return (
        get_latest("weight"),
        get_latest("body_fat"),
        get_latest("muscle_mass"),
    )


# =========================================================
# Session State
# =========================================================
defaults = {
    "photo_analysis_hash": "",
    "photo_analysis_foods": "",
    "photo_analysis_balance": "",
    "photo_analysis_improvement": "",
    "photo_analysis_score": 0,
    "photo_record_saved": False,
    "photo_record_meal": "",
    "photo_record_food": "",
    "photo_record_note": "",
    "photo_record_date": "",
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# ヘッダー
# =========================================================
render_page_header(
    title="写真で記録",
    subtitle=(
        "食事の写真から内容を自動で読み取り、"
        "かんたんに記録できます。"
    ),
    icon_file=(
        "ShufuMate_home_icons_8/"
        "camera.png"
    ),
    emoji="📷",
)


intro_html = (
    '<div class="photo-intro">'
    '食事の写真を撮るか選ぶと、'
    'ShufuMateが写真を見て食事内容を自動で読み取ります。'
    '結果を確認・修正してから記録できます。'
    '</div>'
)

st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# 写真
# =========================================================
st.markdown(
    '<div style="color:#5c4033; '
    'font-size:1.35rem; font-weight:900; '
    'margin:28px 0 14px;">'
    '食事の写真'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="photo-step">'
    '写真を撮るか、保存してある写真を選びます。'
    '</div>',
    unsafe_allow_html=True,
)


photo_method = st.radio(
    "写真の選び方",
    [
        "カメラで撮る",
        "写真を選ぶ",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="photo_method",
)


uploaded_photo = None


if photo_method == "カメラで撮る":

    uploaded_photo = st.camera_input(
        "食事を撮影",
        key="meal_camera",
    )

else:

    uploaded_photo = st.file_uploader(
        "写真を選択",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="meal_photo_upload",
    )


# =========================================================
# 写真選択後
# =========================================================
if uploaded_photo is not None:

    st.image(
    uploaded_photo,
    use_container_width=True,
)

    image_bytes = uploaded_file_bytes(
        uploaded_photo
    )

    current_hash = image_hash(
        image_bytes
    )

    mime_type = getattr(
        uploaded_photo,
        "type",
        "image/jpeg",
    )

    # =====================================================
    # 新しい写真なら自動解析
    # 同じ写真ではAPIを繰り返し呼ばない
    # =====================================================
    if (
        current_hash
        and current_hash
        != st.session_state[
            "photo_analysis_hash"
        ]
    ):

        with st.spinner(
            "写真から食事内容を読み取っています…"
        ):

            try:

                analysis = analyze_meal_photo(
                    image_bytes,
                    mime_type,
                )

                st.session_state[
                    "photo_analysis_hash"
                ] = current_hash

                st.session_state[
                    "photo_analysis_foods"
                ] = analysis[
                    "foods"
                ]

                st.session_state[
                    "photo_analysis_balance"
                ] = analysis[
                    "balance"
                ]

                st.session_state[
                    "photo_analysis_improvement"
                ] = analysis[
                    "improvement"
                ]

                st.session_state[
                    "photo_analysis_score"
                ] = analysis[
                    "score"
                ]

                # 編集欄にもAI結果を入れる
                st.session_state[
                    "photo_food_text"
                ] = analysis[
                    "foods"
                ]

                # 新しい写真なので保存済み表示を解除
                st.session_state[
                    "photo_record_saved"
                ] = False

            except Exception as e:

                st.error(
                    "写真を解析できませんでした。"
                )

                st.caption(
                    f"エラー内容：{e}"
                )


# =========================================================
# AI解析結果
# =========================================================
analysis_foods = clean_text(
    st.session_state.get(
        "photo_analysis_foods",
        "",
    )
)

analysis_balance = clean_text(
    st.session_state.get(
        "photo_analysis_balance",
        "",
    )
)

analysis_improvement = clean_text(
    st.session_state.get(
        "photo_analysis_improvement",
        "",
    )
)

analysis_score = st.session_state.get(
    "photo_analysis_score",
    0,
)


if uploaded_photo is not None and analysis_foods:

    render_section_header(
        title="ShufuMateの写真分析",
        icon_file=(
            "ShufuMate_home_icons_8/"
            "advice.png"
        ),
        emoji="🌿",
    )

    score_html = (
        '<div class="photo-result-card">'
        '<div class="photo-result-title">'
        '食事バランス'
        '</div>'
        f'<div class="photo-score">'
        f'{analysis_score}点'
        '</div>'
        f'<div>{safe_html_with_br(analysis_balance)}</div>'
        '</div>'
    )

    st.markdown(
        score_html,
        unsafe_allow_html=True,
    )

    improvement_html = (
        '<div class="photo-result-card">'
        '<div class="photo-result-title">'
        'もう少し整えるなら'
        '</div>'
        f'{safe_html_with_br(analysis_improvement)}'
        '</div>'
    )

    st.markdown(
        improvement_html,
        unsafe_allow_html=True,
    )


# =========================================================
# 食事内容
# =========================================================
st.markdown(
    '<div style="color:#5c4033; '
    'font-size:1.35rem; font-weight:900; '
    'margin:28px 0 14px;">'
    '食事の内容'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="photo-step">'
    'AIが読み取った内容を確認してください。'
    '違うところがあれば、そのまま修正できます。'
    '</div>',
    unsafe_allow_html=True,
)


meal_type = st.radio(
    "食事",
    [
        "朝食",
        "昼食",
        "夕食",
        "間食",
        "その他",
    ],
    horizontal=True,
    key="photo_meal_type",
)


food_text = st.text_area(
    "食べたもの",
    placeholder=(
        "写真を選ぶとAIが自動入力します。"
    ),
    height=120,
    key="photo_food_text",
)


note_text = st.text_area(
    "ひとことメモ",
    placeholder=(
        "例：ヨガのあと。"
        "少しお腹が空いていた。"
    ),
    height=80,
    key="photo_note_text",
)


# =========================================================
# 保存
# =========================================================
st.markdown(
    '<div style="color:#5c4033; '
    'font-size:1.35rem; font-weight:900; '
    'margin:28px 0 14px;">'
    '記録する'
    '</div>',
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="photo-step">'
    'AIの解析結果と食事内容を確認して保存します。'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# 最新体組成
# =========================================================
latest_weight, latest_fat, latest_muscle = (
    latest_body_values()
)


with st.expander(
    "今日の体組成を見る",
    expanded=False,
):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "体重",
            (
                f"{latest_weight:.1f} kg"
                if latest_weight is not None
                else "—"
            ),
        )

    with col2:

        st.metric(
            "体脂肪率",
            (
                f"{latest_fat:.1f} %"
                if latest_fat is not None
                else "—"
            ),
        )

    with col3:

        st.metric(
            "筋肉量",
            (
                f"{latest_muscle:.1f} kg"
                if latest_muscle is not None
                else "—"
            ),
        )


# =========================================================
# 保存ボタン
# =========================================================
if st.button(
    "この食事を記録する",
    key="photo_save_button",
    use_container_width=True,
):

    if uploaded_photo is None:

        st.warning(
            "食事の写真を撮るか選んでください。"
        )

    elif not clean_text(food_text):

        st.warning(
            "食事内容を確認してください。"
        )

    else:

        save_date = jst_today_str()

        cleaned_food = clean_text(
            food_text
        )

        cleaned_note = clean_text(
            note_text
        )

        cleaned_balance = clean_text(
            analysis_balance
        )

        cleaned_improvement = clean_text(
            analysis_improvement
        )

        meal_memo_parts = [
            f"【写真で記録・{meal_type}】",
            cleaned_food,
        ]

        if cleaned_note:

            meal_memo_parts.append(
                f"メモ：{cleaned_note}"
            )

        if cleaned_balance:

            meal_memo_parts.append(
                f"バランス：{cleaned_balance}"
            )

        if cleaned_improvement:

            meal_memo_parts.append(
                f"改善ポイント：{cleaned_improvement}"
            )

        if analysis_score:

            meal_memo_parts.append(
                f"食事スコア：{analysis_score}点"
            )

        meal_memo = "\n".join(
            meal_memo_parts
        )

        try:

            # =============================================
            # DietLogsへ永続保存
            # 体組成は空欄にして重複させない
            # =============================================
            save_diet_log(
                user_id,
                {
                    "log_date":
                        save_date,

                    "weight":
                        "",

                    "body_fat":
                        "",

                    "muscle_mass":
                        "",

                    "meal_memo":
                        meal_memo,
                },
            )

            st.session_state[
                "photo_record_saved"
            ] = True

            st.session_state[
                "photo_record_meal"
            ] = meal_type

            st.session_state[
                "photo_record_food"
            ] = cleaned_food

            st.session_state[
                "photo_record_note"
            ] = cleaned_note

            st.session_state[
                "photo_record_date"
            ] = save_date

            st.success(
                "食事を記録しました ✨"
            )

        except Exception as e:

            st.error(
                "食事記録の保存中に"
                "エラーが発生しました。"
            )

            st.caption(
                f"エラー内容：{e}"
            )


# =========================================================
# 保存結果
# =========================================================
if st.session_state.get(
    "photo_record_saved",
    False,
):

    saved_date = clean_text(
        st.session_state.get(
            "photo_record_date",
            "",
        )
    )

    saved_meal = clean_text(
        st.session_state.get(
            "photo_record_meal",
            "",
        )
    )

    saved_food = clean_text(
        st.session_state.get(
            "photo_record_food",
            "",
        )
    )

    saved_note = clean_text(
        st.session_state.get(
            "photo_record_note",
            "",
        )
    )

    result_parts = []

    if saved_date:

        result_parts.append(
            f'<div>{safe_html(saved_date)}</div>'
        )

    if saved_meal:

        result_parts.append(
            '<div>'
            f'<strong>{safe_html(saved_meal)}</strong>'
            '</div>'
        )

    if saved_food:

        result_parts.append(
            '<div>'
            f'{safe_html_with_br(saved_food)}'
            '</div>'
        )

    if saved_note:

        result_parts.append(
            '<div style="margin-top:8px;">'
            'メモ：'
            f'{safe_html_with_br(saved_note)}'
            '</div>'
        )

    result_html = (
        '<div class="photo-result-card">'
        '<div class="photo-result-title">'
        '記録できました'
        '</div>'
        + "".join(result_parts)
        + '</div>'
    )

    st.markdown(
        result_html,
        unsafe_allow_html=True,
    )


# =========================================================
# 注意書き
# =========================================================
note_html = (
    '<div class="photo-small">'
    '写真の解析結果はAIによる推定です。'
    '料理や食材、量を正確に判定できない場合があります。'
    '内容を確認・修正してから記録してください。'
    '</div>'
)

st.markdown(
    note_html,
    unsafe_allow_html=True,
)
