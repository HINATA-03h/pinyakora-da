import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("CodeCraft HTML/CSS")

# index.html を読み込む
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# HTMLを表示
components.html(html_code, height=900, scrolling=True)