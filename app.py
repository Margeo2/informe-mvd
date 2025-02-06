import streamlit as st
from connection_github import load_parquet_from_github, get_file_update_date_from_github, optimize_dataframe
from data_processing import group_by_program_type, filter_by_date, process_data
from file_export import download_excel, convertir_a_excel, download_simple_excel
import pandas as pd
from module_css import apply_custom_css, csstitulo, csstabla, csstablafiltro
import data_processing

# Aplicar estilos CSS personalizados
###PRUEBAAA
apply_custom_css()

# Parámetros de archivo y vistas disponibles

file_path = "VT_NOMINA_REP_RECUPERO_X_ANIO_MVD_LTGO_SEMILLA.parquet"
vistas = {
    "Mas Vida Digna": "VT_RECUPERO_CALENDARIO_MVD.parquet",
    "Lo Tengo": "VT_RECUPERO_CALENDARIO_LTGO.parquet",
    "Semilla": "VT_RECUPERO_CALENDARIO_SEMILLA.parquet",
}

# Título personalizado en la barra lateral
st.sidebar.markdown('<p style="font-size: 20px; font-weight: bold;">RECUPERO</p>', unsafe_allow_html=True)

# Selector de vista en la barra lateral
vista_seleccionada = st.sidebar.selectbox("Selecciona Programa", list(vistas.keys()))
# Cargar datos solo cuando el usuario selecciona algo
if vista_seleccionada:
    file_path2 = vistas[vista_seleccionada]
    df_calendario = load_parquet_from_github(file_path2)
    # Validar que los datos se cargaron correctamente
    if df_calendario is None:
        st.error(f"Error al cargar los datos del archivo {file_path2}. Revisa la conexión o el repositorio.")
        st.stop()
    df_calendario = optimize_dataframe(df_calendario)  # Optimiza el DataFrame

#df_calendario = data

# Aplicar el CSS al markdown
st.markdown(f'<style>{csstitulo}</style>', unsafe_allow_html=True)

# Encabezado del informe
update_date = get_file_update_date_from_github(file_path)
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

# Cargar datos de VT_NOMINA_REP_RECUPERO_X_ANIO_MVD_LTGO_SEMILLA
df_nomina = load_parquet_from_github(file_path)
if df_nomina is None:
    st.error(f"Error al cargar los datos del archivo {file_path}. Revisa la conexión o el repositorio.")
    st.stop()
df = optimize_dataframe(df_nomina)

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
    st.error("No se pudo cargar el archivo principal desde GitHub.")      

# Cerrar el contenedor
st.markdown('</div>', unsafe_allow_html=True)        

# Crear un contenedor para las tablas (usando el CSS definido)
st.markdown('<div class="table-container">', unsafe_allow_html=True)

# Aplicar el CSS al markdown
st.markdown(f'<style>{csstablafiltro}</style>', unsafe_allow_html=True)

# Ruta del archivo
archivo_inscripciones = "T_INSCRIPCIONES_MVD_LTGO_SEMILLA.parquet"

# Lista de columnas necesarias (ajusta según tus necesidades)
columnas_necesarias = ["ID_INSCRIPCION", "ID_VIN", "ID_GRUPO_UNICO", "NRO_DOCUMENTO", "ID_SEXO", "PAI_COD_PAIS", "ID_NUMERO", "TIPO_PROGRAMA", "ID_PROGRAMA"]  # Cambia estos nombres según tu archivo.

# Carga y optimiza el DataFrame
@st.cache_data
def cargar_datos_inscripciones(file_path, columnas):
    """
    Carga el archivo Parquet de inscripciones con las columnas necesarias.
    """
    data = load_parquet_from_github(file_path, columns=columnas)
    return optimize_dataframe(data)

# Carga los datos al DataFrame
df_inscripciones = cargar_datos_inscripciones(archivo_inscripciones, columnas_necesarias)

# Configurar el tamaño del título usando HTML y CSS
st.markdown(
    """
    <h1 style='text-align: center; font-size: 18px;'>Inscripciones de Programas</h1>
    """,
    unsafe_allow_html=True
)

# Convertir solo las columnas numéricas a cadenas sin comas (solo para visualización)
df_display = df_inscripciones.head(5).copy()  # Mostrar solo los primeros 5 registros

# Identificar columnas numéricas (int, float)
numeric_cols = df_display.select_dtypes(include=['int', 'float']).columns

# Aplicar el formateo solo a las columnas numéricas
for col in numeric_cols:
    df_display[col] = df_display[col].apply(lambda x: f"{x:.0f}" if pd.notnull(x) else "")

# Mostrar el dataframe sin comas
st.dataframe(df_display, use_container_width=True)

download_simple_excel(df_inscripciones, "T_INSCRIPCIONES_MVD_LTGO_SEMILLA.xlsx")  # Descargar el archivo

#*******************************************************************************************************************
# Cargar datos de la vista seleccionada
st.markdown(f"### Recupero de: {vista_seleccionada}")

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
        st.sidebar.header("Filtros por Mes y Año")
        mes_inicio = st.sidebar.selectbox("Selecciona el Mes de inicio", meses_disponibles, index=meses_disponibles.index(9))
        anio_inicio = st.sidebar.selectbox("Selecciona el Año de inicio", anios_disponibles, index=anios_disponibles.index(2023))
        mes_fin = st.sidebar.selectbox("Selecciona el Mes de fin", meses_disponibles)
        anio_fin = st.sidebar.selectbox("Selecciona el Año de fin", anios_disponibles, index=anios_disponibles.index(2024))
        
        # Botón "Actualizar Cache" en la barra lateral
        if st.sidebar.button("Actualizar Cache"):
            st.cache_data.clear()
            st.sidebar.success("¡Cache actualizado correctamente!")

        # Crear fechas de inicio y fin
        fecha_inicio = pd.Timestamp(year=anio_inicio, month=mes_inicio, day=1)
        fecha_fin = pd.Timestamp(year=anio_fin, month=mes_fin, day=1) + pd.offsets.MonthEnd()

        # Filtrar por fechas
        df_filtrado = filter_by_date(df_calendario, fecha_inicio, fecha_fin)

        # Agregar saltos de línea
        st.write("\n\n\n\n\n\n\n")  # Esto agrega saltos de línea

        # Hacer el texto en negrita y cambiar el tamaño usando HTML
        #st.markdown('<p style="font-size: 18px; font-weight: bold;">RECUPERO:</p>', unsafe_allow_html=True)

        st.write(f"Datos filtrados desde {fecha_inicio.strftime('%d-%m-%Y')} hasta {fecha_fin.strftime('%d-%m-%Y')}:")
        
        # Formateo campo AÑO
        df_filtrado.loc[:, 'AÑO'] = df_filtrado['AÑO'].astype(str)

        # Eliminar la columna 'PERIODO_CUOTA'
        df_filtrado = df_filtrado.drop(columns=['PERIODO_CUOTA'])
        st.dataframe(df_filtrado)

        # Botón para descargar como Excel
        download_excel(df_filtrado, fecha_inicio, fecha_fin, alias=vista_seleccionada)
    else:
        st.error("La columna 'PERIODO_CUOTA' no existe en el archivo.")

# Cerrar el contenedor
st.markdown('</div>', unsafe_allow_html=True)              

print(dir(data_processing))  