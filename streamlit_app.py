import streamlit as st
import re
import pdfplumber
import pandas as pd

def process_monex(file):
    all_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"

    pattern = re.compile(r'(\d{2}/\w{3})\s+([\w\s]+?)(?:\s+(\d{8}))?\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})')

    matches = find_matches(all_text, pattern)

    column_names = ['Fecha', 'Descripción', 'Referencia', 'Abonos', 'Cargos', 'Movimiento Garantía', 'Saldo No Disponible', 'Saldo Disponible', 'Saldo Total']
    data = [dict(zip(column_names, match)) for match in matches]

    df = pd.DataFrame(data)
    return df

def find_matches(text, pattern):
    return [m.groups() for m in re.finditer(pattern, text)]

# Streamlit code
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
        # Aquí debes decidir cómo combinar los DataFrames en dfs si hay más de uno.
        # Por ejemplo, puedes concatenarlos uno debajo del otro:
        final_df = pd.concat(dfs, ignore_index=True)

        # Guardar y descargar el archivo Excel
        excel_file = 'Estados_de_Cuenta.xlsx'
        final_df.to_excel(excel_file, index=False)
        st.write(f'Se han descargado {len(dfs)} estados de cuenta en formato Excel.')
