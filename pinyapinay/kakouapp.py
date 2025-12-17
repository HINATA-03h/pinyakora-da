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
        }}
        .block-container {{
            background-color: rgba(255,255,255,0.97);
            padding: 2rem;
            border-radius: 16px;
        }}
        * {{
            color: black !important;
        }}
        button {{
            background-color: #1f77b4 !important;
            color: white !important;
            font-weight: bold;
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
    if poster and photo_name and photo:
        path = os.path.join(IMAGE_DIR, f"{photo_name}_{poster}_{photo.name}")
        Image.open(photo).save(path)

        df = pd.read_csv(PHOTO_FILE)
        df.loc[len(df)] = [poster, photo_name, path]
        df.to_csv(PHOTO_FILE, index=False)

        st.success("投稿完了！")
        st.rerun()
    else:
        st.warning("すべて入力してください")

# =====================
# ② 投票
# =====================
st.header("② 投票する")

photo_df = pd.read_csv(PHOTO_FILE)

if len(photo_df) > 0:
    voter = st.text_input("あなたの名前（投票者）")

    for _, r in photo_df.iterrows():
        st.image(r["画像ファイル"], width=200)
        st.write(f"{r['写真名']}（投稿者：{r['投稿者']}）")
        st.markdown("---")

    choice = st.radio("どれを買いたいですか？", photo_df["写真名"].tolist())

    if st.button("投票する"):
        if voter:
            vote_df = pd.read_csv(VOTE_FILE)
            vote_df.loc[len(vote_df)] = [voter, choice]
            vote_df.to_csv(VOTE_FILE, index=False)
            st.success("投票完了！")
            st.rerun()
        else:
            st.warning("名前を入力してください")
else:
    st.info("写真が投稿されると投票できます")

# =====================
# ③ 投票結果（動き付き）
# =====================
st.header("③ 投票結果発表 🎉")

if "step" not in st.session_state:
    st.session_state.step = 0

vote_df = pd.read_csv(VOTE_FILE)

if len(vote_df) > 0:
    result = vote_df["写真名"].value_counts().reset_index()
    result.columns = ["写真名", "投票数"]
    result = result.merge(photo_df, on="写真名", how="left")
    top3 = result.head(3)

    if st.button("📢 次の順位を発表"):
        st.session_state.step += 1
        st.rerun()

    for i in range(min(st.session_state.step, len(top3))):
        r = top3.iloc[i]
        st.subheader(f"🏆 第{i+1}位")
        st.image(r["画像ファイル"], width=250)
        st.write(f"{r['写真名']}｜投票数：{r['投票数']}")
        st.markdown("---")

    if st.session_state.step >= 3:
        st.balloons()
else:
    st.info("まだ投票がありません")

# =====================
# ④ 完全リセット
# =====================
st.header("④ 管理者用リセット")

if st.button("⚠ すべてリセット"):
    pd.DataFrame(columns=["投稿者", "写真名", "画像ファイル"]).to_csv(PHOTO_FILE, index=False)
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)

    for f in os.listdir(IMAGE_DIR):
        os.remove(os.path.join(IMAGE_DIR, f))

    st.session_state.step = 0
    st.success("リセット完了")
    st.rerun()
