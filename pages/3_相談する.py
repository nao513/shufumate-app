# =========================================================
# ShufuMate
# pages/3_相談する.py
# 最終完全版
# =========================================================

import streamlit as st
import pandas as pd
import html

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

/* -----------------------------------------
   説明カード
----------------------------------------- */
.consult-intro {
    background: rgba(255,250,244,.92);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #6f584b;
    line-height: 1.85;
    margin-bottom: 22px;
}


/* -----------------------------------------
   テーマ説明
----------------------------------------- */
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


/* -----------------------------------------
   回答
----------------------------------------- */
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
    box-shadow:
        0 5px 18px rgba(91,64,49,.05);
    margin-top: 10px;
    margin-bottom: 18px;
}

.consult-answer-title {
    font-weight: 900;
    color: #5c4033;
    font-size: 1.08rem;
    margin-bottom: 10px;
}


/* -----------------------------------------
   質問表示
----------------------------------------- */
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


/* -----------------------------------------
   注意書き
----------------------------------------- */
.consult-small {
    font-size: .84rem;
    color: #927c70;
    line-height: 1.75;
    margin-top: 18px;
    margin-bottom: 18px;
}


/* -----------------------------------------
   入力欄
----------------------------------------- */
div[data-testid="stTextArea"] textarea {
    border-radius: 16px !important;
}


/* -----------------------------------------
   Expander
----------------------------------------- */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,.60);
    border: 1px solid rgba(139,100,72,.10);
    border-radius: 17px;
}


/* -----------------------------------------
   モバイル
----------------------------------------- */
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
def text_value(value):
    """文字列を安全に整える"""
    return clean_text(value)


def safe_html(value):
    """HTML特殊文字をエスケープ"""
    return html.escape(
        str(value or "")
    )


def safe_html_with_br(value):
    """改行を <br> に変換"""
    return safe_html(value).replace(
        "\n",
        "<br>"
    )


def latest_numeric(df, column):
    """指定列の最新の有効数値"""

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
    """指定列の1つ前の有効数値"""

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
    """前回との差を表示"""

    if (
        latest is None
        or previous is None
    ):
        return ""

    diff = latest - previous

    if abs(diff) < 0.05:
        return "前回とほぼ同じ"

    if diff > 0:
        return (
            f"前回より +{diff:.1f}{unit}"
        )

    return (
        f"前回より {diff:.1f}{unit}"
    )


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
    ).reset_index(
        drop=True
    )


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


# =========================================================
# 前回データ
# =========================================================
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

    # -----------------------------------------
    # 旧データの列ずれ対策
    # 数字だけなら食事メモとして使わない
    # -----------------------------------------
    if latest_meal:

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
intro_html = (
    '<div class="consult-intro">'
    '「今日何を食べたらいい？」'
    '「運動した方がいい？」'
    '「最近の数字はどう？」など、'
    '気になっていることをそのまま入力してください。'
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
)


