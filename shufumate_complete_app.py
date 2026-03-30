import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("Google Sheets 接続テスト")

try:
    creds_dict = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    gc = gspread.authorize(creds)

    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    sh = gc.open_by_key(sheet_id)

    st.success("認証成功")
    st.write("シート名:", sh.title)
    st.write("タブ一覧:", [ws.title for ws in sh.worksheets()])

except Exception as e:
    st.error("認証または接続に失敗しました")
    st.code(repr(e))
