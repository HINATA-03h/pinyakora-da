import streamlit as st
import pandas as pd
import os
from PIL import Image

# =====================
# 基本設定
# =====================
st.set_page_config(page_title="写真投稿＆投票アプリ", layout="centered")
st.title("📸 写真投稿＆投票アプリ")

PHOTO_FILE = "photos.csv"
VOTE_FILE = "votes.csv"
IMAGE_DIR = "images"

os.makedirs(IMAGE_DIR, exist_ok=True)

# =====================
# CSV 初期化（超安全）
# =====================
def init_csv():
    # 写真CSV
    if not os.path.exists(PHOTO_FILE):
        pd.DataFrame(
            columns=["投稿者", "写真名", "画像ファイル"]
        ).to_csv(PHOTO_FILE, index=False)
    else:
        df = pd.read_csv(PHOTO_FILE)
        for col in ["投稿者", "写真名", "画像ファイル"]:
            if col not in df.columns:
                df[col] = ""
        df.to_csv(PHOTO_FILE, index=False)

    # 投票CSV
    if not os.path.exists(VOTE_FILE):
        pd.DataFrame(
            columns=["投票者", "写真名"]
        ).to_csv(VOTE_FILE, index=False)

init_csv()

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
        # 画像保存（同名回避）
        save_name = f"{photo_name}_{poster}_{photo.name}"
        image_path = os.path.join(IMAGE_DIR, save_name)

        image = Image.open(photo)
        image.save(image_path)

        photo_df = pd.read_csv(PHOTO_FILE)

        new_row = pd.DataFrame(
            [[poster, photo_name, image_path]],
            columns=["投稿者", "写真名", "画像ファイル"]
        )

        photo_df = pd.concat([photo_df, new_row], ignore_index=True)
        photo_df.to_csv(PHOTO_FILE, index=False)

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

    st.subheader("📷 投稿された写真一覧")

    for _, row in photo_df.iterrows():
        img = row["画像ファイル"]

        if isinstance(img, str) and img != "" and os.path.exists(img):
            st.image(img, width=200)
        else:
            st.write("（画像なし）")

        st.write(f"写真名：{row['写真名']} ／ 投稿者：{row['投稿者']}")
        st.markdown("---")

    selected = st.radio(
        "どの写真（商品）を買いたいですか？",
        photo_df["写真名"].tolist(),
        index=None,
        key="vote_choice"
    )

    if st.button("投票する"):
        if voter == "":
            st.warning("名前を入力してください")
        elif selected is None:
            st.warning("写真を選択してください")
        else:
            vote_df = pd.read_csv(VOTE_FILE)

            new_vote = pd.DataFrame(
                [[voter, selected]],
                columns=["投票者", "写真名"]
            )

            vote_df = pd.concat([vote_df, new_vote], ignore_index=True)
            vote_df.to_csv(VOTE_FILE, index=False)

            st.success("投票しました！")
            del st.session_state["vote_choice"]
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
        img = row["画像ファイル"]

        if isinstance(img, str) and img != "" and os.path.exists(img):
            st.image(img, width=200)
        else:
            st.write("（画像なし）")

        st.write(
            f"📷 {row['写真名']} ｜ 投稿者：{row['投稿者']} ｜ 投票数：{row['投票数']}"
        )
        st.markdown("---")

# =====================
# ④ 投票リセット
# =====================
st.header("④ 投票リセット（管理用）")

if st.button("⚠ 投票結果をリセットする"):
    pd.DataFrame(columns=["投票者", "写真名"]).to_csv(VOTE_FILE, index=False)
    st.success("投票結果をリセットしました")
    st.rerun()