# =========================================================
# テーマ説明
# =========================================================
theme_help = {

    "食事": (
        "今日の献立、食べる順番、間食、"
        "たんぱく質などを相談できます。"
    ),

    "運動": (
        "筋トレ、ヨガ、ウォーキング、"
        "ランニング、休養などを相談できます。"
    ),

    "からだの変化": (
        "体重・体脂肪率・筋肉量の"
        "変化について確認できます。"
    ),

    "体調・生活": (
        "疲れ、睡眠、むくみ、"
        "生活リズムなどを相談できます。"
    ),

    "なんでも相談": (
        "気になっていることを"
        "自由に入力してください。"
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
# 質問入力
# =========================================================
question = st.text_area(
    "相談したいこと",
    placeholder=(
        "例：今日は筋トレをしました。"
        "夜ごはんは何を食べるのがいい？"
    ),
    height=125,
    key="consult_question_input",
)


# =========================================================
# 回答生成
# =========================================================
def build_answer(
    selected_theme,
    question_text,
):

    question_text = clean_text(
        question_text
    )

    answer_parts = []


    # =====================================================
    # 導入
    # =====================================================
    if question_text:

        answer_parts.append(
            "今の記録と設定、相談内容を合わせて考えると、"
            "次のように整えるのがおすすめです。"
        )

    else:

        answer_parts.append(
            "今の記録から、今日意識するとよいことをまとめます。"
        )


    # =====================================================
    # 食事
    # =====================================================
    if selected_theme == "食事":

        if food_style:

            answer_parts.append(
                f"食事スタイルは「{food_style}」で設定されています。"
                "このスタイルを基本にしながら、"
                "主食・たんぱく質・野菜を"
                "極端に抜かないようにしましょう。"
            )


        if fridge_items:

            answer_parts.append(
                f"家にある食材は「{fridge_items}」。"
                "この中から、まずたんぱく質になるものを1品、"
                "次に野菜や汁物を選ぶと献立を決めやすくなります。"
            )


        if avoid_foods:

            answer_parts.append(
                f"「{avoid_foods}」は避ける条件として考えます。"
            )


        if favorite_meals:

            answer_parts.append(
                f"好きなメニューとして"
                f"「{favorite_meals}」が登録されています。"
                "無理に特別な食事へ変えるより、"
                "好きなメニューを整えて続ける方法もおすすめです。"
            )


        if latest_meal:

            answer_parts.append(
                "最新の食事記録もあるので、"
                "同じ食品に偏りすぎていないか、"
                "たんぱく質や野菜が不足していないかを"
                "確認しながら次の食事を決めましょう。"
            )


        answer_parts.append(
            "迷った日は、"
            "①たんぱく質を1品、"
            "②野菜または汁物、"
            "③その日の活動量に合わせた主食、"
            "の3つをそろえるだけでも十分です。"
        )


    # =====================================================
    # 運動
    # =====================================================
    elif selected_theme == "運動":

        if activity:

            answer_parts.append(
                f"普段の活動量は「{activity}」で設定されています。"
            )


        if workout:

            answer_parts.append(
                f"普段の運動は「{workout}」。"
                "同じ部位へ強い負荷が続かないように、"
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
                    "今日は運動量だけを増やすより、"
                    "食事・睡眠・回復までセットで考えましょう。"
                )

            elif diff > 0.1:

                answer_parts.append(
                    "筋肉量は前回より増えています。"
                    "今の運動習慣を大きく変えず、"
                    "継続を優先するのがよさそうです。"
                )

            else:

                answer_parts.append(
                    "筋肉量は前回と大きく変わっていません。"
                    "急に負荷を増やすより、"
                    "今の習慣を安定して続ける方がよさそうです。"
                )


        answer_parts.append(
            "疲労が強い日は、"
            "強い運動か完全休養かの二択にせず、"
            "軽いストレッチ・ヨガ・散歩へ"
            "切り替える方法もあります。"
        )


    # =====================================================
    # からだの変化
    # =====================================================
    elif selected_theme == "からだの変化":

        body_messages = []


        if latest_weight is not None:

            text = change_text(
                latest_weight,
                previous_weight,
                "kg",
            )

            if text:

                body_messages.append(
                    f"体重は {latest_weight:.1f}kgで、{text}です。"
                )


        if latest_fat is not None:

            text = change_text(
                latest_fat,
                previous_fat,
                "%",
            )

            if text:

                body_messages.append(
                    f"体脂肪率は {latest_fat:.1f}%で、{text}です。"
                )


        if latest_muscle is not None:

            text = change_text(
                latest_muscle,
                previous_muscle,
                "kg",
            )

            if text:

                body_messages.append(
                    f"筋肉量は {latest_muscle:.1f}kgで、{text}です。"
                )


        if body_messages:

            answer_parts.extend(
                body_messages
            )

        else:

            answer_parts.append(
                "比較できる記録がまだ十分にありません。"
                "記録が増えると、前回との変化を確認できます。"
            )


        answer_parts.append(
            "1回の測定値だけで判断せず、"
            "数週間単位の傾向を見るのがおすすめです。"
            "体重だけでなく、体脂肪率と筋肉量を"
            "一緒に見ると変化が分かりやすくなります。"
        )


    # =====================================================
    # 体調・生活
    # =====================================================
    elif selected_theme == "体調・生活":

        answer_parts.append(
            "体調は運動だけでなく、"
            "睡眠・食事・疲労・水分・生活リズムなどの"
            "影響も受けます。"
        )


        answer_parts.append(
            "今日は「頑張れるか」だけで決めず、"
            "睡眠・疲れ・食欲・からだの重さを確認して、"
            "その日の負荷を決めるのがおすすめです。"
        )


        if activity:

            answer_parts.append(
                f"普段の活動量は「{activity}」。"
                "日常生活ですでによく動いた日は、"
                "追加の運動を軽めにしても構いません。"
            )


    # =====================================================
    # なんでも相談
    # =====================================================
    else:

        if goal:

            answer_parts.append(
                f"現在の目的は「{goal}」。"
                "この目的から大きく外れない範囲で、"
                "無理なく続けられる方法を優先しましょう。"
            )


        if latest_muscle is not None:

            answer_parts.append(
                "体重だけでなく筋肉量も記録できているので、"
                "数字を減らすことだけを目標にせず、"
                "からだの中身の変化も一緒に見ていくのがおすすめです。"
            )


    # =====================================================
    # 質問内容から追加アドバイス
    # =====================================================

    # 夜ごはん
    if (
        "夜" in question_text
        and (
            "食" in question_text
            or "ごはん" in question_text
            or "夕食" in question_text
        )
    ):

        answer_parts.append(
            "夜ごはんについては、"
            "たんぱく質＋野菜・汁物を先に決め、"
            "主食はその日の運動量と空腹感に合わせると"
            "調整しやすくなります。"
        )


    # 間食
    if (
        "間食" in question_text
        or "おやつ" in question_text
    ):

        answer_parts.append(
            "間食は我慢だけで調整せず、"
            "ヨーグルトや果物など、"
            "次の食事に響きにくいものを"
            "少量選ぶ方法があります。"
        )


    # 疲労
    if (
        "疲" in question_text
        or "だる" in question_text
    ):

        answer_parts.append(
            "疲れやだるさが強い日は、"
            "運動強度を落として回復を優先してください。"
        )


    # 筋トレ
    if (
        "筋トレ" in question_text
        or "トレーニング" in question_text
    ):

        answer_parts.append(
            "筋トレをした日は、"
            "運動だけで終わらせず、"
            "食事・水分・睡眠まで含めて"
            "回復を考えるのがおすすめです。"
        )


    # ヨガ
    if "ヨガ" in question_text:

        answer_parts.append(
            "ヨガをする日は、"
            "柔軟性だけを追わず、"
            "呼吸や疲労感を確認しながら"
            "無理のない範囲で動きましょう。"
        )


    # ランニング
    if (
        "ランニング" in question_text
        or "走" in question_text
    ):

        answer_parts.append(
            "走った日は脚への負荷も考えて、"
            "追加の下半身トレーニングを"
            "やりすぎないように調整するとよいでしょう。"
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
    ] = clean_text(
        question
    )

    st.session_state[
        "shufumate_consult_theme"
    ] = theme


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


if answer:

    render_section_header(
        title="ShufuMateから",
        icon_file="ShufuMate_home_icons_8/advice.png",
        emoji="🌿",
    )


    # -----------------------------------------
    # 質問内容
    # -----------------------------------------
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


    # -----------------------------------------
    # 回答
    # -----------------------------------------
    answer_html = (
        '<div class="consult-answer">'
        '<div class="consult-answer-title">'
        '今日のアドバイス'
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


    if fridge_items:

        st.write(
            f"家にある食材：{fridge_items}"
        )


    if avoid_foods:

        st.write(
            f"避けたい食品：{avoid_foods}"
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
notice_html = (
    '<div class="consult-small">'
    'ShufuMateの提案は、毎日の生活を整えるための参考情報です。'
    '強い痛みや体調不良がある場合は、運動を無理に続けず、'
    '必要に応じて医療機関へ相談してください。'
    '</div>'
)

st.markdown(
    notice_html,
    unsafe_allow_html=True,
)
