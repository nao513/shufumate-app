import streamlit as st
import pandas as pd
from datetime import datetime
from app_core import *

st.set_page_config(page_title="家計簿｜ShufuMate", layout="wide")

reload_user_data_if_needed()

st.header("💰 家計簿")
st.caption("レシート読み取りや手入力で、家計の記録を管理できます。")

st.info(
    "毎日の支出を見返しやすく整理しながら、"
    "無理のない家計管理に役立てていただけます。"
)

st.subheader("📷 レシート読取")
st.caption("レシートを撮影またはアップロードして、家計簿に使う内容を自動で読み取れます。")
st.caption("※ Take Photo＝その場で撮影、Upload＝保存済み写真を追加")

if "receipt_scan_images" not in st.session_state:
    st.session_state["receipt_scan_images"] = []
if "selected_receipt_index" not in st.session_state:
    st.session_state["selected_receipt_index"] = 0
if "receipt_result" not in st.session_state:
    st.session_state["receipt_result"] = ""
if "receipt_store" not in st.session_state:
    st.session_state["receipt_store"] = ""
if "receipt_date_text" not in st.session_state:
    st.session_state["receipt_date_text"] = ""
if "receipt_amount" not in st.session_state:
    st.session_state["receipt_amount"] = 0
if "receipt_memo" not in st.session_state:
    st.session_state["receipt_memo"] = ""

receipt_camera = st.camera_input("レシートを撮る", key="receipt_camera")

col_a, col_b = st.columns(2)

with col_a:
    if receipt_camera is not None and st.button("➕ 撮ったレシートを追加", key="add_receipt_camera"):
        resized = resize_image(receipt_camera, max_size=1200)
        st.session_state["receipt_scan_images"].append(resized)
        st.success("レシート画像を追加しました。")
        st.rerun()

with col_b:
    if st.button("🧹 レシート画像を全部クリア", key="clear_receipt_images"):
        st.session_state["receipt_scan_images"] = []
        st.session_state["receipt_result"] = ""
        st.session_state["receipt_store"] = ""
        st.session_state["receipt_date_text"] = ""
        st.session_state["receipt_amount"] = 0
        st.session_state["receipt_memo"] = ""
        st.rerun()

receipt_uploads = st.file_uploader(
    "またはレシート画像をアップロード（複数OK）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key="receipt_upload_multi"
)

if receipt_uploads:
    if st.button("📥 アップロードしたレシートを追加", key="add_receipt_uploads"):
        for photo in receipt_uploads:
            resized = resize_image(photo, max_size=1200)
            st.session_state["receipt_scan_images"].append(resized)
        st.success("レシート画像を追加しました。")
        st.rerun()

if st.session_state["receipt_scan_images"]:
    st.write(f"保存中のレシート画像: {len(st.session_state['receipt_scan_images'])}枚")

    if st.session_state["selected_receipt_index"] >= len(st.session_state["receipt_scan_images"]):
        st.session_state["selected_receipt_index"] = max(0, len(st.session_state["receipt_scan_images"]) - 1)

    selected_receipt_index = st.selectbox(
        "読み取りに使うレシートを選んでください",
        list(range(len(st.session_state["receipt_scan_images"]))),
        index=st.session_state["selected_receipt_index"],
        format_func=lambda x: f"レシート画像 {x + 1}",
        key="selected_receipt_index"
    )
    st.session_state["selected_receipt_index"] = selected_receipt_index

    max_preview = 8
    preview_images = st.session_state["receipt_scan_images"][:max_preview]

    if len(st.session_state["receipt_scan_images"]) > max_preview:
        st.caption(f"表示は先頭 {max_preview} 枚までです。")

    for i, img in enumerate(preview_images):
        st.image(img, caption=f"レシート画像 {i+1}", use_container_width=True)

        if st.button(f"🗑 このレシートを削除 {i+1}", key=f"delete_receipt_{i}", use_container_width=True):
            st.session_state["receipt_scan_images"].pop(i)
            if st.session_state["selected_receipt_index"] >= len(st.session_state["receipt_scan_images"]):
                st.session_state["selected_receipt_index"] = max(0, len(st.session_state["receipt_scan_images"]) - 1)
            st.rerun()

    selected_receipt = st.session_state["receipt_scan_images"][selected_receipt_index]

    if st.button("🧾 レシートを読み取る", key="read_receipt_multi"):
        client = get_openai_client()
        with st.spinner("レシートを読み取り中..."):
            result = extract_receipt_info(client, selected_receipt)

        st.session_state["receipt_result"] = result
        parsed = parse_receipt_result(result)
        st.session_state["receipt_store"] = parsed["store"]
        st.session_state["receipt_date_text"] = parsed["date"]
        st.session_state["receipt_amount"] = parsed["amount"]
        st.session_state["receipt_memo"] = parsed["memo"]
        st.success("レシート内容を読み取りました。")
        st.rerun()

