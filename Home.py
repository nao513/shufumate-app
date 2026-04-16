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
    background: linear-gradient(180deg, #f5f1ea 0%, #f8f4ee 100%);
}

.block-container {
    max-width: 980px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

.hero-wrap {
    background: #f8f3ec;
    border: 1px solid #e7ddd2;
    border-radius: 36px;
    padding: 2.6rem 2rem 2.2rem 2rem;
    box-shadow: 0 10px 30px rgba(90, 68, 52, 0.05);
    margin-bottom: 1.6rem;
}

.logo-wrap {
    max-width: 420px;
    margin: 0 auto 1rem auto;
}

.main-copy {
    text-align: center;
    color: #5c4032;
    font-size: 2.3rem;
    font-weight: 700;
    line-height: 1.45;
    margin-top: 0.8rem;
}

.sub-copy {
    text-align: center;
    color: #7d6656;
    font-size: 1rem;
    line-height: 1.9;
    margin-top: 0.9rem;
    margin-bottom: 1.3rem;
}

.divider-deco {
    text-align: center;
    color: #caa27f;
    font-size: 1rem;
    letter-spacing: 0.25rem;
    margin: 0.6rem 0 1.6rem 0;
}

.card-grid {
    margin-top: 0.6rem;
}

.feature-card {
    background: #fcf8f2;
    border: 1px solid #eadfd2;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 4px 14px rgba(91, 58, 41, 0.04);
    min-height: 138px;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #5b3a29;
    margin-bottom: 0.55rem;
}

.feature-text {
    color: #6f5a4d;
    font-size: 0.96rem;
    line-height: 1.75;
}

.start-card {
    background: #f7efe6;
    border: 1px solid #e9d7c2;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-top: 0.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.start-text {
    color: #6a4a39;
    font-size: 1rem;
    line-height: 1.8;
}

.start-btn {
    background: #b68556;
    color: white;
    padding: 0.7rem 1.2rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
    display: inline-block;
}

.small-note {
    color: #8e7968;
    font-size: 0.9rem;
    margin-top: 0.8rem;
    text-align: center;
}

/* sidebarを少しやわらかく */
section[data-testid="stSidebar"] {
    background: #f3efe9;
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
            レシート撮影や手入力で、シンプルに記録して見返しやすく管理できます。
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">献立・運動プラン</div>
        <div class="feature-text">
            その日の状態や食材、目標に合わせて、無理なく続けやすい提案を作れます。
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
            体型情報、食事スタイル、地域などを登録しておくと、他のページにも反映されます。
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

st.markdown("""
<div class="small-note">
やさしく、見やすく、毎日使いたくなる雰囲気を目指したホームデザインです。
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
