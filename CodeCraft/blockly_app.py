import streamlit as st
import streamlit.components.v1 as components
import os

BASE_DIR = os.path.dirname(__file__)
html_path = os.path.join(BASE_DIR, "index.html")

with open(html_path, encoding="utf-8") as f:
    html = f.read()

components.html(html, height=800, scrolling=True)