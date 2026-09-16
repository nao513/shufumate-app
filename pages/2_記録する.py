# =========================================================
# ShufuMate
# pages/2_記録する.py
# 最終完全版
# =========================================================

import html
import math

import altair as alt
import pandas as pd
import streamlit as st

from app_core import (
    require_login,
    get_user_id,
    get_page_icon,
    inject_shufumate_css,
    render_page_header,
    render_section_header,
    save_diet_log,
    load_diet_dataframe,
    clean_text,
    jst_today_str,
)


# =========================================================
# ページ設定
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

require_login()

user_id = get_user_id()


# =========================================================
# ページ専用CSS
# =========================================================
st.markdown(
    """
<style>

.record-sub-title {
    color: #5c4033;
    font-size: 1.45rem;
    font-weight: 900;
    margin-top: 30px;
    margin-bottom: 4px;
}

.record-sub-desc {
    color: #8a7468;
    font-size: .90rem;
    line-height: 1.7;
    margin-bottom: 18px;
}

.record-date {
    background: rgba(255,250,244,.92);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 16px;
    padding: 12px 15px;
    color: #765f52;
    margin-bottom: 18px;
}

.record-group-title {
    color: #5d4438;
    font-size: 1.12rem;
    font-weight: 900;
    margin-top: 12px;
    margin-bottom: 10px;
}

.record-latest-card {
    background: rgba(255,250,244,.92);
    border: 1px solid rgba(139,100,72,.12);
    border-radius: 20px;
    padding: 17px 19px;
    color: #685145;
    line-height: 1.85;
    margin-top: 12px;
    margin-bottom: 16px;
}

.record-meal-card {
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 18px;
    padding: 16px 18px;
    color: #665044;
    line-height: 1.85;
    margin-top: 10px;
}

.soft-divider {
    height: 1px;
    background: rgba(139,100,72,.16);
    margin: 30px 0;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 15px !important;
}

div[data-testid="stNumberInput"] input {
    border-radius: 14px !important;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.80);
    border: 1px solid rgba(139,100,72,.11);
    border-radius: 18px;
    padding: 13px 15px;
}

@media (max-width: 640px) {

    .record-sub-title {
        font-size: 1.30rem;
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
    return html.escape(
        str(value or "")
    )


def safe_html_with_br(value):
    return safe_html(value).replace(
        "\n",
        "<br>"
    )


def latest_valid_value(
    dataframe,
    column,
):
    if (
        dataframe is None
        or dataframe.empty
        or column not in dataframe.columns
    ):
        return None

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    values = values.dropna()
    values = values[values > 0]

    if values.empty:
        return None

    return float(
        values.iloc[-1]
    )


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="記録する",
    subtitle=(
        "体組成と食事を記録して、"
        "毎日の変化を確認できます。"
    ),
    icon_file="ShufuMate_home_icons_8/record.png",
    emoji="📝",
)


# =========================================================
# 今日の記録
# ★ アイコンなし
# =========================================================
st.markdown(
    '<div class="record-sub-title">'
    '今日の記録'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="record-sub-desc">'
    '今日の体組成と食事を入力します。'
    '</div>',
    unsafe_allow_html=True,
)


today = jst_today_str()


date_html = (
    '<div class="record-date">'
    f'記録日：<strong>{safe_html(today.replace("-", "/"))}</strong>'
    '</div>'
)

st.markdown(
    date_html,
    unsafe_allow_html=True,
)


# =========================================================
# 入力フォーム
# =========================================================
with st.form(
    "daily_log_form",
    clear_on_submit=False,
):

    # =====================================================
    # 体組成
    # =====================================================
    st.markdown(
        '<div class="record-group-title">'
        '体組成'
        '</div>',
        unsafe_allow_html=True,
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


    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True,
    )


    # =====================================================
    # 食事
    # =====================================================
    st.markdown(
        '<div class="record-group-title">'
        '食事'
        '</div>',
        unsafe_allow_html=True,
    )


    breakfast = st.text_area(
        "朝食",
        placeholder=(
            "例：白湯、豆乳、"
            "アサイー、キウイ"
        ),
        height=80,
        key="record_breakfast",
    )


    lunch = st.text_area(
        "昼食",
        placeholder=(
            "例：鮭枝豆おにぎり、"
            "鶏むね肉、卵、味噌汁"
        ),
        height=80,
        key="record_lunch",
    )


    dinner = st.text_area(
        "夕食",
        placeholder=(
            "例：豚しゃぶ、"
            "豆腐、野菜、ご飯"
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


    memo = st.text_area(
        "運動・体調など",
        placeholder=(
            "例：筋トレ＋ラン20分。"
            "脚は軽い。睡眠7時間。"
        ),
        height=90,
        key="record_memo",
    )


    submitted = st.form_submit_button(
        "保存する",
        use_container_width=True,
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
        f"朝: {clean_text(breakfast)}\n"
        f"昼: {clean_text(lunch)}\n"
        f"夜: {clean_text(dinner)}\n"
        f"間食: {clean_text(snack)}\n"
        f"メモ: {clean_text(memo)}"
    )


    log_data = {
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
            "記録の保存中にエラーが発生しました。"
        )

        st.caption(
            f"エラー内容：{e}"
        )


# =========================================================
# 記録取得
# =========================================================
try:

    df = load_diet_dataframe(
        user_id
    )

except Exception as e:

    df = pd.DataFrame()

    st.warning(
        "記録を読み込めませんでした。"
    )

    st.caption(
        f"エラー内容：{e}"
    )


if not df.empty:

    if "log_date" in df.columns:

        df["log_date"] = pd.to_datetime(
            df["log_date"],
            errors="coerce",
        )

        df = df.dropna(
            subset=["log_date"]
        )

        df = df.sort_values(
            "log_date"
        ).reset_index(
            drop=True
        )


    for column in [
        "weight",
        "body_fat",
        "muscle_mass",
    ]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )


# =========================================================
# 区切り
# =========================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# 最近の変化
# =========================================================
render_section_header(
    title="最近の変化",
    icon_file="ShufuMate_home_icons_8/trend.png",
    emoji="📈",
)


if df.empty:

    st.info(
        "記録が増えると、ここに変化が表示されます。"
    )


else:

    # =====================================================
    # 表示期間
    # =====================================================
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


    if period == "直近30日":

        latest_date = chart_df[
            "log_date"
        ].max()

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

        latest_date = chart_df[
            "log_date"
        ].max()

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
    # グラフ関数
    # =====================================================
    def render_chart(
        dataframe,
        value_col,
        title,
        unit,
        minimum_span,
    ):

        if (
            dataframe.empty
            or value_col not in dataframe.columns
        ):

            st.info(
                f"{title}の記録がありません。"
            )

            return


        data = dataframe[
            [
                "log_date",
                value_col,
            ]
        ].copy()


        data[value_col] = pd.to_numeric(
            data[value_col],
            errors="coerce",
        )


        data = data.dropna(
            subset=[
                "log_date",
                value_col,
            ]
        )


        data = data[
            data[value_col] > 0
        ]


        if data.empty:

            st.info(
                f"{title}の記録がありません。"
            )

            return


        min_value = float(
            data[value_col].min()
        )

        max_value = float(
            data[value_col].max()
        )


        actual_span = (
            max_value
            - min_value
        )


        display_span = max(
            actual_span * 1.4,
            minimum_span,
        )


        center = (
            max_value
            + min_value
        ) / 2


        y_min = max(
            0,
            center
            - display_span / 2,
        )


        y_max = (
            center
            + display_span / 2
        )


        y_min = (
            math.floor(
                y_min * 2
            )
            / 2
        )


        y_max = (
            math.ceil(
                y_max * 2
            )
            / 2
        )


        if period == "直近30日":

            x_format = "%m/%d"
            tick_count = 5


        elif period == "直近90日":

            x_format = "%m/%d"
            tick_count = 6


        else:

            x_format = "%Y/%m"

            month_count = (
                data["log_date"]
                .dt.to_period("M")
                .nunique()
            )

            tick_count = max(
                3,
                min(
                    int(month_count),
                    8,
                ),
            )


        label_expr = (
            "datum.label + ' %'"
            if unit == "%"
            else "datum.label + ' kg'"
        )


        chart = (
            alt.Chart(
                data
            )
            .mark_line(
                point=True
            )
            .encode(

                x=alt.X(
                    "log_date:T",
                    title=None,
                    axis=alt.Axis(
                        format=x_format,
                        labelAngle=0,
                        tickCount=tick_count,
                    ),
                ),

                y=alt.Y(
                    f"{value_col}:Q",
                    title=None,
                    scale=alt.Scale(
                        domain=[
                            y_min,
                            y_max,
                        ],
                        zero=False,
                    ),
                    axis=alt.Axis(
                        labelExpr=label_expr,
                        labelPadding=8,
                    ),
                ),

                tooltip=[
                    alt.Tooltip(
                        "log_date:T",
                        title="日付",
                        format="%Y/%m/%d",
                    ),

                    alt.Tooltip(
                        f"{value_col}:Q",
                        title=title,
                        format=".1f",
                    ),
                ],
            )
            .properties(
                height=240
            )
        )


        st.altair_chart(
            chart,
            use_container_width=True,
        )


    # =====================================================
    # 体脂肪率
    # =====================================================
    st.markdown(
        '<div class="record-group-title">'
        '体脂肪率'
        '</div>',
        unsafe_allow_html=True,
    )

    render_chart(
        chart_df,
        "body_fat",
        "体脂肪率",
        "%",
        8.0,
    )


    # =====================================================
    # 筋肉量
    # =====================================================
    st.markdown(
        '<div class="record-group-title">'
        '筋肉量'
        '</div>',
        unsafe_allow_html=True,
    )

    render_chart(
        chart_df,
        "muscle_mass",
        "筋肉量",
        "kg",
        5.0,
    )


    # =====================================================
    # 体重
    # =====================================================
    st.markdown(
        '<div class="record-group-title">'
        '体重'
        '</div>',
        unsafe_allow_html=True,
    )

    render_chart(
        chart_df,
        "weight",
        "体重",
        "kg",
        10.0,
    )


# =========================================================
# 区切り
# =========================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# 最新の記録
# =========================================================
render_section_header(
    title="最新の記録",
    icon_file="ShufuMate_home_icons_8/latest.png",
    emoji="📋",
)


if df.empty:

    st.info(
        "まだ記録がありません。"
    )


else:

    latest = df.iloc[-1]


    latest_date = latest.get(
        "log_date"
    )


    if pd.notna(
        latest_date
    ):

        latest_date_html = (
            '<div class="record-latest-card">'
            '最新記録：'
            f'<strong>{latest_date.strftime("%Y/%m/%d")}</strong>'
            '</div>'
        )

        st.markdown(
            latest_date_html,
            unsafe_allow_html=True,
        )


    # =====================================================
    # 最新値
    # =====================================================
    latest_weight = latest_valid_value(
        df,
        "weight",
    )

    latest_fat = latest_valid_value(
        df,
        "body_fat",
    )

    latest_muscle = latest_valid_value(
        df,
        "muscle_mass",
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


    # =====================================================
    # 最新の食事・メモ
    # =====================================================
    meal_memo = clean_text(
        latest.get(
            "meal_memo",
            ""
        )
    )


    # 数字だけなら旧列ずれデータとして表示しない
    if meal_memo:

        try:

            float(
                meal_memo
            )

            meal_memo = ""

        except Exception:

            pass


    if meal_memo:

        st.markdown(
            '<div class="record-group-title">'
            '食事・メモ'
            '</div>',
            unsafe_allow_html=True,
        )


        meal_html = (
            '<div class="record-meal-card">'
            f'{safe_html_with_br(meal_memo)}'
            '</div>'
        )


        st.markdown(
            meal_html,
            unsafe_allow_html=True,
        )

    else:

        st.caption(
            "最新の食事・メモはありません。"
        )
