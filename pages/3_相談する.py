# =========================================================
# ShufuMate
# pages/3_相談する.py
# AI相談・写真対応 完全版
# =========================================================

import base64
import html

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
    load_user_settings,
    load_diet_dataframe,
    clean_text,
)


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="相談する｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/chat.png",
        "💬",
    ),
    layout="centered",
)

inject_shufumate_css()
require_login()

user_id = get_user_id()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

.consult-intro {
    background: rgba(255,250,244,.92);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #6f584b;
    line-height: 1.85;
    margin-bottom: 22px;
}

.consult-theme {
    background: rgba(255,255,255,.80);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 18px;
    padding: 14px 16px;
    color: #654b3d;
    line-height: 1.75;
    margin-top: 8px;
    margin-bottom: 18px;
}

.consult-photo-help {
    background: rgba(255,250,244,.72);
    border-radius: 16px;
    padding: 12px 15px;
    color: #7b6559;
    line-height: 1.7;
    margin: 5px 0 12px;
    font-size: .9rem;
}

.consult-answer {
    background:
        linear-gradient(
            135deg,
            rgba(255,250,242,.98),
            rgba(249,239,227,.98)
        );
    border: 1px solid rgba(139,100,72,.14);
    border-radius: 22px;
    padding: 20px 21px;
    color: #5d473b;
    line-height: 1.95;
    box-shadow: 0 5px 18px rgba(91,64,49,.05);
    margin-top: 10px;
    margin-bottom: 18px;
}

.consult-answer-title {
    font-weight: 900;
    color: #5c4033;
    font-size: 1.08rem;
    margin-bottom: 10px;
}

.consult-question {
    background: rgba(255,255,255,.72);
    border-left: 4px solid #c7a891;
    border-radius: 14px;
    padding: 13px 15px;
    color: #70584b;
    line-height: 1.75;
    margin-bottom: 14px;
}

.consult-question-label {
    font-size: .82rem;
    font-weight: 800;
    color: #9a8173;
    margin-bottom: 3px;
}

.consult-small {
    font-size: .84rem;
    color: #927c70;
    line-height: 1.75;
    margin-top: 18px;
    margin-bottom: 18px;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 16px !important;
}

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.60);
    border-radius: 18px;
}

div[data-testid="stImage"] img {
    border-radius: 17px;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,.60);
    border: 1px solid rgba(139,100,72,.10);
    border-radius: 17px;
}

@media (max-width: 640px) {

    .consult-intro {
        padding: 15px 16px;
    }

    .consult-answer {
        padding: 17px 18px;
    }

}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def safe_html(value):
    return html.escape(str(value or ""))


def safe_html_with_br(value):
    return safe_html(value).replace("\n", "<br>")


def latest_numeric(df, column):

    if (
        df is None
        or df.empty
        or column not in df.columns
    ):
        return None

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    series = series.dropna()
    series = series[series > 0]

    if series.empty:
        return None

    return float(series.iloc[-1])


def previous_numeric(df, column):

    if (
        df is None
        or df.empty
        or column not in df.columns
    ):
        return None

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    series = series.dropna()
    series = series[series > 0]

    if len(series) < 2:
        return None

    return float(series.iloc[-2])


def image_to_data_url(uploaded_file):

    image_bytes = uploaded_file.getvalue()

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    mime_type = (
        getattr(
            uploaded_file,
            "type",
            None,
        )
        or "image/jpeg"
    )

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# =========================================================
# 設定読み込み
# =========================================================
try:
    settings = (
        load_user_settings(user_id)
        or {}
    )
except Exception:
    settings = {}


# =========================================================
# 記録読み込み
# =========================================================
try:
    df = load_diet_dataframe(user_id)

except Exception:

    df = pd.DataFrame(
        columns=[
            "user_id",
            "log_date",
            "weight",
            "body_fat",
            "muscle_mass",
            "meal_memo",
        ]
    )


if not df.empty:

    df = df.sort_values(
        "log_date"
    ).reset_index(drop=True)


# =========================================================
# 最新値
# =========================================================
latest_weight = latest_numeric(
    df,
    "weight",
)

latest_fat = latest_numeric(
    df,
    "body_fat",
)

latest_muscle = latest_numeric(
    df,
    "muscle_mass",
)

