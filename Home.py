import streamlit as st
from app_core import *

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

ensure_headers()
reload_user_data_if_needed()

st.title("🏠 ShufuMate")
st.caption("主婦の毎日に寄り添うアプリ")

st.markdown("""
左のページ一覧から使いたい機能を選んでください。

- なんでも相談
- 初期設定
- 写真で記録
- 家計簿
- ダイエット管理
- 献立・運動プラン
""")
