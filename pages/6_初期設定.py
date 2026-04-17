import streamlit as st
from app_core import *

st.set_page_config(page_title="初期設定｜ShufuMate", layout="wide")

reload_user_data_if_needed()

st.header("⚙️ 初期設定")
st.caption("ShufuMateを使いやすくするための基本情報を登録できます。")

st.info(
    "体型情報や食事スタイル、地域などを登録しておくと、"
    "他のページにも内容が反映され、毎日の記録や相談がより使いやすくなります。"
)

st.subheader("📌 基本の設定")
st.selectbox("性別（任意）", ["未選択", "女性", "男性", "その他", "回答しない"], key="common_gender")
st.number_input("年齢", min_value=20, max_value=100, step=1, key="common_age")
st.number_input("身長（cm）", min_value=145.0, max_value=200.0, step=0.5, format="%.1f", key="common_height")
st.number_input("スタート時の体重（kg）", min_value=39.0, max_value=200.0, step=0.1, format="%.1f", key="common_weight")
st.number_input("目標体重（kg）", min_value=39.0, max_value=150.0, step=0.1, format="%.1f", key="common_target_weight")
st.number_input("スタート時の体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_body_fat")
st.number_input("目標体脂肪率（%）", min_value=5.0, max_value=60.0, step=0.1, format="%.1f", key="common_target_body_fat")
st.number_input("筋肉量（kg）", min_value=10.0, max_value=80.0, step=0.1, format="%.1f", key="common_muscle_mass")

st.subheader("🍽 食事・運動の初期値")
st.radio("食事スタイル", ["和食中心", "バランス", "おしゃれカフェ風", "タンパク質おにぎり＆味噌玉味噌汁"], horizontal=True, key="meal_style")
st.radio("調理レベル", ["超かんたん", "普通", "しっかり"], horizontal=True, key="ease_level")
st.radio("主食の好み", ["ごはん派", "パン派", "どちらも"], horizontal=True, key="staple_preference")
st.text_area("よくある冷蔵庫の食材", key="fridge_items")
st.text_area("食べられないもの・避けたいもの", key="avoid_foods", placeholder="例：えび、かに、牡蠣、辛いもの、牛乳 など")
st.text_area("わたしの定番・好きな食事", key="favorite_meals", placeholder="例：納豆、豆乳、ブルーベリー")

st.radio("プランタイプ初期値", ["通常", "外食", "コンビニ"], horizontal=True, key="plan_type")
st.selectbox("平日のお昼スタイル", ["指定なし", "お弁当", "コンビニ", "おすすめ定番", "外食", "自宅"], key="lunch_style")
st.selectbox("運動強度", ["ゆるめ", "普通", "しっかり"], key="exercise_intensity")
st.checkbox("主婦リアル提案モード初期値", key="real_mode")
st.selectbox("食事の流れ初期値", ["普通", "朝しっかり・昼軽め", "食べすぎた", "あまり食べてない"], key="daily_flow")
st.checkbox("運動あり初期値", key="workout_today")
st.selectbox("目的初期値", ["バランス", "脚やせ", "脂肪燃焼", "むくみ改善"], key="body_goal")

st.subheader("🧘 体質・体型チェック")
st.selectbox(
    "アーユルヴェーダ体質",
    ["", "ヴァータ", "ピッタ", "カパ", "未設定"],
    key="dosha_type"
)

st.selectbox(
    "体型チェック",
    ["全体バランス", "下半身", "お腹まわり", "二の腕", "姿勢", "むくみ", "ヒップ", "太もも"],
    key="body_shape_goal"
)

st.multiselect(
    "今の状態チェック",
    ["疲れやすい", "むくみやすい", "冷えやすい", "食欲が乱れやすい", "便秘気味", "寝不足気味", "ストレスが強い", "なんとなくだるい"],
    key="current_state_checks"
)

st.subheader("📍 地域設定")

prefectures = [
    "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
    "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
    "新潟県","富山県","石川県","福井県","山梨県","長野県",
    "岐阜県","静岡県","愛知県","三重県",
    "滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
    "鳥取県","島根県","岡山県","広島県","山口県",
    "徳島県","香川県","愛媛県","高知県",
    "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"
]

area_candidates = [
    "仙台駅周辺", "長命ヶ丘", "泉中央", "八乙女", "吉成", "北山", "石巻", "利府", "多賀城"
]

st.selectbox("都道府県", [""] + prefectures, key="home_prefecture")
st.selectbox("よく使う地域・最寄りエリア（候補から選ぶ）", [""] + area_candidates, key="home_area")
st.text_input("候補にない地域は自由入力", key="home_area_custom", placeholder="例：仙台市泉区南光台")

c1, c2 = st.columns(2)

with c1:
    if st.button("💾 初期設定を保存", use_container_width=True):
        save_user_settings()
        st.success("初期設定を保存しました。")
        st.rerun()

with c2:
    if st.button("↺ 初期設定をリセット", use_container_width=True):
        reset_user_settings()
        save_user_settings()
        st.success("初期設定をリセットしました。")
        st.rerun()
