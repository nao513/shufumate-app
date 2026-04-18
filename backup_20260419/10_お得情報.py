import streamlit as st
from app_core import *

ensure_headers()
reload_user_data_if_needed()

st.set_page_config(page_title="お得情報", layout="wide")

st.header("🎁 お得情報")

prefecture = st.session_state.get("home_prefecture", "").strip()
area = st.session_state.get("home_area", "").strip()

if prefecture or area:
    st.info(f"現在の地域設定: {prefecture} {area}".strip())
else:
    st.warning("まだ地域設定がありません。初期設定で地域を入れると、お得情報を地域向けに広げやすくなります。")

st.subheader("📍 地域向けに追加予定のお得情報")
st.write("・スーパー、ドラッグストア、日用品のお得情報")
st.write("・子育て支援、地域の助成、家計に役立つ制度")
st.write("・旅行、マイル、ポイ活、節約情報")
st.write("・地域イベント、学び、習い事情報")
st.write("・広告やおすすめ情報の地域最適化")

st.divider()

st.subheader("📝 今後の使い方イメージ")
if prefecture or area:
    st.write(f"ShufuMate では、**{prefecture} {area}** に合わせて次のような情報を出しやすくなります。".strip())
    st.write("・近くのお店や施設に関するお得情報")
    st.write("・その地域で使いやすい節約・ポイ活情報")
    st.write("・子育て、教育、暮らしに役立つ地域情報")
else:
    st.write("地域設定を入れると、近くで使いやすい情報に寄せた表示へ広げやすくなります。")

st.divider()

st.subheader("💡 こんな情報を増やせます")
st.write("・食費節約の買い方")
st.write("・お小遣いを増やす工夫")
st.write("・ポイ活、マイル、旅行節約")
st.write("・主婦向けのお得なサービス")

