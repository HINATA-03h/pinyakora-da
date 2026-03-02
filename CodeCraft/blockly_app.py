import streamlit as st
import streamlit.components.v1 as components
import os

st.write("現在のフォルダ:", os.getcwd())
st.write("中身:", os.listdir())

with open("index.html", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=800, scrolling=True)