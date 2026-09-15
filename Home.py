import streamlit as st
import pandas as pd
from pathlib import Path
import base64
import textwrap
import html

from app_core import (
    require_login,
    get_user_id,
    get_nickname,
    load_diet_logs,
    jst_today,
)


# =========================================================
# ページ設定
# ※ 最初のStreamlit命令
# =========================================================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🌿",
    layout="centered",
)


# =========================================================
# ログイン
# =========================================================
require_login()

user_id = get_user_id()
nickname = get_nickname()


# =========================================================
# パス
# =========================================================
APP_ROOT = Path(__file__).resolve().parent

ICON_ROOT = (
    APP_ROOT
    / "assets"
    / "icons"
)

WATERCOLOR_ICON_DIR = (
    ICON_ROOT
    / "ShufuMate_home_icons_8"
)


# =========================================================
# CSS
# =========================================================
st.markdown(
    textwrap.dedent(
        """
        <style>

        /* =========================================
           全体
        ========================================= */

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    #fffaf4 0%,
                    #fff4e8 48%,
                    #fffaf4 100%
                );
        }

        .block-container {
            max-width: 900px;
            padding-top: 3rem !important;
            padding-bottom: 3rem;
        }


        /* =========================================
           タイトル
        ========================================= */

        .sm-home-title {
            color: #5b4033;
            font-size: 2.30rem;
            font-weight: 900;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }

        .sm-home-subtitle {
            color: #857063;
            font-size: 0.96rem;
            line-height: 1.75;
            margin-bottom: 1.4rem;
        }


        /* =========================================
           セクション見出し
        ========================================= */

        .sm-home-section {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-top: 30px;
            margin-bottom: 14px;
        }

        .sm-home-section-icon {
            width: 58px;
            min-width: 58px;
            height: 58px;

            display: flex;
            align-items: center;
            justify-content: center;
        }

        .sm-home-section-icon img {
            width: 58px;
            height: 58px;
            object-fit: contain;
        }

        .sm-home-section-emoji {
            font-size: 2rem;
            line-height: 1;
        }

        .sm-home-section-title {
            color: #5b4033;
            font-size: 1.38rem;
            font-weight: 900;
            line-height: 1.3;
        }

        .sm-home-section-desc {
            color: #8a786c;
            font-size: 0.86rem;
            line-height: 1.6;
            margin-top: 3px;
        }


        /* =========================================
           Metric
        ========================================= */

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.90);

            border:
                1px solid
                rgba(168, 126, 88, 0.14);

            border-radius: 18px;

            padding: 15px;

            box-shadow:
                0 5px 15px
                rgba(105, 75, 52, 0.05);
        }

        div[data-testid="stMetricLabel"] {
            color: #806c60;
        }

        div[data-testid="stMetricValue"] {
            color: #5b4033;
        }


        /* =========================================
           最新記録
        ========================================= */

        .sm-home-note {
            background: rgba(255, 253, 248, 0.92);

            border:
                1px solid
                rgba(139, 100, 72, 0.14);

            border-radius: 18px;

            padding: 14px 17px;

            margin-top: 12px;

            color: #755544;

            font-size: 0.90rem;

            line-height: 1.75;
        }


        /* =========================================
           今日の整え方
        ========================================= */

        .sm-home-advice {
            background: #f4f8ef;

            border:
                1px solid
                rgba(92, 130, 83, 0.17);

            border-radius: 20px;

            padding: 18px 19px;

            color: #50644c;

            font-size: 0.94rem;

            line-height: 1.85;

            box-shadow:
                0 4px 12px
                rgba(82, 112, 74, 0.04);
        }


        /* =========================================
           最近の変化
        ========================================= */

        .sm-change-card {
            background: rgba(255, 255, 255, 0.92);

            border:
                1px solid
                rgba(168, 126, 88, 0.14);

            border-radius: 18px;

            padding: 15px 8px;

            min-height: 96px;

            display: flex;
            flex-direction: column;
            justify-content: center;

            text-align: center;

            box-shadow:
                0 4px 12px
                rgba(105, 75, 52, 0.05);
        }

        .sm-change-label {
            color: #8a786c;
            font-size: 0.80rem;
            margin-bottom: 6px;
        }

        .sm-change-value {
            color: #5b4033;
            font-size: 1.15rem;
            font-weight: 900;
        }

        .sm-change-sub {
            color: #a08d81;
            font-size: 0.72rem;
            margin-top: 4px;
        }


        /* =========================================
           区切り
        ========================================= */

        .sm-home-divider {
            height: 1px;
            background: #eadfce;
            margin: 2.2rem 0 1.7rem 0;
        }


        /* =========================================
           メニュー
        ========================================= */

        .sm-menu-title {
            text-align: center;
            color: #5b4033;
            font-size: 1.10rem;
            font-weight: 900;
            margin-top: 5px;
            margin-bottom: 3px;
        }

        .sm-menu-desc {
            text-align: center;
            color: #8a786c;
            font-size: 0.80rem;
            min-height: 34px;
            line-height: 1.5;
            margin-bottom: 9px;
        }


        /* =========================================
           ボタン
        ========================================= */

        .stButton > button {
            border-radius: 14px;
            border: none;
            background: #8d6e63;
            color: white;
            font-weight: 800;
            min-height: 45px;

            box-shadow:
                0 3px 8px
                rgba(96, 65, 45, 0.10);
        }

        .stButton > button:hover {
            background: #76594f;
            color: white;
            border: none;
        }


        /* =========================================
           スマホ
        ========================================= */

        @media (max-width: 640px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.4rem !important;
            }

            .sm-home-title {
                font-size: 1.90rem;
            }

            .sm-home-section {
                gap: 10px;
                margin-top: 24px;
            }

            .sm-home-section-icon {
                width: 50px;
                min-width: 50px;
                height: 50px;
            }

            .sm-home-section-icon img {
                width: 50px;
                height: 50px;
            }

            .sm-home-section-title {
                font-size: 1.18rem;
            }

            .sm-home-section-desc {
                font-size: 0.80rem;
            }

            .sm-change-card {
                min-height: 88px;
                padding: 12px 5px;
            }

            .sm-change-value {
                font-size: 0.98rem;
            }
        }

        </style>
        """
    ).strip(),
    unsafe_allow_html=True,
)


