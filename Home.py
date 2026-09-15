import streamlit as st
import pandas as pd
from pathlib import Path

from app_core import (
    require_login,
    get_user_id,
    get_nickname,
    load_log_chart_df,
    jst_today,
)


# =========================================================
# ページ設定
# ※ Streamlit命令の中で必ず最初
# =========================================================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
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

WATERCOLOR_ICON_DIR = (
    APP_ROOT
    / "assets"
    / "icons"
    / "ShufuMate_home_icons_8"
)

OLD_ICON_DIR = (
    APP_ROOT
    / "assets"
    / "icons"
)


# =========================================================
# CSS
# =========================================================
st.markdown(
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
    max-width: 920px;
    padding-top: 3rem !important;
    padding-bottom: 3rem;
}


/* =========================================
   タイトル
========================================= */

.app-title {
    font-size: 2.25rem;
    font-weight: 900;
    color: #5b4033;
    margin-bottom: 0.15rem;
}

.app-subtitle {
    color: #857063;
    font-size: 0.96rem;
    line-height: 1.7;
    margin-bottom: 1.5rem;
}


/* =========================================
   セクション
========================================= */

.home-section-head {
    display: flex;
    align-items: center;
    gap: 14px;

    margin-top: 30px;
    margin-bottom: 13px;
}

.home-section-icon {
    width: 58px;
    min-width: 58px;
    height: 58px;

    display: flex;
    align-items: center;
    justify-content: center;
}

.home-section-icon img {
    width: 58px;
    height: 58px;
    object-fit: contain;
}

.home-section-title {
    color: #5b4033;
    font-size: 1.40rem;
    font-weight: 900;
    line-height: 1.3;
}

.home-section-desc {
    color: #8a786c;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-top: 2px;
}


/* =========================================
   Metric
========================================= */

div[data-testid="stMetric"] {
    background: #ffffff;

    border-radius: 18px;

    padding: 15px 16px;

    border:
        1px solid
        rgba(168, 126, 88, 0.14);

    box-shadow:
        0 5px 15px
        rgba(105, 75, 52, 0.06);
}


/* =========================================
   状態メモ
========================================= */

