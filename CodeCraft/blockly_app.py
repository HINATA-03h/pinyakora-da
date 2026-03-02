import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

with open("CodeCraft/index.html", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=900, scrolling=False)