# =========================================================
# 安全文字
# =========================================================
def safe_text(value):

    if value is None:
        return ""

    return html.escape(
        str(value)
    )


# =========================================================
# アイコンパス
# =========================================================
def icon_path(filename):

    candidates = [
        WATERCOLOR_ICON_DIR / filename,
        ICON_ROOT / filename,
    ]

    for path in candidates:

        if path.exists():
            return path

    return None


# =========================================================
# アイコンHTML
# =========================================================
def make_icon_html(
    filename,
    fallback="🌿",
):

    path = icon_path(
        filename
    )

    if path is None:

        return (
            '<div class="sm-home-section-emoji">'
            f'{safe_text(fallback)}'
            '</div>'
        )

    suffix = path.suffix.lower()

    if suffix == ".png":
        mime = "image/png"

    elif suffix in [
        ".jpg",
        ".jpeg",
    ]:
        mime = "image/jpeg"

    elif suffix == ".webp":
        mime = "image/webp"

    else:
        mime = "image/png"

    try:

        with open(
            path,
            "rb",
        ) as f:

            encoded = (
                base64.b64encode(
                    f.read()
                )
                .decode(
                    "utf-8"
                )
            )

        return (
            f'<img '
            f'src="data:{mime};base64,{encoded}" '
            f'alt="">'
        )

    except Exception:

        return (
            '<div class="sm-home-section-emoji">'
            f'{safe_text(fallback)}'
            '</div>'
        )


# =========================================================
# セクション見出し
# =========================================================
def render_home_section(
    title,
    description,
    filename,
    fallback="🌿",
):

    image_html = make_icon_html(
        filename,
        fallback,
    )

    section_html = f"""
    <div class="sm-home-section">
        <div class="sm-home-section-icon">
            {image_html}
        </div>
        <div>
            <div class="sm-home-section-title">
                {safe_text(title)}
            </div>
            <div class="sm-home-section-desc">
                {safe_text(description)}
            </div>
        </div>
    </div>
    """

    st.markdown(
        textwrap.dedent(
            section_html
        ).strip(),
        unsafe_allow_html=True,
    )


# =========================================================
# DietLogs取得
# =========================================================
try:

    logs = load_diet_logs(
        user_id
    )

    df = pd.DataFrame(
        logs
    )

except Exception as e:

    st.error(
        "記録データの読み込み中にエラーが発生しました。"
    )

    st.caption(
        str(e)
    )

    df = pd.DataFrame()


