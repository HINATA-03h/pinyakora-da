import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image

# =====================
# 基本設定
# =====================
st.set_page_config(page_title="写真投稿＆投票アプリ", layout="centered")

BASE_DIR = os.path.dirname(__file__)
PHOTO_FILE = os.path.join(BASE_DIR, "photos.csv")
VOTE_FILE = os.path.join(BASE_DIR, "votes.csv")
IMAGE_DIR = os.path.join(BASE_DIR, "images")
BACKGROUND_IMAGE = os.path.join(BASE_DIR, "Background.png")

os.makedirs(IMAGE_DIR, exist_ok=True)

# =====================
# 背景画像（Base64）
# =====================
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_file):
    if not os.path.exists(image_file):
        st.warning("背景画像が見つかりません")
        return

    img_base64 = get_base64_of_image(image_file)

    st.markdown(
        f"""
        <style>
        /* 背景 */
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 中央コンテンツ */
        .block-container {{
            background-color: rgba(255,255,255,0.92);
            padding: 2rem;
            border-radius: 14px;
            color: black;
        }}

        /* 文字色 */
        h1, h2, h3, h4, h5, h6, p, span, label {{
            color: black !important;
        }}

        /* =====================
           🔥 ボタン完全強化 🔥
           ===================== */
        div.stButton > button {{
            background-color: #2563eb;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 0.6rem 1.4rem;
            border-radius: 10px;
            border: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
            transition: all 0.2s ease;
        }}

        div.stButton > button:hover {{
            background-color: #1e40af;
            transform: translateY(-2px);
        }}

        div.stButton > button:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.25);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(BACKGROUND_IMAGE)

st.title("📸 写真投稿＆投票アプリ")

# =====================
# CSV 初期化
# =====================
def init_csv():
    if not os.path.exists(PHOTO_FILE):
        pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    if not os.path.exists(VOTE_FILE):
        pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

init_csv()

# =====================
# ① 写真投稿
# =====================
st.header("① 写真を投稿する")

poster = st.text_input("あなたの名前（投稿者）")
photo_name = st.text_input("写真（商品の）名前")
photo = st.file_uploader("写真をアップロード", type=["png", "jpg", "jpeg"])

if st.button("📤 写真を投稿"):
    if poster == "" or photo_name == "" or photo is None:
        st.warning("すべて入力してください")
    else:
        save_name = f"{photo_name}_{poster}_{photo.name}"
        image_path = os.path.join(IMAGE_DIR, save_name)

        image = Image.open(photo)
        image.save(image_path)

        df = pd.read_csv(PHOTO_FILE)
        df = pd.concat(
            [df, pd.DataFrame([[poster, photo_name, image_path]],
            columns=["投稿者", "写真名", "画像ファイル"])],
            ignore_index=True
        )
        df.to_csv(PHOTO_FILE, index=False)

        st.success("写真を投稿しました！")
        st.image(image, width=250)
        st.rerun()

# =====================
# ② 投票
# =====================
st.header("② 投票する")

photo_df = pd.read_csv(PHOTO_FILE)

if len(photo_df) == 0:
    st.info("写真が投稿されると投票できます")
else:
    voter = st.text_input("あなたの名前（投票者）")

    for _, row in photo_df.iterrows():
        if os.path.exists(row["画像ファイル"]):
            st.image(row["画像ファイル"], width=200)
        st.write(f"📷 写真名：{row['写真名']} ／ 投稿者：{row['投稿者']}")
        st.markdown("---")

    choice = st.radio(
        "どれを買いたいですか？",
        photo_df["写真名"].tolist(),
        index=None
    )

    if st.button("🗳 投票する"):
        if voter == "" or choice is None:
            st.warning("名前と選択をしてください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df = pd.concat(
                [vote_df, pd.DataFrame([[voter, choice]], columns=["投票者", "写真名"])],
                ignore_index=True
            )
            vote_df.to_csv(VOTE_FILE, index=False)
            st.success("投票しました！")
            st.rerun()

# =====================
# ③ 投票結果
# =====================
st.header("③ 投票結果")

vote_df = pd.read_csv(VOTE_FILE)

if len(vote_df) == 0:
    st.write("まだ投票がありません")
else:
    result = vote_df["写真名"].value_counts().reset_index()
    result.columns = ["写真名", "投票数"]
    result = result.merge(photo_df, on="写真名", how="left")

    for _, row in result.iterrows():
        if os.path.exists(row["画像ファイル"]):
            st.image(row["画像ファイル"], width=200)
        st.write(f"🏆 {row['写真名']} ｜ 投稿者：{row['投稿者']} ｜ 投票数：{row['投票数']}")
        st.markdown("---")

# =====================
# ④ 完全リセット
# =====================
st.header("④ 完全リセット（管理用）")

if st.button("⚠ 写真・投票をすべてリセット"):
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

    for f in os.listdir(IMAGE_DIR):
        os.remove(os.path.join(IMAGE_DIR, f))

    st.success("すべてリセットしました")
    st.rerun()
