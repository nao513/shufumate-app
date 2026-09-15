import streamlit as st
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html
import requests
import io


# =========================================================
# パス・アイコン
# =========================================================
THIS_FILE = Path(__file__).resolve()

if THIS_FILE.parent.name == "pages":
    APP_ROOT = THIS_FILE.parent.parent
else:
    APP_ROOT = THIS_FILE.parent

ICON_DIR = APP_ROOT / "assets" / "icons"


def get_page_icon(filename, fallback="📷"):
    path = ICON_DIR / filename

    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            return fallback

    return fallback


def file_to_base64(path):
    if not path.exists():
        return None

    suffix = path.suffix.lower()

    if suffix == ".png":
        mime = "image/png"
    elif suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    data = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime};base64,{data}"


def load_icon(filename):
    if not filename:
        return None

    path = ICON_DIR / filename

    if path.exists():
        return file_to_base64(path)

    return None


def safe_text(value):
    return html.escape(str(value))


def safe_html_with_br(value):
    return html.escape(
        str(value)
    ).replace("\n", "<br>")


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon=get_page_icon(
        "camera.png",
        "📷"
    ),
    layout="centered",
)


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

/* =========================
   全体
========================= */

.stApp {
    background:
        linear-gradient(
            180deg,
            #fffaf4 0%,
            #fff4e8 45%,
            #fffaf4 100%
        );
}

.block-container {
    max-width: 820px;
    padding-top: 3.8rem;
    padding-bottom: 3rem;
}


/* =========================
   ページTOP
========================= */

.top-card {
    background: #ffffff;
    border-radius: 26px;
    padding: 22px 20px;
    box-shadow:
        0 8px 24px
        rgba(96, 65, 45, 0.10);
    border:
        1px solid
        rgba(139, 100, 72, 0.12);
    margin-bottom: 20px;
}

.page-head {
    display: flex;
    align-items: center;
    gap: 16px;
}

.page-head-icon {
    width: 78px;
    min-width: 78px;
    height: 78px;

    border-radius: 22px;

    background: #fff8ef;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 4px 12px
        rgba(96, 65, 45, 0.09);

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: hidden;
}

.page-head-icon img {
    width: 66px;
    height: 66px;
    object-fit: contain;
}

.page-title {
    font-size: 1.75rem;
    font-weight: 900;
    color: #5c4033;
    margin-bottom: 5px;
}

.page-subtitle {
    font-size: 0.95rem;
    color: #7b6658;
    line-height: 1.7;
    font-weight: 600;
}


/* =========================
   セクション
========================= */

.section-head {
    display: flex;
    align-items: center;
    gap: 12px;

    margin:
        28px 0 12px 0;
}

.section-head-icon {
    width: 52px;
    min-width: 52px;
    height: 52px;

    border-radius: 17px;

    background: #ffffff;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 4px 12px
        rgba(96, 65, 45, 0.09);

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: hidden;
}

.section-head-icon img {
    width: 43px;
    height: 43px;
    object-fit: contain;
}

.section-head-title {
    font-size: 1.2rem;
    font-weight: 900;
    color: #5c4033;
}


/* =========================
   カード
========================= */

.soft-card {
    background: #fffdf8;

    border-radius: 20px;

    padding: 16px 18px;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    color: #6b4c3b;

    font-size: 0.94rem;
    line-height: 1.75;

    margin-bottom: 16px;
}


.ai-card {
    background: #f2f8ef;

    border-radius: 22px;

    padding: 18px;

    border:
        1px solid
        rgba(78, 140, 82, 0.16);

    color: #426047;

    line-height: 1.8;

    margin:
        10px 0 20px 0;
}


.latest-card {
    background: #ffffff;

    border-radius: 22px;

    padding: 18px;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 5px 16px
        rgba(96, 65, 45, 0.07);

    color: #5c4033;

    line-height: 1.8;

    margin-bottom: 14px;
}


.message-card {
    background: #fff8ef;

    border-radius: 20px;

    padding: 17px;

    color: #7b6658;

    font-size: 0.92rem;
    line-height: 1.8;

    border:
        1px solid
        rgba(139, 100, 72, 0.10);

    margin-top: 28px;
}


/* =========================
   Streamlit入力
========================= */

