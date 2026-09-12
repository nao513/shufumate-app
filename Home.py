import streamlit as st
import pandas as pd
import altair as alt
import math

from pathlib import Path
from PIL import Image

from app_core import (
    require_login,
    get_user_id,
    load_diet_logs,
    jst_today,
)


# =========================================================
# パス設定
# =========================================================
APP_ROOT = Path(__file__).resolve().parent

ICON_DIR = APP_ROOT / "assets" / "icons"
HOME_ICON_DIR = APP_ROOT / "assets" / "home_icons"
TOP_VISUAL_DIR = HOME_ICON_DIR / "top"


# =========================================================
# ページアイコン
# =========================================================
def get_page_icon(filename, fallback="🏠"):

    path = ICON_DIR / filename

    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            return fallback

    return fallback


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="ShufuMate",
    page_icon=get_page_icon("home.png", "🏠"),
    layout="centered",
)


# =========================================================
# ログイン確認
# =========================================================
require_login()

user_id = get_user_id()


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
                #fff6ed 45%,
                #fffaf4 100%
            );
    }

    .block-container {
        max-width: 900px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 18px;
        padding: 14px 16px;

        border:
            1px solid
            rgba(139, 100, 72, 0.10);

        box-shadow:
            0 4px 12px
            rgba(96, 65, 45, 0.05);
    }

    .stButton > button {
        background-color: #8d6e63;
        color: white;

        border: none;
        border-radius: 14px;

        padding: 0.75rem 1rem;
        font-weight: 800;
    }

    .stButton > button:hover {
        background-color: #76594f;
        color: white;
    }

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# セクション見出し
# =========================================================
def render_section_header(
    title,
    icon_file=None,
    emoji="",
):

    col_icon, col_title = st.columns(
        [1, 9],
        vertical_alignment="center",
    )

    with col_icon:

        icon_path = None

        if icon_file:

            candidates = [
                ICON_DIR / icon_file,
                HOME_ICON_DIR / icon_file,
            ]

            for path in candidates:

                if path.exists():
                    icon_path = path
                    break

        if icon_path:

            st.image(
                str(icon_path),
                width=42,
            )

        elif emoji:

            st.markdown(
                f"### {emoji}"
            )

    with col_title:

        st.markdown(
            f"## {title}"
        )


# =========================================================
# トップビジュアル
# =========================================================
top_visual_path = (
    TOP_VISUAL_DIR
    / "top_visual.png"
)

if top_visual_path.exists():

    st.image(
        str(top_visual_path),
        use_container_width=True,
    )

else:

    st.title(
        "ShufuMate"
    )

    st.caption(
        "体重だけでなく、体脂肪・筋肉量・食事・体調を"
        "一緒に見ながら整えていくアプリです。"
    )


# =========================================================
# 記録取得
# =========================================================
logs = load_diet_logs(
    user_id
)

df = pd.DataFrame()


