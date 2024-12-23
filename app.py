import streamlit as st
from supabase_connection import connect_supabase, load_parquet_from_supabase, get_file_update_date
from data_processing import group_by_program_type, group_by_desembolso, filter_by_date, process_data
from file_export import download_excel
import pandas as pd
from module_css import apply_custom_css, csstitulo, csstabla, csstablafiltro
import data_processing

# Llamamos a la función que aplica el CSS
apply_custom_css()

# Conectar a Supabase
client = connect_supabase()

# Parámetros de archivo
bucket_name = "INFO"
file_name = "VT_NOMINA_REP_RECUPERO_X_ANIO_MVD.parquet"
file_name_calendario = "VT_RECUPERO_CALENDARIO.parquet"

# Aplicar el CSS al markdown
st.markdown(f'<style>{csstitulo}</style>', unsafe_allow_html=True)

# Obtener fecha de actualización
update_date = get_file_update_date(client, bucket_name, file_name)
st.markdown(
    f"""
    <div class="custom-header">
        INFORME  <br>
        MAS VIDA DIGNA - LO TENGO - SEMILLA <br>
        <span class="updated-text">Actualizado al</span>
        <b class="date-text">{update_date}</b>
    </div>
    """,
    unsafe_allow_html=True,
)

# Crear un contenedor para las tablas (usando el CSS definido)
st.markdown('<div class="table-container">', unsafe_allow_html=True)

# Aplicar el CSS al markdown
st.markdown(f'<style>{csstabla}</style>', unsafe_allow_html=True)

# Cargar datos de VT_NOMINA_REP_RECUPERO_X_ANIO_MVD
df = load_parquet_from_supabase(client, bucket_name, file_name)

if df is not None:
    # Agrupar datos
    df_grouped = group_by_program_type(df)
    
    # Filtrado ID_DESEMBOLSO x MAS VIDA DIGNA
    try:
        df_procesado = process_data(df, filtro_tipo_programa="MVD")

        # Mostrar las tablas una al lado de la otra usando el contenedor
        st.markdown(
            """
            <div class="table-container">
                <div class="table">
                    <p class="df_grouped_header">Resumen - Programas</p>
                    {0}
                </div>
                <div class="table">
                    <p class="df_grouped_header">Resumen - Desembolsos Mas Vida Digna</p>
                    {1}
                </div>
            </div>
            """.format(df_grouped.to_html(index=False), df_procesado.to_html(index=False)),
            unsafe_allow_html=True
        )
        
    except ValueError as e:
        # Manejar errores en caso de que las columnas necesarias no estén presentes
        st.error(f"Error al procesar los datos: {str(e)}")
else:
    st.error("No se pudo cargar el archivo desde Supabase.")      

# Cerrar el contenedor
st.markdown('</div>', unsafe_allow_html=True)        

# Crear un contenedor para las tablas (usando el CSS definido)
st.markdown('<div class="table-container">', unsafe_allow_html=True)

# Aplicar el CSS al markdown
st.markdown(f'<style>{csstablafiltro}</style>', unsafe_allow_html=True)

# Cargar y filtrar datos de VT_RECUPERO_CALENDARIO
df_calendario = load_parquet_from_supabase(client, bucket_name, file_name_calendario)
if df_calendario is not None:
    if 'PERIODO_CUOTA' in df_calendario.columns:
        # Convertir PERIODO_CUOTA a datetime
        df_calendario['PERIODO_CUOTA'] = pd.to_datetime(df_calendario['PERIODO_CUOTA'], format='%m/%Y')
        
        # Crear columnas separadas para mes y año
        df_calendario['MES'] = df_calendario['PERIODO_CUOTA'].dt.month
        df_calendario['AÑO'] = df_calendario['PERIODO_CUOTA'].dt.year
        
        # Reordenar las columnas, colocando 'AÑO' y 'MES' al principio
        cols = ['AÑO', 'MES'] + [col for col in df_calendario.columns if col not in ['AÑO', 'MES']]
        df_calendario = df_calendario[cols]
        
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

        # Agregar saltos de línea
        st.write("\n\n\n\n\n\n\n")  # Esto agrega saltos de línea

        # Hacer el texto en negrita y cambiar el tamaño usando HTML
        st.markdown('<p style="font-size: 18px; font-weight: bold;">RECUPERO:</p>', unsafe_allow_html=True)

        st.write(f"Datos filtrados desde {fecha_inicio.strftime('%d-%m-%Y')} hasta {fecha_fin.strftime('%d-%m-%Y')}:")
        
        # Formateo campo AÑO
        df_filtrado['AÑO'] = df_filtrado['AÑO'].astype(str)

        # Eliminar la columna 'PERIODO_CUOTA'
        df_filtrado = df_filtrado.drop(columns=['PERIODO_CUOTA'])
        st.dataframe(df_filtrado)

        # Botón para descargar como Excel
        download_excel(df_filtrado, fecha_inicio, fecha_fin)
    else:
        st.error("La columna 'PERIODO_CUOTA' no existe en el archivo.")

# Cerrar el contenedor
st.markdown('</div>', unsafe_allow_html=True)              

print(dir(data_processing))  