.home-note {
    background: #fffdf8;

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

.advice-card {
    background: #f4f8ef;

    border:
        1px solid
        rgba(92, 130, 83, 0.16);

    border-radius: 20px;

    padding: 17px 18px;

    margin-top: 8px;

    color: #50644c;

    font-size: 0.93rem;

    line-height: 1.85;
}


/* =========================================
   最近の変化
========================================= */

.change-card {
    background: #ffffff;

    border:
        1px solid
        rgba(168, 126, 88, 0.14);

    border-radius: 18px;

    padding: 15px 16px;

    color: #5b4033;

    text-align: center;

    box-shadow:
        0 4px 12px
        rgba(105, 75, 52, 0.05);
}

.change-label {
    color: #8a786c;
    font-size: 0.82rem;
    margin-bottom: 5px;
}

.change-value {
    color: #5b4033;
    font-size: 1.12rem;
    font-weight: 900;
}


/* =========================================
   区切り
========================================= */

.soft-divider {
    height: 1px;
    background: #eadfce;
    margin: 2.2rem 0;
}


/* =========================================
   メニュー
========================================= */

.menu-title {
    text-align: center;

    font-size: 1.12rem;
    font-weight: 900;

    color: #5b4033;

    margin-top: 5px;
    margin-bottom: 4px;
}

.menu-desc {
    text-align: center;

    font-size: 0.82rem;

    color: #8a786c;

    min-height: 36px;

    margin-bottom: 10px;
}


/* =========================================
   ボタン
========================================= */

.stButton > button {

    border-radius: 14px;

    border: none;

    background: #8d6e63;

    color: #ffffff;

    font-weight: 800;

    min-height: 46px;

    box-shadow:
        0 3px 8px
        rgba(96, 65, 45, 0.10);
}

.stButton > button:hover {

    background: #76594f;

    color: #ffffff;

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

    .app-title {
        font-size: 1.9rem;
    }

    .home-section-icon {
        width: 50px;
        min-width: 50px;
        height: 50px;
    }

    .home-section-icon img {
        width: 50px;
        height: 50px;
    }

    .home-section-title {
        font-size: 1.20rem;
    }

    .home-section-desc {
        font-size: 0.82rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# アイコン取得
# =========================================================
def icon_path(filename):

    candidates = [
        WATERCOLOR_ICON_DIR / filename,
        OLD_ICON_DIR / filename,
    ]

    for path in candidates:

        if path.exists():
            return str(path)

    return None


# =========================================================
# セクション見出し
# =========================================================
def render_home_section(
    title,
    description,
    filename,
):

    path = icon_path(filename)

    if path:

        import base64

        suffix = path.lower()

        if suffix.endswith(".png"):
            mime = "image/png"

        elif suffix.endswith(
            (".jpg", ".jpeg")
        ):
            mime = "image/jpeg"

        else:
            mime = "image/png"

        with open(path, "rb") as f:

            encoded = (
                base64.b64encode(
                    f.read()
                ).decode("utf-8")
            )

        icon_html = (
            f'<img src="data:{mime};base64,{encoded}">'
        )

    else:

        icon_html = "🌿"

    st.markdown(
        f"""
<div class="home-section-head">

    <div class="home-section-icon">
        {icon_html}
    </div>

    <div>

        <div class="home-section-title">
            {title}
        </div>

        <div class="home-section-desc">
            {description}
        </div>

    </div>

</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# DietLogs
# app_core.py の共通処理だけを使用
# =========================================================
df = load_log_chart_df(
    user_id
)


# =========================================================
# 念のため列を数値化
# =========================================================
if not df.empty:

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

    df = df.sort_values(
        "log_date"
    )


# =========================================================
# 最新の有効値
# 空欄・0は除外
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

    row = temp.iloc[-1]

    return (
        float(row[column]),
        row["log_date"],
    )


latest_weight, weight_date = (
    latest_valid("weight")
)

latest_body_fat, fat_date = (
    latest_valid("body_fat")
)

latest_muscle, muscle_date = (
    latest_valid("muscle_mass")
)


# =========================================================
# 前回との差
# =========================================================
def latest_difference(column):

    if (
        df.empty
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

    if len(temp) < 2:
        return None

    return (
        float(temp.iloc[-1][column])
        - float(temp.iloc[-2][column])
    )


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
    '<div class="app-title">ShufuMate</div>',
    unsafe_allow_html=True,
)


if nickname:

    subtitle = (
        f"{nickname}さんの毎日の暮らしとからだを、"
        "無理なく整える"
    )

else:

    subtitle = (
        "毎日の暮らしとからだを、"
        "無理なく整える"
    )


st.markdown(
    f"""
<div class="app-subtitle">
    {subtitle}
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 今日の状態
# =========================================================
render_home_section(
    "今日の状態",
    "最新の記録から、今のからだの状態を確認します。",
    "state.png",
)


if not df.empty:

    col1, col2, col3 = st.columns(
        3
    )


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
                f"{latest_body_fat:.1f} %"
                if latest_body_fat is not None
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


    # -----------------------------------------------------
    # 最新記録日
    # -----------------------------------------------------
    available_dates = [
        d
        for d in [
            weight_date,
            fat_date,
            muscle_date,
        ]
        if d is not None
    ]


    if available_dates:

        newest_date = max(
            available_dates
        )

        st.markdown(
            f"""
<div class="home-note">
最新記録：{newest_date.strftime("%Y/%m/%d")}
</div>
""",
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
    "今日の整え方",
    "最近の記録から、今日意識したいポイントです。",
    "advice.png",
)


advice_lines = []


if muscle_diff is not None:

    if muscle_diff > 0.3:

        advice_lines.append(
            "筋肉量が増えています。"
            "今の運動と食事の流れを続けていきましょう。"
        )

    elif muscle_diff < -0.3:

        advice_lines.append(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養を意識してみましょう。"
        )


if fat_diff is not None:

    if fat_diff > 1:

        advice_lines.append(
            "体脂肪率が少し上がっています。"
            "食事を減らしすぎず、間食や活動量を確認してみましょう。"
        )

    elif fat_diff < -1:

        advice_lines.append(
            "体脂肪率は下がっています。"
            "筋肉量を守りながら今のペースを続けましょう。"
        )


if not advice_lines:

    advice_lines.append(
        "大きく変えすぎず、"
        "食事・運動・休養を整えながら"
        "今のペースを続けていきましょう。"
    )


advice_html = "<br><br>".join(
    advice_lines
)


st.markdown(
    f"""
<div class="advice-card">
    {advice_html}
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 最近の変化
#
# Homeでは詳細グラフを置かない。
# 詳細グラフは「記録する」に一本化。
# =========================================================
render_home_section(
    "最近の変化",
    "前回の記録との変化をかんたんに確認できます。",
    "trend.png",
)


def format_diff(
    value,
    unit,
):

    if value is None:
        return "—"

    if abs(value) < 0.05:
        return "±0.0 " + unit

    sign = (
        "+"
        if value > 0
        else ""
    )

    return (
        f"{sign}{value:.1f} {unit}"
    )


c1, c2, c3 = st.columns(
    3
)


with c1:

    st.markdown(
        f"""
<div class="change-card">

    <div class="change-label">
        体重
    </div>

    <div class="change-value">
        {format_diff(weight_diff, "kg")}
    </div>

</div>
""",
        unsafe_allow_html=True,
    )


with c2:

    st.markdown(
        f"""
<div class="change-card">

    <div class="change-label">
        体脂肪率
    </div>

    <div class="change-value">
        {format_diff(fat_diff, "%")}
    </div>

</div>
""",
        unsafe_allow_html=True,
    )


with c3:

    st.markdown(
        f"""
<div class="change-card">

    <div class="change-label">
        筋肉量
    </div>

    <div class="change-value">
        {format_diff(muscle_diff, "kg")}
    </div>

</div>
""",
        unsafe_allow_html=True,
    )


st.caption(
    "※前回の有効な記録との比較です。"
)


# =========================================================
# メニュー
# =========================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)


render_home_section(
    "メニュー",
    "使いたい機能を選んでください。",
    "latest.png",
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


    if path:

        left, center, right = st.columns(
            [
                1.25,
                1.1,
                1.25,
            ]
        )


        with center:

            st.image(
                path,
                use_container_width=True,
            )


    st.markdown(
        f"""
<div class="menu-title">
    {title}
</div>

<div class="menu-desc">
    {description}
</div>
""",
        unsafe_allow_html=True,
    )


    if st.button(
        "開く",
        key=button_key,
        use_container_width=True,
    ):

        st.switch_page(
            page
        )


# =========================================================
# メニュー 1段目
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
        button_key="home_menu_record",
        page="pages/2_記録する.py",
    )


with col2:

    menu_card(
        image_file="chat.png",
        title="相談する",
        description="気になることを相談",
        button_key="home_menu_chat",
        page="pages/3_相談する.py",
    )


# =========================================================
# メニュー 2段目
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
        button_key="home_menu_camera",
        page="pages/4_写真で記録.py",
    )


with col4:

    menu_card(
        image_file="settings.png",
        title="設定",
        description="プロフィールや目標を設定",
        button_key="home_menu_settings",
        page="pages/1_設定.py",
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
