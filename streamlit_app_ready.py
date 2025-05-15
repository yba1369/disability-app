
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="מערכת חיפוש ורסטילית", layout="wide")

st.markdown("## משרד עורך דין יוסי בן אבו")
st.markdown("### ביטוח לאומי ודיני עבודה")
st.markdown("---")

uploaded_file = st.file_uploader("העלה קובץ Excel", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)
st.success("✅ הקובץ נטען בהצלחה")

# שמירת סינונים
filters = {}
multiselects = {}

# חלוקה לעמודות a–c ויתר
column_names = list(df.columns)
early_columns = column_names[:3]
other_columns = column_names[3:]

with st.form("filters_form"):
    st.markdown("### סינון לפי עמודות:")

    for col in early_columns:
        st.text_input(f"חיפוש חופשי בעמודה: {col}", key=f"text_{col}")
        options = sorted(df[col].dropna().unique().tolist())
        st.multiselect(f"בחר ערכים מתוך עמודה: {col}", options=options, key=f"multi_{col}")

    for col in other_columns:
        st.text_input(f"חיפוש חופשי בעמודה: {col}", key=f"text_{col}")

    submitted = st.form_submit_button("סנן")

if submitted:
    df_filtered = df.copy()
    for col in column_names:
        text_val = st.session_state.get(f"text_{col}", "").strip()
        multi_val = st.session_state.get(f"multi_{col}", [])

        if text_val:
            df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(text_val, case=False, na=False)]

        if col in early_columns and multi_val:
            df_filtered = df_filtered[df_filtered[col].isin(multi_val)]

    if df_filtered.empty:
        st.warning("⚠️ לא נמצאו תוצאות תואמות לסינון")
    else:
        st.success(f"נמצאו {len(df_filtered)} תוצאות")
        st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)

        # הורדת Excel
        def convert_df_to_excel(dataframe):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Filtered")
            output.seek(0)
            return output

        excel_data = convert_df_to_excel(df_filtered)
        st.download_button(
            label="📥 הורד תוצאות לאקסל",
            data=excel_data,
            file_name="תוצאות_חיפוש.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
