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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    st.error("El token de GitHub (GITHUB_TOKEN) no está configurado. Asegúrate de definirlo como una variable de entorno.")
    raise ValueError("El token GITHUB_TOKEN es obligatorio para acceder a repositorios privados.")

def get_github_file_url(repo: str, branch: str, file_path: str, username: str) -> str:
    """
    Construye la URL de descarga de un archivo desde GitHub.
    """
    return f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/{file_path}"


def load_parquet_from_github(file_path: str) -> pd.DataFrame:
    """
    Carga un archivo Parquet desde un repositorio de GitHub como un DataFrame de pandas.
    """
    try:
        # Construir la URL del archivo en GitHub
        url = get_github_file_url(GITHUB_REPO, GITHUB_BRANCH, file_path, GITHUB_USERNAME)
        headers = {}

        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"  # Si el repo es privado

        # Descargar el archivo desde GitHub
        response = requests.get(url, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            raise FileNotFoundError(f"No se pudo descargar el archivo '{file_path}'. HTTP {response.status_code}")

        # Leer el archivo Parquet
        parquet_file = io.BytesIO(response.content)
        return pd.read_parquet(parquet_file)

    except Exception as e:
        st.error(f"Error al cargar los datos desde GitHub: {e}")
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
