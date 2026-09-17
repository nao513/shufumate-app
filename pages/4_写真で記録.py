# =========================================================
# ShufuMate
# pages/4_写真で記録.py
# 最終完全版
# =========================================================

import html

import pandas as pd
import streamlit as st

from app_core import (
    require_login,
    get_user_id,
    get_page_icon,
    inject_shufumate_css,
    render_page_header,
    render_section_header,
    load_diet_dataframe,
    save_photo_meal_log,
    clean_text,
    jst_today_str,
)


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


.photo-result-card {
    background:
        linear-gradient(
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
    margin-bottom: 14px;
}


.photo-result-title {
    color: #5c4033;
    font-weight: 900;
    font-size: 1.05rem;
    margin-bottom: 7px;
}


.photo-body-note {
    background: rgba(247,250,243,.88);
    border: 1px solid rgba(92,130,83,.12);
    border-radius: 16px;
    padding: 13px 15px;
    color: #61705d;
    font-size: .88rem;
    line-height: 1.7;
    margin-top: 10px;
}


.photo-small {
    color: #917b70;
    font-size: .85rem;
    line-height: 1.7;
    margin-top: 10px;
    margin-bottom: 18px;
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


div[data-testid="stExpander"] {
    background: rgba(255,255,255,.60);
    border: 1px solid rgba(139,100,72,.10);
    border-radius: 17px;
}


@media (max-width: 640px) {

    .photo-intro {
        padding: 15px 16px;
    }

    .photo-step {
        padding: 14px 15px;
    }

    .photo-result-card {
        padding: 17px 18px;
    }

}

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 補助関数
# =========================================================
def safe_html(value):
    """
    HTML表示用。
    ユーザー入力を安全に表示する。
    """
    return html.escape(
        str(value or "")
    )


def safe_html_with_br(value):
    """
    改行を保持して安全にHTML表示する。
    """
    return safe_html(value).replace(
        "\n",
        "<br>"
    )


def latest_body_values():
    """
    DietLogsから最新の有効な
    体重・体脂肪率・筋肉量を取得する。

    ※表示専用。
    写真保存時にはDietLogsへ再保存しない。
    """

    try:
        df = load_diet_dataframe(
            user_id
        )

    except Exception:
        return None, None, None


    if (
        df is None
        or df.empty
    ):
        return None, None, None


    if "log_date" in df.columns:

        df = df.sort_values(
            "log_date"
        ).reset_index(
            drop=True
        )


    def get_latest(column):

        if column not in df.columns:
            return None

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        values = values.dropna()

        values = values[
            values > 0
        ]

        if values.empty:
            return None

        return float(
            values.iloc[-1]
        )


    return (
        get_latest("weight"),
        get_latest("body_fat"),
        get_latest("muscle_mass"),
    )


# =========================================================
# セッション初期化
# =========================================================
if "photo_record_saved" not in st.session_state:
    st.session_state[
        "photo_record_saved"
    ] = False


if "photo_record_meal" not in st.session_state:
    st.session_state[
        "photo_record_meal"
    ] = ""


if "photo_record_food" not in st.session_state:
    st.session_state[
        "photo_record_food"
    ] = ""


if "photo_record_note" not in st.session_state:
    st.session_state[
        "photo_record_note"
    ] = ""


if "photo_record_date" not in st.session_state:
    st.session_state[
        "photo_record_date"
    ] = ""


# =========================================================
# ヘッダー
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
# ページ説明
# =========================================================
intro_html = (
    '<div class="photo-intro">'
    '食事を細かく入力するのが面倒な日は、'
    '写真を1枚残して簡単に記録。'
    '食べたものを少し入力しておけば、'
    'あとの相談にも使いやすくなります。'
    '</div>'
)

st.markdown(
    intro_html,
    unsafe_allow_html=True,
)


# =========================================================
# STEP 1
# 写真
# =========================================================
st.markdown(
    '<div style="color:#5c4033; font-size:1.35rem; '
    'font-weight:900; margin:28px 0 14px;">'
    '食事の写真'
    '</div>',
    unsafe_allow_html=True,
)


step1_html = (
    '<div class="photo-step">'
    '写真を撮るか、保存してある写真を選びます。'
    '</div>'
)

st.markdown(
    step1_html,
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
    key="photo_method",
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
# 食事内容
# =========================================================
st.markdown(
    '<div style="color:#5c4033; font-size:1.35rem; '
    'font-weight:900; margin:28px 0 14px;">'
    '食事の内容'
    '</div>',
    unsafe_allow_html=True,
)

step2_html = (
    '<div class="photo-step">'
    '分かる範囲で食べたものを入力します。'
    '細かい量まで入力しなくても大丈夫です。'
    '</div>'
)

st.markdown(
    step2_html,
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
    key="photo_meal_type",
)


food_text = st.text_area(
    "食べたもの",
    placeholder=(
        "例：鮭おにぎり、味噌汁、"
        "納豆、キウイ"
    ),
    height=100,
    key="photo_food_text",
)


note_text = st.text_area(
    "ひとことメモ",
    placeholder=(
        "例：ヨガのあと。"
        "少しお腹が空いていた。"
    ),
    height=80,
    key="photo_note_text",
)


# =========================================================
# STEP 3
# 保存
# =========================================================
st.markdown(
    '<div style="color:#5c4033; font-size:1.35rem; '
    'font-weight:900; margin:28px 0 14px;">'
    '記録する'
    '</div>',
    unsafe_allow_html=True,
)


step3_html = (
    '<div class="photo-step">'
    '内容を確認して食事の記録として保存します。'
    '</div>'
)

st.markdown(
    step3_html,
    unsafe_allow_html=True,
)


# =========================================================
# 最新体組成
# 表示のみ
# =========================================================
latest_weight, latest_fat, latest_muscle = (
    latest_body_values()
)


with st.expander(
    "今日の体組成を見る",
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


    body_note_html = (
        '<div class="photo-body-note">'
        'ここに表示している体組成は、'
        '「記録する」に保存されている最新データです。'
        '写真を保存しても、体組成を重複して保存しません。'
        '</div>'
    )

    st.markdown(
        body_note_html,
        unsafe_allow_html=True,
    )


# =========================================================
# 保存ボタン
# =========================================================
if st.button(
    "この食事を記録する",
    key="photo_save_button",
    use_container_width=True,
):

    # -----------------------------------------
    # 入力確認
    # -----------------------------------------
    if uploaded_photo is None:

        st.warning(
            "食事の写真を撮るか選んでください。"
        )


    elif not clean_text(food_text):

        st.warning(
            "食べたものを入力してください。"
        )


    else:

        save_date = jst_today_str()

        cleaned_food = clean_text(
            food_text
        )

        cleaned_note = clean_text(
            note_text
        )


        try:

            # =====================================
            # 写真記録として保存
            #
            # DietLogsには保存しない。
            # 体組成の重複を防止する。
            # =====================================
            save_photo_meal_log(
                user_id=user_id,
                log_date=save_date,
                meal_type=meal_type,
                food_text=cleaned_food,
                note_text=cleaned_note,
            )


            # =====================================
            # 保存結果表示用
            # =====================================
            st.session_state[
                "photo_record_saved"
            ] = True

            st.session_state[
                "photo_record_meal"
            ] = meal_type

            st.session_state[
                "photo_record_food"
            ] = cleaned_food

            st.session_state[
                "photo_record_note"
            ] = cleaned_note

            st.session_state[
                "photo_record_date"
            ] = save_date


            st.success(
                "食事を記録しました ✨"
            )


        except Exception as e:

            st.error(
                "食事記録の保存中に"
                "エラーが発生しました。"
            )

            st.caption(
                f"エラー内容：{e}"
            )


# =========================================================
# 保存結果
# =========================================================
if st.session_state.get(
    "photo_record_saved",
    False,
):

    saved_date = clean_text(
        st.session_state.get(
            "photo_record_date",
            "",
        )
    )

    saved_meal = clean_text(
        st.session_state.get(
            "photo_record_meal",
            "",
        )
    )

    saved_food = clean_text(
        st.session_state.get(
            "photo_record_food",
            "",
        )
    )

    saved_note = clean_text(
        st.session_state.get(
            "photo_record_note",
            "",
        )
    )


    result_parts = []


    if saved_date:

        result_parts.append(
            f'<div>{safe_html(saved_date)}</div>'
        )


    if saved_meal:

        result_parts.append(
            '<div>'
            f'<strong>{safe_html(saved_meal)}</strong>'
            '</div>'
        )


    if saved_food:

        result_parts.append(
            '<div>'
            f'{safe_html_with_br(saved_food)}'
            '</div>'
        )


    if saved_note:

        result_parts.append(
            '<div style="margin-top:8px;">'
            'メモ：'
            f'{safe_html_with_br(saved_note)}'
            '</div>'
        )


    result_html = (
        '<div class="photo-result-card">'
        '<div class="photo-result-title">'
        '記録できました'
        '</div>'
        + "".join(result_parts)
        + '</div>'
    )


    st.markdown(
        result_html,
        unsafe_allow_html=True,
    )


# =========================================================
# これからできること
# =========================================================
render_section_header(
    title="これからできること",
    icon_file="ShufuMate_home_icons_8/advice.png",
    emoji="✨",
)


future_html = (
    '<div class="photo-result-card">'
    '<div class="photo-result-title">'
    '写真から自動で記録'
    '</div>'
    '今後は写真を見て、料理や食材を'
    'ShufuMateが候補として表示。'
    '内容を確認・修正して、'
    'そのまま記録できるようにします。'
    '<br><br>'
    'さらに記録した食事から、'
    '「今日はたんぱく質が少なそう」'
    '「夜は野菜を足そう」など、'
    '次の食事につながる提案も'
    'できる形にします。'
    '</div>'
)

st.markdown(
    future_html,
    unsafe_allow_html=True,
)


# =========================================================
# 注意書き
# =========================================================
note_html = (
    '<div class="photo-small">'
    '現在は写真を見ながら食事内容を入力して記録する方式です。'
    '写真そのものの永続保存と自動解析は、'
    '今後追加する機能です。'
    '自動解析を追加した後も、'
    '最終的な食事内容は確認・修正してから'
    '保存できる設計にします。'
    '</div>'
)

st.markdown(
    note_html,
    unsafe_allow_html=True,
)