st.text_area("読み取り結果", key="receipt_result", height=220)

st.divider()
st.subheader("✍ 家計簿に登録")

default_date = parse_receipt_date_to_dateobj(st.session_state.get("receipt_date_text", ""))
if default_date is None:
    default_date = datetime.today().date()

with st.form("budget_form"):
    date_value = st.date_input("日付", value=default_date)
    category = st.selectbox("カテゴリ", ["食費", "日用品", "教育費", "交際費", "医療費", "その他"])
    store_name = st.text_input("店名", value=st.session_state.get("receipt_store", ""))
    amount = st.number_input(
        "金額（円）",
        min_value=0,
        step=100,
        value=int(st.session_state.get("receipt_amount", 0))
    )
    memo_default = st.session_state.get("receipt_memo", "")
    memo = st.text_input("メモ", value=memo_default)
    submitted = st.form_submit_button("記録する")

if submitted:
    expense = {
        "日付": str(date_value),
        "カテゴリ": category,
        "店名": store_name,
        "金額": amount,
        "メモ": memo
    }
    append_expense(expense)
    st.session_state["expenses"] = load_expenses()
    st.success("支出を保存しました。")
    st.rerun()

if st.session_state.get("expenses"):
    df_exp = pd.DataFrame(st.session_state["expenses"])

    st.subheader("📈 集計")

    if not df_exp.empty:
        df_exp["日付"] = pd.to_datetime(df_exp["日付"], errors="coerce")

        today = datetime.today()
        current_month_df = df_exp[
            (df_exp["日付"].dt.year == today.year) &
            (df_exp["日付"].dt.month == today.month)
        ].copy()

        total_all = int(df_exp["金額"].sum())
        total_month = int(current_month_df["金額"].sum()) if not current_month_df.empty else 0

        c1, c2 = st.columns(2)
        c1.metric("累計合計", f"{total_all:,}円")
        c2.metric("今月の合計", f"{total_month:,}円")

        st.markdown("#### 🧺 カテゴリ別合計")
        category_df = (
            df_exp.groupby("カテゴリ", as_index=False)["金額"]
            .sum()
            .sort_values("金額", ascending=False)
        )
        st.dataframe(category_df, use_container_width=True, hide_index=True)

        st.markdown("#### 🗓 月別合計")
        month_df = df_exp.copy()
        month_df["年月"] = month_df["日付"].dt.strftime("%Y-%m")
        monthly_summary = (
            month_df.groupby("年月", as_index=False)["金額"]
            .sum()
            .sort_values("年月", ascending=False)
        )
        st.dataframe(monthly_summary, use_container_width=True, hide_index=True)

    st.subheader("📊 記録一覧")

    display_df = df_exp.drop(columns=["_sheet_row"], errors="ignore").copy()
    display_df["日付"] = pd.to_datetime(display_df["日付"], errors="coerce").dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True)

    st.markdown("#### 🗑 記録を削除")
    delete_options = []
    for item in st.session_state["expenses"]:
        label = f"No.{item['_sheet_row']}｜{item['日付']}｜{item['カテゴリ']}｜{item['店名']}｜{item['金額']}円｜{item['メモ']}"
        delete_options.append((label, item["_sheet_row"]))

    selected_label = st.selectbox(
        "削除する記録を選んでください",
        [x[0] for x in delete_options],
        key="expense_delete_label"
    )

    selected_row = next(row for label, row in delete_options if label == selected_label)

    if st.button("この記録を削除する"):
        delete_expense(selected_row)
        st.session_state["expenses"] = load_expenses()
        st.success("家計簿の記録を削除しました。")
        st.rerun()

    csv = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 家計簿CSVダウンロード",
        data=csv,
        file_name="kakeibo.csv",
        mime="text/csv"
    )

