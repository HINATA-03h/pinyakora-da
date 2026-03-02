import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

with open("CodeCraft/index.html", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=900, scrolling=False)import streamlit as st
import streamlit.components.v1 as components

# ✅ Streamlitの余白を完全削除
st.set_page_config(layout="wide")

st.markdown("""
<style>
/* 上の余白削除 */
.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
}

/* メニュー・フッター非表示 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# HTML読み込み
with open("CodeCraft/index.html", encoding="utf-8") as f:
    html = f.read()

# ✅ 高さを画面いっぱいに
components.html(html, height=1000, scrolling=False)