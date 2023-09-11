import re
import streamlit as st
import pdfplumber
import pandas as pd

# Función para extraer texto del PDF
def extract_pdf_text(file_path):
    all_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"
    return all_text

# Función para encontrar coincidencias en el texto extraído
def find_matches_monex(text):
    pattern = re.compile(r'(\d{2}/\w{3})\s+([\w\s]+?)(?:\s+(\d{8}))?\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d+\.\d{2}|\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d+\.\d{2}|-?\d{1,3}(?:,\d{3})*\.\d{2})')
    return [m.groups() for m in re.finditer(pattern, text)]

st.title("Conversor de PDF a Excel")

# Elegir el banco
banco = st.selectbox("Selecciona el banco de tu estado de cuenta:", ["MONEX", "Otro"])

# Subir archivo PDF
uploaded_file = st.file_uploader("Sube tu estado de cuenta en PDF:", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Procesando el archivo PDF..."):
        
        # Extracción de texto del PDF
        text = extract_pdf_text(uploaded_file)
        
        if banco == "MONEX":
            matches = find_matches_monex(text)
        
        # Si tienes más bancos, puedes añadir más condiciones aquí.
        
        column_names = ['Fecha', 'Descripción', 'Referencia', 'Abonos', 'Cargos', 'Movimiento Garantía', 'Saldo No Disponible', 'Saldo Disponible', 'Saldo Total']
        data = [dict(zip(column_names, match)) for match in matches]
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Guardar como archivo Excel
        nombre_archivo = 'Estado_de_Cuenta.xlsx'
        df.to_excel(nombre_archivo, index=False)
        
    st.success(f"Se ha exportado el DataFrame a {nombre_archivo}")
    st.download_button("Descargar archivo Excel", file=nombre_archivo, file_name=nombre_archivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
