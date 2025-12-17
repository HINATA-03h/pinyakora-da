import streamlit as st
import pandas as pd
import os
import base64
from PIL import Image
import shutil

# =====================
# ページ設定
# =====================
st.set_page_config(page_title="写真投稿＆投票アプリ", layout="centered")

# =====================
# パス設定
# =====================
PHOTO_FILE = "photos.csv"
VOTE_FILE = "votes.csv"
IMAGE_DIR = "images"
BACKGROUND_IMAGE = "Background.png"

os.makedirs(IMAGE_DIR, exist_ok=True)

# =====================
# 背景画像（Base64）
# =====================
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_file):
    if not os.path.exists(image_file):
        return
    img_base64 = get_base64_of_image(image_file)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.88);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(BACKGROUND_IMAGE)

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
# タイトル
# =====================
st.title("📸 写真投稿＆投票アプリ")

# =====================
# ① 写真投稿
# =====================
st.header("① 写真を投稿する")

poster = st.text_input("あなたの名前（投稿者）")
photo_name = st.text_input("写真（商品）の名前")
photo = st.file_uploader("写真をアップロード", type=["png", "jpg", "jpeg"])

if st.button("写真を投稿"):
    if poster == "" or photo_name == "" or photo is None:
        st.warning("すべて入力してください")
    else:
        filename = f"{photo_name}_{poster}_{photo.name}"
        image_path = os.path.join(IMAGE_DIR, filename)

        img = Image.open(photo)
        img.save(image_path)

        df = pd.read_csv(PHOTO_FILE)
        df = pd.concat(
            [df, pd.DataFrame([[poster, photo_name, image_path]],
                              columns=["投稿者", "写真名", "画像ファイル"])],
            ignore_index=True
        )
        df.to_csv(PHOTO_FILE, index=False)

        st.success("写真を投稿しました")
        st.image(img, width=250)
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

    st.subheader("📷 投稿された写真")

    for _, row in photo_df.iterrows():
        if os.path.exists(row["画像ファイル"]):
            st.image(row["画像ファイル"], width=200)
        st.write(f"写真名：{row['写真名']} ／ 投稿者：{row['投稿者']}")
        st.markdown("---")

    selected = st.radio(
        "どの写真（商品）を買いたいですか？",
        photo_df["写真名"].tolist(),
        index=None
    )

    if st.button("投票する"):
        if voter == "":
            st.warning("名前を入力してください")
        elif selected is None:
            st.warning("写真を選択してください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df = pd.concat(
                [vote_df, pd.DataFrame([[voter, selected]],
                                       columns=["投票者", "写真名"])],
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
    result = result.merge(photo_df, on="写真名", how="left")

    for _, row in result.iterrows():
        if os.path.exists(row["画像ファイル"]):
            st.image(row["画像ファイル"], width=200)
        st.write(
            f"📷 {row['写真名']} ｜ 投稿者：{row['投稿者']} ｜ 投票数：{row['投票数']}"
        )
        st.markdown("---")

# =====================
# ④ 完全リセット
# =====================
st.header("④ 全データリセット（管理用）")

if st.button("⚠ 写真・投票・画像をすべて削除"):
    # CSV削除
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

    # 画像フォルダ削除→再作成
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    st.success("すべてリセットしました")
    st.rerun()