div[data-testid="stRadio"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label {
    color: #5c4033;
    font-weight: 700;
}


/* =========================
   ボタン
========================= */

.stButton > button {
    background-color: #9a786b;
    color: #ffffff;

    border: none;
    border-radius: 14px;

    min-height: 48px;

    font-size: 1rem;
    font-weight: 800;

    box-shadow:
        0 3px 8px
        rgba(96, 65, 45, 0.10);
}

.stButton > button:hover {
    background-color: #806055;
    color: #ffffff;
    border: none;
}


/* =========================
   画像
========================= */

div[data-testid="stImage"] img {
    border-radius: 20px;
}


/* =========================
   スマホ
========================= */

@media (max-width: 640px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.4rem;
    }

    .top-card {
        padding: 17px 15px;
    }

    .page-head-icon {
        width: 64px;
        min-width: 64px;
        height: 64px;
        border-radius: 19px;
    }

    .page-head-icon img {
        width: 54px;
        height: 54px;
    }

    .page-title {
        font-size: 1.45rem;
    }

    .page-subtitle {
        font-size: 0.87rem;
    }

    .section-head-icon {
        width: 46px;
        min-width: 46px;
        height: 46px;
    }

    .section-head-icon img {
        width: 38px;
        height: 38px;
    }

    .section-head-title {
        font-size: 1.08rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# デザイン関数
# =========================================================
def render_page_header(
    title,
    subtitle,
    icon_file
):
    icon_src = load_icon(
        icon_file
    )

    if icon_src:
        icon_html = (
            f'<img src="{icon_src}" '
            f'alt="{safe_text(title)}">'
        )
    else:
        icon_html = "📷"

    st.markdown(
        f"""
<div class="top-card">
    <div class="page-head">

        <div class="page-head-icon">
            {icon_html}
        </div>

        <div>
            <div class="page-title">
                {safe_text(title)}
            </div>

            <div class="page-subtitle">
                {safe_html_with_br(subtitle)}
            </div>
        </div>

    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_section_header(
    title,
    icon_file
):
    icon_src = load_icon(
        icon_file
    )

    if icon_src:
        icon_html = (
            f'<img src="{icon_src}" '
            f'alt="{safe_text(title)}">'
        )
    else:
        icon_html = ""

    st.markdown(
        f"""
<div class="section-head">

    <div class="section-head-icon">
        {icon_html}
    </div>

    <div class="section-head-title">
        {safe_text(title)}
    </div>

</div>
""",
        unsafe_allow_html=True,
    )


def render_soft_card(text):
    st.markdown(
        f"""
<div class="soft-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_ai_card(text):
    st.markdown(
        f"""
<div class="ai-card">
    {safe_html_with_br(text)}
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# ログイン
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# ページTOP
# =========================================================
render_page_header(
    title="写真で記録",
    subtitle=(
        "食事の写真を撮るだけ。"
        "AIが内容を確認して、"
        "かんたんに記録できます。"
    ),
    icon_file="camera.png",
)


render_soft_card(
    "きれいに撮らなくても大丈夫です。"
    "食事全体が写るように撮影すると、"
    "内容を確認しやすくなります。"
)


# =========================================================
# 写真を選ぶ
# =========================================================
render_section_header(
    "写真を選ぶ",
    "camera.png",
)


input_mode = st.radio(
    "入力方法",
    [
        "アップロード",
        "カメラ",
    ],
    horizontal=True,
    key="photo_input_mode",
)


img = None


if input_mode == "アップロード":

    img = st.file_uploader(
        "写真を選択",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="meal_photo_upload",
    )

else:

    img = st.camera_input(
        "撮影する",
        key="meal_photo_camera",
    )


if img:

    st.image(
        img,
        caption="選択した写真",
        use_container_width=True,
    )


# =========================================================
# AI用画像変換
# =========================================================
def encode_image(file):

    image = Image.open(file)

    # PNGなどのRGBA対策
    if image.mode != "RGB":
        image = image.convert("RGB")

    buf = io.BytesIO()

    image.save(
        buf,
        format="JPEG",
        quality=90,
    )

    return base64.b64encode(
        buf.getvalue()
    ).decode("utf-8")


# =========================================================
# AI解析
# =========================================================
if img:

    render_section_header(
        "食事をチェック",
        "advice.png",
    )

    if st.button(
        "AIで食事をチェック",
        use_container_width=True,
        key="photo_ai_check",
    ):

        with st.spinner(
            "食事を確認しています..."
        ):

            try:

                base64_image = encode_image(
                    img
                )

                headers = {
                    "Authorization":
                        f"Bearer {st.secrets['OPENAI_API_KEY']}",
                    "Content-Type":
                        "application/json",
                }

                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "この食事写真を確認して、"
                                        "次の4項目を日本語で"
                                        "簡潔に答えてください。\n\n"
                                        "1. 写っている食事\n"
                                        "2. 食事バランス\n"
                                        "3. 良いところと整えたいところ\n"
                                        "4. 100点満点での目安\n\n"
                                        "写真だけでは判断できない"
                                        "内容は断定しないでください。"
                                    ),
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url":
                                            "data:image/jpeg;base64,"
                                            + base64_image
                                    },
                                },
                            ],
                        }
                    ],
                }

                res = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )

                if res.status_code == 200:

                    ai_result = (
                        res.json()
                        ["choices"][0]
                        ["message"]["content"]
                    )

                    st.session_state[
                        "photo_ai_result"
                    ] = ai_result

                    st.session_state[
                        "auto_food"
                    ] = ai_result

                else:

                    st.error(
                        "AI分析に失敗しました。"
                        "時間をおいてもう一度"
                        "お試しください。"
                    )

            except Exception:

                st.error(
                    "AI分析中にエラーが"
                    "発生しました。"
                )


# =========================================================
# AI結果
# =========================================================
if st.session_state.get(
    "photo_ai_result"
):

    render_section_header(
        "AIからの食事チェック",
        "advice.png",
    )

    render_ai_card(
        st.session_state[
            "photo_ai_result"
        ]
    )


# =========================================================
# 食事内容
# =========================================================
render_section_header(
    "食事内容",
    "record.png",
)


auto_meal = detect_meal_type_by_time(
    jst_now()
)

meal_options = [
    "朝",
    "昼",
    "夜",
    "間食",
]


meal_type = st.radio(
    "食事区分",
    meal_options,
    index=(
        meal_options.index(auto_meal)
        if auto_meal in meal_options
        else 0
    ),
    horizontal=True,
    key="photo_meal_type",
)


default_text = st.session_state.get(
    "auto_food",
    "",
)


food_text = st.text_area(
    "食事内容",
    value=default_text,
    placeholder=(
        "例：鮭おにぎり、"
        "鶏むね肉、サラダ、味噌汁"
    ),
    height=130,
    key="photo_food_text",
)


# =========================================================
# 保存
# =========================================================
if st.button(
    "この食事を記録する",
    use_container_width=True,
    key="photo_save_button",
):

    if img is None:

        st.warning(
            "写真を選択または撮影してください。"
        )

    else:

        try:

            save_photo_meal_log(
                user_id=user_id,
                meal_type=meal_type,
                food_text=food_text,
                image_file=img,
            )

            st.success(
                "食事を記録しました。"
            )

        except Exception:

            st.error(
                "保存中にエラーが発生しました。"
            )


# =========================================================
# 最新記録
# =========================================================
render_section_header(
    "最新の写真記録",
    "latest.png",
)


try:

    logs = load_photo_logs(
        user_id
    )

except Exception:

    logs = []


if logs:

    latest = logs[-1]

    log_date = latest.get(
        "log_date",
        ""
    )

    latest_meal_type = latest.get(
        "meal_type",
        ""
    )

    latest_food = latest.get(
        "food_text",
        ""
    )


    st.markdown(
        f"""
<div class="latest-card">

<strong>記録日</strong><br>
{safe_text(log_date)}

<br><br>

<strong>食事区分</strong><br>
{safe_text(latest_meal_type)}

<br><br>

<strong>食事内容</strong><br>
{safe_html_with_br(latest_food)}

</div>
""",
        unsafe_allow_html=True,
    )


    if latest.get(
        "image_bytes"
    ):

        st.image(
            latest["image_bytes"],
            use_container_width=True,
        )

else:

    render_soft_card(
        "写真の記録はまだありません。"
        "最初の1枚を記録してみましょう。"
    )


# =========================================================
# メッセージ
# =========================================================
st.markdown(
    """
<div class="message-card">
    食事は完璧じゃなくて大丈夫。<br>
    写真を残すだけでも、
    毎日の変化を振り返る大切な記録になります。
</div>
""",
    unsafe_allow_html=True,
)
