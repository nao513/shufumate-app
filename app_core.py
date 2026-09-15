import streamlit as st
import pandas as pd
import altair as alt

from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    load_diet_logs,
    jst_today_str,
    get_page_icon,
    inject_shufumate_css,
    render_page_header,
    render_section_header,
    render_note,
)


# =========================================================
# ページ設定
# ※ 必ず最初のStreamlit命令
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
# ログイン
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# このページ専用CSS
# =========================================================
st.markdown(
    """
<style>

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.90);
    border: 1px solid rgba(168,126,88,0.14);
    border-radius: 18px;
    padding: 14px 16px;
}

div[data-testid="stMetricLabel"] {
    color: #806c60;
}

div[data-testid="stMetricValue"] {
    color: #5b4033;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.42);
    border: 1px solid rgba(168,126,88,0.12);
    border-radius: 20px;
    padding: 18px;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# データ整形
# Homeと同じ考え方
# =========================================================
def prepare_diet_dataframe(logs):

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)

    if df.empty:
        return df


    # -----------------------------------------------------
    # 列名の前後空白削除
    # -----------------------------------------------------
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]


    # -----------------------------------------------------
    # 列名の揺れを吸収
    # -----------------------------------------------------
    aliases = {

        "user_id": [
            "user_id",
            "userid",
            "ユーザーID",
        ],

        "log_date": [
            "log_date",
            "date",
            "日付",
        ],

        "weight": [
            "weight",
            "体重",
            "体重(kg)",
            "体重（kg）",
        ],

        "body_fat": [
            "body_fat",
            "bodyfat",
            "体脂肪",
            "体脂肪率",
            "体脂肪率(%)",
            "体脂肪率（%）",
        ],

        "muscle_mass": [
            "muscle_mass",
            "muscle",
            "muscle_kg",
            "筋肉量",
            "筋肉量(kg)",
            "筋肉量（kg）",
        ],

        "meal_memo": [
            "meal_memo",
            "memo",
            "食事メモ",
        ],
    }


    for standard_name, candidates in aliases.items():

        if standard_name in df.columns:
            continue

        for candidate in candidates:

            if candidate in df.columns:

                df = df.rename(
                    columns={
                        candidate: standard_name
                    }
                )

                break


    # -----------------------------------------------------
    # 旧DietLogs
    #
    # A user_id
    # B log_date
    # C weight
    # D body_fat
    # E muscle_mass
    # F meal_memo
    # -----------------------------------------------------
    columns = list(df.columns)

    expected = [
        "user_id",
        "log_date",
        "weight",
        "body_fat",
        "muscle_mass",
        "meal_memo",
    ]

    for index, standard_name in enumerate(expected):

        if (
            standard_name not in df.columns
            and len(columns) > index
        ):

            old_name = columns[index]

            if old_name not in expected:

                df = df.rename(
                    columns={
                        old_name: standard_name
                    }
                )


    # -----------------------------------------------------
    # 日付
    # -----------------------------------------------------
    if "log_date" in df.columns:

        df["log_date"] = pd.to_datetime(
            df["log_date"],
            errors="coerce",
        )

        df = df.dropna(
            subset=["log_date"]
        )


    # -----------------------------------------------------
    # 数値
    # -----------------------------------------------------
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


    # -----------------------------------------------------
    # 0以下は未入力扱い
    # -----------------------------------------------------
    for column in [
        "weight",
        "body_fat",
        "muscle_mass",
    ]:

        if column in df.columns:

            df.loc[
                df[column] <= 0,
                column
            ] = pd.NA


    # -----------------------------------------------------
    # 日付順
    # -----------------------------------------------------
    if "log_date" in df.columns:

        df = (
            df
            .sort_values("log_date")
            .reset_index(drop=True)
        )


    return df


# =========================================================
# 最新有効値
# =========================================================
def latest_valid_value(
    df,
    column,
):

    if (
        df.empty
        or column not in df.columns
        or "log_date" not in df.columns
    ):
        return None, None


    temp = (
        df[
            ["log_date", column]
        ]
        .dropna()
        .sort_values("log_date")
    )


    if temp.empty:
        return None, None


    row = temp.iloc[-1]

    return (
        float(row[column]),
        row["log_date"],
    )


# =========================================================
# グラフ作成
# =========================================================
def make_body_chart(
    data,
    column,
    label,
    unit,
    minimum_margin,
):

    if (
        data.empty
        or column not in data.columns
    ):
        return None


    plot_df = (
        data[
            ["log_date", column]
        ]
        .dropna()
        .copy()
    )


    if plot_df.empty:
        return None


    plot_df[column] = pd.to_numeric(
        plot_df[column],
        errors="coerce",
    )

    plot_df = plot_df.dropna()


    if plot_df.empty:
        return None


    minimum = float(
        plot_df[column].min()
    )

    maximum = float(
        plot_df[column].max()
    )


    # -----------------------------------------------------
    # 0始まりにしない
    # -----------------------------------------------------
    spread = maximum - minimum

    padding = max(
        spread * 0.35,
        minimum_margin,
    )

    y_min = max(
        0,
        minimum - padding,
    )

    y_max = (
        maximum + padding
    )


    # -----------------------------------------------------
    # 同じ値しかない場合
    # -----------------------------------------------------
    if y_max <= y_min:

        y_min = max(
            0,
            minimum - minimum_margin,
        )

        y_max = (
            maximum + minimum_margin
        )


    base = alt.Chart(
        plot_df
    )


    line = (
        base
        .mark_line(
            point=True
        )
        .encode(

            x=alt.X(
                "log_date:T",
                title=None,
                axis=alt.Axis(
                    format="%m/%d",
                    labelAngle=0,
                    tickCount=6,
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
    )


    return (
        line
        .properties(
            height=300
        )
        .interactive()
    )


# =========================================================
# 現在の記録を先に取得
# =========================================================
try:

    logs = load_diet_logs(
        user_id
    )

except Exception as e:

    st.error(
        "記録データの読み込み中にエラーが発生しました。"
    )

    st.caption(str(e))

    logs = []


df = prepare_diet_dataframe(
    logs
)


# =========================================================
# 入力欄の初期値
# 最新の有効値を使用
# =========================================================
latest_weight, _ = latest_valid_value(
    df,
    "weight",
)

latest_fat, _ = latest_valid_value(
    df,
    "body_fat",
)

latest_muscle, _ = latest_valid_value(
    df,
    "muscle_mass",
)


default_weight = (
    latest_weight
    if latest_weight is not None
    else 50.0
)

default_fat = (
    latest_fat
    if latest_fat is not None
    else 20.0
)

default_muscle = (
    latest_muscle
    if latest_muscle is not None
    else 0.0
)


# =========================================================
# ページタイトル
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
    emoji="🌿",
)


today = jst_today_str()


render_note(
    f"記録日：{today}"
)


# =========================================================
# 入力フォーム
# =========================================================
with st.form(
    "daily_log_form"
):

    st.markdown(
        "#### からだ"
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
            value=float(default_fat),
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
            "測っていない日は0にしてください。"
            "0は未入力として保存します。"
        ),
    )


    st.markdown("---")


    # =====================================================
    # 食事
    # =====================================================
    st.markdown(
        "#### 食事"
    )


    breakfast = st.text_area(
        "朝",
        placeholder=(
            "例：白湯、豆乳、"
            "アサイー、キウイ"
        ),
        height=80,
    )


    lunch = st.text_area(
        "昼",
        placeholder=(
            "例：おにぎり、"
            "鶏むね肉、卵、味噌汁"
        ),
        height=80,
    )


    dinner = st.text_area(
        "夜",
        placeholder=(
            "例：豚しゃぶ、"
            "豆腐、野菜、ご飯"
        ),
        height=80,
    )


    snack = st.text_area(
        "間食",
        placeholder=(
            "例：ヨーグルト、バナナ"
        ),
        height=70,
    )


    st.markdown("---")


    # =====================================================
    # メモ
    # =====================================================
    st.markdown(
        "#### 今日のメモ"
    )


    memo = st.text_area(
        "運動・体調など",
        placeholder=(
            "例：筋トレ＋ラン20分。"
            "脚は軽い。睡眠7時間。"
        ),
        height=100,
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

        "user_id":
            user_id,

        "log_date":
            today,

        "weight":
            round(
                float(weight),
                1,
            ),

        "body_fat":
            round(
                float(body_fat),
                1,
            ),

        "muscle_mass":
            muscle_value,

        "meal_memo":
            meal_memo,
    }


    try:

        save_diet_log(
            user_id,
            log,
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
        "上のフォームから記録すると、"
        "ここにグラフが表示されます。"
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

        latest_date = (
            chart_df["log_date"].max()
        )

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

        latest_date = (
            chart_df["log_date"].max()
        )

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
        "### 体脂肪率"
    )


    fat_chart = make_body_chart(
        data=chart_df,
        column="body_fat",
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


    # =====================================================
    # 筋肉量
    # =====================================================
    st.markdown(
        "### 筋肉量"
    )


    muscle_chart = make_body_chart(
        data=chart_df,
        column="muscle_mass",
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


    # =====================================================
    # 体重
    # =====================================================
    st.markdown(
        "### 体重"
    )


    weight_chart = make_body_chart(
        data=chart_df,
        column="weight",
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
# 最新記録
# =========================================================
render_section_header(
    title="最新記録",
    icon_file="ShufuMate_home_icons_8/latest.png",
    emoji="📋",
)


if not df.empty:

    latest_row = (
        df
        .sort_values("log_date")
        .iloc[-1]
    )


    latest_date = latest_row[
        "log_date"
    ]


    if pd.notna(latest_date):

        render_note(
            "最新記録："
            + latest_date.strftime(
                "%Y/%m/%d"
            )
        )


    # =====================================================
    # 各項目の最新有効値
    # =====================================================
    latest_weight, weight_date = (
        latest_valid_value(
            df,
            "weight",
        )
    )

    latest_fat, fat_date = (
        latest_valid_value(
            df,
            "body_fat",
        )
    )

    latest_muscle, muscle_date = (
        latest_valid_value(
            df,
            "muscle_mass",
        )
    )


    metric1, metric2, metric3 = (
        st.columns(3)
    )


    with metric1:

        st.metric(
            "体重",
            (
                f"{latest_weight:.1f} kg"
                if latest_weight is not None
                else "—"
            ),
        )


    with metric2:

        st.metric(
            "体脂肪率",
            (
                f"{latest_fat:.1f} %"
                if latest_fat is not None
                else "—"
            ),
        )


    with metric3:

        st.metric(
            "筋肉量",
            (
                f"{latest_muscle:.1f} kg"
                if latest_muscle is not None
                else "—"
            ),
        )


    # =====================================================
    # 食事・メモ
    # 最新行のものを表示
    # =====================================================
    if "meal_memo" in df.columns:

        meal_memo = (
            latest_row.get(
                "meal_memo",
                ""
            )
        )


        if (
            pd.notna(meal_memo)
            and str(meal_memo).strip()
        ):

            st.markdown(
                "#### 食事・メモ"
            )

            st.text(
                str(meal_memo)
            )


else:

    st.info(
        "まだ記録がありません。"
    )
