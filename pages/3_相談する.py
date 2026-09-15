# =========================================================
# ShufuMate
# 3_相談する.py
# 完全版
# =========================================================

import streamlit as st
import pandas as pd

from app_core import *


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


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログイン確認
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# ページ専用CSS
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
        margin-bottom: 18px;
    }

    .consult-theme {
        background: rgba(255,255,255,.80);
        border: 1px solid rgba(139,100,72,.12);
        border-radius: 18px;
        padding: 14px 16px;
        color: #654b3d;
        line-height: 1.7;
        margin-bottom: 10px;
    }

    .consult-theme-title {
        font-weight: 900;
        color: #5c4033;
        margin-bottom: 4px;
    }

    .consult-context {
        background: #fff8ef;
        border-radius: 18px;
        padding: 15px 17px;
        color: #765f52;
        line-height: 1.8;
        margin-top: 8px;
        margin-bottom: 16px;
    }

    .consult-answer {
        background: linear-gradient(
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
        margin-bottom: 16px;
    }

    .consult-answer-title {
        font-weight: 900;
        color: #5c4033;
        font-size: 1.05rem;
        margin-bottom: 10px;
    }

    .consult-small {
        font-size: .85rem;
        color: #927c70;
        line-height: 1.7;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 16px !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,.60);
        border: 1px solid rgba(139,100,72,.10);
        border-radius: 17px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def text_value(value):
    return clean_text(value)


def numeric_value(value):
    try:
        if pd.isna(value):
            return None

        number = float(value)

        if number <= 0:
            return None

        return number

    except Exception:
        return None


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

    series = series[
        series > 0
    ]

    if series.empty:
        return None

    return float(
        series.iloc[-1]
    )


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

    series = series[
        series > 0
    ]

    if len(series) < 2:
        return None

    return float(
        series.iloc[-2]
    )


def change_text(
    latest,
    previous,
    unit,
):

    if (
        latest is None
        or previous is None
    ):
        return ""

    diff = latest - previous

    if abs(diff) < 0.05:
        return "前回とほぼ同じ"

    if diff > 0:
        return f"前回より +{diff:.1f}{unit}"

    return f"前回より {diff:.1f}{unit}"


# =========================================================
# 設定読み込み
# =========================================================
try:

    settings = (
        load_user_settings(
            user_id
        )
        or {}
    )

except Exception:

    settings = {}


# =========================================================
# 記録読み込み
# =========================================================
try:

    df = load_diet_dataframe(
        user_id
    )

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
# 最新データ
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
# 最新食事メモ
# =========================================================
latest_meal = ""

if (
    not df.empty
    and "meal_memo" in df.columns
):

    latest_meal = text_value(
        df.iloc[-1].get(
            "meal_memo",
            ""
        )
    )

    # 古い列ずれデータ対策
    try:
        float(latest_meal)
        latest_meal = ""
    except Exception:
        pass


# =========================================================
# 設定値
# =========================================================
goal = text_value(
    settings.get(
        "user_type",
        "健康維持",
    )
)

activity = text_value(
    settings.get(
        "activity_level",
        "普通",
    )
)

food_style = text_value(
    settings.get(
        "food_style",
        "",
    )
)

workout = text_value(
    settings.get(
        "workout_today",
        "",
    )
)

fridge_items = text_value(
    settings.get(
        "fridge_items",
        "",
    )
)

avoid_foods = text_value(
    settings.get(
        "avoid_foods",
        "",
    )
)

favorite_meals = text_value(
    settings.get(
        "favorite_meals",
        "",
    )
)


# =========================================================
# ページヘッダー
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


# =========================================================
# 説明
# =========================================================
st.markdown(
    """
    <div class="consult-intro">
        「今日何を食べたらいい？」
        「運動した方がいい？」
        「最近の数字はどう？」
        など、気になっていることをそのまま入力してください。
    </div>
    """,
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
)


# =========================================================
# テーマ別ヒント
# =========================================================
theme_help = {

    "食事":
        "今日の献立、食べる順番、間食、"
        "たんぱく質などを相談できます。",

    "運動":
        "筋トレ、ヨガ、ウォーキング、"
        "ランニング、休養などを相談できます。",

    "からだの変化":
        "体重・体脂肪率・筋肉量の"
        "変化について確認できます。",

    "体調・生活":
        "疲れ、睡眠、むくみ、"
        "生活リズムなどを相談できます。",

    "なんでも相談":
        "気になっていることを"
        "自由に入力してください。",
}

st.markdown(
    (
        '<div class="consult-theme">'
        f'{safe_text(theme_help[theme])}'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# =========================================================
# 質問入力
# =========================================================
question = st.text_area(
    "相談したいこと",
    placeholder=(
        "例：今日は筋トレをしました。"
        "夜ごはんは何を食べるのがいい？"
    ),
    height=125,
)


# =========================================================
# 回答生成
# =========================================================
def build_answer(
    selected_theme,
    question_text,
):

    question_text = (
        clean_text(question_text)
    )

    answer_parts = []


    # -----------------------------------------------------
    # 最初の一言
    # -----------------------------------------------------
    if question_text:

        answer_parts.append(
            "今の記録と設定をもとに考えると、"
            "次のように整えるのがおすすめです。"
        )

    else:

        answer_parts.append(
            "今の記録から、今日意識するとよいことをまとめます。"
        )


    # -----------------------------------------------------
    # 食事
    # -----------------------------------------------------
    if selected_theme == "食事":

        if latest_muscle is not None:

            answer_parts.append(
                "筋肉量も記録しているので、"
                "食事を減らすことより、"
                "たんぱく質を毎食確保することを優先しましょう。"
            )

        if food_style:

            answer_parts.append(
                f"設定している食事スタイルは"
                f"「{food_style}」です。"
                "これを基本に、主食・たんぱく質・野菜を"
                "極端に抜かない組み合わせが向いています。"
            )

        if fridge_items:

            answer_parts.append(
                f"家にある食材として"
                f"「{fridge_items}」が登録されています。"
                "まずこの中からたんぱく質源と野菜を選ぶと、"
                "献立を決めやすくなります。"
            )

        if avoid_foods:

            answer_parts.append(
                f"「{avoid_foods}」は避ける条件として考えます。"
            )

        answer_parts.append(
            "迷った日は、"
            "①たんぱく質を1品、"
            "②野菜または汁物、"
            "③活動量に合わせた主食、"
            "の3つをそろえるだけでも十分です。"
        )


    # -----------------------------------------------------
    # 運動
    # -----------------------------------------------------
    elif selected_theme == "運動":

        if activity:

            answer_parts.append(
                f"普段の活動量は「{activity}」で設定されています。"
            )

        if workout:

            answer_parts.append(
                f"普段の運動は「{workout}」。"
                "同じ部位に強い負荷が続かないよう、"
                "筋トレ・有酸素運動・柔軟性・休養を"
                "組み合わせるのがおすすめです。"
            )

        if (
            latest_muscle is not None
            and previous_muscle is not None
        ):

            diff = (
                latest_muscle
                - previous_muscle
            )

            if diff < -0.1:

                answer_parts.append(
                    "筋肉量は前回より少し下がっています。"
                    "今日は運動量を増やしすぎるより、"
                    "食事と回復までセットで考えましょう。"
                )

            elif diff > 0.1:

                answer_parts.append(
                    "筋肉量は前回より増えています。"
                    "今の運動習慣を大きく変えず、"
                    "継続を優先するのがよさそうです。"
                )

        answer_parts.append(
            "疲労が強い日は、完全に何もしないか"
            "強い運動をするかの二択にせず、"
            "軽いストレッチやヨガ、散歩に切り替えてもOKです。"
        )


    # -----------------------------------------------------
    # からだの変化
    # -----------------------------------------------------
    elif selected_theme == "からだの変化":

        if latest_weight is not None:

            text = change_text(
                latest_weight,
                previous_weight,
                "kg",
            )

            if text:

                answer_parts.append(
                    f"体重は {latest_weight:.1f}kgで、{text}です。"
                )

        if latest_fat is not None:

            text = change_text(
                latest_fat,
                previous_fat,
                "%",
            )

            if text:

                answer_parts.append(
                    f"体脂肪率は {latest_fat:.1f}%で、{text}です。"
                )

        if latest_muscle is not None:

            text = change_text(
                latest_muscle,
                previous_muscle,
                "kg",
            )

            if text:

                answer_parts.append(
                    f"筋肉量は {latest_muscle:.1f}kgで、{text}です。"
                )

        answer_parts.append(
            "1回の測定値だけで判断せず、"
            "数週間単位の傾向を見るのがおすすめです。"
            "特に体重だけではなく、体脂肪率と筋肉量を"
            "一緒に見ると変化が分かりやすくなります。"
        )


    # -----------------------------------------------------
    # 体調・生活
    # -----------------------------------------------------
    elif selected_theme == "体調・生活":

        answer_parts.append(
            "体調は運動だけでなく、睡眠・食事・疲労・"
            "水分などの影響も受けます。"
        )

        answer_parts.append(
            "今日は『頑張れるか』より、"
            "睡眠・疲れ・食欲・からだの重さを確認して、"
            "負荷を決めるのがおすすめです。"
        )

        if activity:

            answer_parts.append(
                f"普段の活動量は「{activity}」なので、"
                "日常ですでによく動いた日は、"
                "追加の運動を軽めにしても十分です。"
            )


    # -----------------------------------------------------
    # なんでも相談
    # -----------------------------------------------------
    else:

        if goal:

            answer_parts.append(
                f"現在の目的は「{goal}」。"
                "この目的から外れない範囲で、"
                "無理なく続けられる方法を優先しましょう。"
            )

        if latest_muscle is not None:

            answer_parts.append(
                "体重だけでなく筋肉量も記録できているので、"
                "数字を減らすことだけを目標にせず、"
                "からだの中身の変化も一緒に見ていくのがおすすめです。"
            )


    # -----------------------------------------------------
    # 質問文から簡単な補足
    # -----------------------------------------------------
    q = question_text.lower()

    if (
        "夜" in question_text
        and
        (
            "食" in question_text
            or "ごはん" in question_text
        )
    ):

        answer_parts.append(
            "夜は、たんぱく質＋野菜・汁物を先に決め、"
            "主食はその日の運動量と空腹感に合わせると"
            "調整しやすいです。"
        )

    if (
        "間食" in question_text
        or "おやつ" in question_text
    ):

        answer_parts.append(
            "間食は我慢だけで調整せず、"
            "ヨーグルト・果物など、"
            "次の食事に響きにくいものを少量選ぶ方法があります。"
        )

    if (
        "疲" in question_text
        or "だる" in question_text
    ):

        answer_parts.append(
            "疲れやだるさが強い日は、"
            "強度を落として回復を優先してください。"
        )


    return "\n\n".join(
        answer_parts
    )


# =========================================================
# 相談ボタン
# =========================================================
if st.button(
    "ShufuMateに相談する",
    key="consult_submit_button",
    use_container_width=True,
):

    answer = build_answer(
        theme,
        question,
    )

    st.session_state[
        "shufumate_consult_answer"
    ] = answer

    st.session_state[
        "shufumate_consult_question"
    ] = question

    st.session_state[
        "shufumate_consult_theme"
    ] = theme


# =========================================================
# 回答
# =========================================================
if st.session_state.get(
    "shufumate_consult_answer"
):

    render_section_header(
        title="ShufuMateから",
        icon_file="ShufuMate_home_icons_8/advice.png",
        emoji="🌿",
    )

    answer = st.session_state[
        "shufumate_consult_answer"
    ]

    answer_html = safe_html_with_br(
        answer
    )

    st.markdown(
        (
            '<div class="consult-answer">'
            '<div class="consult-answer-title">'
            '今日のアドバイス'
            '</div>'
            f'{answer_html}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# 記録を確認
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

    if latest_meal:

        st.write(
            "最新の食事・メモ："
        )

        st.write(
            latest_meal
        )


# =========================================================
# 注意
# =========================================================
st.markdown(
    """
    <div class="consult-small">
        ShufuMateの提案は、毎日の生活を整えるための参考情報です。
        強い痛みや体調不良がある場合は、運動を無理に続けず、
        必要に応じて医療機関へ相談してください。
    </div>
    """,
    unsafe_allow_html=True,
)
