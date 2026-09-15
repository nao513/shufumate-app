import streamlit as st
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html
import requests
import io
import textwrap


# =========================================================
# パス設定
# =========================================================
THIS_FILE = Path(__file__).resolve()

if THIS_FILE.parent.name == "pages":
    APP_ROOT = THIS_FILE.parent.parent
else:
    APP_ROOT = THIS_FILE.parent

ICON_DIR = APP_ROOT / "assets" / "icons"


# =========================================================
# アイコン関数
# =========================================================
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

/* -----------------------------------------
   全体
----------------------------------------- */

.stApp {
    background:
        linear-gradient(
            180deg,
            #fffaf4 0%,
            #fff5e9 48%,
            #fffaf4 100%
        );
}

.block-container {
    max-width: 820px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}


/* -----------------------------------------
   ページヘッダー
----------------------------------------- */

.top-card {
    background: #ffffff;

    border-radius: 26px;

    padding: 22px 22px;

    margin-bottom: 18px;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 8px 24px
        rgba(96, 65, 45, 0.09);
}

.page-head {
    display: flex;
    align-items: center;
    gap: 17px;
}

.page-head-icon {
    width: 78px;
    min-width: 78px;
    height: 78px;

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: hidden;

    border-radius: 21px;

    background: #fff8ef;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 4px 12px
        rgba(96, 65, 45, 0.08);
}

.page-head-icon img {
    width: 72px;
    height: 72px;
    object-fit: cover;
    border-radius: 18px;
}

.page-title {
    color: #5c4033;

    font-size: 1.75rem;
    font-weight: 900;

    line-height: 1.3;

    margin-bottom: 5px;
}

.page-subtitle {
    color: #7b6658;

    font-size: 0.95rem;
    font-weight: 600;

    line-height: 1.7;
}


/* -----------------------------------------
   案内カード
----------------------------------------- */

.soft-card {
    background: #fffdf8;

    border:
        1px solid
        rgba(139, 100, 72, 0.14);

    border-radius: 18px;

    padding: 14px 17px;

    margin:
        0 0 22px 0;

    color: #755544;

    font-size: 0.92rem;

    line-height: 1.75;
}


/* -----------------------------------------
   セクション見出し
----------------------------------------- */

.section-head {
    display: flex;
    align-items: center;

    gap: 12px;

    margin:
        28px 0 12px 0;
}

.section-head-icon {
    width: 50px;
    min-width: 50px;
    height: 50px;

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: hidden;

    border-radius: 15px;

    background: #ffffff;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    box-shadow:
        0 3px 10px
        rgba(96, 65, 45, 0.08);
}

.section-head-icon img {
    width: 46px;
    height: 46px;

    object-fit: cover;

    border-radius: 13px;
}

.section-head-title {
    color: #5c4033;

    font-size: 1.22rem;
    font-weight: 900;
}


/* -----------------------------------------
   AI結果
----------------------------------------- */

.ai-card {
    background: #f2f8ef;

    border:
        1px solid
        rgba(79, 133, 81, 0.18);

    border-radius: 20px;

    padding: 18px;

    margin:
        8px 0 18px 0;

    color: #466148;

    font-size: 0.94rem;

    line-height: 1.85;
}


/* -----------------------------------------
   最新記録
----------------------------------------- */

.latest-card {
    background: #ffffff;

    border:
        1px solid
        rgba(139, 100, 72, 0.12);

    border-radius: 20px;

    padding: 18px;

    margin-bottom: 15px;

    color: #5c4033;

    font-size: 0.94rem;

    line-height: 1.8;

    box-shadow:
        0 4px 14px
        rgba(96, 65, 45, 0.06);
}

.latest-label {
    color: #9a786b;

    font-size: 0.78rem;
    font-weight: 800;

    margin-bottom: 2px;
}

.latest-value {
    color: #4e3a31;

    font-size: 0.96rem;

    margin-bottom: 14px;
}


/* -----------------------------------------
   最後のメッセージ
----------------------------------------- */

.message-card {
    background: #fff8ef;

    border:
        1px solid
        rgba(139, 100, 72, 0.11);

    border-radius: 18px;

    padding: 16px 18px;

    margin-top: 30px;

    color: #7b6658;

    font-size: 0.9rem;

    line-height: 1.8;
}


/* -----------------------------------------
   入力
----------------------------------------- */

div[data-testid="stRadio"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stCameraInput"] label {

    color: #5c4033;

    font-weight: 700;
}


/* -----------------------------------------
   テキストエリア
----------------------------------------- */

textarea {
    border-radius: 14px !important;
}


/* -----------------------------------------
   ボタン
----------------------------------------- */

