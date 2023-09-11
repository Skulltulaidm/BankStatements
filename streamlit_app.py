import re
import pdfplumber
import pandas as pd
import streamlit as st
from io import BytesIO
import base64

def process_monex(file):
    all_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"

    pattern = re.compile(r'(\d{2}/\w{3})\s+([\w\s]+?)(?:\s+(\d{8}))?\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})')

    matches = [m.groups() for m in re.finditer(pattern, all_text)]
    column_names = ['Fecha', 'Descripción', 'Referencia', 'Abonos', 'Cargos', 'Movimiento Garantía', 'Saldo No Disponible', 'Saldo Disponible', 'Saldo Total']
    data = [dict(zip(column_names, match)) for match in matches]

    df = pd.DataFrame(data)
    return df

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename='data.xlsx', text='Descargar archivo Excel'):
    val = to_excel(df)
    b64 = base64.b64encode(val).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'

# Streamlit UI
st.title('Procesador de Estados de Cuenta')

bank_option = st.selectbox('Selecciona tu banco:', ('MONEX', 'Otro banco'))

uploaded_files = st.file_uploader("Carga tus estados de cuenta aquí", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    st.write(f'Has subido {len(uploaded_files)} estados de cuenta.')

if st.button('Descargar'):
    dfs = []
    for file in uploaded_files:
        if bank_option == 'MONEX':
            df = process_monex(file)
            dfs.append(df)

    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        st.write(f'Se han procesado {len(dfs)} estados de cuenta.')
        st.markdown(get_table_download_link(final_df), unsafe_allow_html=True)
