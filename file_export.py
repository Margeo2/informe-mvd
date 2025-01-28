import io
import pandas as pd
import streamlit as st

@st.cache_data
def convertir_a_excel(df: pd.DataFrame) -> bytes:
    """Convierte el DataFrame a un archivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos Filtrados')
    return output.getvalue()

def download_excel(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp, alias: str):
    """Crea un botón para descargar el DataFrame como archivo Excel."""
    if not df.empty:
        archivo_excel = convertir_a_excel(df)
        archivo_nombre = f"{alias}_datos_filtrados_{start_date.strftime('%d-%m-%Y')}_a_{end_date.strftime('%d-%m-%Y')}.xlsx"

        st.download_button(
            label="Descargar datos filtrados en Excel",
            data=archivo_excel,
            file_name=archivo_nombre,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay datos para el rango de fechas seleccionado.")

def download_simple_excel(df: pd.DataFrame, filename):
    """
    Descarga un archivo Excel sin parámetros adicionales.
    """
    if not df.empty:
        archivo_excel = convertir_a_excel(df)
        st.download_button(
            label="Descargar archivo Excel: Inscripciones",
            data=archivo_excel,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay datos para descargar.")