previous_weight = previous_numeric(
    df,
    "weight",
)

previous_fat = previous_numeric(
    df,
    "body_fat",
)

previous_muscle = previous_numeric(
    df,
    "muscle_mass",
)


# =========================================================
# 最近の食事記録
# =========================================================
recent_meals = []

if (
    not df.empty
    and "meal_memo" in df.columns
):

    for _, row in df.tail(5).iterrows():

        meal = clean_text(
            row.get(
                "meal_memo",
                ""
            )
        )

        if not meal:
            continue

        # 古い列ずれ対策
        try:
            float(meal)
            continue
        except Exception:
            pass

        log_date = clean_text(
            row.get(
                "log_date",
                ""
            )
        )

        recent_meals.append(
            f"{log_date}：{meal}"
        )


# =========================================================
# 設定値
# =========================================================
goal = clean_text(
    settings.get(
        "user_type",
        "健康維持",
    )
)

activity = clean_text(
    settings.get(
        "activity_level",
        "普通",
    )
)

food_style = clean_text(
    settings.get(
        "food_style",
        "",
    )
)

workout = clean_text(
    settings.get(
        "workout_today",
        "",
    )
)

fridge_items = clean_text(
    settings.get(
        "fridge_items",
        "",
    )
)

avoid_foods = clean_text(
    settings.get(
        "avoid_foods",
        "",
    )
)

favorite_meals = clean_text(
    settings.get(
        "favorite_meals",
        "",
    )
)

target_weight = clean_text(
    settings.get(
        "target_weight",
        "",
    )
)

target_body_fat = clean_text(
    settings.get(
        "target_body_fat",
        "",
    )
)

target_muscle = clean_text(
    settings.get(
        "target_muscle_mass",
        "",
    )
)


