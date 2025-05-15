import streamlit as st
import pandas as pd
import io
import os
import tempfile
import pdfkit
from datetime import datetime

st.set_page_config(page_title="מערכת לאיתור אחוזי נכות", layout="centered")
today = datetime.today().strftime("%d/%m/%Y")

logo_svg = ""

st.markdown(f"""
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
      <h2 style='margin: 0; font-size: 32px; color: #003366;'>משרד עורך דין יוסי בן אבו</h2>
      <p style='margin: 5px 0 0; font-size: 18px; color: #004466;'>ביטוח לאומי ודיני עבודה</p>
    </div>
  </div>
</div>

<hr style='margin: 20px 0; border: none; border-top: 1px solid #007ACC;' />
<h1 style="
    text-align: center;
    font-size: 36px;
    color: #003366;
    margin: 0;
    position: relative;
">מערכת לאיתור אחוזי נכות</h1>
""", unsafe_allow_html=True)

# העלאת קובץ אקסל
uploaded_file = st.file_uploader("בחר קובץ Excel", type=["xlsx"], label_visibility="collapsed")

# פונקציית סינון
def render_table_with_colors(df):
    st.markdown("---")
    st.markdown("### תוצאות החיפוש:")
    st.dataframe(df, use_container_width=True)

# המרות וייצוא
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return output.getvalue()

def create_pdf_from_df(df):
    html = df.to_html(index=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        f.write(html.encode("utf-8"))
        html_path = f.name
    pdf_path = html_path.replace(".html", ".pdf")
    pdfkit.from_file(html_path, pdf_path)
    return pdf_path

# עיבוד
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    search_term = st.text_input("🔍 חיפוש חופשי בטקסט", "", key="free_text", placeholder="הקלד טקסט לחיפוש...")
    if search_term:
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False)).any(axis=1)]
    else:
        filtered_df = df

    if not filtered_df.empty:
        render_table_with_colors(filtered_df)

        col1, col2 = st.columns(2)
        with col1:
            excel_data = convert_df_to_excel(filtered_df)
            st.download_button("📥 הורד כ-Excel", data=excel_data, file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col2:
            pdf_path = create_pdf_from_df(filtered_df)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 הורד כ-PDF", data=f, file_name="filtered_data.pdf", mime="application/pdf")
    else:
        st.info("לא נמצאו תוצאות לחיפוש.")
