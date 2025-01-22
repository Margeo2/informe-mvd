import streamlit as st

# Estilos CSS para el encabezado y la visualización de las tablas
csstitulo = """
.custom-header {
    font-family: Arial, sans-serif;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    color: #333;
}

.custom-header .updated-text {
    font-size: 14px;
    color: #FF5733;
}

.custom-header .date-text {
    font-size: 18px;
    color: #2C3E50;
}
"""

def apply_custom_css():
    """
    Aplica los estilos CSS personalizados para ajustar la visualización de las tablas y el cuadro de texto.
    """
    st.markdown("""
    <style>
        /* Modificar tamaño de la grilla df_filtrado */
        .dataframe {
            width: 80% !important;   /* Ancho del 80% */
            margin: auto;
            font-size: 14px;         /* Tamaño de fuente de las celdas */
        }

        /* Modificar tamaño de la cabecera de la grilla */
        .dataframe thead th {
            font-size: 14px !important;
            text-align: center; /* Centrado */    
        }

        /* Estilo personalizado para el Titulo del cuadro df_grouped (Desembolsos Mas Vida Digna) */
        .df_grouped_header {
            font-size: 18px; /* Tamaño de la fuente para el cuadro df_grouped */
            color: #333;  /* Color para el nombre */
            font-weight: bold; /* Negrita */
            text-align: center; /* Centrado */
        }
    </style>
    """, unsafe_allow_html=True)


# CSS para organizar las tablas una al lado de la otra
csstabla = """
.table-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;  /* Espacio entre las tablas */
    width: 100%;  /* Hace que el contenedor ocupe todo el ancho disponible */
}

.table-container .table {
    width: 48%;  /* Ajuste del tamaño de las tablas */
}
"""

# CSS para asegurar que las tablas ocupen todo el ancho disponible
csstablafiltro = """
.table-container {
    width: 100%;  /* Hace que el contenedor ocupe todo el ancho disponible */
    overflow-x: auto;  /* Permite desplazamiento horizontal si la tabla es muy ancha */
}

.stDataFrame > div {
    width: 100% !important;  /* Asegura que el ancho de la tabla sea 100% */
}

.stDataFrame table {
    width: 100% !important;  /* Hace que la tabla ocupe todo el ancho */
    table-layout: fixed;  /* Hace que las celdas se distribuyan uniformemente */
}
"""