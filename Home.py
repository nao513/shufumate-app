import streamlit as st
import pandas as pd

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


# =========================================================
# ログイン確認
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# タイトル
# =========================================================
st.title("🏠 ShufuMate")

st.caption(
    "体重だけでなく、体脂肪・筋肉量・食事・体調を"
    "一緒に見ながら整えていくアプリです。"
)


# =========================================================
# 記録取得
# =========================================================
logs = load_diet_logs(user_id)

df = pd.DataFrame()

if logs:

    df = pd.DataFrame(logs)
# =========================================================
# DietLogs 列名の統一
# =========================================================
df.columns = [
    str(col).strip()
    for col in df.columns
]

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
                        alias: standard_name
                    }
                )

                break


# E列に筋肉量が入っている旧データへの対応
# A=user_id
# B=log_date
# C=weight
# D=body_fat
# E=muscle_mass
if (
    "muscle_mass" not in df.columns
    and len(df.columns) >= 5
):
    old_muscle_column = df.columns[4]

    df = df.rename(
        columns={
            old_muscle_column: "muscle_mass"
        }
    )

    # -------------------------
    # 日付
    # -------------------------
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

    # -------------------------
    # 数値変換
    # -------------------------
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
# 最新の有効値を取得する関数
# =========================================================
def get_latest_valid_value(
    dataframe,
    column_name,
    positive_only=False,
):

    if dataframe.empty:
        return None, None

    if column_name not in dataframe.columns:
        return None, None

    temp_df = dataframe[
        [
            "log_date",
            column_name,
        ]
    ].copy()

    temp_df[column_name] = pd.to_numeric(
        temp_df[column_name],
        errors="coerce",
    )

    temp_df = temp_df.dropna(
        subset=[
            column_name
        ]
    )

    if positive_only:

        temp_df = temp_df[
            temp_df[column_name] > 0
        ]

    if temp_df.empty:
        return None, None

    row = temp_df.iloc[-1]

    return (
        row[column_name],
        row["log_date"],
    )


# =========================================================
# 最新値
# =========================================================
latest_weight, latest_weight_date = (
    get_latest_valid_value(
        df,
        "weight",
        positive_only=True,
    )
)

latest_body_fat, latest_body_fat_date = (
    get_latest_valid_value(
        df,
        "body_fat",
        positive_only=True,
    )
)

latest_muscle, latest_muscle_date = (
    get_latest_valid_value(
        df,
        "muscle_mass",
        positive_only=True,
    )
)


# =========================================================
# 今日の状態
# =========================================================
st.markdown("## 🌿 今日の状態")

if not df.empty:

    col1, col2, col3 = st.columns(3)

    # -------------------------
    # 体重
    # -------------------------
    with col1:

        if latest_weight is not None:

            st.metric(
                "体重",
                f"{latest_weight:.1f} kg"
            )

        else:

            st.metric(
                "体重",
                "—"
            )

    # -------------------------
    # 体脂肪
    # -------------------------
    with col2:

        if latest_body_fat is not None:

            st.metric(
                "体脂肪",
                f"{latest_body_fat:.1f} %"
            )

        else:

            st.metric(
                "体脂肪",
                "—"
            )

    # -------------------------
    # 筋肉量
    # -------------------------
    with col3:

        if latest_muscle is not None:

            st.metric(
                "筋肉量",
                f"{latest_muscle:.1f} kg"
            )

            if pd.notna(
                latest_muscle_date
            ):

                st.caption(
                    "最終記録："
                    + latest_muscle_date.strftime(
                        "%Y/%m/%d"
                    )
                )

        else:

            st.metric(
                "筋肉量",
                "—"
            )

else:

    st.info(
        "まだ記録がありません。"
        "「記録する」から今日の状態を入力してみましょう。"
    )


# =========================================================
# 今日の整え方
# =========================================================
st.markdown("## 💡 今日の整え方")