# =========================================================
# DietLogs列名を整理
# =========================================================
if not df.empty:

    # -----------------------------------------------------
    # 列名の前後空白を削除
    # -----------------------------------------------------
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]


    # -----------------------------------------------------
    # 日本語・旧列名があれば標準名へ
    # -----------------------------------------------------
    rename_map = {}

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
        )

        if normalized in [
            "userid",
            "ユーザーid",
        ]:
            rename_map[column] = "user_id"

        elif normalized in [
            "logdate",
            "date",
            "日付",
        ]:
            rename_map[column] = "log_date"

        elif normalized in [
            "weight",
            "体重",
            "体重(kg)",
            "体重（kg）",
        ]:
            rename_map[column] = "weight"

        elif normalized in [
            "bodyfat",
            "体脂肪",
            "体脂肪率",
            "体脂肪率(%)",
            "体脂肪率（%）",
        ]:
            rename_map[column] = "body_fat"

        elif normalized in [
            "musclemass",
            "muscle",
            "筋肉量",
            "筋肉量(kg)",
            "筋肉量（kg）",
        ]:
            rename_map[column] = "muscle_mass"

        elif normalized in [
            "mealmemo",
            "memo",
            "食事メモ",
        ]:
            rename_map[column] = "meal_memo"


    if rename_map:

        df = df.rename(
            columns=rename_map
        )


    # =====================================================
    # 旧DietLogs対策
    #
    # A = user_id
    # B = log_date
    # C = weight
    # D = body_fat
    # E = muscle_mass
    # F = meal_memo
    #
    # 現在のGoogle Sheetsの構造にも対応
    # =====================================================

    current_columns = list(
        df.columns
    )


    if (
        "user_id" not in df.columns
        and len(current_columns) >= 1
    ):

        df = df.rename(
            columns={
                current_columns[0]:
                "user_id"
            }
        )


    current_columns = list(
        df.columns
    )

    if (
        "log_date" not in df.columns
        and len(current_columns) >= 2
    ):

        df = df.rename(
            columns={
                current_columns[1]:
                "log_date"
            }
        )


    current_columns = list(
        df.columns
    )

    if (
        "weight" not in df.columns
        and len(current_columns) >= 3
    ):

        df = df.rename(
            columns={
                current_columns[2]:
                "weight"
            }
        )


    current_columns = list(
        df.columns
    )

    if (
        "body_fat" not in df.columns
        and len(current_columns) >= 4
    ):

        df = df.rename(
            columns={
                current_columns[3]:
                "body_fat"
            }
        )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    current_columns = list(
        df.columns
    )

    if (
        "muscle_mass" not in df.columns
        and len(current_columns) >= 5
    ):

        df = df.rename(
            columns={
                current_columns[4]:
                "muscle_mass"
            }
        )


    # -----------------------------------------------------
    # 食事メモ
    # -----------------------------------------------------
    current_columns = list(
        df.columns
    )

    if (
        "meal_memo" not in df.columns
        and len(current_columns) >= 6
    ):

        df = df.rename(
            columns={
                current_columns[5]:
                "meal_memo"
            }
        )


# =========================================================
# 日付・数値を変換
# =========================================================
if not df.empty:

    # -----------------------------------------------------
    # 日付
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
    # 日付順
    # -----------------------------------------------------
    if "log_date" in df.columns:

        df = (
            df
            .sort_values(
                "log_date"
            )
            .reset_index(
                drop=True
            )
        )


# =========================================================
# 最新の有効値
# =========================================================
def latest_valid(
    column
):

    if (
        df.empty
        or "log_date" not in df.columns
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
        subset=[
            "log_date",
            column,
        ]
    )


    # -----------------------------------------------------
    # 0は未入力として除外
    # -----------------------------------------------------
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
        float(
            row[column]
        ),
        row["log_date"],
    )


# =========================================================
# 前回との差
# =========================================================
def latest_difference(
    column
):

    if (
        df.empty
        or "log_date" not in df.columns
        or column not in df.columns
    ):

        return None


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
        subset=[
            "log_date",
            column,
        ]
    )


    temp = temp[
        temp[column] > 0
    ]


    temp = temp.sort_values(
        "log_date"
    )


    if len(temp) < 2:

        return None


    latest_value = float(
        temp.iloc[-1][column]
    )

    previous_value = float(
        temp.iloc[-2][column]
    )


    return (
        latest_value
        - previous_value
    )


