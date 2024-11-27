import streamlit as st
from supabase_connection import connect_supabase, load_parquet_from_supabase, get_file_update_date
from data_processing import group_by_program_type, filter_by_date
from file_export import download_excel
import pandas as pd
from module_css import apply_custom_css

# Llamamos a la función que aplica el CSS
apply_custom_css()

# Conectar a Supabase
client = connect_supabase()

# Parámetros de archivo
bucket_name = "INFO"
file_name = "VT_NOMINA_REP_RECUPERO_X_ANIO_MVD.parquet"
file_name_calendario = "VT_RECUPERO_CALENDARIO.parquet"

# Obtener fecha de actualización
update_date = get_file_update_date(client, bucket_name, file_name)
st.markdown(f"**INFORME** \n\n MAS VIDA DIGNA - LO TENGO - SEMILLA  \n\n Actualizado al **{update_date}**")

# Cargar datos de VT_NOMINA_REP_RECUPERO_X_ANIO_MVD
df = load_parquet_from_supabase(client, bucket_name, file_name)
if df is not None:
    # Agrupar datos
    df_grouped = group_by_program_type(df)
    # Mostrar el cuadro agrupado con nombre personalizado
    st.markdown('<p class="df_grouped_header">Resumen por TIPO_PROGRAMA</p>', unsafe_allow_html=True)
    st.dataframe(df_grouped)

# Cargar y filtrar datos de VT_RECUPERO_CALENDARIO
df_calendario = load_parquet_from_supabase(client, bucket_name, file_name_calendario)
if df_calendario is not None:
    if 'PERIODO_CUOTA' in df_calendario.columns:
        # Convertir PERIODO_CUOTA a datetime
        df_calendario['PERIODO_CUOTA'] = pd.to_datetime(df_calendario['PERIODO_CUOTA'], format='%m/%Y')
        
        # Crear columnas separadas para mes y año
        df_calendario['MES'] = df_calendario['PERIODO_CUOTA'].dt.month
        df_calendario['AÑO'] = df_calendario['PERIODO_CUOTA'].dt.year
        
        #df_calendario['AÑO'] = df_calendario['AÑO'].astype(str).str.replace(',', '', regex=False)#.astype(int)

        # Verificar que la conversión se hizo correctamente
        st.write(f"Tipo de dato de la columna 'AÑO' después de la conversión: {df_calendario['AÑO'].dtype}")

        # Reordenar las columnas, colocando 'AÑO' y 'MES' al principio
        cols = ['AÑO', 'MES'] + [col for col in df_calendario.columns if col not in ['AÑO', 'MES']]
        df_calendario = df_calendario[cols]
        
        # Eliminar la columna 'PERIODO_CUOTA'
        #df_calendario = df_calendario.drop(columns=['PERIODO_CUOTA'])

        # Filtros por mes y año en Streamlit
        meses_disponibles = sorted(df_calendario['MES'].unique())
        anios_disponibles = sorted(df_calendario['AÑO'].unique())
        
        # Selectores en la barra lateral para el mes y año
        st.sidebar.header("RECUPERO \n Filtros por Mes y Año")
        mes_inicio = st.sidebar.selectbox("Selecciona el Mes de inicio", meses_disponibles)
        anio_inicio = st.sidebar.selectbox("Selecciona el Año de inicio", anios_disponibles)
        mes_fin = st.sidebar.selectbox("Selecciona el Mes de fin", meses_disponibles)
        anio_fin = st.sidebar.selectbox("Selecciona el Año de fin", anios_disponibles)

        # Crear fechas de inicio y fin
        fecha_inicio = pd.Timestamp(year=anio_inicio, month=mes_inicio, day=1)
        fecha_fin = pd.Timestamp(year=anio_fin, month=mes_fin, day=1) + pd.offsets.MonthEnd()

        # Filtrar por fechas
        df_filtrado = filter_by_date(df_calendario, fecha_inicio, fecha_fin)
        st.write(f"Datos filtrados desde {fecha_inicio.strftime('%d-%m-%Y')} hasta {fecha_fin.strftime('%d-%m-%Y')}:")
        st.dataframe(df_filtrado)

        # Botón para descargar como Excel
        download_excel(df_filtrado, fecha_inicio, fecha_fin)
    else:
        st.error("La columna 'PERIODO_CUOTA' no existe en el archivo.")