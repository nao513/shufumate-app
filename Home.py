import streamlit as st
import base64
from pathlib import Path
from app_core import *

st.set_page_config(
    page_title="ShufuMate｜主婦の味方アプリ",
    layout="wide"
)

ensure_headers()
reload_user_data_if_needed()


def img_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode()


def show_top_image(path: str):
    img_b64 = img_to_base64(path)

    if not img_b64:
        st.warning(f"画像が見つかりません: {path}")
        return

    st.markdown(
        f'''
        <div class="top-visual-wrap">
            <img src="data:image/png;base64,{img_b64}">
        </div>
        ''',
        unsafe_allow_html=True
    )


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
    max-width: 980px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

.home-shell {
    background: #f8f3ec;
    border: 1px solid #e7ddd2;
    border-radius: 38px;
    padding: 1.8rem 1.8rem 2.2rem 1.8rem;
    box-shadow: 0 10px 28px rgba(91, 58, 41, 0.05);
}

/* ---------- 上部画像 ---------- */

.top-visual-wrap {
    margin-bottom: 1.35rem;
    overflow: hidden;
    border-radius: 26px;
}

.top-visual-wrap img {
    display: block;
    width: 100%;
    height: auto;
}

/* ---------- メインコピー ---------- */

.main-copy {
    text-align: center;
    color: #5b3a29;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.55;
    margin-top: 0.2rem;
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

/* ---------- カード ---------- */

.feature-title-wrap {
    min-height: 68px;
    display: flex;
    align-items: flex-start;
}

.feature-title {
    margin: 0;
    line-height: 1.2;
    color: #2f3446;
    font-size: 1.72rem;
    font-weight: 800;
    white-space: nowrap;
    letter-spacing: 0.01em;
}

.feature-desc {
    color: #4b5563;
    font-size: 0.98rem;
    line-height: 1.85;
    min-height: 122px;
}

.feature-image-box {
    background: #efe7dc;
    border-radius: 18px;
    padding: 12px;
    height: 120px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.feature-image-plain {
    height: 120px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.feature-image-box img,
.feature-image-plain img {
    max-width: 100%;
    height: auto;
    display: block;
    object-fit: contain;
}

/* ---------- ボタン ---------- */

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

/* ---------- 下部案内 ---------- */

.small-note-wrap {
    margin-top: 1.4rem;
    background: #fbf6ef;
    border: 1px solid #eadfce;
    border-radius: 20px;
    padding: 1rem 1.1rem;
}

.small-note-title {
    color: #5b3a29;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

.small-note {
    color: #7a6556;
    font-size: 0.96rem;
    line-height: 1.8;
}

/* ---------- レスポンシブ ---------- */

@media (max-width: 1200px) {
    .feature-title {
        font-size: 1.55rem;
    }
}

@media (max-width: 860px) {
    .feature-title-wrap {
        min-height: auto;
    }

    .feature-title {
        white-space: normal;
        font-size: 1.48rem;
    }

    .feature-desc {
        min-height: auto;
    }
}
</style>
""", unsafe_allow_html=True)


def render_feature_card(
    title,
    desc,
    image_path,
    button_label,
    target_page,
    key_prefix,
    image_width=135,
    image_bg=False
):
    img_b64 = img_to_base64(image_path)

    with st.container(border=True):
        c1, c2 = st.columns([2.6, 1.0], vertical_alignment="top")

        with c1:
            st.markdown(
                f"""
                <div class="feature-title-wrap">
                    <h3 class="feature-title">{title}</h3>
                </div>
                <div class="feature-desc">
                    {desc}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            if image_bg:
                st.markdown(
                    f"""
                    <div class="feature-image-box">
                        <img src="data:image/png;base64,{img_b64}" style="width:{image_width}px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="feature-image-plain">
                        <img src="data:image/png;base64,{img_b64}" style="width:{image_width}px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if st.button(button_label, key=f"{key_prefix}_btn", use_container_width=True):
            st.switch_page(target_page)


st.markdown('<div class="home-shell">', unsafe_allow_html=True)

show_top_image("assets/home_icons/top/top_visual.png")

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
        "体重・体脂肪率・筋肉量の記録や日々の変化チェック、目標に合わせた管理に。",
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
        "8項目から体質傾向をチェックします。チェックが多い体質が、今の自分に近いタイプです。",
        "assets/home_icons/ayurveda.png",
        "アーユルヴェーダへ",
        "pages/7_アーユルヴェーダ.py",
        "ayurveda"
    )

    render_feature_card(
        "教育費・人生設計",
        "子どもの人数や教育方針に合わせて、教育費の目安をざっくり確認できます。",
        "assets/home_icons/education.png",
        "教育費・人生設計へ",
        "pages/9_教育費・人生設計.py",
        "education"
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
        "体型情報、食事スタイル、地域、体質などを登録しておくと他ページにも反映されます。",
        "assets/home_icons/settings.png",
        "初期設定へ",
        "pages/6_初期設定.py",
        "settings"
    )

    render_feature_card(
        "スケジュール",
        "予定管理や生活リズムの目安を見ながら、毎日の流れを整えやすくします。",
        "assets/home_icons/schedule.png",
        "スケジュールへ",
        "pages/8_スケジュール.py",
        "schedule"
    )

    render_feature_card(
        "お得情報",
        "地域設定に合わせて、暮らしや家計に役立つお得情報を見やすく広げていきます。",
        "assets/home_icons/deals.png",
        "お得情報へ",
        "pages/10_お得情報.py",
        "deals"
    )

st.markdown("""
<div class="small-note-wrap">
    <div class="small-note-title">まずは、初期設定から始めるのがおすすめです。</div>
    <div class="small-note">
        体型情報、食事スタイル、地域、体質などを登録しておくと、
        献立・相談・記録ページにも反映されて使いやすくなります。
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
