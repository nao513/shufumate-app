import streamlit as st
import pandas as pd

from app_core import *


# =========================================================
# 水彩アイコン
# =========================================================
WATERCOLOR_ICON_DIR = "ShufuMate_home_icons_8"


def watercolor_icon(filename):
    return f"{WATERCOLOR_ICON_DIR}/{filename}"


# =========================================================
# ページ設定
# ※ 最初のStreamlit命令
# =========================================================
st.set_page_config(
    page_title="記録する｜ShufuMate",
    page_icon=get_page_icon(
        watercolor_icon("record.png"),
        "📝",
    ),
    layout="centered",
)


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログイン
# =========================================================
require_login()

user_id = get_user_id()
today = jst_today_str()


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="記録する",
    subtitle=(
        "体重・体脂肪・筋肉量・食事を記録して、"
        "からだの変化を確認できます。"
    ),
    icon_file=watercolor_icon(
        "record.png"
    ),
    emoji="📝",
)


# =========================================================
# 今日の記録
# =========================================================
render_section_header(
    title="今日の記録",
    icon_file=watercolor_icon(
        "state.png"
    ),
    emoji="🌿",
)

render_note(
    f"記録日：{today}\n"
    "測っていない項目は無理に入力しなくても大丈夫です。"
)


# =========================================================
# 入力フォーム
# =========================================================
with st.form(
    "daily_log_form"
):

    # -----------------------------------------------------
    # からだ
    # -----------------------------------------------------
    st.markdown(
        "### からだ"
    )

    col1, col2 = st.columns(2)

    with col1:

        weight = st.number_input(
            "体重（kg）",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=0.1,
            format="%.1f",
            key="record_weight",
        )

    with col2:

        body_fat = st.number_input(
            "体脂肪率（%）",
            min_value=0.0,
            max_value=60.0,
            value=20.0,
            step=0.1,
            format="%.1f",
            key="record_body_fat",
        )

    muscle_mass = st.number_input(
        "筋肉量（kg）",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        format="%.1f",
        help=(
            "測っていない日は0のままでOKです。"
            "0は未入力として保存します。"
        ),
        key="record_muscle_mass",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 食事
    # -----------------------------------------------------
    st.markdown(
        "### 食事"
    )

    breakfast = st.text_area(
        "朝",
        placeholder=(
            "例：白湯、豆乳、"
            "アサイー、キウイ"
        ),
        height=80,
        key="record_breakfast",
    )

    lunch = st.text_area(
        "昼",
        placeholder=(
            "例：鮭枝豆おにぎり、"
            "鶏むね肉、卵、味噌汁"
        ),
        height=80,
        key="record_lunch",
    )

    dinner = st.text_area(
        "夜",
        placeholder=(
            "例：豚しゃぶ、豆腐、"
            "野菜、ご飯"
        ),
        height=80,
        key="record_dinner",
    )

    snack = st.text_area(
        "間食",
        placeholder=(
            "例：ヨーグルト、バナナ"
        ),
        height=70,
        key="record_snack",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # メモ
    # -----------------------------------------------------
    st.markdown(
        "### 今日のメモ"
    )

    memo = st.text_area(
        "運動・体調など",
        placeholder=(
            "例：筋トレ＋ラン20分。"
            "脚は軽い。睡眠7時間。"
        ),
        height=100,
        key="record_memo",
    )

    submitted = (
        st.form_submit_button(
            "保存する",
            use_container_width=True,
        )
    )


# =========================================================
# 保存
# =========================================================
if submitted:

    muscle_value = (
        round(
            float(muscle_mass),
            1,
        )
        if muscle_mass > 0
        else ""
    )

    meal_memo = (
        f"朝: {breakfast.strip()}\n"
        f"昼: {lunch.strip()}\n"
        f"夜: {dinner.strip()}\n"
        f"間食: {snack.strip()}\n"
        f"メモ: {memo.strip()}"
    )

    log = {
        "user_id": user_id,
        "log_date": today,
        "weight": round(
            float(weight),
            1,
        ),
        "body_fat": round(
            float(body_fat),
            1,
        ),
        "muscle_mass": muscle_value,
        "meal_memo": meal_memo,
    }

    try:

        saved = save_diet_log(
            user_id,
            log,
        )

        if saved:

            st.success(
                "今日の記録を保存しました。"
            )

            st.rerun()

        else:

            st.error(
                "記録を保存できませんでした。"
            )

    except Exception as e:

        st.error(
            "保存中にエラーが発生しました。"
        )

        st.caption(
            str(e)
        )


# =========================================================
# 記録取得
# =========================================================
logs = load_diet_logs(
    user_id
)


# =========================================================
# 記録なし
# =========================================================
if not logs:

    render_divider()

    render_note(
        "まだ記録がありません。\n"
        "上のフォームから今日の記録を保存してみましょう。"
    )

    st.stop()


# =========================================================
# DataFrame
# =========================================================
df = pd.DataFrame(
    logs
)


# =========================================================
# 日付
# =========================================================
if "log_date" in df.columns:

    df["log_date"] = pd.to_datetime(
        df["log_date"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "log_date"
        ]
    )

    df = df.sort_values(
        "log_date"
    )


# =========================================================
# 数値
# =========================================================
for col in [
    "weight",
    "body_fat",
    "muscle_mass",
]:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )


# =========================================================
# 記録グラフ
# =========================================================
render_divider()

render_section_header(
    title="記録グラフ",
    icon_file=watercolor_icon("trend.png"),
    emoji="📊",
)

render_note(
    "体脂肪率・筋肉量・体重の変化を確認できます。"
)


# =========================================================
# 表示期間
# =========================================================
period = st.radio(
    "表示期間",
    [
        "直近30日",
        "直近90日",
        "すべて",
    ],
    horizontal=True,
    key="record_chart_period",
)


chart_df = df.copy()


if (
    not chart_df.empty
    and "log_date" in chart_df.columns
):

    latest_chart_date = chart_df[
        "log_date"
    ].max()

    if period == "直近30日":

        start_date = (
            latest_chart_date
            - pd.Timedelta(days=29)
        )

        chart_df = chart_df[
            chart_df["log_date"]
            >= start_date
        ]

    elif period == "直近90日":

        start_date = (
            latest_chart_date
            - pd.Timedelta(days=89)
        )

        chart_df = chart_df[
            chart_df["log_date"]
            >= start_date
        ]


# =========================================================
# 共通グラフ関数
# =========================================================
def make_body_chart(
    data,
    value_column,
    label,
    unit,
    minimum_margin,
):

    plot_df = (
        data[
            [
                "log_date",
                value_column,
            ]
        ]
        .dropna()
        .copy()
    )

    # 筋肉量など0を未入力扱いする項目
    if value_column == "muscle_mass":

        plot_df = plot_df[
            plot_df[value_column] > 0
        ]

    if plot_df.empty:

        return None


    # -----------------------------------------------------
    # 縦軸の自動範囲
    # -----------------------------------------------------
    value_min = plot_df[
        value_column
    ].min()

    value_max = plot_df[
        value_column
    ].max()


    # 1件だけ、または全部同じ値の場合
    if value_min == value_max:

        y_min = max(
            0,
            value_min - minimum_margin,
        )

        y_max = (
            value_max
            + minimum_margin
        )

    else:

        value_range = (
            value_max
            - value_min
        )

        margin = max(
            value_range * 0.25,
            minimum_margin,
        )

        y_min = max(
            0,
            value_min - margin,
        )

        y_max = (
            value_max
            + margin
        )


    # -----------------------------------------------------
    # グラフ
    # -----------------------------------------------------
    chart = (
        alt.Chart(plot_df)
        .mark_line(
            point=True,
            strokeWidth=3,
        )
        .encode(

            x=alt.X(
                "log_date:T",
                title=None,
                axis=alt.Axis(
                    format="%m/%d",
                    labelAngle=0,
                ),
            ),

            y=alt.Y(
                f"{value_column}:Q",
                title=f"{label}（{unit}）",
                scale=alt.Scale(
                    domain=[
                        y_min,
                        y_max,
                    ],
                    zero=False,
                    nice=True,
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "log_date:T",
                    title="日付",
                    format="%Y/%m/%d",
                ),
                alt.Tooltip(
                    f"{value_column}:Q",
                    title=label,
                    format=".1f",
                ),
            ],
        )
        .properties(
            height=300
        )
    )

    return chart


# =========================================================
# 体脂肪率
# =========================================================
st.markdown(
    "### 体脂肪率"
)

fat_chart = make_body_chart(
    data=chart_df,
    value_column="body_fat",
    label="体脂肪率",
    unit="%",
    minimum_margin=2.0,
)


if fat_chart is not None:

    st.altair_chart(
        fat_chart,
        use_container_width=True,
    )

else:

    st.info(
        "体脂肪率の記録がまだありません。"
    )


# =========================================================
# 筋肉量
# =========================================================
st.markdown(
    "### 筋肉量"
)

muscle_chart = make_body_chart(
    data=chart_df,
    value_column="muscle_mass",
    label="筋肉量",
    unit="kg",
    minimum_margin=1.0,
)


if muscle_chart is not None:

    st.altair_chart(
        muscle_chart,
        use_container_width=True,
    )

else:

    st.info(
        "筋肉量の記録がまだありません。"
    )


# =========================================================
# 体重
# =========================================================
st.markdown(
    "### 体重"
)

weight_chart = make_body_chart(
    data=chart_df,
    value_column="weight",
    label="体重",
    unit="kg",
    minimum_margin=2.0,
)


if weight_chart is not None:

    st.altair_chart(
        weight_chart,
        use_container_width=True,
    )

else:

    st.info(
        "体重の記録がまだありません。"
    )

# =========================================================
# 最近の変化
# =========================================================
render_divider()

render_section_header(
    title="最近の変化",
    icon_file=watercolor_icon(
        "trend.png"
    ),
    emoji="📈",
)

render_note(
    "直近30日の記録から、"
    "からだの変化を確認します。"
)


latest_analysis_date = (
    df[
        "log_date"
    ].max()
)

analysis_start = (
    latest_analysis_date
    - pd.Timedelta(
        days=29
    )
)

analysis_df = df[
    df["log_date"]
    >= analysis_start
].copy()


comments = []


# =========================================================
# 体重分析
# =========================================================
weight_data = (
    analysis_df[
        "weight"
    ].dropna()
    if "weight"
    in analysis_df.columns
    else pd.Series(
        dtype=float
    )
)

weight_diff = None


if len(weight_data) >= 2:

    weight_diff = (
        weight_data.iloc[-1]
        - weight_data.iloc[0]
    )

    if weight_diff < -1.0:

        comments.append(
            "体重はこの30日で減少傾向です。"
        )

    elif weight_diff > 1.0:

        comments.append(
            "体重はこの30日で増加傾向です。"
        )

    else:

        comments.append(
            "体重はこの30日、"
            "大きく変わらず安定しています。"
        )


# =========================================================
# 体脂肪分析
# =========================================================
fat_data = (
    analysis_df[
        "body_fat"
    ].dropna()
    if "body_fat"
    in analysis_df.columns
    else pd.Series(
        dtype=float
    )
)

fat_diff = None


if len(fat_data) >= 2:

    fat_diff = (
        fat_data.iloc[-1]
        - fat_data.iloc[0]
    )

    if fat_diff < -1.0:

        comments.append(
            "体脂肪率はこの30日で下がっています。"
        )

    elif fat_diff > 1.0:

        comments.append(
            "体脂肪率はこの30日で少し上がっています。"
        )

    else:

        comments.append(
            "体脂肪率はこの30日、"
            "ほぼ安定しています。"
        )


# =========================================================
# 筋肉量分析
# =========================================================
if "muscle_mass" in analysis_df.columns:

    muscle_data = (
        analysis_df[
            analysis_df[
                "muscle_mass"
            ] > 0
        ][
            "muscle_mass"
        ]
        .dropna()
    )

else:

    muscle_data = pd.Series(
        dtype=float
    )


muscle_diff = None


if len(muscle_data) >= 2:

    muscle_diff = (
        muscle_data.iloc[-1]
        - muscle_data.iloc[0]
    )

    if muscle_diff > 0.3:

        comments.append(
            "筋肉量はこの30日で増加しています。"
        )

    elif muscle_diff < -0.3:

        comments.append(
            "筋肉量はこの30日で少し下がっています。"
        )

    else:

        comments.append(
            "筋肉量はこの30日、安定しています。"
        )


# =========================================================
# 最近の変化表示
# =========================================================
if comments:

    render_focus_card(
        "\n".join(
            f"・{comment}"
            for comment in comments
        )
    )

else:

    render_note(
        "もう少し記録が増えると、"
        "最近の変化を分析できます。"
    )


# =========================================================
# 今日のアドバイス
# =========================================================
render_section_header(
    title="今日のアドバイス",
    icon_file=watercolor_icon(
        "advice.png"
    ),
    emoji="💡",
)


if (
    muscle_diff is not None
    and muscle_diff > 0.3
):

    advice = (
        "筋肉量が増えています。\n"
        "食事を減らしすぎず、"
        "今の運動とたんぱく質を"
        "続けていきましょう。"
    )

elif (
    muscle_diff is not None
    and muscle_diff < -0.3
):

    advice = (
        "筋肉量が少し下がっています。\n"
        "たんぱく質・筋トレ・休養の"
        "バランスを確認してみましょう。"
    )

elif (
    fat_diff is not None
    and fat_diff > 1.0
):

    advice = (
        "体脂肪率が少し上がっています。\n"
        "食事を極端に減らすのではなく、"
        "間食・夜の食事・活動量を"
        "一度確認してみましょう。"
    )

else:

    advice = (
        "大きく変えすぎず、"
        "食事・運動・休養を整えながら"
        "続けていきましょう。"
    )


render_answer_card(
    advice
)


# =========================================================
# 最新記録
# =========================================================
render_divider()

render_section_header(
    title="最新記録",
    icon_file=watercolor_icon(
        "latest.png"
    ),
    emoji="📋",
)


latest = df.iloc[-1]

latest_date = latest.get(
    "log_date"
)


if pd.notna(
    latest_date
):

    render_note(
        "記録日："
        f"{latest_date.strftime('%Y/%m/%d')}"
    )


col1, col2, col3 = (
    st.columns(3)
)


# =========================================================
# 最新体重
# =========================================================
with col1:

    latest_weight = (
        latest.get(
            "weight"
        )
    )

    if pd.notna(
        latest_weight
    ):

        st.metric(
            "体重",
            f"{latest_weight:.1f} kg",
        )

    else:

        st.metric(
            "体重",
            "—",
        )


# =========================================================
# 最新体脂肪
# =========================================================
with col2:

    latest_fat = (
        latest.get(
            "body_fat"
        )
    )

    if pd.notna(
        latest_fat
    ):

        st.metric(
            "体脂肪",
            f"{latest_fat:.1f} %",
        )

    else:

        st.metric(
            "体脂肪",
            "—",
        )


# =========================================================
# 最新筋肉量
# =========================================================
with col3:

    latest_muscle = None

    if "muscle_mass" in df.columns:

        valid_muscle = (
            df[
                df[
                    "muscle_mass"
                ] > 0
            ][
                "muscle_mass"
            ]
            .dropna()
        )

        if not valid_muscle.empty:

            latest_muscle = (
                valid_muscle.iloc[-1]
            )

    if latest_muscle is not None:

        st.metric(
            "筋肉量",
            f"{latest_muscle:.1f} kg",
        )

    else:

        st.metric(
            "筋肉量",
            "—",
        )


# =========================================================
# 最新食事・メモ
# =========================================================
meal_memo = latest.get(
    "meal_memo",
    "",
)


if (
    meal_memo
    and
    str(meal_memo).strip()
):

    render_section_header(
        title="最新の食事・メモ",
        icon_file=watercolor_icon(
            "record.png"
        ),
        emoji="🍽️",
    )

    render_card(
        str(meal_memo)
    )
