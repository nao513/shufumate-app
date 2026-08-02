import streamlit as st
from app_core import *

from pathlib import Path
from PIL import Image
import base64
import html
import requests
import io


# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="写真で記録｜ShufuMate",
    page_icon="📷",
    layout="centered",
)

require_login()
user_id = get_user_id()


# =========================
# ヘッダー
# =========================
st.title("📷 写真で記録")
st.caption("写真から食事をかんたん記録＆自動チェック")


# =========================
# 写真入力
# =========================
st.markdown("## 📸 写真を選ぶ")

input_mode = st.radio(
    "入力方法",
    ["アップロード", "カメラ"],
    horizontal=True
)

img = None

if input_mode == "アップロード":
    img = st.file_uploader("写真を選択", type=["jpg", "jpeg", "png"])
else:
    img = st.camera_input("撮影")

if img:
    st.image(img, caption="選択した写真", use_container_width=True)


# =========================
# AI解析
# =========================
def encode_image(file):
    image = Image.open(file)
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

ai_result = None

if img:
    if st.button("🍽 AIで食事チェック", use_container_width=True):

        with st.spinner("AI分析中..."):

            base64_image = encode_image(img)

            headers = {
                "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "この食事を分析して以下を簡潔に出してください：\
①何を食べているか\
②バランス（良い・普通・改善）\
③改善ポイント\
④点数（100点満点）"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if res.status_code == 200:
                ai_result = res.json()["choices"][0]["message"]["content"]

                st.markdown("## 🧠 食事分析")
                st.write(ai_result)

                # 自動入力（ここが神ポイント）
                st.session_state["auto_food"] = ai_result

            else:
                st.error("AI分析失敗")


# =========================
# 食事入力
# =========================
st.markdown("## 🍽 食事内容")

auto_meal = detect_meal_type_by_time(jst_now())

meal_options = ["朝", "昼", "夜", "間食"]

meal_type = st.radio(
    "食事区分",
    meal_options,
    index=meal_options.index(auto_meal) if auto_meal in meal_options else 0,
    horizontal=True
)

default_text = st.session_state.get("auto_food", "")

food_text = st.text_area(
    "食事内容",
    value=default_text,
    height=120
)


# =========================
# 保存
# =========================
if st.button("✅ 記録する", use_container_width=True):

    if img is None:
        st.warning("写真を入れてください")
    else:
        try:
            save_photo_meal_log(
                user_id=user_id,
                meal_type=meal_type,
                food_text=food_text,
                image_file=img,
            )

            st.success("記録しました！")
            st.balloons()

        except Exception:
            st.error("保存失敗")


# =========================
# 最新表示
# =========================
st.markdown("## 📌 最新の記録")

try:
    logs = load_photo_logs(user_id)
except:
    logs = []

if logs:
    latest = logs[-1]

    st.write(f"日付：{latest.get('log_date','')}")
    st.write(f"区分：{latest.get('meal_type','')}")
    st.write(f"内容：{latest.get('food_text','')}")

    if latest.get("image_bytes"):
        st.image(latest["image_bytes"], use_container_width=True)

else:
    st.info("まだ記録なし")


# =========================
# メッセージ
# =========================
st.markdown(
    """
---
食事は完璧じゃなくてOKです。  
写真だけでも立派な記録です。
"""
)
