import streamlit as st
import pandas as pd
import altair as alt
import math

from pathlib import Path

from app_core import (
    require_login,
    get_user_id,
    load_diet_logs,
    jst_today,
)


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered",
)

require_login()

user_id = get_user_id()


# =========================================================
# パス
# =========================================================
APP_ROOT = Path(__file__).resolve().parent
HOME_ICON_DIR = APP_ROOT / "assets" / "home_icons"


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

.stApp {
    background:
        linear-gradient(
            180deg,
            #fffaf4 0%,
            #fff7ef 48%,
            #fffaf4 100%
        );
}

.block-container {
    max-width: 920px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* -------------------------
   ロゴ
------------------------- */

.app-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #5b4033;
    margin-bottom: 0.2rem;
}

.app-subtitle {
    color: #857063;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.8rem;
}

/* -------------------------
   見出し
------------------------- */

.section-title {
    font-size: 1.42rem;
    font-weight: 900;
    color: #5b4033;
    margin: 0;
}

.section-desc {
    color: #8a786c;
    font-size: 0.88rem;
    margin-top: 0.15rem;
}

/* -------------------------
   Metric
------------------------- */

div[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 18px;
    padding: 14px 16px;
    border: 1px solid rgba(168, 126, 88, 0.14);
    box-shadow: 0 5px 15px rgba(105, 75, 52, 0.06);
}

/* -------------------------
   ボタン
------------------------- */

.stButton > button {
    border-radius: 14px;
    border: 1px solid #e2cba9;
    background: #fffaf4;
    color: #5b4033;
    font-weight: 800;
    min-height: 46px;
}

.stButton > button:hover {
    background: #f7ead9;
    border-color: #d2ac7d;
    color: #5b4033;
}

/* -------------------------
   区切り
------------------------- */