# =========================================================
# AI相談
# =========================================================
def ask_shufumate_ai(
    selected_theme,
    question_text,
    uploaded_photo=None,
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

    question_text = clean_text(
        question_text
    )

    body_info = []

    if latest_weight is not None:
        body_info.append(
            f"最新体重：{latest_weight:.1f}kg"
        )

    if latest_fat is not None:
        body_info.append(
            f"最新体脂肪率：{latest_fat:.1f}%"
        )

    if latest_muscle is not None:
        body_info.append(
            f"最新筋肉量：{latest_muscle:.1f}kg"
        )

    if previous_weight is not None:
        body_info.append(
            f"前回体重：{previous_weight:.1f}kg"
        )

    if previous_fat is not None:
        body_info.append(
            f"前回体脂肪率：{previous_fat:.1f}%"
        )

    if previous_muscle is not None:
        body_info.append(
            f"前回筋肉量：{previous_muscle:.1f}kg"
        )

    settings_info = []

    if goal:
        settings_info.append(
            f"目的：{goal}"
        )

    if activity:
        settings_info.append(
            f"活動量：{activity}"
        )

    if food_style:
        settings_info.append(
            f"食事スタイル：{food_style}"
        )

    if workout:
        settings_info.append(
            f"普段の運動：{workout}"
        )

    if fridge_items:
        settings_info.append(
            f"冷蔵庫・家にある食材：{fridge_items}"
        )

    if avoid_foods:
        settings_info.append(
            f"避けたい食品：{avoid_foods}"
        )

    if favorite_meals:
        settings_info.append(
            f"好きなメニュー：{favorite_meals}"
        )

    if target_weight:
        settings_info.append(
            f"目標体重：{target_weight}kg"
        )

    if target_body_fat:
        settings_info.append(
            f"目標体脂肪率：{target_body_fat}%"
        )

    if target_muscle:
        settings_info.append(
            f"目標筋肉量：{target_muscle}kg"
        )

    recent_meal_text = (
        "\n".join(recent_meals)
        if recent_meals
        else "記録なし"
    )

    prompt = f"""
あなたは生活サポートアプリ「ShufuMate」の相談AIです。

ユーザーの日々の食事・運動・体組成・生活を、
やさしく、具体的に、一緒に整理してください。

【相談テーマ】
{selected_theme}

【相談内容】
{question_text if question_text else "文章での相談はありません。添付写真を見て相談に答えてください。"}

【現在の体組成】
{chr(10).join(body_info) if body_info else "記録なし"}

【ユーザー設定】
{chr(10).join(settings_info) if settings_info else "設定なし"}

【最近の食事記録】
{recent_meal_text}

回答ルール：
・日本語で答える
・相談内容に最初に直接答える
・一般論だけで終わらせない
・登録済みの設定や記録が関係するときだけ自然に利用する
・記録にないことを事実として決めつけない
・写真がある場合は、写真で確認できる内容を相談への回答に利用する
・写真から分からない量や食材は断定しない
・食事相談では、実際に食べやすい具体例を出す
・運動相談では、疲労や休養も考慮する
・体組成は1回の数値だけで過度に評価しない
・医療診断はしない
・強い症状や緊急性が疑われる場合は医療機関への相談を案内する
・説教調にしない
・長すぎない
・見出しを多用しない
・最後に、今日すぐできることを1つ具体的に示す
"""

    content = [
        {
            "type": "input_text",
            "text": prompt,
        }
    ]

    if uploaded_photo is not None:

        content.append(
            {
                "type": "input_image",
                "image_url":
                    image_to_data_url(
                        uploaded_photo
                    ),
                "detail": "auto",
            }
        )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    answer = clean_text(
        response.output_text
    )

    if not answer:
        raise ValueError(
            "AIから回答を取得できませんでした。"
        )

    return answer


# =========================================================
# ヘッダー
# =========================================================
render_page_header(
    title="相談する",
    subtitle=(
        "食事・運動・からだのこと。"
        "今の記録を見ながら一緒に考えます。"
    ),
    icon_file="ShufuMate_home_icons_8/chat.png",
    emoji="💬",
)


intro_html = (
    '<div class="consult-intro">'
    '「今日何を食べたらいい？」'
    '「運動した方がいい？」'
    '「この写真の食事はどう？」など、'
    '気になっていることをそのまま相談してください。'
    '</div>'
)

st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# 今の状態
# =========================================================
render_section_header(
    title="今の状態",
    icon_file="ShufuMate_home_icons_8/state.png",
    emoji="🌿",
)


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
# 相談テーマ
# =========================================================
render_section_header(
    title="何について相談する？",
    icon_file="ShufuMate_home_icons_8/advice.png",
    emoji="💡",
)


theme = st.radio(
    "相談テーマ",
    [
        "食事",
        "運動",
        "からだの変化",
        "体調・生活",
        "なんでも相談",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="consult_theme",
)


theme_help = {

    "食事": (
        "献立、食べる順番、間食、"
        "写真の食事などを相談できます。"
    ),

    "運動": (
        "筋トレ、ヨガ、ウォーキング、"
        "ランニング、休養などを相談できます。"
    ),

    "からだの変化": (
        "体重・体脂肪率・筋肉量の"
        "変化について相談できます。"
    ),

    "体調・生活": (
        "疲れ、睡眠、むくみ、"
        "生活リズムなどを相談できます。"
    ),

    "なんでも相談": (
        "気になっていることを"
        "自由に相談できます。"
    ),
}


theme_html = (
    '<div class="consult-theme">'
    f'{safe_html(theme_help[theme])}'
    '</div>'
)

st.markdown(
    theme_html,
    unsafe_allow_html=True,
)


# =========================================================
# 相談内容
# =========================================================
question = st.text_area(
    "相談したいこと",
    placeholder=(
        "例：今日のお昼はこれを食べました。"
        "夜は何を食べたらいい？"
    ),
    height=125,
    key="consult_question_input",
)


# =========================================================
# 写真
# =========================================================
st.markdown(
    "#### 写真を添付する（任意）"
)


photo_help_html = (
    '<div class="consult-photo-help">'
    '食事・冷蔵庫・食品など、'
    '相談したいものの写真がある場合だけ添付してください。'
    '</div>'
)

st.markdown(
    photo_help_html,
    unsafe_allow_html=True,
)


photo_method = st.radio(
    "写真の選び方",
    [
        "写真なし",
        "カメラで撮る",
        "写真を選ぶ",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="consult_photo_method",
)


consult_photo = None


if photo_method == "カメラで撮る":

    consult_photo = st.camera_input(
        "相談する写真を撮影",
        key="consult_camera",
    )


elif photo_method == "写真を選ぶ":

    consult_photo = st.file_uploader(
        "相談する写真を選択",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="consult_photo_upload",
    )


if consult_photo is not None:

    # 写真で記録ページより小さめ
    st.image(
        consult_photo,
        width=360,
    )


# =========================================================
# 相談ボタン
# =========================================================
if st.button(
    "ShufuMateに相談する",
    key="consult_submit_button",
    use_container_width=True,
):

    if (
        not clean_text(question)
        and consult_photo is None
    ):

        st.warning(
            "相談したいことを入力するか、写真を添付してください。"
        )

    else:

        with st.spinner(
            "ShufuMateが一緒に考えています…"
        ):

            try:

                answer = ask_shufumate_ai(
                    selected_theme=theme,
                    question_text=question,
                    uploaded_photo=consult_photo,
                )

                st.session_state[
                    "shufumate_consult_answer"
                ] = answer

                st.session_state[
                    "shufumate_consult_question"
                ] = clean_text(
                    question
                )

                st.session_state[
                    "shufumate_consult_theme"
                ] = theme

                st.session_state[
                    "shufumate_consult_had_photo"
                ] = (
                    consult_photo is not None
                )

            except Exception as e:

                st.error(
                    "相談への回答を作成できませんでした。"
                )

                st.caption(
                    f"エラー内容：{e}"
                )


# =========================================================
# 回答表示
# =========================================================
answer = st.session_state.get(
    "shufumate_consult_answer",
    "",
)

saved_question = st.session_state.get(
    "shufumate_consult_question",
    "",
)

had_photo = st.session_state.get(
    "shufumate_consult_had_photo",
    False,
)


if answer:

    render_section_header(
        title="ShufuMateから",
        icon_file="ShufuMate_home_icons_8/advice.png",
        emoji="🌿",
    )


    if saved_question:

        question_html = (
            '<div class="consult-question">'
            '<div class="consult-question-label">'
            '相談したこと'
            '</div>'
            f'{safe_html_with_br(saved_question)}'
            '</div>'
        )

        st.markdown(
            question_html,
            unsafe_allow_html=True,
        )


    elif had_photo:

        question_html = (
            '<div class="consult-question">'
            '<div class="consult-question-label">'
            '相談したこと'
            '</div>'
            '添付した写真について相談'
            '</div>'
        )

        st.markdown(
            question_html,
            unsafe_allow_html=True,
        )


    answer_html = (
        '<div class="consult-answer">'
        '<div class="consult-answer-title">'
        'ShufuMateのアドバイス'
        '</div>'
        f'{safe_html_with_br(answer)}'
        '</div>'
    )

    st.markdown(
        answer_html,
        unsafe_allow_html=True,
    )


# =========================================================
# 参考情報
# =========================================================
with st.expander(
    "今回の相談で参考にしている情報"
):

    st.write(
        f"目的：{goal or '未設定'}"
    )

    st.write(
        f"活動量：{activity or '未設定'}"
    )

    if food_style:

        st.write(
            f"食事スタイル：{food_style}"
        )

    if workout:

        st.write(
            f"普段の運動：{workout}"
        )

    if latest_weight is not None:

        st.write(
            f"最新体重：{latest_weight:.1f} kg"
        )

    if latest_fat is not None:

        st.write(
            f"最新体脂肪率：{latest_fat:.1f} %"
        )

    if latest_muscle is not None:

        st.write(
            f"最新筋肉量：{latest_muscle:.1f} kg"
        )

    if target_muscle:

        st.write(
            f"目標筋肉量：{target_muscle} kg"
        )

    if fridge_items:

        st.write(
            f"家にある食材：{fridge_items}"
        )

    if avoid_foods:

        st.write(
            f"避けたい食品：{avoid_foods}"
        )

    if recent_meals:

        st.write(
            "最近の食事・メモ："
        )

        for meal in recent_meals:

            st.write(
                meal
            )


# =========================================================
# 注意
# =========================================================
notice_html = (
    '<div class="consult-small">'
    'ShufuMateの提案は、毎日の生活を整えるための参考情報です。'
    '写真の内容はAIによる推定を含みます。'
    '強い痛みや体調不良がある場合は無理をせず、'
    '必要に応じて医療機関へ相談してください。'
    '</div>'
)

st.markdown(
    notice_html,
    unsafe_allow_html=True,
)
