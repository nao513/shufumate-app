import streamlit as st
from app_core import *

st.set_page_config(
    page_title="ShufuMate｜主婦の味方アプリ",
    layout="wide"
)

ensure_headers()
reload_user_data_if_needed()

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}
.main-title {
    font-size: 3.2rem;
    font-weight: 800;
    color: #5b3a29;
    margin-bottom: 0.3rem;
}
.sub-title {
    font-size: 1.2rem;
    color: #7a5a49;
    margin-bottom: 2rem;
}
.home-card {
    background: #fffaf5;
    border: 1px solid #f0dfd2;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(91, 58, 41, 0.05);
}
.home-section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #5b3a29;
    margin-bottom: 0.7rem;
}
.home-text {
    color: #6b5a50;
    font-size: 1rem;
    line-height: 1.9;
}
.feature-list {
    color: #5f5148;
    font-size: 1rem;
    line-height: 2;
    padding-left: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.image("ChatGPT Image 2025年5月17日 13_33_39.png", use_container_width=True)

with col2:
    st.markdown('<div class="main-title">ShufuMate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">あなたの暮らしに、やさしくフィット</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="home-card">
        <div class="home-section-title">🌿 アプリについて</div>
        <div class="home-text">
            ShufuMateは、主婦の毎日に寄り添う生活サポートアプリです。<br>
            ダイエット管理、献立づくり、写真記録、家計簿、ちょっとした相談まで、<br>
            毎日の「どうしよう」をやさしく支えます。
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="home-card">
    <div class="home-section-title">📱 できること</div>
    <ul class="feature-list">
        <li>ダイエット管理</li>
        <li>献立・運動プラン作成</li>
        <li>写真で記録（冷蔵庫・体重計）</li>
        <li>なんでも相談</li>
        <li>家計簿</li>
        <li>初期設定</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="home-card">
    <div class="home-section-title">👉 使い方</div>
    <div class="home-text">
        左のメニューから、使いたいページを選んでください。<br>
        はじめて使うときは「初期設定」から始めるのがおすすめです。
    </div>
</div>
""", unsafe_allow_html=True)
