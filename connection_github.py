import pandas as pd
import requests
import streamlit as st
import io
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

# Reemplaza con los detalles de tu repositorio
GITHUB_USERNAME = "Margeo2"  # Tu usuario de GitHub
GITHUB_REPO = "informe-mvd"  # Nombre de tu repositorio
GITHUB_BRANCH = "master"       # Rama donde están los archivos
# Usa el token desde Streamlit secrets
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or st.secrets["GITHUB_TOKEN"]

if not GITHUB_TOKEN:
    st.error("El token de GitHub (GITHUB_TOKEN) no está configurado. Asegúrate de definirlo como una variable de entorno.")
    raise ValueError("El token GITHUB_TOKEN es obligatorio para acceder a repositorios privados.")

def get_github_file_url(repo: str, branch: str, file_path: str, username: str) -> str:
    """
    Construye la URL de descarga de un archivo desde GitHub.
    """
    return f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/{file_path}"

#def get_github_file_api_url(GITHUB_REPO: str, GITHUB_BRANCH: str, file_path: str, GITHUB_USERNAME: str) -> str:
#    """
#    Construye la URL de la API de GitHub para acceder a un archivo.
#    """
#    return f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file_path}?ref={GITHUB_BRANCH}"

@st.cache_data
def load_parquet_from_github(file_path: str, columns: list = None) -> pd.DataFrame:
    """
    Carga un archivo Parquet desde un repositorio de GitHub como un DataFrame de pandas.

    Args:
        file_path (str): Ruta del archivo dentro del repositorio.
        columns (list, optional): Lista de columnas a cargar. Por defecto, carga todas.

    Returns:
        pd.DataFrame: DataFrame con los datos del archivo Parquet.
    """
    try:
        # Construir la URL del archivo en GitHub
        url = get_github_file_url(GITHUB_REPO, GITHUB_BRANCH, file_path, GITHUB_USERNAME)
        headers = {}

        # Configurar cabecera para repositorios privados (si aplica)
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"  # Token para autenticar

        # Descargar el archivo desde GitHub
        response = requests.get(url, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            st.error(f"Error al descargar el archivo '{file_path}'. HTTP {response.status_code} - {response.text}")
            raise FileNotFoundError(
                f"No se pudo descargar el archivo '{file_path}' desde GitHub. "
                f"Respuesta HTTP: {response.status_code}. Detalles: {response.text}"
            )

        # Cargar el archivo Parquet en memoria
        parquet_file = io.BytesIO(response.content)
        try:
            df = pd.read_parquet(parquet_file, columns=columns)
        except ImportError as e:
            raise ImportError(
                "No se pudo leer el archivo Parquet. Asegúrate de tener instaladas las bibliotecas 'pyarrow' o 'fastparquet'."
            ) from e

        return df

    except requests.exceptions.RequestException as e:
        st.error("Error al realizar la solicitud al repositorio de GitHub.")
        st.error(f"Detalles: {e}")
        return None

    except FileNotFoundError as e:
        st.error(f"Archivo no encontrado: {e}")
        return None

    except Exception as e:
        st.error(f"Error desconocido al cargar los datos desde GitHub: {e}")
        return None

def get_file_update_date_from_github(file_path: str) -> str:
    """
    Obtiene una estimación de la última fecha de actualización de un archivo en GitHub.
    Nota: La fecha exacta de un archivo no se puede obtener directamente desde la URL cruda.
    Para más precisión, usa la API de GitHub (requieres autenticación).
    """
    if not GITHUB_TOKEN:
        return "Fecha desconocida (autenticación requerida para verificar)"

    try:
        # URL de la API para obtener el archivo
        api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/commits"
        params = {"path": file_path, "sha": GITHUB_BRANCH}
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        }

        # Llamada a la API de GitHub
        response = requests.get(api_url, headers=headers, params=params)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            raise FileNotFoundError(f"No se pudo obtener la fecha del archivo '{file_path}'. HTTP {response.status_code}")

        # Extraer la fecha del último commit
        commit_data = response.json()
        if len(commit_data) == 0:
            return "Fecha desconocida (sin commits para el archivo)"

        last_commit_date = commit_data[0]['commit']['author']['date']
        return pd.to_datetime(last_commit_date).strftime('%d-%m-%Y')

    except Exception as e:
        st.error(f"Error al obtener la fecha de actualización desde GitHub: {e}")
        return "Fecha desconocida"

def optimize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Optimiza un DataFrame reduciendo el tamaño de las columnas numéricas
    y convirtiendo cadenas de texto a categorías.
    """
    for col in dataframe.select_dtypes(include=["float"]):
        # Convertir a float32 y manejar NaN
        dataframe[col] = pd.to_numeric(dataframe[col], downcast="float")
    for col in dataframe.select_dtypes(include=["int"]):
        # Convertir a int32
        dataframe[col] = pd.to_numeric(dataframe[col], downcast="integer")
    for col in dataframe.select_dtypes(include=["object"]):
        # Convertir texto a categoría si aplica
        num_unique_values = dataframe[col].nunique()
        num_total_values = len(dataframe[col])
        if num_unique_values / num_total_values < 0.5:
            dataframe[col] = dataframe[col].astype("category")
    return dataframe
