import streamlit as st
import pandas as pd
from app_core import *

st.set_page_config(page_title="家計簿｜ShufuMate", layout="wide")

ensure_headers()
reload_user_data_if_needed()

st.header("💰 家計簿")

st.caption("レシート読み取りや手入力で、家計簿を記録できます。")

tab1, tab2 = st.tabs(["手入力", "履歴"])

with tab1:
    st.subheader("✍️ 支出を入力")

    expense_date = st.date_input("日付", key="expense_date_input")
    category = st.selectbox(
        "カテゴリ",
        ["食費", "日用品", "外食", "医療", "交通", "教育", "美容", "趣味", "その他"],
        key="expense_category_input"
    )
    store_name = st.text_input("店名", key="expense_store_name_input")
    amount = st.number_input("金額", min_value=0, step=1, key="expense_amount_input")
    memo = st.text_area("メモ", key="expense_memo_input", height=100)

    if st.button("💾 支出を保存", use_container_width=True):
        if amount <= 0:
            st.warning("金額を入力してください。")
        else:
            expense_dict = {
                "日付": str(expense_date),
                "カテゴリ": category,
                "店名": store_name,
                "金額": int(amount),
                "メモ": memo,
            }
            append_expense(expense_dict)
            st.session_state["expenses"] = load_expenses()
            st.success("支出を保存しました。")
            st.rerun()

with tab2:
    st.subheader("📋 支出履歴")

    expenses = st.session_state.get("expenses", [])

    if expenses:
        df = pd.DataFrame(expenses)

        show_df = df[["日付", "カテゴリ", "店名", "金額", "メモ"]].copy()
        st.dataframe(show_df, use_container_width=True)

        total_amount = int(show_df["金額"].sum())
        st.metric("合計金額", f"{total_amount:,}円")

        st.subheader("🗑 削除")
        delete_index = st.selectbox(
            "削除する行を選んでください",
            list(range(len(expenses))),
            format_func=lambda i: f"{expenses[i]['日付']}｜{expenses[i]['カテゴリ']}｜{expenses[i]['店名']}｜{expenses[i]['金額']}円",
            key="expense_delete_index"
        )

        if st.button("削除する", use_container_width=True):
            sheet_row = expenses[delete_index]["_sheet_row"]
            delete_expense(sheet_row)
            st.session_state["expenses"] = load_expenses()
            st.success("削除しました。")
            st.rerun()
    else:
        st.caption("まだ支出履歴はありません。")
