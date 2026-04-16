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
html, body, [class*="css"] {
    font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f4efe8 0%, #f8f4ee 100%);
}

section[data-testid="stSidebar"] {
    background: #f1ece6;
}

.block-container {
    max-width: 920px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.home-shell {
    background: #f8f3ec;
    border: 1px solid #e6ddd3;
    border-radius: 40px;
    padding: 2.2rem 2rem 2rem 2rem;
    box-shadow: 0 10px 28px rgba(91, 58, 41, 0.05);
}

.logo-wrap {
    max-width: 300px;
    margin: 0 auto 0.8rem auto;
}

.main-copy {
    text-align: center;
    color: #5b3a29;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.5;
    margin-top: 0.8rem;
}

.sub-copy {
    text-align: center;
    color: #7d6656;
    font-size: 1rem;
    line-height: 1.9;
    margin-top: 0.8rem;
    margin-bottom: 1rem;
}

.deco {
    text-align: center;
    color: #c9a27f;
    font-size: 1rem;
    letter-spacing: 0.2rem;
    margin-bottom: 1.2rem;
}

.card-box {
    background: #fcf8f2;
    border: 1px solid #eadfd3;
    border-radius: 18px;
    padding: 1rem 1rem 0.9rem 1rem;
    min-height: 148px;
    box-shadow: 0 4px 12px rgba(91, 58, 41, 0.04);
    margin-bottom: 0.8rem;
}

.card-row {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    align-items: flex-start;
}

.card-text {
    flex: 1;
}

.card-title {
    color: #5b3a29;
    font-size: 1.08rem;
    font-weight: 700;
    margin-bottom: 0.45rem;
}

.card-desc {
    color: #6d5b4f;
    font-size: 0.93rem;
    line-height: 1.75;
}

.card-icon {
    width: 74px;
    height: 74px;
    min-width: 74px;
    border-radius: 18px;
    background: linear-gradient(180deg, #f8eadb 0%, #f4e2cf 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}

.bottom-box {
    background: #f6eee5;
    border: 1px solid #e5d4c1;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    margin-top: 0.6rem;
}

.bottom-title {
    color: #6b4a39;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.bottom-text {
    color: #7a6556;
    font-size: 0.96rem;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="home-shell">', unsafe_allow_html=True)

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

st.markdown('<div class="deco">── ✦ ──</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">ダイエット管理</div>
                <div class="card-desc">
                    体重・体脂肪率の記録や日々の変化チェック、目標に合わせた管理に。
                </div>
            </div>
            <div class="card-icon">⚖️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("ダイエット管理へ", key="go_diet", use_container_width=True):
        st.switch_page("pages/1_ダイエット管理.py")

    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">写真で記録</div>
                <div class="card-desc">
                    冷蔵庫や体重計の写真から、食材や数値を読み取って記録に活かせます。
                </div>
            </div>
            <div class="card-icon">📷</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("写真で記録へ", key="go_photo", use_container_width=True):
        st.switch_page("pages/3_写真で記録.py")

    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">家計簿</div>
                <div class="card-desc">
                    レシート撮影や手入力で、シンプルに記録して見返しやすく管理できます。
                </div>
            </div>
            <div class="card-icon">👛</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("家計簿へ", key="go_money", use_container_width=True):
        st.switch_page("pages/5_家計簿.py")

with right:
    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">献立・運動プラン</div>
                <div class="card-desc">
                    その日の状態や冷蔵庫の食材、目標に合わせて続けやすい提案を作れます。
                </div>
            </div>
            <div class="card-icon">🍽️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("献立・運動プランへ", key="go_plan", use_container_width=True):
        st.switch_page("pages/2_献立・運動プラン.py")

    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">なんでも相談</div>
                <div class="card-desc">
                    夕飯どうする？運動前後は何を食べる？そんな日常の迷いを気軽に相談できます。
                </div>
            </div>
            <div class="card-icon">📝</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("なんでも相談へ", key="go_advice", use_container_width=True):
        st.switch_page("pages/4_なんでも相談.py")

    st.markdown("""
    <div class="card-box">
        <div class="card-row">
            <div class="card-text">
                <div class="card-title">初期設定</div>
                <div class="card-desc">
                    体型情報、食事スタイル、地域などを登録しておくと他ページにも反映されます。
                </div>
            </div>
            <div class="card-icon">⚙️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("初期設定へ", key="go_settings", use_container_width=True):
        st.switch_page("pages/6_初期設定.py")

st.markdown("""
<div class="bottom-box">
    <div class="bottom-title">まずは、初期設定から始めるのがおすすめです。</div>
    <div class="bottom-text">
        食事スタイルや地域、体型情報を登録しておくと、他のページにも反映されて使いやすくなります。
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
