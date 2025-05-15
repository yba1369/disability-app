import streamlit as st
import pandas as pd
import io
import os
import tempfile
import pdfkit
from datetime import datetime

st.set_page_config(page_title="משרד עורך דין יוסי בן אבו", layout="centered")
today = datetime.today().strftime("%d/%m/%Y")

logo_svg = ""

st.markdown("""
<div style='
    background: linear-gradient(to right, #e0f7fa, #ffffff);
    padding: 25px;
    border: 2px solid #007ACC;
    border-radius: 12px;
    margin-bottom: 20px;
    direction: rtl;
    position: relative;
'>
  <div style='display: flex; justify-content: space-between; align-items: center;'>
    <div style='text-align: right;'>
        <h2 style="margin: 0; font-size: 32px; color: #003366;">משרד עורך דין יוסי בן אבו</h2>
        <p style="margin: 5px 0 0; font-size: 18px; color: #004466;">ביטוח לאומי ודיני עבודה</p>
    </div>
    <div style='max-width: 120px; max-height: 80px; overflow: hidden; display: flex; align-items: center; justify-content: center;'>
        {{logo_svg}}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 36px; color: #003366; margin: 0;'>מערכת לאיתור אחוזי נכות</h1>", unsafe_allow_html=True)
