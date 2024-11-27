from supabase import create_client, Client
import pandas as pd
import io
import streamlit as st

SUPABASE_URL = "https://ukmhibmggfvklxwftnuo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrbWhpYm1nZ2Z2a2x4d2Z0bnVvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjExNjk2MiwiZXhwIjoyMDQ3NjkyOTYyfQ.nZwRZDlUwtxgzYueW6UXydDccKL78INiQIoYmU1r-74"


def connect_supabase() -> Client:
    """Establece la conexión con Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_parquet_from_supabase(client: Client, bucket: str, file_path: str) -> pd.DataFrame:
    """Carga un archivo Parquet desde Supabase."""
    try:
        response = client.storage.from_(bucket).download(file_path)
        if not isinstance(response, bytes):
            raise Exception("El archivo no se descargó correctamente o está vacío.")
        parquet_file = io.BytesIO(response)
        return pd.read_parquet(parquet_file)
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

def get_file_update_date(client: Client, bucket: str, file_path: str) -> str:
    """Obtiene la fecha de la última actualización de un archivo en Supabase."""
    try:
        files = client.storage.from_(bucket).list()
        for file in files:
            if file['name'] == file_path:
                last_modified = file['updated_at']
                return pd.to_datetime(last_modified).strftime('%d-%m-%Y')
        raise FileNotFoundError(f"El archivo '{file_path}' no se encontró.")
    except Exception as e:
        st.error(f"Error al obtener la fecha de actualización: {e}")
        return "Fecha desconocida"
