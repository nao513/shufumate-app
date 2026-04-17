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
    max-width: 930px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.home-shell {
    background: #f8f3ec;
    border: 1px solid #e7ddd2;
    border-radius: 42px;
    padding: 2.3rem 2rem 2rem 2rem;
    box-shadow: 0 10px 28px rgba(91, 58, 41, 0.05);
}

.logo-wrap {
    max-width: 310px;
    margin: 0 auto 0.9rem auto;
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
    color: #7a6454;
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

.small-note {
    color: #7a6556;
    font-size: 0.96rem;
    line-height: 1.8;
}

div.stButton > button {
    background: #fbf6ef;
    color: #6a4a39;
    border: 1px solid #e2d2c1;
    border-radius: 999px;
    font-weight: 700;
    min-height: 2.8rem;
}
div.stButton > button:hover {
    background: #f1e5d7;
    border-color: #d6b99c;
    color: #5b3a29;
}
</style>
""", unsafe_allow_html=True)


def render_feature_card(title, desc, image_path, button_label, target_page, key_prefix):
    with st.container(border=True):
        c1, c2 = st.columns([2.4, 0.9])

        with c1:
            st.markdown(
                f"""
                <div style="
                    min-height: 84px;
                    display: flex;
                    align-items: flex-start;
                ">
                    <h3 style="
                        margin: 0;
                        line-height: 1.25;
                        color: #2f3446;
                        font-size: 2.1rem;
                        font-weight: 800;
                    ">
                        {title}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="
                    color:#2f3446;
                    font-size: 1rem;
                    line-height: 1.8;
                    min-height: 118px;
                ">
                    {desc}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.image(image_path, width=120)

        if st.button(button_label, key=f"{key_prefix}_btn", use_container_width=True):
            st.switch_page(target_page)


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
    render_feature_card(
        "ダイエット管理",
        "体重・体脂肪率の記録や日々の変化チェック、目標に合わせた管理に。",
        "assets/home_icons/diet.png",
        "ダイエット管理へ",
        "pages/1_ダイエット管理.py",
        "diet"
    )
    render_feature_card(
        "写真で記録",
        "冷蔵庫や体重計の写真から、食材や数値を読み取って記録に活かせます。",
        "assets/home_icons/photo.png",
        "写真で記録へ",
        "pages/3_写真で記録.py",
        "photo"
    )
    render_feature_card(
        "家計簿",
        "レシート撮影や手入力で、シンプルに記録して見返しやすく管理できます。",
        "assets/home_icons/money.png",
        "家計簿へ",
        "pages/5_家計簿.py",
        "money"
    )
    render_feature_card(
        "アーユルヴェーダ",
        "体質傾向と今の状態をチェックして、食事や過ごし方のヒントに活かせます。",
        "assets/home_icons/ayurveda.png",
        "アーユルヴェーダへ",
        "pages/7_ayurveda.py"
        "ayurveda"
    )

with right:
    render_feature_card(
        "献立・運動プラン",
        "その日の状態や冷蔵庫の食材、目標に合わせて続けやすい提案を作れます。",
        "assets/home_icons/plan.png",
        "献立・運動プランへ",
        "pages/2_献立・運動プラン.py",
        "plan"
    )
    render_feature_card(
        "なんでも相談",
        "夕飯どうする？運動前後は何を食べる？そんな日常の迷いを気軽に相談できます。",
        "assets/home_icons/advice.png",
        "なんでも相談へ",
        "pages/4_なんでも相談.py",
        "advice"
    )
    render_feature_card(
        "初期設定",
        "体型情報、食事スタイル、地域などを登録しておくと他ページにも反映されます。",
        "assets/home_icons/settings.png",
        "初期設定へ",
        "pages/6_初期設定.py",
        "settings"
    )

st.markdown("### まずは、初期設定から始めるのがおすすめです。")
st.markdown(
    '<div class="small-note">食事スタイルや地域、体型情報を登録しておくと、他のページにも反映されて使いやすくなります。</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
