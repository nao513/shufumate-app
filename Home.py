import streamlit as st
import pandas as pd

from app_core import (
    require_login,
    get_user_id,
    load_diet_logs,
    jst_today,
)

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="ShufuMate",
    page_icon="🏠",
    layout="centered",
)

# =========================
# ログイン確認
# =========================
require_login()

user_id = get_user_id()

# =========================
# タイトル
# =========================
st.title("🏠 ShufuMate")

st.caption(
    "体重だけでなく、体脂肪・筋肉量・食事・体調を"
    "一緒に見ながら整えていくアプリです。"
)

# =========================
# 記録取得
# =========================
logs = load_diet_logs(user_id)

df = pd.DataFrame()

if logs:
    df = pd.DataFrame(logs)

    # 日付変換
    if "log_date" in df.columns:
        df["log_date"] = pd.to_datetime(
            df["log_date"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["log_date"]
        )

        df = df.sort_values(
            "log_date"
        )

    # 数値変換
    for col in [
        "weight",
        "body_fat",
        "muscle_mass",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )


# =========================
# 今日の状態
# =========================
st.markdown("## 🌿 今日の状態")

if not df.empty:

    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    # -------------------------
    # 体重
    # -------------------------
    with col1:

        weight = latest.get(
            "weight"
        )

        if pd.notna(weight):
            st.metric(
                "体重",
                f"{weight:.1f} kg"
            )
        else:
            st.metric(
                "体重",
                "--"
            )

    # -------------------------
    # 体脂肪
    # -------------------------
    with col2:

        body_fat = latest.get(
            "body_fat"
        )

        if pd.notna(body_fat):
            st.metric(
                "体脂肪",
                f"{body_fat:.1f} %"
            )
        else:
            st.metric(
                "体脂肪",
                "--"
            )

    # -------------------------
    # 筋肉量
    # -------------------------
    with col3:

        muscle_mass = latest.get(
            "muscle_mass"
        )

        if pd.notna(muscle_mass):
            st.metric(
                "筋肉量",
                f"{muscle_mass:.1f} kg"
            )
        else:
            st.metric(
                "筋肉量",
                "--"
            )

else:

    st.info(
        "まだ記録がありません。"
        "「記録する」から今日の状態を入力してみましょう。"
    )


# =========================
# 今日の整え方
# =========================
st.markdown("## 💡 今日の整え方")

if not df.empty:

    comments = []

    first = df.iloc[0]
    latest = df.iloc[-1]

    # =====================
    # 体重
    # =====================
    if (
        "weight" in df.columns
        and pd.notna(first.get("weight"))
        and pd.notna(latest.get("weight"))
    ):

        diff_weight = (
            latest["weight"]
            - first["weight"]
        )

        if diff_weight < -1:
            comments.append(
                "体重は開始時より減っています。"
            )

        elif diff_weight > 1:
            comments.append(
                "体重は開始時より少し増えています。"
            )

        else:
            comments.append(
                "体重は大きく変わらず安定しています。"
            )

    # =====================
    # 体脂肪
    # =====================
    if (
        "body_fat" in df.columns
        and pd.notna(first.get("body_fat"))
        and pd.notna(latest.get("body_fat"))
    ):

        diff_body_fat = (
            latest["body_fat"]
            - first["body_fat"]
        )

        if diff_body_fat < -1:
            comments.append(
                "体脂肪は開始時より減っています。"
            )

        elif diff_body_fat > 1:
            comments.append(
                "体脂肪は開始時より少し増えています。"
            )

        else:
            comments.append(
                "体脂肪は大きく変わらず安定しています。"
            )

    # =====================
    # 筋肉量
    # =====================
    if (
        "muscle_mass" in df.columns
        and pd.notna(first.get("muscle_mass"))
        and pd.notna(latest.get("muscle_mass"))
    ):

        diff_muscle = (
            latest["muscle_mass"]
            - first["muscle_mass"]
        )

        if diff_muscle > 0.3:
            comments.append(
                "筋肉量は開始時より増えています。"
            )

        elif diff_muscle < -0.3:
            comments.append(
                "筋肉量は開始時より少し減っています。"
            )

        else:
            comments.append(
                "筋肉量は安定して維持できています。"
            )

    # =====================
    # コメント表示
    # =====================
    if comments:

        for comment in comments:
            st.write(
                "・" + comment
            )

    else:

        st.info(
            "記録が増えると、"
            "体重・体脂肪・筋肉量の変化を"
            "ここで確認できます。"
        )


    # =====================
    # ワンポイント
    # =====================
    latest_body_fat = (
        latest.get("body_fat")
        if "body_fat" in df.columns
        else None
    )

    latest_muscle = (
        latest.get("muscle_mass")
        if "muscle_mass" in df.columns
        else None
    )

    # 筋肉量を優先して評価
    if (
        pd.notna(latest_muscle)
        and "diff_muscle" in locals()
        and diff_muscle > 0.3
    ):

        st.success(
            "筋肉量が増えています。"
            "食事を減らしすぎず、"
            "今の運動とたんぱく質を"
            "続けていきましょう。"
        )

    elif (
        "diff_body_fat" in locals()
        and diff_body_fat > 1
    ):

        st.warning(
            "体脂肪が少し増えています。"
            "食事を極端に減らすのではなく、"
            "間食・夜の食事・活動量を"
            "一度見直してみましょう。"
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


# =========================
# 最近の変化
# =========================
st.markdown("## 📈 最近の変化")

if not df.empty:

    chart_columns = []

    if (
        "weight" in df.columns
        and not df["weight"].isna().all()
    ):
        chart_columns.append(
            "weight"
        )

    if (
        "body_fat" in df.columns
        and not df["body_fat"].isna().all()
    ):
        chart_columns.append(
            "body_fat"
        )

    if (
        "muscle_mass" in df.columns
        and not df["muscle_mass"].isna().all()
    ):
        chart_columns.append(
            "muscle_mass"
        )

    if chart_columns:

        chart_df = (
            df[
                ["log_date"]
                + chart_columns
            ]
            .set_index(
                "log_date"
            )
        )

        st.line_chart(
            chart_df,
            use_container_width=True
        )

    else:

        st.info(
            "グラフに表示できる記録が"
            "まだありません。"
        )

else:

    st.info(
        "記録が増えると、"
        "ここに変化のグラフが表示されます。"
    )


# =========================
# 最新記録
# =========================
st.markdown("## 📝 最新記録")

if not df.empty:

    latest = df.iloc[-1]

    log_date = latest.get(
        "log_date"
    )

    if pd.notna(log_date):
        st.write(
            f"**記録日："
            f"{log_date.strftime('%Y/%m/%d')}**"
        )

    latest_weight = latest.get(
        "weight"
    )

    latest_body_fat = latest.get(
        "body_fat"
    )

    latest_muscle = latest.get(
        "muscle_mass"
    )

    meal_memo = latest.get(
        "meal_memo",
        ""
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if pd.notna(latest_weight):
            st.write(
                f"体重：{latest_weight:.1f} kg"
            )
        else:
            st.write(
                "体重：--"
            )

    with col2:
        if pd.notna(latest_body_fat):
            st.write(
                f"体脂肪：{latest_body_fat:.1f} %"
            )
        else:
            st.write(
                "体脂肪：--"
            )

    with col3:
        if pd.notna(latest_muscle):
            st.write(
                f"筋肉量：{latest_muscle:.1f} kg"
            )
        else:
            st.write(
                "筋肉量：--"
            )

    if (
        meal_memo
        and str(meal_memo).strip()
    ):

        st.markdown(
            "**食事メモ**"
        )

        st.write(
            meal_memo
        )

else:

    st.info(
        "最新記録はまだありません。"
    )


# =========================
# クイックメニュー
# =========================
st.markdown("---")
st.markdown("## 📋 メニュー")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "📝 記録する",
        use_container_width=True
    ):
        st.switch_page(
            "pages/2_記録する.py"
        )

    if st.button(
        "📷 写真で記録",
        use_container_width=True
    ):
        st.switch_page(
            "pages/4_写真で記録.py"
        )

with col2:

    if st.button(
        "💬 相談する",
        use_container_width=True
    ):
        st.switch_page(
            "pages/3_相談する.py"
        )

    if st.button(
        "⚙️ 設定",
        use_container_width=True
    ):
        st.switch_page(
            "pages/1_設定.py"
        )


# =========================
# フッター
# =========================
st.markdown("---")

st.caption(
    f"今日の日付："
    f"{jst_today().strftime('%Y/%m/%d')}"
)
