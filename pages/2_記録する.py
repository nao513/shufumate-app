# =========================================================
# ShufuMate
# 2_記録する.py
# 完全版
# =========================================================

import streamlit as st
import pandas as pd
import altair as alt

from app_core import *


# =========================================================
# ページ設定
# ※ 最初のStreamlit命令
# =========================================================
st.set_page_config(
    page_title="記録する｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/record.png",
        "📝",
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
# このページ専用CSS
# =========================================================
st.markdown(
    """
    <style>

    /* 入力フォーム */
    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.58);
        border: 1px solid rgba(139,100,72,0.12);
        border-radius: 22px;
        padding: 20px;
    }

    /* 入力欄 */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 13px !important;
    }

    /* ラジオボタン */
    div[role="radiogroup"] {
        gap: 1rem;
    }

    /* グラフ見出し */
    .record-chart-title {
        color: #5c4033;
        font-size: 1.35rem;
        font-weight: 900;
        margin-top: 22px;
        margin-bottom: 5px;
    }

    .record-chart-caption {
        color: #8a7568;
        font-size: 0.88rem;
        margin-bottom: 10px;
    }

    /* 最新記録 */
    .latest-date-card {
        background: rgba(255,250,244,0.95);
        border: 1px solid rgba(139,100,72,0.12);
        border-radius: 18px;
        padding: 14px 17px;
        color: #765747;
        margin-bottom: 15px;
    }

    /* 食事メモ */
    .meal-log-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(139,100,72,0.12);
        border-radius: 20px;
        padding: 18px 20px;
        color: #5c4033;
        line-height: 1.9;
        margin-top: 10px;
    }

    .meal-log-label {
        color: #8a6b59;
        font-weight: 800;
    }

    /* metric */
    div[data-testid="stMetric"] {
        min-height: 132px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    div[data-testid="stMetricValue"] {
        color: #604436;
    }

    @media (max-width: 640px) {

        div[data-testid="stMetric"] {
            min-height: 105px;
            padding: 11px !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.55rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def numeric_or_none(value):

    try:

        if pd.isna(value):
            return None

        number = float(value)

        if number <= 0:
            return None

        return number

    except Exception:
        return None


def latest_value(df, column):

    if (
        df is None
        or df.empty
        or column not in df.columns
        or "log_date" not in df.columns
    ):
        return None, None

    temp = df[
        ["log_date", column]
    ].copy()

    temp[column] = pd.to_numeric(
        temp[column],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[
            "log_date",
            column,
        ]
    )

    temp = temp[
        temp[column] > 0
    ]

    if temp.empty:
        return None, None

    temp = temp.sort_values(
        "log_date"
    )

    row = temp.iloc[-1]

    return (
        float(row[column]),
        row["log_date"],
    )


# =========================================================
# 食事メモ分解
# =========================================================
def parse_meal_memo(value):

    result = {
        "朝": "",
        "昼": "",
        "夜": "",
        "間食": "",
        "メモ": "",
    }

    text = clean_text(value)

    if not text:
        return result

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        matched = False

        for key in result.keys():

            prefixes = [
                f"{key}:",
                f"{key}：",
            ]

            for prefix in prefixes:

                if line.startswith(prefix):

                    result[key] = (
                        line[len(prefix):]
                        .strip()
                    )

                    matched = True
                    break

            if matched:
                break

    return result


# =========================================================
# グラフ作成
# =========================================================
def make_body_chart(
    df,
    column,
    label,
    unit,
    minimum_margin,
):

    if (
        df is None
        or df.empty
        or column not in df.columns
        or "log_date" not in df.columns
    ):
        return None

    plot_df = df[
        ["log_date", column]
    ].copy()

    plot_df[column] = pd.to_numeric(
        plot_df[column],
        errors="coerce",
    )

    plot_df = plot_df.dropna(
        subset=[
            "log_date",
            column,
        ]
    )

    plot_df = plot_df[
        plot_df[column] > 0
    ]

    if plot_df.empty:
        return None

    plot_df = plot_df.sort_values(
        "log_date"
    )

    minimum = float(
        plot_df[column].min()
    )

    maximum = float(
        plot_df[column].max()
    )

    difference = (
        maximum - minimum
    )

    margin = max(
        difference * 0.30,
        minimum_margin,
    )

    y_min = max(
        0,
        minimum - margin,
    )

    y_max = (
        maximum + margin
    )

    if maximum == minimum:

        y_min = max(
            0,
            minimum - minimum_margin,
        )

        y_max = (
            maximum + minimum_margin
        )

    line = (
        alt.Chart(plot_df)
        .mark_line(
            point=alt.OverlayMarkDef(
                size=55
            ),
            strokeWidth=3,
        )
        .encode(

            x=alt.X(
                "log_date:T",
                title=None,
                axis=alt.Axis(
                    format="%m/%d",
                    labelAngle=0,
                    tickCount=6,
                    grid=False,
                ),
            ),

            y=alt.Y(
                f"{column}:Q",
                title=f"{label}（{unit}）",
                scale=alt.Scale(
                    domain=[
                        y_min,
                        y_max,
                    ],
                    zero=False,
                ),
                axis=alt.Axis(
                    grid=True,
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "log_date:T",
                    title="日付",
                    format="%Y/%m/%d",
                ),

                alt.Tooltip(
                    f"{column}:Q",
                    title=label,
                    format=".1f",
                ),
            ],
        )
        .properties(
            height=290
        )
    )

    return line


# =========================================================
# DietLogs読み込み
# app_core.pyの共通処理だけを使用
# =========================================================
try:

    df = load_diet_dataframe(
        user_id
    )

except Exception as e:

    st.error(
        "記録データを読み込めませんでした。"
    )

    st.caption(
        str(e)
    )

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


# =========================================================
# 最新有効値
# =========================================================
latest_weight, _ = latest_value(
    df,
    "weight",
)

latest_body_fat, _ = latest_value(
    df,
    "body_fat",
)

latest_muscle, _ = latest_value(
    df,
    "muscle_mass",
)


# =========================================================
# 入力初期値
# =========================================================
default_weight = (
    latest_weight
    if latest_weight is not None
    else 50.0
)

default_body_fat = (
    latest_body_fat
    if latest_body_fat is not None
    else 20.0
)

default_muscle = (
    latest_muscle
    if latest_muscle is not None
    else 0.0
)


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="記録する",
    subtitle=(
        "体重・体脂肪率・筋肉量・食事を記録して、"
        "からだの変化を確認できます。"
    ),
    icon_file="ShufuMate_home_icons_8/record.png",
    emoji="📝",
)


# =========================================================
# 今日の記録
# =========================================================
render_section_header(
    title="今日の記録",
    icon_file="ShufuMate_home_icons_8/record.png",
    emoji="📝",
)

today = jst_today_str()

render_note(
    f"記録日：{today.replace('-', '/')}"
)


# =========================================================
# 入力フォーム
# =========================================================
with st.form(
    "shufumate_daily_record_form"
):

    st.markdown(
        "### からだ"
    )

    col1, col2 = st.columns(2)

    with col1:

        weight = st.number_input(
            "体重（kg）",
            min_value=0.0,
            max_value=200.0,
            value=float(default_weight),
            step=0.1,
            format="%.1f",
        )

    with col2:

        body_fat = st.number_input(
            "体脂肪率（%）",
            min_value=0.0,
            max_value=60.0,
            value=float(default_body_fat),
            step=0.1,
            format="%.1f",
        )

    muscle_mass = st.number_input(
        "筋肉量（kg）",
        min_value=0.0,
        max_value=100.0,
        value=float(default_muscle),
        step=0.1,
        format="%.1f",
        help=(
            "測定していない場合は0にすると、"
            "未入力として保存します。"
        ),
    )

    st.markdown("---")

    st.markdown(
        "### 食事"
    )

    breakfast = st.text_area(
        "朝",
        placeholder=(
            "例：白湯、豆乳、アサイー、"
            "キウイ、納豆"
        ),
        height=75,
    )

    lunch = st.text_area(
        "昼",
        placeholder=(
            "例：おにぎり、味噌汁、"
            "鶏むね肉、卵"
        ),
        height=75,
    )

    dinner = st.text_area(
        "夜",
        placeholder=(
            "例：豚しゃぶ、野菜、"
            "豆腐、ご飯"
        ),
        height=75,
    )

    snack = st.text_area(
        "間食",
        placeholder=(
            "例：ヨーグルト、"
            "バナナ、プルーン"
        ),
        height=70,
    )

    st.markdown("---")

    st.markdown(
        "### 今日のメモ"
    )

    memo = st.text_area(
        "運動・体調・気づいたこと",
        placeholder=(
            "例：筋トレ＋ラン20分。"
            "脚が軽かった。"
        ),
        height=90,
    )

    submitted = (
        st.form_submit_button(
            "今日の記録を保存する",
            use_container_width=True,
        )
    )


# =========================================================
# 保存
# =========================================================
if submitted:

    meal_memo = (
        f"朝: {clean_text(breakfast)}\n"
        f"昼: {clean_text(lunch)}\n"
        f"夜: {clean_text(dinner)}\n"
        f"間食: {clean_text(snack)}\n"
        f"メモ: {clean_text(memo)}"
    )

    log_data = {

        "log_date":
            today,

        "weight":
            (
                round(
                    float(weight),
                    1,
                )
                if weight > 0
                else ""
            ),

        "body_fat":
            (
                round(
                    float(body_fat),
                    1,
                )
                if body_fat > 0
                else ""
            ),

        "muscle_mass":
            (
                round(
                    float(muscle_mass),
                    1,
                )
                if muscle_mass > 0
                else ""
            ),

        "meal_memo":
            meal_memo,
    }

    try:

        save_diet_log(
            user_id,
            log_data,
        )

        st.success(
            "今日の記録を保存しました ✨"
        )

        st.rerun()

    except Exception as e:

        st.error(
            "保存中にエラーが発生しました。"
        )

        st.caption(
            str(e)
        )


# =========================================================
# からだの変化
# =========================================================
render_section_header(
    title="からだの変化",
    icon_file="ShufuMate_home_icons_8/trend.png",
    emoji="📈",
)


if df.empty:

    st.info(
        "まだ記録がありません。"
    )

else:

    period = st.radio(
        "表示期間",
        [
            "直近30日",
            "直近90日",
            "すべて",
        ],
        horizontal=True,
        key="record_period",
    )

    chart_df = df.copy()

    if not chart_df.empty:

        latest_date = (
            chart_df[
                "log_date"
            ].max()
        )

        if period == "直近30日":

            start_date = (
                latest_date
                - pd.Timedelta(
                    days=29
                )
            )

            chart_df = chart_df[
                chart_df["log_date"]
                >= start_date
            ]

        elif period == "直近90日":

            start_date = (
                latest_date
                - pd.Timedelta(
                    days=89
                )
            )

            chart_df = chart_df[
                chart_df["log_date"]
                >= start_date
            ]


    # =====================================================
    # 体脂肪率
    # =====================================================
    st.markdown(
        """
        <div class="record-chart-title">
            体脂肪率
        </div>
        <div class="record-chart-caption">
            体重だけでなく、からだの中身の変化を確認します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    fat_chart = make_body_chart(
        chart_df,
        "body_fat",
        "体脂肪率",
        "%",
        1.5,
    )

    if fat_chart is None:

        st.info(
            "体脂肪率の記録がまだありません。"
        )

    else:

        st.altair_chart(
            fat_chart,
            use_container_width=True,
        )


    # =====================================================
    # 筋肉量
    # =====================================================
    st.markdown(
        """
        <div class="record-chart-title">
            筋肉量
        </div>
        <div class="record-chart-caption">
            筋肉を維持できているかを確認します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    muscle_chart = make_body_chart(
        chart_df,
        "muscle_mass",
        "筋肉量",
        "kg",
        1.0,
    )

    if muscle_chart is None:

        st.info(
            "筋肉量の記録がまだありません。"
        )

    else:

        st.altair_chart(
            muscle_chart,
            use_container_width=True,
        )


    # =====================================================
    # 体重
    # =====================================================
    st.markdown(
        """
        <div class="record-chart-title">
            体重
        </div>
        <div class="record-chart-caption">
            日々の数字より、長い目で変化を確認します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    weight_chart = make_body_chart(
        chart_df,
        "weight",
        "体重",
        "kg",
        1.5,
    )

    if weight_chart is None:

        st.info(
            "体重の記録がまだありません。"
        )

    else:

        st.altair_chart(
            weight_chart,
            use_container_width=True,
        )


# =========================================================
# 最新記録
# =========================================================
render_section_header(
    title="最新記録",
    icon_file="ShufuMate_home_icons_8/latest.png",
    emoji="📋",
)


if df.empty:

    st.info(
        "まだ記録がありません。"
    )

else:

    # -----------------------------------------------------
    # 最新行
    # -----------------------------------------------------
    latest_row = (
        df
        .sort_values("log_date")
        .iloc[-1]
    )

    latest_date = latest_row.get(
        "log_date"
    )

    if pd.notna(latest_date):

        date_text = (
            latest_date.strftime(
                "%Y/%m/%d"
            )
        )

    else:

        date_text = "—"

    st.markdown(
        f"""
        <div class="latest-date-card">
            最新記録：{safe_text(date_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # 各項目は最新有効値
    # -----------------------------------------------------
    display_weight, _ = latest_value(
        df,
        "weight",
    )

    display_fat, _ = latest_value(
        df,
        "body_fat",
    )

    display_muscle, _ = latest_value(
        df,
        "muscle_mass",
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "体重",
            (
                f"{display_weight:.1f} kg"
                if display_weight is not None
                else "—"
            ),
        )

    with col2:

        st.metric(
            "体脂肪率",
            (
                f"{display_fat:.1f} %"
                if display_fat is not None
                else "—"
            ),
        )

    with col3:

        st.metric(
            "筋肉量",
            (
                f"{display_muscle:.1f} kg"
                if display_muscle is not None
                else "—"
            ),
        )


    # =====================================================
    # 食事・メモ
    #
    # 重要：
    # 必ず meal_memo 列だけを見る
    # muscle_mass は一切参照しない
    # =====================================================
    render_section_header(
        title="食事・メモ",
        icon_file="ShufuMate_home_icons_8/advice.png",
        emoji="🍽️",
    )

    raw_meal_memo = ""

    if "meal_memo" in df.columns:

        raw_meal_memo = clean_text(
            latest_row.get(
                "meal_memo",
                ""
            )
        )


    # -----------------------------------------------------
    # meal_memoが本当に食事メモか確認
    #
    # 旧データで「37」等が入ってしまった場合は
    # 表示しない
    # -----------------------------------------------------
    parsed = parse_meal_memo(
        raw_meal_memo
    )

    has_structured_meal = any(
        clean_text(value)
        for value in parsed.values()
    )


    if has_structured_meal:

        meal_html_parts = []

        for label in [
            "朝",
            "昼",
            "夜",
            "間食",
            "メモ",
        ]:

            value = clean_text(
                parsed.get(
                    label,
                    ""
                )
            )

            if value:

                meal_html_parts.append(
                    f"""
                    <div>
                        <span class="meal-log-label">
                            {safe_text(label)}：
                        </span>
                        {safe_text(value)}
                    </div>
                    """
                )

        meal_html = "\n".join(
            meal_html_parts
        )

        st.markdown(
            f"""
            <div class="meal-log-card">
                {meal_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif raw_meal_memo:

        # -------------------------------------------------
        # 古い形式の食事文章なら表示
        # 数字だけなら筋肉量誤読の可能性があるので除外
        # -------------------------------------------------
        try:

            float(
                raw_meal_memo
            )

            is_only_number = True

        except Exception:

            is_only_number = False


        if is_only_number:

            st.info(
                "この日の食事・メモはありません。"
            )

        else:

            st.markdown(
                f"""
                <div class="meal-log-card">
                    {safe_html_with_br(raw_meal_memo)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "この日の食事・メモはありません。"
        )
