import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image
import shutil
import time

# =====================
# 基本設定
# =====================
st.set_page_config(page_title="写真投稿＆投票アプリ", layout="centered")
st.title("📸 写真投稿＆投票アプリ")

PHOTO_FILE = "photos.csv"
VOTE_FILE = "votes.csv"
IMAGE_DIR = "images"
BACKGROUND_IMAGE = "Background.png"

os.makedirs(IMAGE_DIR, exist_ok=True)

# =====================
# 🔥 起動時 完全初期化（重要）
# =====================
if "initialized" not in st.session_state:
    # CSV削除
    if os.path.exists(PHOTO_FILE):
        os.remove(PHOTO_FILE)
    if os.path.exists(VOTE_FILE):
        os.remove(VOTE_FILE)

    # 画像削除
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    st.session_state.initialized = True

# =====================
# CSV 初期化
# =====================
pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

# =====================
# 背景画像（キャッシュ無効化）
# =====================
def set_background(image_file):
    if not os.path.exists(image_file):
        return

    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    cache_buster = int(time.time())

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}?v={cache_buster}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255,255,255,0.9);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(BACKGROUND_IMAGE)

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
        filename = f"{int(time.time())}_{photo.name}"
        path = os.path.join(IMAGE_DIR, filename)

        image = Image.open(photo)
        image.save(path)

        df = pd.read_csv(PHOTO_FILE)
        df.loc[len(df)] = [poster, photo_name, path]
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
        st.write(f"📷 {row['写真名']} ／ 投稿者：{row['投稿者']}")
        st.markdown("---")

    choice = st.radio(
        "どれを買いたいですか？",
        photo_df["写真名"].tolist(),
        index=None
    )

    if st.button("投票する"):
        if voter == "" or choice is None:
            st.warning("名前と選択をしてください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df.loc[len(vote_df)] = [voter, choice]
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
        st.write(f"🏆 {row['写真名']} ｜ {row['投票数']} 票")
        st.markdown("---")

# =====================
# ④ 完全リセット
# =====================
st.header("④ 完全リセット")

if st.button("⚠ すべて初期化する"):
    shutil.rmtree(IMAGE_DIR)
    os.makedirs(IMAGE_DIR)
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)
    st.success("完全に初期化しました")
    st.rerun()

