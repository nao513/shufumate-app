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
html, body, [class*="css"]  {
    font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f4efe8 0%, #f8f4ee 100%);
}

.block-container {
    max-width: 980px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #f1ece6;
}

.hero-wrap {
    background: #f8f3ec;
    border: 1px solid #e8ddd0;
    border-radius: 38px;
    padding: 2.6rem 2rem 2.2rem 2rem;
    box-shadow: 0 10px 28px rgba(91, 58, 41, 0.05);
    margin-bottom: 1.6rem;
}

.logo-wrap {
    max-width: 360px;
    margin: 0 auto 0.8rem auto;
}

.main-copy {
    text-align: center;
    color: #5b3a29;
    font-size: 2.25rem;
    font-weight: 700;
    line-height: 1.45;
    margin-top: 0.8rem;
}

.sub-copy {
    text-align: center;
    color: #7a6454;
    font-size: 1rem;
    line-height: 1.9;
    margin-top: 0.9rem;
    margin-bottom: 1.2rem;
}

.divider-deco {
    text-align: center;
    color: #c7a17c;
    font-size: 1rem;
    letter-spacing: 0.2rem;
    margin: 0.3rem 0 1.5rem 0;
}

.feature-card {
    background: #fcf8f3;
    border: 1px solid #eadfd4;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 4px 12px rgba(91, 58, 41, 0.04);
    min-height: 135px;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #5b3a29;
    margin-bottom: 0.5rem;
}

.feature-text {
    color: #6c5a4f;
    font-size: 0.95rem;
    line-height: 1.75;
}

.start-card {
    background: #f6eee5;
    border: 1px solid #e6d6c6;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-top: 0.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.start-text {
    color: #694b3a;
    font-size: 1rem;
    line-height: 1.8;
}

.start-btn {
    background: #b38356;
    color: #ffffff;
    padding: 0.72rem 1.25rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
st.image("ChatGPT Image 2025年5月17日 13_33_39.png", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="main-copy">
主婦の毎日に寄り添う<br>
ダイエット・献立・記録・家計アプリ
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sub-copy">
毎日のちょっとした悩みを、やさしくサポートします。
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider-deco">·· ✦ ··</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">ダイエット管理</div>
        <div class="feature-text">
            体重・体脂肪率の記録や、日々の変化チェック、目標に合わせた管理に。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">写真で記録</div>
        <div class="feature-text">
            冷蔵庫や体重計の写真から、食材や数値を読み取って記録に活かせます。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">家計簿</div>
        <div class="feature-text">
            レシート撮影や手入力で、家計の記録をシンプルに見返しやすく管理できます。
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">献立・運動プラン</div>
        <div class="feature-text">
            その日の状態や冷蔵庫の食材、目標に合わせて続けやすい提案を作れます。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">なんでも相談</div>
        <div class="feature-text">
            夕飯どうする？ 運動前後は何を食べる？ そんな日常の迷いを気軽に相談できます。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">初期設定</div>
        <div class="feature-text">
            体型情報、食事スタイル、地域などを登録しておくと、他ページにも反映されます。
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="start-card">
    <div class="start-text">
        <strong>まずは、初期設定から始めるのがおすすめです。</strong><br>
        左のメニューから、使いたい機能を選んでください。
    </div>
    <div class="start-btn">初期設定へ</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