.stButton > button {

    background-color: #9a786b;

    color: #ffffff;

    border: none;

    border-radius: 14px;

    min-height: 48px;

    font-size: 0.96rem;

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


/* -----------------------------------------
   写真
----------------------------------------- */

div[data-testid="stImage"] img {
    border-radius: 18px;
}


/* -----------------------------------------
   アップローダー
----------------------------------------- */

div[data-testid="stFileUploader"] section {

    border-radius: 16px;

    background: #f7f8fb;
}


/* -----------------------------------------
   区切り
----------------------------------------- */

.page-divider {

    height: 1px;

    background:
        rgba(139, 100, 72, 0.18);

    margin:
        30px 0 8px 0;
}


/* -----------------------------------------
   スマホ
----------------------------------------- */

@media (max-width: 640px) {

    .block-container {

        padding-top: 1.3rem;

        padding-left: 1rem;
        padding-right: 1rem;
    }

    .top-card {

        padding: 16px;
        border-radius: 22px;
    }

    .page-head {

        gap: 12px;
    }

    .page-head-icon {

        width: 64px;
        min-width: 64px;
        height: 64px;

        border-radius: 18px;
    }

    .page-head-icon img {

        width: 58px;
        height: 58px;
    }

    .page-title {

        font-size: 1.42rem;
    }

    .page-subtitle {

        font-size: 0.84rem;
    }

    .section-head-icon {

        width: 45px;
        min-width: 45px;
        height: 45px;
    }

    .section-head-icon img {

        width: 41px;
        height: 41px;
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


    html_code = f"""
<div class="top-card">
<div class="page-head">
<div class="page-head-icon">{icon_html}</div>
<div>
<div class="page-title">{safe_text(title)}</div>
<div class="page-subtitle">{safe_html_with_br(subtitle)}</div>
</div>
</div>
</div>
"""

    st.markdown(
        textwrap.dedent(
            html_code
        ).strip(),
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


    html_code = f"""
<div class="section-head">
<div class="section-head-icon">{icon_html}</div>
<div class="section-head-title">{safe_text(title)}</div>
</div>
"""

    st.markdown(
        textwrap.dedent(
            html_code
        ).strip(),
        unsafe_allow_html=True,
    )


def render_soft_card(
    text
):

    html_code = f"""
<div class="soft-card">{safe_html_with_br(text)}</div>
"""

    st.markdown(
        textwrap.dedent(
            html_code
        ).strip(),
        unsafe_allow_html=True,
    )


def render_ai_card(
    text
):

    html_code = f"""
<div class="ai-card">{safe_html_with_br(text)}</div>
"""

    st.markdown(
        textwrap.dedent(
            html_code
        ).strip(),
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
        "食事の写真から、"
        "かんたんに記録できます。"
    ),
    icon_file="camera.png",
)


render_soft_card(
    "食事全体が写るように撮影すると、"
    "内容を確認しやすくなります。"
    "きれいに撮れなくても大丈夫です。"
)


# =========================================================
# 写真を選ぶ
# =========================================================
render_section_header(
    title="写真を選ぶ",
    icon_file="camera.png",
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
        "写真を撮る",
        key="meal_photo_camera",
    )


# =========================================================
# 写真表示
# =========================================================
if img is not None:

    st.image(
        img,
        caption="選択した写真",
        use_container_width=True,
    )


# =========================================================
# AI画像変換
# =========================================================
def encode_image(file):

    image = Image.open(
        file
    )

    if image.mode != "RGB":

        image = image.convert(
            "RGB"
        )

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
if img is not None:

    render_section_header(
        title="食事をチェック",
        icon_file="advice.png",
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

                    "model":
                        "gpt-4o-mini",

                    "messages": [

                        {

                            "role":
                                "user",

                            "content": [

                                {

                                    "type":
                                        "text",

                                    "text":
                                        (
                                            "この食事写真を確認してください。\n\n"

                                            "次の4項目を、"
                                            "日本語で簡潔に答えてください。\n\n"

                                            "1. 写っている食事\n"
                                            "2. 食事バランス\n"
                                            "3. 良いところと整えたいところ\n"
                                            "4. 100点満点での目安\n\n"

                                            "写真から分からないことは"
                                            "断定しないでください。"
                                        ),
                                },

                                {

                                    "type":
                                        "image_url",

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
                        "時間をおいて、もう一度お試しください。"
                    )


            except Exception:

                st.error(
                    "AI分析中にエラーが発生しました。"
                )


# =========================================================
# AI結果表示
# =========================================================
if st.session_state.get(
    "photo_ai_result"
):

    render_section_header(
        title="食事チェック",
        icon_file="advice.png",
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
    title="食事内容",
    icon_file="record.png",
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


if auto_meal in meal_options:

    meal_index = meal_options.index(
        auto_meal
    )

else:

    meal_index = 0


meal_type = st.radio(
    "食事区分",
    meal_options,
    index=meal_index,
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


            # 保存後にAI結果を残す
            # 写真を変えたときに再チェックできます


        except Exception:

            st.error(
                "保存中にエラーが発生しました。"
            )


# =========================================================
# 区切り
# =========================================================
st.markdown(
    '<div class="page-divider"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# 最新の写真記録
# =========================================================
render_section_header(
    title="最新の写真記録",
    icon_file="latest.png",
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


    latest_html = f"""
<div class="latest-card">

<div class="latest-label">
記録日
</div>

<div class="latest-value">
{safe_text(log_date)}
</div>

<div class="latest-label">
食事区分
</div>

<div class="latest-value">
{safe_text(latest_meal_type)}
</div>

<div class="latest-label">
食事内容
</div>

<div class="latest-value">
{safe_html_with_br(latest_food)}
</div>

</div>
"""


    st.markdown(
        textwrap.dedent(
            latest_html
        ).strip(),
        unsafe_allow_html=True,
    )


    if latest.get(
        "image_bytes"
    ):

        st.image(
            latest[
                "image_bytes"
            ],
            use_container_width=True,
        )


else:

    render_soft_card(
        "写真の記録はまだありません。"
        "最初の食事を記録してみましょう。"
    )


# =========================================================
# 最後のメッセージ
# =========================================================
message_html = """
<div class="message-card">
食事は完璧じゃなくて大丈夫です。<br>
写真を残すだけでも、
毎日の食事を振り返る記録になります。
</div>
"""


st.markdown(
    textwrap.dedent(
        message_html
    ).strip(),
    unsafe_allow_html=True,
)
