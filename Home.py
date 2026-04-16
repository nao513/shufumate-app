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
    background: linear-gradient(180deg, #f7f4ed 0%, #fcfaf6 100%);
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero-wrap {
    background: rgba(255,255,255,0.55);
    border: 1px solid #eee4d8;
    border-radius: 28px;
    padding: 2.2rem 2rem 2rem 2rem;
    box-shadow: 0 8px 30px rgba(106, 82, 60, 0.06);
    margin-bottom: 1.5rem;
}

.catch {
    text-align: center;
    font-size: 1.15rem;
    color: #7a5a49;
    margin-top: 0.4rem;
    margin-bottom: 1.6rem;
    line-height: 1.9;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #5b3a29;
    margin-bottom: 0.9rem;
}

.info-card {
    background: #fffaf5;
    border: 1px solid #eedfce;
    border-radius: 20px;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    box-shadow: 0 3px 12px rgba(91, 58, 41, 0.05);
    height: 100%;
}

.info-card h3 {
    margin: 0 0 0.6rem 0;
    font-size: 1.05rem;
    color: #5b3a29;
}

.info-card p {
    margin: 0;
    color: #6d5b4f;
    font-size: 0.98rem;
    line-height: 1.8;
}

.start-box {
    background: #fff3e8;
    border: 1px solid #f3d7bf;
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-top: 1rem;
    color: #6a4b39;
    font-size: 1rem;
    line-height: 1.8;
}

.small-note {
    color: #8b7567;
    font-size: 0.92rem;
    margin-top: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.4, 1])

with col2:
    st.image("ChatGPT Image 2025年5月17日 13_33_39.png", use_container_width=True)

st.markdown(
    """
    <div class="catch">
        主婦の毎日に寄り添う、<br>
        ダイエット・献立・記録・家計簿のやさしいサポートアプリ
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🌿 ShufuMateでできること</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="info-card">
        <h3>📘 ダイエット管理</h3>
        <p>体重・体脂肪率の記録、日々の変化チェック、目標に合わせた管理ができます。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-top:1rem;">
        <h3>📷 写真で記録</h3>
        <p>冷蔵庫写真や体重計写真から、食材や数値を読み取って記録に活かせます。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-top:1rem;">
        <h3>💬 なんでも相談</h3>
        <p>夕飯どうする？ 運動前後に何を食べる？ そんな日常の迷いを気軽に相談できます。</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="info-card">
        <h3>🍽 献立・運動プラン</h3>
        <p>その日の状態や目標、冷蔵庫の食材に合わせて、無理なく続けやすい提案を作れます。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-top:1rem;">
        <h3>💰 家計簿</h3>
        <p>レシート撮影や手入力で、家計の記録と見返しをシンプルに行えます。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-top:1rem;">
        <h3>⚙️ 初期設定</h3>
        <p>体型情報、食事スタイル、地域などを登録しておくと、他のページにも反映されて使いやすくなります。</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="start-box">
    <strong>はじめて使うときは「初期設定」からがおすすめです。</strong><br>
    左のメニューから、使いたいページを選んでください。
</div>
<div class="small-note">
    使いやすく、続けやすく、主婦の毎日にそっと寄り添うデザインを目指しています。
</div>
""", unsafe_allow_html=True)