# =========================================================
# 最新値
# =========================================================
latest_weight, weight_date = (
    latest_valid(
        "weight"
    )
)

latest_body_fat, fat_date = (
    latest_valid(
        "body_fat"
    )
)

latest_muscle, muscle_date = (
    latest_valid(
        "muscle_mass"
    )
)


# =========================================================
# 前回比
# =========================================================
weight_diff = latest_difference(
    "weight"
)

fat_diff = latest_difference(
    "body_fat"
)

muscle_diff = latest_difference(
    "muscle_mass"
)


# =========================================================
# タイトル
# =========================================================
st.markdown(
    '<div class="sm-home-title">'
    'ShufuMate'
    '</div>',
    unsafe_allow_html=True,
)


if nickname:

    subtitle = (
        f"{safe_text(nickname)}さんの毎日の暮らしとからだを、"
        "無理なく整える"
    )

else:

    subtitle = (
        "毎日の暮らしとからだを、"
        "無理なく整える"
    )


subtitle_html = f"""
<div class="sm-home-subtitle">
{subtitle}
</div>
"""


st.markdown(
    textwrap.dedent(
        subtitle_html
    ).strip(),
    unsafe_allow_html=True,
)


# =========================================================
# 今日の状態
# =========================================================
render_home_section(
    title="今日の状態",
    description=(
        "最新の記録から、"
        "今のからだの状態を確認します。"
    ),
    filename="state.png",
    fallback="🌿",
)


# =========================================================
# 最新値表示
# =========================================================
if not df.empty:

    metric_col1, metric_col2, metric_col3 = (
        st.columns(
            3
        )
    )


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    with metric_col1:

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


    # -----------------------------------------------------
    # 体脂肪率
    # -----------------------------------------------------
    with metric_col2:

        if latest_body_fat is not None:

            st.metric(
                "体脂肪率",
                f"{latest_body_fat:.1f} %",
            )

        else:

            st.metric(
                "体脂肪率",
                "—",
            )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    with metric_col3:

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


    # -----------------------------------------------------
    # 最新記録日
    # -----------------------------------------------------
    available_dates = [
        value
        for value in [
            weight_date,
            fat_date,
            muscle_date,
        ]
        if value is not None
    ]


    if available_dates:

        newest_date = max(
            available_dates
        )


        date_html = f"""
        <div class="sm-home-note">
        最新記録：{newest_date.strftime("%Y/%m/%d")}
        </div>
        """


        st.markdown(
            textwrap.dedent(
                date_html
            ).strip(),
            unsafe_allow_html=True,
        )


else:

    st.info(
        "まだ記録がありません。"
        "「記録する」から入力してみましょう。"
    )


# =========================================================
# 今日の整え方
# =========================================================
render_home_section(
    title="今日の整え方",
    description=(
        "最近の記録から、"
        "今日意識したいポイントです。"
    ),
    filename="advice.png",
    fallback="💡",
)


# =========================================================
# アドバイス
# =========================================================
advice_lines = []


# ---------------------------------------------------------
# 筋肉量
# ---------------------------------------------------------
if muscle_diff is not None:

    if muscle_diff > 0.3:

        advice_lines.append(
            "筋肉量が増えています。"
            "今の運動と食事の流れを"
            "続けていきましょう。"
        )

    elif muscle_diff < -0.3:

        advice_lines.append(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養を"
            "意識してみましょう。"
        )


# ---------------------------------------------------------
# 体脂肪率
# ---------------------------------------------------------
if fat_diff is not None:

    if fat_diff > 1.0:

        advice_lines.append(
            "体脂肪率が少し上がっています。"
            "食事を極端に減らさず、"
            "間食や活動量を確認してみましょう。"
        )

    elif fat_diff < -1.0:

        advice_lines.append(
            "体脂肪率は下がっています。"
            "筋肉量を守りながら"
            "今のペースを続けましょう。"
        )


# ---------------------------------------------------------
# 大きな変化なし
# ---------------------------------------------------------
if not advice_lines:

    advice_lines.append(
        "大きく変えすぎず、"
        "食事・運動・休養を整えながら"
        "今のペースを続けていきましょう。"
    )


advice_text = "<br><br>".join(
    safe_text(line)
    for line in advice_lines
)


advice_html = f"""
<div class="sm-home-advice">
{advice_text}
</div>
"""


