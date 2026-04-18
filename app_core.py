def load_log_chart_df(user_id: str) -> pd.DataFrame:
    ws = get_dietlogs_sheet()
    records = ws.get_all_records()
    user_logs = [r for r in records if str(r.get("user_id", "")) == user_id]

    if not user_logs:
        return pd.DataFrame()

    df = pd.DataFrame(user_logs)

    if "log_date" not in df.columns:
        return pd.DataFrame()

    df["log_date_sort"] = pd.to_datetime(df["log_date"], errors="coerce")
    df["created_at_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")
    df["weight_num"] = pd.to_numeric(df.get("weight"), errors="coerce")
    df["body_fat_num"] = pd.to_numeric(df.get("body_fat"), errors="coerce")

    df = df.dropna(subset=["log_date_sort"])
    df = df.sort_values(
        by=["log_date_sort", "created_at_sort"],
        ascending=[True, True],
        na_position="last",
    )

    # 同じ日付に複数記録がある場合は最後の記録を採用
    df = df.drop_duplicates(subset=["log_date"], keep="last")

    chart_df = pd.DataFrame(
        {
            "日付": df["log_date_sort"],
            "体重(kg)": df["weight_num"],
            "体脂肪(%)": df["body_fat_num"],
        }
    ).set_index("日付")

    return chart_df