if not df.empty:

    comments = []

    latest_date = df[
        "log_date"
    ].max()

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


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    weight_data = pd.Series(
        dtype=float
    )

    if "weight" in analysis_df.columns:

        weight_data = (
            analysis_df["weight"]
            .dropna()
        )

        weight_data = weight_data[
            weight_data > 0
        ]

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
                "体重はこの30日、大きく変わらず安定しています。"
            )


    # -----------------------------------------------------
    # 体脂肪
    # -----------------------------------------------------
    fat_data = pd.Series(
        dtype=float
    )

    if "body_fat" in analysis_df.columns:

        fat_data = (
            analysis_df["body_fat"]
            .dropna()
        )

        fat_data = fat_data[
            fat_data > 0
        ]

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
                "体脂肪率はこの30日、ほぼ安定しています。"
            )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    muscle_data = pd.Series(
        dtype=float
    )

    if "muscle_mass" in analysis_df.columns:

        muscle_data = (
            analysis_df["muscle_mass"]
            .dropna()
        )

        muscle_data = muscle_data[
            muscle_data > 0
        ]

    muscle_diff = None

    if len(muscle_data) >= 2:

        muscle_diff = (
            muscle_data.iloc[-1]
            - muscle_data.iloc[0]
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


    # -----------------------------------------------------
    # コメント表示
    # -----------------------------------------------------
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


    # -----------------------------------------------------
    # ワンポイント
    # -----------------------------------------------------
    if (
        muscle_diff is not None
        and muscle_diff > 0.3
    ):

        st.success(
            "筋肉量が増えています。"
            "食事を減らしすぎず、"
            "今の運動とたんぱく質を"
            "続けていきましょう。"
        )

    elif (
        muscle_diff is not None
        and muscle_diff < -0.3
    ):

        st.warning(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養の"
            "バランスを確認してみましょう。"
        )

    elif (
        fat_diff is not None
        and fat_diff > 1.0
    ):

        st.warning(
            "体脂肪率が少し上がっています。"
            "食事を極端に減らすのではなく、"
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
        "コメントがここに表示されます。"
    )


# =========================================================
# 最近の変化
# =========================================================
st.markdown("## 📈 最近の変化")

if not df.empty:

    # -------------------------
    # 表示期間
    # -------------------------
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

    chart_latest_date = chart_df[
        "log_date"
    ].max()

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


    # =====================================================
    # 体脂肪率
    # =====================================================
    st.markdown("### 📉 体脂肪率")

    if "body_fat" in chart_df.columns:

        fat_df = (
            chart_df[
                [
                    "log_date",
                    "body_fat",
                ]
            ]
            .dropna()
        )

        fat_df = fat_df[
            fat_df["body_fat"] > 0
        ]

        if not fat_df.empty:

            fat_df = (
                fat_df
                .set_index(
                    "log_date"
                )
                .rename(
                    columns={
                        "body_fat":
                        "体脂肪率（%）"
                    }
                )
            )

            st.line_chart(
                fat_df,
                use_container_width=True,
            )

        else:

            st.info(
                "体脂肪率の記録がありません。"
            )

    else:

        st.info(
            "体脂肪率の記録がありません。"
        )


    # =====================================================
    # 筋肉量
    # =====================================================
    st.markdown("### 💪 筋肉量")

    if "muscle_mass" in chart_df.columns:

        muscle_df = (
            chart_df[
                [
                    "log_date",
                    "muscle_mass",
                ]
            ]
            .dropna()
        )

        muscle_df = muscle_df[
            muscle_df["muscle_mass"] > 0
        ]

        if not muscle_df.empty:

            muscle_df = (
                muscle_df
                .set_index(
                    "log_date"
                )
                .rename(
                    columns={
                        "muscle_mass":
                        "筋肉量（kg）"
                    }
                )
            )

            st.line_chart(
                muscle_df,
                use_container_width=True,
            )

        else:

            st.info(
                "筋肉量の記録がありません。"
            )

    else:

        st.info(
            "筋肉量の記録がありません。"
        )


    # =====================================================
    # 体重
    # =====================================================
    st.markdown("### ⚖️ 体重")

    if "weight" in chart_df.columns:

        weight_df = (
            chart_df[
                [
                    "log_date",
                    "weight",
                ]
            ]
            .dropna()
        )

        weight_df = weight_df[
            weight_df["weight"] > 0
        ]

        if not weight_df.empty:

            weight_df = (
                weight_df
                .set_index(
                    "log_date"
                )
                .rename(
                    columns={
                        "weight":
                        "体重（kg）"
                    }
                )
            )

            st.line_chart(
                weight_df,
                use_container_width=True,
            )

        else:

            st.info(
                "体重の記録がありません。"
            )

    else:

        st.info(
            "体重の記録がありません。"
        )

else:

    st.info(
        "記録が増えると、"
        "ここに変化のグラフが表示されます。"
    )


# =========================================================
# 最新記録
# =========================================================
st.markdown("## 📝 最新記録")

if not df.empty:

    latest = df.iloc[-1]

    log_date = latest.get(
        "log_date"
    )

    if pd.notna(
        log_date
    ):

        st.write(
            f"**記録日："
            f"{log_date.strftime('%Y/%m/%d')}**"
        )

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    with col1:

        if latest_weight is not None:

            st.metric(
                "体重",
                f"{latest_weight:.1f} kg"
            )

        else:

            st.metric(
                "体重",
                "—"
            )


    # -----------------------------------------------------
    # 体脂肪
    # -----------------------------------------------------
    with col2:

        if latest_body_fat is not None:

            st.metric(
                "体脂肪",
                f"{latest_body_fat:.1f} %"
            )

        else:

            st.metric(
                "体脂肪",
                "—"
            )


    # -----------------------------------------------------
    # 筋肉量
    # -----------------------------------------------------
    with col3:

        if latest_muscle is not None:

            st.metric(
                "筋肉量",
                f"{latest_muscle:.1f} kg"
            )

        else:

            st.metric(
                "筋肉量",
                "—"
            )


    # -----------------------------------------------------
    # 筋肉量の記録日
    # -----------------------------------------------------
    if (
        latest_muscle is not None
        and pd.notna(
            latest_muscle_date
        )
        and pd.notna(
            log_date
        )
        and latest_muscle_date.date()
        != log_date.date()
    ):

        st.caption(
            "※筋肉量は直近の有効記録 "
            + latest_muscle_date.strftime(
                "%Y/%m/%d"
            )
            + " の値です。"
        )


    # -----------------------------------------------------
    # 食事メモ
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
            "### 🍽️ 食事・メモ"
        )

        st.text(
            str(meal_memo)
        )

else:

    st.info(
        "最新記録はまだありません。"
    )


# =========================================================
# クイックメニュー
# =========================================================
st.markdown("---")
st.markdown("## 📋 メニュー")

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