if logs:

    df = pd.DataFrame(
        logs
    )

    # -----------------------------------------------------
    # 列名整理
    # -----------------------------------------------------
    df.columns = [
        str(col).strip()
        for col in df.columns
    ]


    # -----------------------------------------------------
    # 表記揺れ対応
    # -----------------------------------------------------
    column_aliases = {

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


    for standard_name, aliases in column_aliases.items():

        if standard_name not in df.columns:

            for alias in aliases:

                if alias in df.columns:

                    df = df.rename(
                        columns={
                            alias:
                            standard_name
                        }
                    )

                    break


    # -----------------------------------------------------
    # 旧DietLogs保険
    # A=user_id
    # B=log_date
    # C=weight
    # D=body_fat
    # E=muscle_mass
    # -----------------------------------------------------
    if (
        "muscle_mass"
        not in df.columns
        and len(df.columns) >= 5
    ):

        df = df.rename(
            columns={
                df.columns[4]:
                "muscle_mass"
            }
        )


    # -----------------------------------------------------
    # 日付変換
    # -----------------------------------------------------
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


    # -----------------------------------------------------
    # 数値変換
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
# 最新有効値取得
# =========================================================
def get_latest_valid_value(
    dataframe,
    column_name,
):

    if dataframe.empty:
        return None, None

    if column_name not in dataframe.columns:
        return None, None

    temp = dataframe[
        [
            "log_date",
            column_name,
        ]
    ].copy()

    temp[column_name] = pd.to_numeric(
        temp[column_name],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=[
            column_name
        ]
    )

    temp = temp[
        temp[column_name] > 0
    ]

    if temp.empty:
        return None, None

    row = temp.iloc[-1]

    return (
        float(
            row[column_name]
        ),
        row["log_date"],
    )


latest_weight, latest_weight_date = (
    get_latest_valid_value(
        df,
        "weight",
    )
)

latest_body_fat, latest_body_fat_date = (
    get_latest_valid_value(
        df,
        "body_fat",
    )
)

latest_muscle, latest_muscle_date = (
    get_latest_valid_value(
        df,
        "muscle_mass",
    )
)


# =========================================================
# 今日の状態
# =========================================================
render_section_header(
    "今日の状態",
    icon_file="home.png",
    emoji="🌿",
)


if not df.empty:

    col1, col2, col3 = st.columns(3)

    with col1:

        if latest_weight is not None:

            st.metric(
                "体重",
                f"{latest_weight:.1f} kg",
            )

        else:

            st.metric(
                "体重",
                "—",
            )


    with col2:

        if latest_body_fat is not None:

            st.metric(
                "体脂肪",
                f"{latest_body_fat:.1f} %",
            )

        else:

            st.metric(
                "体脂肪",
                "—",
            )


    with col3:

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


    if (
        latest_muscle is not None
        and pd.notna(
            latest_muscle_date
        )
    ):

        st.caption(
            "筋肉量 最終記録："
            + latest_muscle_date.strftime(
                "%Y/%m/%d"
            )
        )

else:

    st.info(
        "まだ記録がありません。"
        "「記録する」から今日の状態を入力してみましょう。"
    )


# =========================================================
# 今日の整え方
# =========================================================
render_section_header(
    "今日の整え方",
    icon_file="advice.png",
    emoji="💡",
)


if not df.empty:

    latest_date = (
        df["log_date"]
        .max()
    )

    analysis_start = (
        latest_date
        - pd.Timedelta(
            days=29
        )
    )

    analysis_df = df[
        df["log_date"]
        >= analysis_start
    ].copy()

    comments = []

    weight_diff = None
    fat_diff = None
    muscle_diff = None


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    if "weight" in analysis_df.columns:

        data = (
            analysis_df["weight"]
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

            if weight_diff < -1:

                comments.append(
                    "体重はこの30日で減少傾向です。"
                )

            elif weight_diff > 1:

                comments.append(
                    "体重はこの30日で増加傾向です。"
                )

            else:

                comments.append(
                    "体重はこの30日、大きく変わらず安定しています。"
                )


    # -----------------------------------------------------
    # 体脂肪
    # -----------------------------------------------------
    if "body_fat" in analysis_df.columns:

        data = (
            analysis_df["body_fat"]
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

            if fat_diff < -1:

                comments.append(
                    "体脂肪率はこの30日で下がっています。"
                )

            elif fat_diff > 1:

                comments.append(
                    "体脂肪率はこの30日で少し上がっています。"
                )

            else:

                comments.append(
                    "体脂肪率はこの30日、ほぼ安定しています。"
                )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    if "muscle_mass" in analysis_df.columns:

        data = (
            analysis_df["muscle_mass"]
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

            if muscle_diff > 0.3:

                comments.append(
                    "筋肉量はこの30日で増えています。"
                )

            elif muscle_diff < -0.3:

                comments.append(
                    "筋肉量はこの30日で少し下がっています。"
                )

            else:

                comments.append(
                    "筋肉量はこの30日、安定しています。"
                )


    if comments:

        for comment in comments:

            st.write(
                "・" + comment
            )

    else:

        st.info(
            "もう少し記録が増えると、"
            "最近の変化を分析できます。"
        )


    if (
        muscle_diff is not None
        and muscle_diff > 0.3
    ):

        st.success(
            "筋肉量が増えています。"
            "食事を減らしすぎず、"
            "運動・たんぱく質・休養を"
            "続けていきましょう。"
        )

    elif (
        muscle_diff is not None
        and muscle_diff < -0.3
    ):

        st.warning(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養を"
            "確認してみましょう。"
        )

    elif (
        fat_diff is not None
        and fat_diff > 1
    ):

        st.warning(
            "体脂肪率が少し上がっています。"
            "食事を極端に減らさず、"
            "間食・夜の食事・活動量を"
            "確認してみましょう。"
        )

    else:

        st.info(
            "大きく変えすぎず、"
            "食事・運動・休養を整えながら"
            "続けていきましょう。"
        )

else:

    st.info(
        "記録を続けると、"
        "あなたの変化に合わせた"
        "コメントが表示されます。"
    )


# =========================================================
# グラフ共通関数
# =========================================================
def render_body_chart(
    dataframe,
    value_col,
    title,
    unit,
    period,
    minimum_span,
):

    if value_col not in dataframe.columns:

        st.info(
            f"{title}の記録がありません。"
        )

        return


    chart_data = dataframe[
        [
            "log_date",
            value_col,
        ]
    ].copy()


    chart_data[value_col] = pd.to_numeric(
        chart_data[value_col],
        errors="coerce",
    )


    chart_data = chart_data.dropna(
        subset=[
            "log_date",
            value_col,
        ]
    )


    chart_data = chart_data[
        chart_data[value_col] > 0
    ]


    if chart_data.empty:

        st.info(
            f"{title}の記録がありません。"
        )

        return


    # -----------------------------------------------------
    # 縦軸：個人＋期間ごとに自動
    # -----------------------------------------------------
    value_min = float(
        chart_data[value_col]
        .min()
    )

    value_max = float(
        chart_data[value_col]
        .max()
    )


    actual_span = (
        value_max
        - value_min
    )


    display_span = max(
        actual_span * 1.4,
        minimum_span,
    )


    center = (
        value_max
        + value_min
    ) / 2


    y_min = (
        center
        - display_span / 2
    )

    y_max = (
        center
        + display_span / 2
    )


    y_min = max(
        0,
        y_min,
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

        axis_format = "%m/%d"
        tick_count = 5

    elif period == "直近90日":

        axis_format = "%Y/%m"
        tick_count = 5

    else:

        axis_format = "%Y"

        year_count = (
            chart_data[
                "log_date"
            ]
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


    chart = (
        alt.Chart(
            chart_data
        )

        .mark_line(
            point=True
        )

        .encode(

            x=alt.X(
                "log_date:T",
                title="",
                axis=alt.Axis(
                    format=axis_format,
                    labelAngle=0,
                    tickCount=tick_count,
                ),
            ),

            y=alt.Y(
                f"{value_col}:Q",
                title=unit,
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
                    f"{value_col}:Q",
                    title=title,
                    format=".1f",
                ),
            ],
        )

        .properties(
            height=260
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
    icon_file="exercise.png",
    emoji="📈",
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
        key="home_chart_period",
    )


    chart_df = df.copy()


    chart_latest_date = (
        chart_df[
            "log_date"
        ]
        .max()
    )


    if period == "直近30日":

        start_date = (
            chart_latest_date
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
            chart_latest_date
            - pd.Timedelta(
                days=89
            )
        )

        chart_df = chart_df[
            chart_df["log_date"]
            >= start_date
        ]


    st.markdown("#### 体脂肪率")

    render_body_chart(
        chart_df,
        value_col="body_fat",
        title="体脂肪率",
        unit="%",
        period=period,
        minimum_span=10.0,
    )


    st.markdown("#### 筋肉量")

    render_body_chart(
        chart_df,
        value_col="muscle_mass",
        title="筋肉量",
        unit="kg",
        period=period,
        minimum_span=5.0,
    )


    st.markdown("#### 体重")

    render_body_chart(
        chart_df,
        value_col="weight",
        title="体重",
        unit="kg",
        period=period,
        minimum_span=10.0,
    )

else:

    st.info(
        "記録が増えると、"
        "ここに変化のグラフが表示されます。"
    )


# =========================================================
# 最新記録
# =========================================================
render_section_header(
    "最新記録",
    icon_file="note.png",
    emoji="📝",
)


if not df.empty:

    latest = df.iloc[-1]

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


    col1, col2, col3 = st.columns(3)


    with col1:

        if latest_weight is not None:

            st.metric(
                "体重",
                f"{latest_weight:.1f} kg",
            )

        else:

            st.metric(
                "体重",
                "—",
            )


    with col2:

        if latest_body_fat is not None:

            st.metric(
                "体脂肪",
                f"{latest_body_fat:.1f} %",
            )

        else:

            st.metric(
                "体脂肪",
                "—",
            )


    with col3:

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


    if (
        latest_muscle is not None
        and pd.notna(
            latest_muscle_date
        )
        and pd.notna(
            latest_log_date
        )
        and latest_muscle_date.date()
        != latest_log_date.date()
    ):

        st.caption(
            "※筋肉量は直近の有効記録 "
            + latest_muscle_date.strftime(
                "%Y/%m/%d"
            )
            + " の値です。"
        )


    meal_memo = latest.get(
        "meal_memo",
        ""
    )

    if (
        meal_memo
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
        "最新記録はまだありません。"
    )


# =========================================================
# メニュー
# =========================================================
render_section_header(
    "メニュー",
    icon_file="menu.png",
    emoji="📋",
)


col1, col2 = st.columns(2)


with col1:

    if st.button(
        "📝 記録する",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_記録する.py"
        )


    if st.button(
        "📷 写真で記録",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/4_写真で記録.py"
        )


with col2:

    if st.button(
        "💬 相談する",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/3_相談する.py"
        )


    if st.button(
        "⚙️ 設定",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/1_設定.py"
        )


# =========================================================
# フッター
# =========================================================
st.markdown("---")

st.caption(
    "今日の日付："
    + jst_today().strftime(
        "%Y/%m/%d"
    )
)
