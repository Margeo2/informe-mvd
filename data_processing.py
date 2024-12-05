import pandas as pd

def group_by_program_type(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa el DataFrame por el tipo de programa y cuenta inscripciones únicas."""
    df_grouped = df.groupby('TIPO_PROGRAMA').agg({'ID_INSCRIPCION': 'nunique'}).reset_index()
    df_grouped = df_grouped.rename(columns={'TIPO_PROGRAMA': 'TIPO DE PROGRAMA', 'ID_INSCRIPCION': 'INSCRIPCIONES'})
    total_row = pd.DataFrame({'TIPO DE PROGRAMA': ['TOTAL'], 'INSCRIPCIONES': [df_grouped['INSCRIPCIONES'].sum()]})
    return pd.concat([df_grouped, total_row], ignore_index=True)

def filter_by_date(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Filtra el DataFrame por el rango de fechas proporcionado."""
    return df[(df['PERIODO_CUOTA'] >= start_date) & (df['PERIODO_CUOTA'] <= end_date)]


def filtrar_por_tipo_programa(df: pd.DataFrame, filtro="MVD_II") -> pd.DataFrame:
    """
    Filtra el DataFrame para que sólo incluya filas donde la columna 'Tipo_programa'
    contenga el texto especificado en el parámetro filtro.

    Args:
        df (pd.DataFrame): El DataFrame a filtrar.
        filtro (str): Texto que debe estar contenido en la columna 'Tipo_programa'.

    Returns:
        pd.DataFrame: DataFrame filtrado.
    """
    if 'TIPO_PROGRAMA' not in df.columns:
        raise ValueError("La columna 'TIPO_PROGRAMA' no está presente en el DataFrame.")
    
    # Aplicar el filtro con str.contains
    df_filtrado = df[df['TIPO_PROGRAMA'].str.contains(filtro, case=False, na=False)].copy()
    return df_filtrado
  
def group_by_desembolso(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa el DataFrame por el tipo de desembolsos y calcula el total de inscripciones únicas.
    
    Parámetros:
        df (pd.DataFrame): DataFrame con las columnas 'ID_DESEMBOLSO' e 'ID_INSCRIPCION'.
    
    Retorna:
        pd.DataFrame: DataFrame agrupado con el total de inscripciones y una fila de total.
    """
    if 'ID_DESEMBOLSO' not in df.columns or 'ID_INSCRIPCION' not in df.columns:
        raise ValueError("El DataFrame debe contener las columnas 'ID_DESEMBOLSO' e 'ID_INSCRIPCION'.")
    
     # Crear una copia del DataFrame para evitar el SettingWithCopyWarning
    df = df.copy()

    # Convertir 'ID_DESEMBOLSO' a str antes de agrupar
    df['ID_DESEMBOLSO'] = df['ID_DESEMBOLSO'].astype(str)

    # Agrupar por 'ID_DESEMBOLSO' y contar inscripciones únicas
    df_grouped_desembolso = (
        df.groupby('ID_DESEMBOLSO')
        .agg(INSCRIPCIONES=('ID_INSCRIPCION', 'nunique'))
        .reset_index()
        .rename(columns={'ID_DESEMBOLSO': 'DESEMBOLSO'})
    )

    # Agregar fila con el total
    total_row = pd.DataFrame({'DESEMBOLSO': ['TOTAL'], 'INSCRIPCIONES': [df_grouped_desembolso['INSCRIPCIONES'].sum()]})
        
    # Concatenar el total al DataFrame agrupado
    df_grouped_desembolso = pd.concat([df_grouped_desembolso, total_row], ignore_index=True)

    # Cambiar el nombre de la columna INSCRIPCIONES a una cadena vacía
    df_grouped_desembolso.rename(columns={'INSCRIPCIONES': ''}, inplace=True)

    return df_grouped_desembolso

def process_data(df: pd.DataFrame, filtro_tipo_programa="MVD") -> pd.DataFrame:
    df_filtrado = filtrar_por_tipo_programa(df, filtro=filtro_tipo_programa)
    df_resultado = group_by_desembolso(df_filtrado)
    return df_resultado

