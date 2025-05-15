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
            <p style='margin: 5px 0 0 0; font-size: 18px; color: #004466;'>ביטוח לאומי ודיני עבודה</p>
        </div>
        <div style='max-width: 120px; max-height: 80px; overflow: hidden; display: flex; align-items: center; justify-content: center;'>
            
        </div>
    </div>
    <hr style='margin: 20px 0; border: none; border-top: 1px solid #007ACC;' />
    <h1 style='
        text-align: center;
        font-size: 36px;
        color: #003366;
        margin: 0;
        position: relative;
    '>
        מערכת לאיתור אחוזי נכות
        <div style='
            height: 4px;
            background-color: #007ACC;
            width: 50px;
            margin: 8px auto 0 auto;
            border-radius: 2px;
            animation: expand 2s ease-out;
        '></div>
    </h1>
    <div style='
        text-align: left;
        font-size: 12px;
        color: #666;
        margin-top: 15px;
    '>
        גרסה 1.0 | {today}
    </div>
</div>

<style>
@keyframes expand {{
    from {{ width: 0; opacity: 0; }}
    to {{ width: 50px; opacity: 1; }}
}}
</style>
""", unsafe_allow_html=True)
def render_table_with_colors(df):
    df_html = df.to_html(classes='styled-table', escape=False)
    css_block = '''
    <style>
        .styled-table {
        overflow-x: auto;
        display: block;
        max-width: 100%;
            border-collapse: collapse;
            width: 100%;
            font-size: 16px;
            direction: rtl;
        }
        .styled-table th, .styled-table td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
            max-width: 250px;
            white-space: pre-wrap;
            word-wrap: break-word;
            vertical-align: top;
        }
        .styled-table tr:nth-child(even) { background-color: #e0f7fa; }
        .styled-table tr:nth-child(odd) { background-color: #f1fafe; }
        .styled-table tr:hover { background-color: #b2ebf2; cursor: pointer; }
        th { position: sticky; top: 0; background-color: #d0e9f7; }
    </style>
    '''
    st.markdown(css_block, unsafe_allow_html=True)
    st.markdown(df_html, unsafe_allow_html=True)

uploaded_file = st.file_uploader("טען קובץ Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.session_state["df"] = df

if "df" in st.session_state:
    df = st.session_state["df"]
    st.markdown("### 🎛 חיפוש וסינון")

    # תיבת חיפוש כללית
    st.markdown("""
    <div style='
        border: 2px solid #007ACC;
        padding: 10px;
        background-color: #f0fbff;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    '>
    <b style='color: #003366;'>🔍 חיפוש חופשי בכל הטבלה</b>
    </div>
    """, unsafe_allow_html=True)

    general_query = st.text_input("", placeholder="הקלד מילה לחיפוש בכלל השורות...")

    search_inputs = {}
    multiselects = {}

    with st.form("filters"):
        cols_per_row = 1
        cols = st.columns(cols_per_row)

        for i, col in enumerate(df.columns):
            with cols[i % cols_per_row]:
                st.text_input(f"חיפוש חופשי ב-{col}", key=f"text_{col}")
                search_inputs[col] = st.session_state.get(f"text_{col}", "")
                if i < 3:
                    options = sorted(df[col].dropna().unique(), key=str)
                    st.multiselect(f"בחירה מרובה ב-{col}", options=options, key=f"multi_{col}")
                    multiselects[col] = st.session_state.get(f"multi_{col}", [])

            if (i + 1) % cols_per_row == 0 and i + 1 < len(df.columns):
                cols = st.columns(cols_per_row)

        st.markdown("---")
        min_percent = st.number_input("אחוז נכות מ-", min_value=0, max_value=100, value=0)
        max_percent = st.number_input("עד אחוז נכות", min_value=0, max_value=100, value=100)
        submitted = st.form_submit_button("סנן")

    if submitted:
        df_filtered = df.copy().fillna("")

        if general_query:
            df_filtered = df_filtered[df_filtered.astype(str).apply(lambda row: row.str.contains(general_query, case=False, na=False)).any(axis=1)]

        for col in df.columns:
            txt = search_inputs.get(col, "")
            if txt:
                df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(txt, case=False, na=False)]
            if col in multiselects and multiselects[col]:
                df_filtered = df_filtered[df_filtered[col].isin(multiselects[col])]

        if "אחוז נכות" in df_filtered.columns:
            df_filtered["אחוז נכות"] = pd.to_numeric(df_filtered["אחוז נכות"], errors="coerce")
            df_filtered = df_filtered[df_filtered["אחוז נכות"].between(min_percent, max_percent)]
        if df_filtered.empty:
            st.warning("⚠️ לא נמצאו תוצאות")
        else:
            st.success(f"נמצאו {len(df_filtered)} תוצאות תואמות")

            # בחירת עמודות להצגה
            selected_cols = st.multiselect(
                "בחר עמודות להצגה",
                options=list(df_filtered.columns),
                default=list(df_filtered.columns)
            )

            # הצגת הטבלה עם עיצוב וצבעים
            render_table_with_colors(df_filtered[selected_cols].reset_index(drop=True))

            # הורדת Excel
            def convert_df_to_excel(df):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Filtered')
                output.seek(0)
                return output

            st.download_button(
                "📥 הורד תוצאה לאקסל",
                data=convert_df_to_excel(df_filtered),
                file_name="תוצאות_מסוננות.xlsx"
            )

            # הורדת PDF
            def create_pdf_from_df(df):
                html = f"""
                <html dir="rtl">
                <head>
                <meta charset="UTF-8">
                <style>
                    table {{ border-collapse: collapse; width: 100%; font-size: 14px; direction: rtl; }}
                    th, td {{ border: 1px solid black; padding: 8px; text-align: right; vertical-align: top; white-space: pre-wrap; word-wrap: break-word; }}
                    th {{ background-color: #e0f7fa; }}
                </style>
                </head>
                <body>
                <h2>תוצאות מסוננות</h2>
                {df.to_html(index=False, escape=False)}
                </body>
                </html>
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

            pdf_file = create_pdf_from_df(df_filtered)
            if pdf_file and os.path.exists(pdf_file):
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "📄 הורד PDF",
                        data=f,
                        file_name="תוצאות.pdf",
                        mime="application/pdf"
                    )
