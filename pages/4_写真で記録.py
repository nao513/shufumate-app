# =========================================================
# ShufuMate
# 4_写真で記録.py
# 完全版
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime

from app_core import *


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon=get_page_icon(
        "ShufuMate_home_icons_8/camera.png",
        "📷",
    ),
    layout="centered",
)


# =========================================================
# 共通デザイン
# =========================================================
inject_shufumate_css()


# =========================================================
# ログイン確認
# =========================================================
require_login()

user_id = get_user_id()


# =========================================================
# ページ専用CSS
# =========================================================
st.markdown(
    """
    <style>

    .photo-intro {
        background: rgba(255,250,244,.95);
        border: 1px solid rgba(139,100,72,.12);
        border-radius: 20px;
        padding: 17px 19px;
        color: #6e584c;
        line-height: 1.85;
        margin-bottom: 18px;
    }

    .photo-step {
        background: rgba(255,255,255,.82);
        border: 1px solid rgba(139,100,72,.11);
        border-radius: 18px;
        padding: 15px 17px;
        margin: 8px 0 15px 0;
        color: #665044;
        line-height: 1.75;
    }

    .photo-step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #9b7a69;
        color: white;
        font-weight: 800;
        margin-right: 7px;
    }

    .photo-preview {
        background: rgba(255,255,255,.88);
        border: 1px solid rgba(139,100,72,.11);
        border-radius: 20px;
        padding: 13px;
        margin-bottom: 15px;
    }

    .photo-result-card {
        background: linear-gradient(
            135deg,
            rgba(255,250,243,.98),
            rgba(249,239,227,.98)
        );
        border: 1px solid rgba(139,100,72,.14);
        border-radius: 21px;
        padding: 18px 20px;
        color: #5d473b;
        line-height: 1.9;
        margin-top: 12px;
    }

    .photo-result-title {
        color: #5c4033;
        font-weight: 900;
        margin-bottom: 7px;
    }

    .photo-small {
        color: #917b70;
        font-size: .85rem;
        line-height: 1.7;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(255,255,255,.60);
        border-radius: 18px;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 15px !important;
    }

    div[data-testid="stImage"] img {
        border-radius: 17px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def get_latest_body_values():

    try:

        df = load_diet_dataframe(
            user_id
        )

    except Exception:

        return None, None, None

    if df is None or df.empty:

        return None, None, None

    df = df.sort_values(
        "log_date"
    )

    def latest_number(column):

        if column not in df.columns:
            return None

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        values = values[
            values > 0
        ]

        if values.empty:
            return None

        return float(
            values.iloc[-1]
        )

    return (
        latest_number("weight"),
        latest_number("body_fat"),
        latest_number("muscle_mass"),
    )


def meal_label_to_prefix(
    meal_type
):

    mapping = {
        "朝食": "朝",
        "昼食": "昼",
        "夕食": "夜",
        "間食": "間食",
        "その他": "メモ",
    }

    return mapping.get(
        meal_type,
        "メモ",
    )


def build_meal_memo(
    meal_type,
    food_text,
    note_text,
):

    prefix = meal_label_to_prefix(
        meal_type
    )

    lines = []

    if clean_text(food_text):

        lines.append(
            f"{prefix}: "
            f"{clean_text(food_text)}"
        )

    if clean_text(note_text):

        lines.append(
            f"メモ: "
            f"{clean_text(note_text)}"
        )

    return "\n".join(lines)


# =========================================================
# セッション初期化
# =========================================================
if "photo_record_saved" not in st.session_state:

    st.session_state[
        "photo_record_saved"
    ] = False


# =========================================================
# ページヘッダー
# =========================================================
render_page_header(
    title="写真で記録",
    subtitle=(
        "食事の写真を残して、"
        "かんたんに今日の食事を記録できます。"
    ),
    icon_file="ShufuMate_home_icons_8/camera.png",
    emoji="📷",
)


# =========================================================
# 説明
# =========================================================
st.markdown(
    """
    <div class="photo-intro">
        食事を細かく入力するのが面倒な日は、
        写真を1枚残して簡単に記録。
        食べたものを少し入力しておけば、
        あとの相談にも使いやすくなります。
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# STEP 1
# =========================================================
render_section_header(
    title="食事の写真",
    icon_file="ShufuMate_home_icons_8/camera.png",
    emoji="📷",
)

st.markdown(
    """
    <div class="photo-step">
        <span class="photo-step-number">1</span>
        写真を撮るか、保存してある写真を選びます。
    </div>
    """,
    unsafe_allow_html=True,
)


photo_method = st.radio(
    "写真の選び方",
    [
        "カメラで撮る",
        "写真を選ぶ",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


uploaded_photo = None


if photo_method == "カメラで撮る":

    uploaded_photo = st.camera_input(
        "食事を撮影",
        key="meal_camera",
    )

else:

    uploaded_photo = st.file_uploader(
        "写真を選択",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="meal_photo_upload",
    )


# =========================================================
# 写真プレビュー
# =========================================================
if uploaded_photo is not None:

    st.image(
        uploaded_photo,
        caption="記録する写真",
        use_container_width=True,
    )


# =========================================================
# STEP 2
# =========================================================
render_section_header(
    title="食事の内容",
    icon_file="ShufuMate_home_icons_8/record.png",
    emoji="🍽️",
)

st.markdown(
    """
    <div class="photo-step">
        <span class="photo-step-number">2</span>
        分かる範囲で食べたものを入力します。
        細かい量まで入力しなくても大丈夫です。
    </div>
    """,
    unsafe_allow_html=True,
)


meal_type = st.radio(
    "食事",
    [
        "朝食",
        "昼食",
        "夕食",
        "間食",
        "その他",
    ],
    horizontal=True,
)


food_text = st.text_area(
    "食べたもの",
    placeholder=(
        "例：鮭おにぎり、味噌汁、"
        "納豆、キウイ"
    ),
    height=100,
)


note_text = st.text_area(
    "ひとことメモ",
    placeholder=(
        "例：ヨガのあと。"
        "少しお腹が空いていた。"
    ),
    height=80,
)


# =========================================================
# STEP 3
# =========================================================
render_section_header(
    title="記録する",
    icon_file="ShufuMate_home_icons_8/latest.png",
    emoji="✓",
)

st.markdown(
    """
    <div class="photo-step">
        <span class="photo-step-number">3</span>
        内容を確認して今日の記録に追加します。
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 現在の体組成値
# =========================================================
latest_weight, latest_fat, latest_muscle = (
    get_latest_body_values()
)


with st.expander(
    "一緒に保存される体組成を見る",
    expanded=False,
):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "体重",
            (
                f"{latest_weight:.1f} kg"
                if latest_weight is not None
                else "—"
            ),
        )

    with col2:

        st.metric(
            "体脂肪率",
            (
                f"{latest_fat:.1f} %"
                if latest_fat is not None
                else "—"
            ),
        )

    with col3:

        st.metric(
            "筋肉量",
            (
                f"{latest_muscle:.1f} kg"
                if latest_muscle is not None
                else "—"
            ),
        )


# =========================================================
# 保存
# =========================================================
if st.button(
    "この食事を記録する",
    key="photo_save_button",
    use_container_width=True,
):

    if uploaded_photo is None:

        st.warning(
            "食事の写真を撮るか選んでください。"
        )

    elif not clean_text(food_text):

        st.warning(
            "食べたものを入力してください。"
        )

    else:

        meal_memo = build_meal_memo(
            meal_type,
            food_text,
            note_text,
        )

        log_data = {
            "log_date":
                jst_today_str(),

            "weight":
                (
                    latest_weight
                    if latest_weight is not None
                    else ""
                ),

            "body_fat":
                (
                    latest_fat
                    if latest_fat is not None
                    else ""
                ),

            "muscle_mass":
                (
                    latest_muscle
                    if latest_muscle is not None
                    else ""
                ),

            "meal_memo":
                meal_memo,
        }

        try:

            # ---------------------------------------------
            # DietLogsへ保存
            # ---------------------------------------------
            save_diet_log(
                user_id,
                log_data,
            )


            # ---------------------------------------------
            # 写真情報
            #
            # 現在のapp_core.pyでは
            # PhotoLogsは簡易保存のため、
            # 対応関数がある場合だけ保存
            # ---------------------------------------------
            try:

                save_photo_meal_log(
                    user_id=user_id,
                    log_date=jst_today_str(),
                    meal_type=meal_type,
                    food_text=food_text,
                    note_text=note_text,
                )

            except Exception:

                pass


            st.session_state[
                "photo_record_saved"
            ] = True

            st.session_state[
                "photo_record_meal"
            ] = meal_type

            st.session_state[
                "photo_record_food"
            ] = clean_text(
                food_text
            )

            st.success(
                "食事を記録しました ✨"
            )

        except Exception as e:

            st.error(
                "記録の保存中にエラーが発生しました。"
            )

            st.caption(
                str(e)
            )


# =========================================================
# 保存後
# =========================================================
if st.session_state.get(
    "photo_record_saved"
):

    saved_meal = (
        st.session_state.get(
            "photo_record_meal",
            ""
        )
    )

    saved_food = (
        st.session_state.get(
            "photo_record_food",
            ""
        )
    )

    result_html = (
        '<div class="photo-result-card">'
        '<div class="photo-result-title">'
        '記録できました'
        '</div>'
        f'<strong>{safe_text(saved_meal)}</strong><br>'
        f'{safe_text(saved_food)}'
        '</div>'
    )

    st.markdown(
        result_html,
        unsafe_allow_html=True,
    )


# =========================================================
# AI解析予定
# =========================================================
render_section_header(
    title="これからできること",
    icon_file="ShufuMate_home_icons_8/advice.png",
    emoji="✨",
)

future_html = (
    '<div class="photo-result-card">'
    '<div class="photo-result-title">写真から自動で記録</div>'
    '今後は写真を見て、料理や食材をShufuMateが候補として表示。'
    '内容を確認・修正して、そのまま記録できるようにします。'
    '<br><br>'
    'さらに記録した食事から、'
    '「今日はたんぱく質が少なそう」'
    '「夜は野菜を足そう」'
    'など、次の食事につながる提案もできる形にします。'
    '</div>'
)

st.markdown(
    future_html,
    unsafe_allow_html=True,
)


# =========================================================
# 注意
# =========================================================
note_html = (
    '<div class="photo-small">'
    '写真だけでは食材や量を正確に判断できない場合があります。'
    '自動解析を追加した後も、最終的な食事内容は'
    '確認・修正して保存できる設計にします。'
    '</div>'
)

st.markdown(
    note_html,
    unsafe_allow_html=True,
)
    unsafe_allow_html=True,
)
