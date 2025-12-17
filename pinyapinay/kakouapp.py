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
# 背景画像（Base64）
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

        /* 中央コンテンツ */
        .block-container {{
            background-color: rgba(255,255,255,0.96);
            padding: 2rem;
            border-radius: 16px;
        }}

        /* 文字は黒 */
        html, body, h1, h2, h3, h4, p, label, span, div {{
            color: #000000 !important;
        }}

        /* 入力ボックス */
        input, textarea {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #999 !important;
        }}

        /* ファイルアップローダー */
        section[data-testid="stFileUploader"] {{
            background-color: #ffffff !important;
            padding: 12px;
            border-radius: 10px;
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
            border-radius: 8px;
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
        df.loc[len(df)] = [poster, photo_name, image_path]
        df.to_csv(PHOTO_FILE, index=False)

        st.success("写真を投稿しました")
        st.image(image, width=250)
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
        if os.path.exists(row["画像ファイル"]):
            st.image(row["画像ファイル"], width=220)
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
# ③ 投票結果（アニメーション）
# =====================
st.header("③ 投票結果")

vote_df = pd.read_csv(VOTE_FILE)

if vote_df.empty:
    st.write("まだ投票がありません")
else:
    if st.button("🏆 投票結果を見る"):
        result = vote_df["写真名"].value_counts().reset_index()
        result.columns = ["写真名", "投票数"]
        result = result.head(3)

        placeholder = st.empty()

        for i, row in enumerate(result.itertuples(), start=1):
            placeholder.markdown(
                f"## 🥇 第{i}位：{row.写真名}（{row.投票数}票）"
            )
            time.sleep(1.5)

        st.balloons()  # 🎉 クラッカー

# =====================
# ④ 完全リセット
# =====================
st.header("④ 管理者用リセット")

if st.button("⚠ 写真・投票をすべてリセット"):
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

    for f in os.listdir(IMAGE_DIR):
        os.remove(os.path.join(IMAGE_DIR, f))

    st.success("すべてリセットしました")
    st.rerun()