st.markdown(
    textwrap.dedent(
        advice_html
    ).strip(),
    unsafe_allow_html=True,
)


# =========================================================
# 最近の変化
# =========================================================
render_home_section(
    title="最近の変化",
    description=(
        "前回の有効な記録との変化を"
        "かんたんに確認できます。"
    ),
    filename="trend.png",
    fallback="📈",
)


# =========================================================
# 前回比表示
# =========================================================
def format_diff(
    value,
    unit,
):

    if value is None:

        return "—"


    if abs(value) < 0.05:

        return (
            f"±0.0 {unit}"
        )


    sign = (
        "+"
        if value > 0
        else ""
    )


    return (
        f"{sign}{value:.1f} {unit}"
    )


# =========================================================
# 変化カード
# =========================================================
def render_change_card(
    label,
    value,
):

    card_html = f"""
    <div class="sm-change-card">
        <div class="sm-change-label">
            {safe_text(label)}
        </div>
        <div class="sm-change-value">
            {safe_text(value)}
        </div>
        <div class="sm-change-sub">
            前回比
        </div>
    </div>
    """


    st.markdown(
        textwrap.dedent(
            card_html
        ).strip(),
        unsafe_allow_html=True,
    )


change_col1, change_col2, change_col3 = (
    st.columns(
        3
    )
)


with change_col1:

    render_change_card(
        "体重",
        format_diff(
            weight_diff,
            "kg",
        ),
    )


with change_col2:

    render_change_card(
        "体脂肪率",
        format_diff(
            fat_diff,
            "%",
        ),
    )


with change_col3:

    render_change_card(
        "筋肉量",
        format_diff(
            muscle_diff,
            "kg",
        ),
    )


st.caption(
    "※ 前回の有効な記録との比較です。"
)


# =========================================================
# 区切り
# =========================================================
st.markdown(
    '<div class="sm-home-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# メニュー
# =========================================================
render_home_section(
    title="メニュー",
    description=(
        "使いたい機能を選んでください。"
    ),
    filename="latest.png",
    fallback="📋",
)


# =========================================================
# メニューカード
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


    # -----------------------------------------------------
    # アイコン
    # -----------------------------------------------------
    if path is not None:

        left, center, right = (
            st.columns(
                [
                    1.2,
                    1.0,
                    1.2,
                ]
            )
        )

        with center:

            st.image(
                str(path),
                use_container_width=True,
            )


    # -----------------------------------------------------
    # タイトル・説明
    # -----------------------------------------------------
    menu_html = f"""
    <div class="sm-menu-title">
        {safe_text(title)}
    </div>
    <div class="sm-menu-desc">
        {safe_text(description)}
    </div>
    """


    st.markdown(
        textwrap.dedent(
            menu_html
        ).strip(),
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # ボタン
    # -----------------------------------------------------
    if st.button(
        "開く",
        key=button_key,
        use_container_width=True,
    ):

        st.switch_page(
            page
        )


# =========================================================
# メニュー1段目
# =========================================================
menu_col1, menu_col2 = (
    st.columns(
        2,
        gap="large",
    )
)


with menu_col1:

    menu_card(
        image_file="record.png",
        title="記録する",
        description=(
            "体重・食事・体調を記録"
        ),
        button_key="home_menu_record",
        page="pages/2_記録する.py",
    )


with menu_col2:

    menu_card(
        image_file="chat.png",
        title="相談する",
        description=(
            "気になることを相談"
        ),
        button_key="home_menu_chat",
        page="pages/3_相談する.py",
    )


# =========================================================
# メニュー2段目
# =========================================================
menu_col3, menu_col4 = (
    st.columns(
        2,
        gap="large",
    )
)


with menu_col3:

    menu_card(
        image_file="camera.png",
        title="写真で記録",
        description=(
            "写真からかんたん記録"
        ),
        button_key="home_menu_camera",
        page="pages/4_写真で記録.py",
    )


with menu_col4:

    menu_card(
        image_file="settings.png",
        title="設定",
        description=(
            "プロフィールや目標を設定"
        ),
        button_key="home_menu_settings",
        page="pages/1_設定.py",
    )


# =========================================================
# フッター
# =========================================================
st.markdown(
    '<div class="sm-home-divider"></div>',
    unsafe_allow_html=True,
)


st.caption(
    "今日の日付："
    + jst_today().strftime(
        "%Y/%m/%d"
    )
)
