import streamlit as st
from app_core import *

st.set_page_config(page_title="ShufuMate｜主婦の味方アプリ", layout="wide")

ensure_headers()
reload_user_data_if_needed()

st.title("🏠 ShufuMate")
st.caption("主婦の毎日に寄り添うアプリ")
