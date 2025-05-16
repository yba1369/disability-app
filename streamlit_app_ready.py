import streamlit as st
import pandas as pd
import io
import os
import tempfile
import pdfkit
from datetime import datetime

st.set_page_config(page_title="מערכת לאיתור אחוזי נכות", layout="wide")
today = datetime.today().strftime("%d/%m/%Y")

# טעינת קובץ לוגו SVG
logo_svg = ""
if os.path.exists("logo_svg.svg"):
    with open("logo_svg.svg", "r", encoding="utf-8") as logo_file:
        logo_svg = logo_file.read()

# כותרת ראשית
st.markdown(f"""
<div style='background: linear-gradient(to right, #e0f7fa, #ffffff); padding: 25px; border: 2px solid #007ACC; border-radius: 12px; margin-bottom: 20px; direction: rtl; position: relative;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div style='text-align: right;'>
            <h2 style='margin: 0; font-size: 28px; color: #003366;'>משרד עורכי דין יוסי בן אבו</h2>
            <p style='margin: 5px 0 0 0; font-size: 16px; color: #004466;'>מומחים בייצוג מול ועדות רפואיות</p>
        </div>
        <div style='max-width: 100px;'>{logo_svg}</div>
    </div>
    <hr style='margin: 15px 0;' />
    <h1 style='text-align: center; font-size: 32px; color: #003366;'>מערכת לאיתור אחוזי נכות</h1>
    <div style='text-align: left; font-size: 12px; color: #666; margin-top: 10px;'>גרסה 1.0 | {today}</div>
</div>
""", unsafe_allow_html=True)

# טבלת תוצאה מעוצבת
def render_table_with_colors(df):
    df_html = df.to_html(classes='styled-table', escape=False)
    css_block = '''
    <style>
        .styled-table {
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
            direction: rtl;
        }
        .styled-table th, .styled-table td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            white-space: pre-wrap;
            word-wrap: break-word;
            vertical-align: top;
        }
        .styled-table tr:nth-child(even) { background-color: #e0f7fa; }
        .styled-table tr:nth-child(odd) { background-color: #f1fafe; }
        .styled-table tr:hover { background-color: #b2ebf2; }
        th { position: sticky; top: 0; background-color: #d0e9f7; }
    </style>
    '''
    st.markdown(css_block, unsafe_allow_html=True)
    st.markdown(df_html, unsafe_allow_html=True)

# טעינת קובץ
uploaded_file = st.file_uploader("טען קובץ Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.session_state["df"] = df

# סינון והצגה
if "df" in st.session_state:
    df = st.session_state["df"]
    st.markdown("### 🔍 חיפוש וסינון")

    general_query = st.text_input("חיפוש בכל השדות", placeholder="הקלד מונח...")

    search_inputs = {}
    multiselects = {}

    with st.form("filters"):
        for col in df.columns:
            st.text_input(f"חיפוש ב-{col}", key=f"text_{col}")
            search_inputs[col] = st.session_state.get(f"text_{col}", "")
            options = sorted(df[col].dropna().unique(), key=str)
            st.multiselect(f"בחירה מרובה ב-{col}", options=options, key=f"multi_{col}")
            multiselects[col] = st.session_state.get(f"multi_{col}", [])
        min_percent = st.number_input("אחוז נכות מ-", min_value=0, max_value=100, value=0)
        max_percent = st.number_input("עד אחוז נכות", min_value=0, max_value=100, value=100)
        submitted = st.form_submit_button("סנן")

    if submitted:
        df_filtered = df.copy().fillna("")

        if general_query:
            df_filtered = df_filtered[df_filtered.astype(str).apply(lambda row: row.str.contains(general_query, case=False, na=False)).any(axis=1)]

        for col in df.columns:
            if search_inputs[col]:
                df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(search_inputs[col], case=False, na=False)]
            if multiselects[col]:
                df_filtered = df_filtered[df_filtered[col].isin(multiselects[col])]

        if "אחוז נכות" in df_filtered.columns:
            df_filtered["אחוז נכות"] = pd.to_numeric(df_filtered["אחוז נכות"], errors="coerce")
            df_filtered = df_filtered[df_filtered["אחוז נכות"].between(min_percent, max_percent)]

        st.session_state["filtered_df"] = df_filtered

    if "filtered_df" in st.session_state:
        df_filtered = st.session_state["filtered_df"]
        all_columns = list(df_filtered.columns)
        selected = st.multiselect("בחר עמודות להצגה", options=all_columns, default=all_columns)
        selected_cols = [col for col in all_columns if col in selected]

        if df_filtered.empty:
            st.warning("⚠️ לא נמצאו תוצאות")
        else:
            st.success(f"נמצאו {len(df_filtered)} תוצאות תואמות")
            render_table_with_colors(df_filtered[selected_cols].reset_index(drop=True))

            def convert_df_to_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Filtered')
                output.seek(0)
                return output

            st.download_button("📥 הורד Excel", data=convert_df_to_excel(df_filtered[selected_cols]), file_name="תוצאות_מסוננות.xlsx")

            def create_pdf_from_df(df):
                html = f"""
                <html dir="rtl">
                <head><meta charset="UTF-8"></head>
                <body>
                <h2>תוצאות מסוננות</h2>
                {df.to_html(index=False, escape=False)}
                </body></html>
                """
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as f:
                    f.write(html)
                    html_path = f.name
                pdf_path = html_path.replace(".html", ".pdf")
                try:
                    pdfkit.from_file(html_path, pdf_path)
                    return pdf_path
                except Exception as e:
                    st.error("שגיאה ביצירת PDF: " + str(e))
                    return None

            pdf_file = create_pdf_from_df(df_filtered[selected_cols])
            if pdf_file and os.path.exists(pdf_file):
                with open(pdf_file, "rb") as f:
                    st.download_button("📄 הורד PDF", data=f, file_name="תוצאות.pdf", mime="application/pdf")
