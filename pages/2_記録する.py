import streamlit as st
import pandas as pd

from app_core import (
    require_login,
    get_user_id,
    save_diet_log,
    load_diet_logs,
    jst_today_str,
)


# =========================================================
# ページ設定
# ※ 必ず最初のStreamlit命令にする
# =========================================================
st.set_page_config(
    page_title="記録する｜ShufuMate",
    page_icon="📝",
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
st.title("📝 記録する")

st.caption(
    "体重・体脂肪・筋肉量・食事を記録して、"
    "からだの変化を確認できます。"
)


# =========================================================
# 今日の記録
# =========================================================
st.markdown("## 🌿 今日の記録")

today = jst_today_str()


with st.form("daily_log_form"):

    st.caption(f"記録日：{today}")

    # -----------------------------------------------------
    # からだ
    # -----------------------------------------------------
    st.markdown("### ⚖️ からだ")

    col1, col2 = st.columns(2)

    with col1:
        weight = st.number_input(
            "体重（kg）",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=0.1,
            format="%.1f",
        )

    with col2:
        body_fat = st.number_input(
            "体脂肪率（%）",
            min_value=0.0,
            max_value=60.0,
            value=20.0,
            step=0.1,
            format="%.1f",
        )

    muscle_mass = st.number_input(
        "筋肉量（kg）",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        format="%.1f",
        help="測っていない日は0のままでOKです。0は未入力として保存します。",
    )

    st.markdown("---")

    # -----------------------------------------------------
    # 食事
    # -----------------------------------------------------
    st.markdown("### 🍽️ 食事")

    breakfast = st.text_area(
        "朝",
        placeholder="例：白湯、豆乳、アサイー、キウイ",
        height=80,
    )

    lunch = st.text_area(
        "昼",
        placeholder="例：鮭枝豆おにぎり、鶏むね肉、卵、味噌汁",
        height=80,
    )

    dinner = st.text_area(
        "夜",
        placeholder="例：豚しゃぶ、豆腐、野菜、ご飯",
        height=80,
    )

    snack = st.text_area(
        "間食",
        placeholder="例：ヨーグルト、バナナ",
        height=70,
    )

    # -----------------------------------------------------
    # メモ
    # -----------------------------------------------------
    st.markdown("### ✏️ 今日のメモ")

    memo = st.text_area(
        "運動・体調など",
        placeholder=(
            "例：筋トレ＋ラン20分。"
            "脚は軽い。睡眠7時間。"
        ),
        height=100,
    )

    submitted = st.form_submit_button(
        "💾 保存する",
        use_container_width=True,
    )


# =========================================================
# 保存処理
# =========================================================
if submitted:

    # 筋肉量0は「未入力」として扱う
    muscle_value = (
        round(float(muscle_mass), 1)
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
        "weight": round(float(weight), 1),
        "body_fat": round(float(body_fat), 1),
        "muscle_mass": muscle_value,
        "meal_memo": meal_memo,
    }

    try:
        save_diet_log(
            user_id,
            log,
        )

        st.success("今日の記録を保存しました ✨")

        st.rerun()

    except Exception as e:
        st.error(
            "保存中にエラーが発生しました。"
        )


# =========================================================
# 記録取得
# =========================================================
st.markdown("---")
st.markdown("## 📊 からだの変化")

logs = load_diet_logs(
    user_id
)


if logs:

    df = pd.DataFrame(
        logs
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

    # -----------------------------------------------------
    # 表示期間
    # -----------------------------------------------------
    period = st.radio(
        "表示期間",
        [
            "直近30日",
            "直近90日",
            "すべて",
        ],
        horizontal=True,
    )

    chart_df = df.copy()

    if period == "直近30日":

        latest_date = chart_df[
            "log_date"
        ].max()

        start_date = (
            latest_date
            - pd.Timedelta(days=29)
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
            - pd.Timedelta(days=89)
        )

        chart_df = chart_df[
            chart_df["log_date"]
            >= start_date
        ]


    # =====================================================
    # 体脂肪
    # =====================================================
    st.markdown("### 📉 体脂肪率")

    if (
        "body_fat" in chart_df.columns
        and not chart_df["body_fat"].dropna().empty
    ):

        fat_df = (
            chart_df[
                ["log_date", "body_fat"]
            ]
            .dropna()
            .set_index("log_date")
            .rename(
                columns={
                    "body_fat": "体脂肪率（%）"
                }
            )
        )

        st.line_chart(
            fat_df,
            use_container_width=True,
        )

    else:

        st.info(
            "体脂肪率の記録がまだありません。"
        )


    # =====================================================
    # 筋肉量
    # =====================================================
    st.markdown("### 💪 筋肉量")

    if (
        "muscle_mass" in chart_df.columns
        and not chart_df["muscle_mass"].dropna().empty
    ):

        muscle_df = (
            chart_df[
                ["log_date", "muscle_mass"]
            ]
            .dropna()
        )

        # 過去に0で保存された記録は除外
        muscle_df = muscle_df[
            muscle_df["muscle_mass"] > 0
        ]

        if not muscle_df.empty:

            muscle_df = (
                muscle_df
                .set_index("log_date")
                .rename(
                    columns={
                        "muscle_mass": "筋肉量（kg）"
                    }
                )
            )

            st.line_chart(
                muscle_df,
                use_container_width=True,
            )

        else:

            st.info(
                "筋肉量の記録がまだありません。"
            )

    else:

        st.info(
            "筋肉量の記録がまだありません。"
        )


    # =====================================================
    # 体重
    # =====================================================
    st.markdown("### ⚖️ 体重")

    if (
        "weight" in chart_df.columns
        and not chart_df["weight"].dropna().empty
    ):

        weight_df = (
            chart_df[
                ["log_date", "weight"]
            ]
            .dropna()
            .set_index("log_date")
            .rename(
                columns={
                    "weight": "体重（kg）"
                }
            )
        )

        st.line_chart(
            weight_df,
            use_container_width=True,
        )

    else:

        st.info(
            "体重の記録がまだありません。"
        )


    # =====================================================
    # 最近の傾向
    # =====================================================
    st.markdown("---")
    st.markdown("## 🧠 最近の傾向")

    # 直近30日を基本に分析
    latest_date = df[
        "log_date"
    ].max()

    analysis_start = (
        latest_date
        - pd.Timedelta(days=29)
    )

    analysis_df = df[
        df["log_date"]
        >= analysis_start
    ].copy()


    comments = []


    # -----------------------------------------------------
    # 体重
    # -----------------------------------------------------
    weight_data = (
        analysis_df["weight"]
        .dropna()
        if "weight" in analysis_df.columns
        else pd.Series(dtype=float)
    )

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
    fat_data = (
        analysis_df["body_fat"]
        .dropna()
        if "body_fat" in analysis_df.columns
        else pd.Series(dtype=float)
    )

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
    if "muscle_mass" in analysis_df.columns:

        muscle_data = (
            analysis_df[
                analysis_df["muscle_mass"] > 0
            ]["muscle_mass"]
            .dropna()
        )

    else:

        muscle_data = pd.Series(
            dtype=float
        )

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


    # =====================================================
    # コメント表示
    # =====================================================
    if comments:

        for comment in comments:

            st.write(
                "・" + comment
            )

    else:

        st.info(
            "もう少し記録が増えると、"
            "最近の傾向を分析できます。"
        )


    # =====================================================
    # 今日のアドバイス
    # =====================================================
    st.markdown("### 💡 今日のアドバイス")

    # 筋肉量を優先
    if (
        len(muscle_data) >= 2
        and muscle_diff > 0.3
    ):

        st.success(
            "筋肉量が増えています。"
            "食事を減らしすぎず、"
            "今の運動とたんぱく質を続けていきましょう。"
        )

    elif (
        len(muscle_data) >= 2
        and muscle_diff < -0.3
    ):

        st.warning(
            "筋肉量が少し下がっています。"
            "たんぱく質・筋トレ・休養の"
            "バランスを確認してみましょう。"
        )

    elif (
        len(fat_data) >= 2
        and fat_diff > 1.0
    ):

        st.warning(
            "体脂肪率が少し上がっています。"
            "食事を極端に減らすのではなく、"
            "間食・夜の食事・活動量を"
            "一度確認してみましょう。"
        )

    else:

        st.info(
            "大きく変えすぎず、"
            "食事・運動・休養を整えながら"
            "続けていきましょう。"
        )


    # =====================================================
    # 最新記録
    # =====================================================
    st.markdown("---")
    st.markdown("## 📋 最新記録")

    latest = df.iloc[-1]

    latest_date = latest.get(
        "log_date"
    )

    if pd.notna(
        latest_date
    ):

        st.write(
            f"**日付："
            f"{latest_date.strftime('%Y/%m/%d')}**"
        )

    col1, col2, col3 = st.columns(3)

    # 体重
    with col1:

        latest_weight = latest.get(
            "weight"
        )

        if pd.notna(
            latest_weight
        ):

            st.metric(
                "体重",
                f"{latest_weight:.1f} kg"
            )

        else:

            st.metric(
                "体重",
                "—"
            )

    # 体脂肪
    with col2:

        latest_fat = latest.get(
            "body_fat"
        )

        if pd.notna(
            latest_fat
        ):

            st.metric(
                "体脂肪",
                f"{latest_fat:.1f} %"
            )

        else:

            st.metric(
                "体脂肪",
                "—"
            )

    # 筋肉量
    with col3:

        latest_muscle = None

        if "muscle_mass" in df.columns:

            valid_muscle = df[
                df["muscle_mass"] > 0
            ]["muscle_mass"].dropna()

            if not valid_muscle.empty:

                latest_muscle = (
                    valid_muscle.iloc[-1]
                )

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


    # =====================================================
    # 最新食事メモ
    # =====================================================
    meal_memo = latest.get(
        "meal_memo",
        ""
    )

    if (
        meal_memo
        and str(meal_memo).strip()
    ):

        st.markdown(
            "### 🍽️ 最新の食事・メモ"
        )

        st.text(
            str(meal_memo)
        )


else:

    st.info(
        "まだ記録がありません。"
        "上のフォームから今日の記録を保存してみましょう。"
    )
