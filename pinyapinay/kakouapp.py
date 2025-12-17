import streamlit as st
import pandas as pd
import os
import base64
import time
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
# CSV 初期化
# =====================
if not os.path.exists(PHOTO_FILE):
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)

if not os.path.exists(VOTE_FILE):
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

# =====================
# 背景画像
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
        .block-container {{
            background-color: rgba(255,255,255,0.96);
            padding: 2rem;
            border-radius: 16px;
        }}
        html, body, h1, h2, h3, p, label {{
            color: black !important;
        }}
        input, textarea {{
            background-color: white !important;
            color: black !important;
        }}
        section[data-testid="stFileUploader"] * {{
            color: black !important;
            font-weight: 600;
        }}
        button {{
            background-color: #1f77b4 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================
# セッション状態
# =====================
if "show_image" not in st.session_state:
    st.session_state.show_image = None

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

        Image.open(photo).save(image_path)

        df = pd.read_csv(PHOTO_FILE)
        df.loc[len(df)] = [poster, photo_name, image_path]
        df.to_csv(PHOTO_FILE, index=False)

        st.success("写真を投稿しました")
        st.rerun()

# =====================
# ② 投票
# =====================
st.header("② 投票する")

photo_df = pd.read_csv(PHOTO_FILE)

if photo_df.empty:
    st.info("写真が投稿されると投票できます")
else:
    voter = st.text_input("あなたの名前（投票者）")

    for _, row in photo_df.iterrows():
        st.image(row["画像ファイル"], width=200)
        st.write(f"📷 {row['写真名']}（投稿者：{row['投稿者']}）")
        st.markdown("---")

    choice = st.radio("どれを買いたいですか？", photo_df["写真名"].tolist())

    if st.button("投票する"):
        if voter == "":
            st.warning("名前を入力してください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df.loc[len(vote_df)] = [voter, choice]
            vote_df.to_csv(VOTE_FILE, index=False)
            st.success("投票しました")
            st.rerun()

# =====================
# ③ 投票結果（写真付き＋アニメ）
# =====================
st.header("③ 投票結果")

vote_df = pd.read_csv(VOTE_FILE)

if not vote_df.empty:
    if st.button("🏆 投票結果を見る"):
        result = vote_df["写真名"].value_counts().reset_index()
        result.columns = ["写真名", "投票数"]
        result = result.head(3)

        merged = result.merge(photo_df, on="写真名", how="left")

        for i, row in enumerate(merged.itertuples(), start=1):
            st.markdown(f"## 🥇 第{i}位：{row.写真名}（{row.投票数}票）")
            st.image(row.画像ファイル, width=300)

            if st.button(f"🔍 {row.写真名} を拡大表示", key=row.写真名):
                st.session_state.show_image = row.画像ファイル

            time.sleep(1.5)

        st.balloons()

# =====================
# 拡大表示
# =====================
if st.session_state.show_image:
    st.markdown("## 🖼 写真を拡大表示")
    st.image(st.session_state.show_image, use_container_width=True)

    if st.button("❌ 閉じる"):
        st.session_state.show_image = None
        st.rerun()

# =====================
# ④ リセット
# =====================
st.header("④ 管理者用リセット")

if st.button("⚠ 写真・投票をすべてリセット"):
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

    for f in os.listdir(IMAGE_DIR):
        os.remove(os.path.join(IMAGE_DIR, f))

    st.success("すべてリセットしました")
    st.rerun()
