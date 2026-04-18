import streamlit as st

st.markdown("""
<style>
/* 全体 */
html, body, [class*="css"]  {
    font-family: "Hiragino Sans", "Yu Gothic", sans-serif;
}

/* カード */
.feature-card {
    border: 1px solid #d8d1c7;
    border-radius: 20px;
    padding: 26px 26px 22px 26px;
    background: #f8f5ef;
    min-height: 360px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
}

/* 上段 */
.feature-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;   /* ← イラストを上に合わせる */
    gap: 20px;
}

/* 左側 */
.feature-left {
    flex: 1;
    min-width: 0;
}

/* タイトル */
.feature-title {
    margin: 0 0 18px 0;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.15;
    color: #27314a;
    white-space: nowrap;       /* ← 1行固定 */
    letter-spacing: 0.02em;
}

/* 説明文 */
.feature-desc {
    margin: 0;
    font-size: 1.05rem;
    line-height: 1.9;
    color: #4b5568;
}

/* 右側イラスト */
.feature-illust {
    width: 118px;
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 2px;
}

.feature-illust img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 18px;
    object-fit: contain;
}

/* ボタン */
.feature-btn-wrap {
    margin-top: 24px;
}

.feature-btn {
    width: 100%;
    text-align: center;
    padding: 16px 20px;
    border: 1.5px solid #d8c5b4;
    border-radius: 999px;
    color: #7a563f !important;
    font-size: 1.05rem;
    font-weight: 700;
    background: #fffaf4;
    text-decoration: none !important;
    display: inline-block;
    box-sizing: border-box;
}

/* 少し狭い画面ではタイトルを少しだけ縮める */
@media (max-width: 1200px) {
    .feature-title {
        font-size: 1.85rem;
    }

    .feature-illust {
        width: 104px;
    }
}

/* スマホでは折り返しOK */
@media (max-width: 768px) {
    .feature-top {
        flex-direction: column;
        align-items: flex-start;
    }

    .feature-title {
        white-space: normal;
        font-size: 1.7rem;
    }

    .feature-illust {
        width: 88px;
    }

    .feature-card {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)
