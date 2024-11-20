import streamlit as st
from supabase import create_client, Client
import pandas as pd
import io

# Configuración de Supabase
SUPABASE_URL = "https://ukmhibmggfvklxwftnuo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrbWhpYm1nZ2Z2a2x4d2Z0bnVvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjExNjk2MiwiZXhwIjoyMDQ3NjkyOTYyfQ.nZwRZDlUwtxgzYueW6UXydDccKL78INiQIoYmU1r-74"

def connect_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_parquet_from_supabase(client: Client, bucket: str, file_path: str) -> pd.DataFrame:
    try:
        # Descarga el archivo Parquet desde Supabase
        response = client.storage.from_(bucket).download(file_path)
        
        # Verificar que la descarga fue exitosa
        if isinstance(response, bytes):
            # Usar io.BytesIO para leer el archivo binario en memoria
            parquet_file = io.BytesIO(response)
            
            # Leer el archivo Parquet con pandas
            return pd.read_parquet(parquet_file)
        else:
            raise Exception("No se pudo descargar el archivo correctamente.")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

# Configuración de Streamlit
st.title("Informe Interactivo con Streamlit y Supabase")

# Conectar a Supabase
client = connect_supabase()

# Cargar los datos
bucket_name = "INFO"
file_name = "VT_NOMINA_REP_RECUPERO_X_ANIO_MVD.parquet"

# Cargar y mostrar los datos
df = load_parquet_from_supabase(client, bucket_name, file_name)


# Procesar los datos después de cargarlos

if df is not None:
    # Agrupar por TIPO_PROGRAMA y contar ID_INSCRIPCION
    df_grouped = df.groupby('TIPO_PROGRAMA').agg({'ID_INSCRIPCION': 'nunique'}).reset_index()
    
    # Renombrar la columna de conteo
    df_grouped = df_grouped.rename(columns={'ID_INSCRIPCION': 'COUNT_INSCRIPCIONES'})


# Mostrar los resultados en una tabla interactiva
if df_grouped is not None:
    st.write("Conteo de Inscripciones por Tipo de Programa:")
    st.dataframe(df_grouped)