.soft-divider {
    height: 1px;
    background: #eadfce;
    margin: 2rem 0;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 共通関数
# =========================================================
def icon_path(filename):
    path = HOME_ICON_DIR / filename
    return str(path) if path.exists() else None


def render_section_header(
    title,
    description,
    filename,
):

    c1, c2 = st.columns(
        [1, 7],
        vertical_alignment="center",
    )

    with c1:
        path = icon_path(filename)

        if path:
            st.image(
                path,
                width=72,
            )

    with c2:
        st.markdown(
            f'<div class="section-title">{title}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="section-desc">{description}</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# タイトル
# =========================================================
st.markdown(
    '<div class="app-title">ShufuMate</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="app-subtitle">
毎日の暮らしとからだを、無理なく整える
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DietLogs取得
# =========================================================
logs = load_diet_logs(
    user_id
)

df = pd.DataFrame()


if logs:

    df = pd.DataFrame(
        logs
    )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # -----------------------------------------------------
    # 列名の揺れを吸収
    # -----------------------------------------------------
    aliases = {

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
    }

    for standard_name, candidates in aliases.items():

        if standard_name not in df.columns:

            for candidate in candidates:

                if candidate in df.columns:

                    df = df.rename(
                        columns={
                            candidate:
                            standard_name
                        }
                    )
                    break

    # -----------------------------------------------------
    # 旧DietLogs対応
    # A=user_id
    # B=log_date
    # C=weight
    # D=body_fat
    # E=muscle_mass
    # -----------------------------------------------------
    if (
        "muscle_mass" not in df.columns
        and len(df.columns) >= 5
    ):

        df = df.rename(
            columns={
                df.columns[4]:
                "muscle_mass"
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

        df = df.sort_values(
            "log_date"
        )

    # -----------------------------------------------------
    # 数値
    # -----------------------------------------------------
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
# 最新有効値
# =========================================================
def latest_valid(column):

    if (
        df.empty
        or column not in df.columns
    ):
        return None, None

    temp = df[
        [
            "log_date",
            column,
        ]
    ].copy()

    temp[column] = pd.to_numeric(
        temp[column],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[column]
    )

    temp = temp[
        temp[column] > 0
    ]

    if temp.empty:
        return None, None

    row = temp.iloc[-1]

    return (
        float(row[column]),
        row["log_date"],
    )


latest_weight, weight_date = latest_valid(
    "weight"
)

latest_body_fat, fat_date = latest_valid(
    "body_fat"
)

latest_muscle, muscle_date = latest_valid(
    "muscle_mass"
)


# =========================================================
# 今日の状態
# =========================================================
render_section_header(
    "今日の状態",
    "最新の記録から、今のからだの状態です。",
    "state.png",
)


if not df.empty:

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "体重",
            (
                f"{latest_weight:.1f} kg"
                if latest_weight is not None
                else "—"
            ),
        )

    with c2:
        st.metric(
            "体脂肪率",
            (
                f"{latest_body_fat:.1f} %"
                if latest_body_fat is not None
                else "—"
            ),
        )

    with c3:
        st.metric(
            "筋肉量",
            (
                f"{latest_muscle:.1f} kg"
                if latest_muscle is not None
                else "—"
            ),
        )

    if (
        muscle_date is not None
        and fat_date is not None
        and weight_date is not None
    ):

        latest_dates = [
            weight_date,
            fat_date,
            muscle_date,
        ]

        oldest_latest = min(
            latest_dates
        )

        newest_latest = max(
            latest_dates
        )

        if oldest_latest.date() != newest_latest.date():

            st.caption(
                "※項目によって最新記録日が異なります。"
            )

else:

    st.info(
        "まだ記録がありません。"
    )


# =========================================================
# 今日の整え方
# =========================================================
render_section_header(
    "今日の整え方",
    "最近の変化からのアドバイスです。",
    "advice.png",
)


weight_diff = None
fat_diff = None
muscle_diff = None


if not df.empty:

    latest_date = (
        df["log_date"]
        .max()
    )

    start_date = (
        latest_date
        - pd.Timedelta(
            days=29
        )
    )

    analysis = df[
        df["log_date"]
        >= start_date
    ].copy()


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    if "weight" in analysis.columns:

        data = (
            analysis["weight"]
            .dropna()
        )

        data = data[
            data > 0
        ]

        if len(data) >= 2:

            weight_diff = (
                data.iloc[-1]
                - data.iloc[0]
            )


    # -----------------------------------------------------
    # 体脂肪
    # -----------------------------------------------------
    if "body_fat" in analysis.columns:

        data = (
            analysis["body_fat"]
            .dropna()
        )

        data = data[
            data > 0
        ]

        if len(data) >= 2:

            fat_diff = (
                data.iloc[-1]
                - data.iloc[0]
            )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    if "muscle_mass" in analysis.columns:

        data = (
            analysis["muscle_mass"]
            .dropna()
        )

        data = data[
            data > 0
        ]

        if len(data) >= 2:

            muscle_diff = (
                data.iloc[-1]
                - data.iloc[0]
            )


    # -----------------------------------------------------
    # コメント
    # -----------------------------------------------------
    if weight_diff is not None:

        if abs(weight_diff) <= 1:

            st.write(
                "・体重はこの30日、大きく変わらず安定しています。"
            )

        elif weight_diff < 0:

            st.write(
                "・体重はこの30日で減少傾向です。"
            )

        else:

            st.write(
                "・体重はこの30日で増加傾向です。"
            )


    if fat_diff is not None:

        if fat_diff < -1:

            st.write(
                "・体脂肪率はこの30日で下がっています。"
            )

        elif fat_diff > 1:

            st.write(
                "・体脂肪率はこの30日で少し上がっています。"
            )

        else:

            st.write(
                "・体脂肪率はこの30日、ほぼ安定しています。"
            )


    if muscle_diff is not None:

        if muscle_diff > 0.3:

            st.write(
                "・筋肉量はこの30日で増えています。"
            )

        elif muscle_diff < -0.3:

            st.write(
                "・筋肉量はこの30日で少し下がっています。"
            )

        else:

            st.write(
                "・筋肉量はこの30日、安定しています。"
            )


    # -----------------------------------------------------
    # アドバイス
    # -----------------------------------------------------
    if (
        muscle_diff is not None
        and muscle_diff > 0.3
    ):

        st.success(
            "筋肉量が増えています。"
            "今の運動・食事・休養を続けていきましょう。"
        )

    elif (
        muscle_diff is not None
        and muscle_diff < -0.3
    ):

        st.warning(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養を確認してみましょう。"
        )

    elif (
        fat_diff is not None
        and fat_diff > 1
    ):

        st.warning(
            "体脂肪率が少し上がっています。"
            "食事を極端に減らさず、"
            "間食・夜の食事・活動量を確認してみましょう。"
        )

    else:

        st.info(
            "大きく変えすぎず、"
            "食事・運動・休養を整えながら続けていきましょう。"
        )


# =========================================================
# グラフ共通関数
# =========================================================
def render_chart(
    dataframe,
    value_col,
    title,
    unit,
    period,
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


    # -----------------------------------------------------
    # 縦軸：人ごと・期間ごとに自動調整
    # -----------------------------------------------------
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


    # -----------------------------------------------------
    # 横軸
    # -----------------------------------------------------
    if period == "直近30日":

        x_format = "%m/%d"
        tick_count = 5

    elif period == "直近90日":

        x_format = "%Y/%m"
        tick_count = 5

    else:

        x_format = "%Y"

        year_count = (
            data["log_date"]
            .dt.year
            .nunique()
        )

        tick_count = max(
            2,
            min(
                int(year_count) + 1,
                8,
            )
        )


    # -----------------------------------------------------
    # 単位
    # -----------------------------------------------------
    if unit == "%":

        label_expr = (
            "datum.label + ' %'"
        )

    else:

        label_expr = (
            "datum.label + ' kg'"
        )


    # -----------------------------------------------------
    # Altair
    # -----------------------------------------------------
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


# =========================================================
# 最近の変化
# =========================================================
render_section_header(
    "最近の変化",
    "記録の推移をグラフで確認できます。",
    "trend.png",
)


if not df.empty:

    period = st.radio(
        "表示期間",
        [
            "直近30日",
            "直近90日",
            "すべて",
        ],
        horizontal=True,
        key="home_period",
    )


    chart_df = df.copy()


    max_date = (
        chart_df["log_date"]
        .max()
    )


    if period == "直近30日":

        chart_df = chart_df[
            chart_df["log_date"]
            >= (
                max_date
                - pd.Timedelta(
                    days=29
                )
            )
        ]


    elif period == "直近90日":

        chart_df = chart_df[
            chart_df["log_date"]
            >= (
                max_date
                - pd.Timedelta(
                    days=89
                )
            )
        ]


    st.markdown(
        "#### 体脂肪率"
    )

    render_chart(
        chart_df,
        "body_fat",
        "体脂肪率",
        "%",
        period,
        10.0,
    )


    st.markdown(
        "#### 筋肉量"
    )

    render_chart(
        chart_df,
        "muscle_mass",
        "筋肉量",
        "kg",
        period,
        5.0,
    )


    st.markdown(
        "#### 体重"
    )

    render_chart(
        chart_df,
        "weight",
        "体重",
        "kg",
        period,
        10.0,
    )


# =========================================================
# 最新記録
# =========================================================
render_section_header(
    "最新記録",
    "直近の記録内容です。",
    "latest.png",
)


if not df.empty:

    latest = (
        df.iloc[-1]
    )

    latest_log_date = latest.get(
        "log_date"
    )


    if pd.notna(
        latest_log_date
    ):

        st.write(
            "**記録日："
            + latest_log_date.strftime(
                "%Y/%m/%d"
            )
            + "**"
        )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "体重",
            (
                f"{latest_weight:.1f} kg"
                if latest_weight is not None
                else "—"
            ),
        )


    with c2:

        st.metric(
            "体脂肪率",
            (
                f"{latest_body_fat:.1f} %"
                if latest_body_fat is not None
                else "—"
            ),
        )


    with c3:

        st.metric(
            "筋肉量",
            (
                f"{latest_muscle:.1f} kg"
                if latest_muscle is not None
                else "—"
            ),
        )


    # -----------------------------------------------------
    # メモ
    # -----------------------------------------------------
    meal_memo = latest.get(
        "meal_memo",
        ""
    )


    if (
        meal_memo
        and str(meal_memo).strip()
    ):

        st.markdown(
            "##### 食事・メモ"
        )

        st.text(
            str(
                meal_memo
            )
        )


# =========================================================
# メニュー
# =========================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">メニュー</div>',
    unsafe_allow_html=True,
)

st.caption(
    "使いたい機能を選んでください。"
)


# =========================================================
# メニューカード共通
# =========================================================
def menu_card(
    image_file,
    title,
    description,
    button_key,
    page,
):

    path = icon_path(
        image_file
    )

    # -------------------------
    # アイコン
    # -------------------------
    if path:

        left, center, right = st.columns(
            [1, 1.45, 1]
        )

        with center:

            st.image(
                path,
                use_container_width=True,
            )

    # -------------------------
    # タイトル
    # -------------------------
    st.markdown(
        f"""
        <div style="
            text-align:center;
            font-size:1.15rem;
            font-weight:800;
            color:#5b4033;
            margin-top:4px;
            margin-bottom:4px;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # 説明
    # -------------------------
    st.markdown(
        f"""
        <div style="
            text-align:center;
            font-size:0.82rem;
            color:#8a786c;
            min-height:34px;
            margin-bottom:10px;
        ">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # 開くボタン
    # -------------------------
    if st.button(
        "開く",
        key=button_key,
        use_container_width=True,
    ):

        st.switch_page(
            page
        )


# =========================================================
# 1段目
# =========================================================
col1, col2 = st.columns(
    2,
    gap="large",
)


with col1:

    menu_card(
        image_file="record.png",
        title="記録する",
        description="体重・食事・体調を記録",
        button_key="menu_record",
        page="pages/2_記録する.py",
    )


with col2:

    menu_card(
        image_file="chat.png",
        title="相談する",
        description="気になることを相談",
        button_key="menu_chat",
        page="pages/3_相談する.py",
    )


# =========================================================
# 2段目
# =========================================================
col3, col4 = st.columns(
    2,
    gap="large",
)


with col3:

    menu_card(
        image_file="camera.png",
        title="写真で記録",
        description="写真からかんたん記録",
        button_key="menu_camera",
        page="pages/4_写真で記録.py",
    )


with col4:

    menu_card(
        image_file="settings.png",
        title="設定",
        description="プロフィールや目標を設定",
        button_key="menu_settings",
        page="pages/1_設定.py",
    )


# =========================================================
# メニューカード 1段目
# =========================================================
m1, m2 = st.columns(2)


with m1:

    path = icon_path(
        "record.png"
    )

    if path:

        a, b, c = st.columns(
            [1, 1.7, 1]
        )

        with b:

            st.image(
                path,
                use_container_width=True,
            )

    st.markdown(
        "<h4 style='text-align:center;'>記録する</h4>",
        unsafe_allow_html=True,
    )

    st.caption(
        "体重・食事・体調を記録"
    )

    if st.button(
        "記録する",
        key="menu_record",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_記録する.py"
        )


with m2:

    path = icon_path(
        "chat.png"
    )

    if path:

        a, b, c = st.columns(
            [1, 1.7, 1]
        )

        with b:

            st.image(
                path,
                use_container_width=True,
            )

    st.markdown(
        "<h4 style='text-align:center;'>相談する</h4>",
        unsafe_allow_html=True,
    )

    st.caption(
        "気になることを相談"
    )

    if st.button(
        "相談する",
        key="menu_chat",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/3_相談する.py"
        )


# =========================================================
# メニューカード 2段目
# =========================================================
m3, m4 = st.columns(2)


with m3:

    path = icon_path(
        "camera.png"
    )

    if path:

        a, b, c = st.columns(
            [1, 1.7, 1]
        )

        with b:

            st.image(
                path,
                use_container_width=True,
            )

    st.markdown(
        "<h4 style='text-align:center;'>写真で記録</h4>",
        unsafe_allow_html=True,
    )

    st.caption(
        "写真からかんたん記録"
    )

    if st.button(
        "写真で記録",
        key="menu_camera",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/4_写真で記録.py"
        )


with m4:

    path = icon_path(
        "settings.png"
    )

    if path:

        a, b, c = st.columns(
            [1, 1.7, 1]
        )

        with b:

            st.image(
                path,
                use_container_width=True,
            )

    st.markdown(
        "<h4 style='text-align:center;'>設定</h4>",
        unsafe_allow_html=True,
    )

    st.caption(
        "プロフィールや目標を設定"
    )

    if st.button(
        "設定",
        key="menu_settings",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/1_設定.py"
        )


# =========================================================
# フッター
# =========================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

st.caption(
    "今日の日付："
    + jst_today().strftime(
        "%Y/%m/%d"
    )
)
