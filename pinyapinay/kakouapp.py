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
# 起動時リセット（リロード＝全消去）
# =====================
pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)
for f in os.listdir(IMAGE_DIR):
    os.remove(os.path.join(IMAGE_DIR, f))

# =====================
# 背景設定（Base64）
# =====================
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

if os.path.exists(BACKGROUND_IMAGE):
    bg = get_base64_of_image(BACKGROUND_IMAGE)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg}");
            background-size: cover;
            background-position: center;
        }}

        /* 白カード */
        .block-container {{
            background-color: rgba(255,255,255,0.96);
            padding: 2.5rem;
            border-radius: 16px;
        }}

        /* 文字をすべて黒に */
        h1, h2, h3, p, label, span, div {{
            color: #000000 !important;
        }}

        /* 入力欄 */
        input, textarea {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}

        /* radio */
        div[role="radiogroup"] label {{
            color: #000000 !important;
            font-weight: 600;
        }}

        /* file uploader */
        section[data-testid="stFileUploader"] {{
            background-color: #f5f5f5;
            padding: 12px;
            border-radius: 10px;
            color: #000000 !important;
        }}

        section[data-testid="stFileUploader"] * {{
            color: #000000 !important;
            font-weight: 600;
        }}

        /* ボタン */
        button {{
            background-color: #1f77b4 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================
# タイトル
# =====================
st.title("📸 写真投稿＆投票アプリ")

# =====================
# ① 写真投稿
# =====================
st.header("① 写真を投稿する")

poster = st.text_input("あなたの名前（投稿者）")
photo_name = st.text_input("写真（商品の）名前")
photo = st.file_uploader("写真をアップロード", type=["png", "jpg", "jpeg"])

if st.button("写真を投稿"):
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

        st.success("写真を投稿しました")
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
            st.image(row["画像ファイル"], width=220)
        st.write(f"写真名：{row['写真名']} ／ 投稿者：{row['投稿者']}")
        st.markdown("---")

    choice = st.radio("どれを買いたいですか？", photo_df["写真名"].tolist())

    if st.button("投票する"):
        if voter == "":
            st.warning("名前を入力してください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df = pd.concat(
                [vote_df, pd.DataFrame([[voter, choice]], columns=["投票者", "写真名"])],
                ignore_index=True
            )
            vote_df.to_csv(VOTE_FILE, index=False)
            st.success("投票しました")
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

    for _, row in result.iterrows():
        st.write(f"📷 {row['写真名']}｜投票数：{row['投票数']}")
