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
