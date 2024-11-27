import streamlit as st

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
            font-size: 16px !important;
        }

        /* Estilo personalizado para el nombre del cuadro df_grouped */
        .df_grouped_header {
            font-size: 18px; /* Tamaño de la fuente para el cuadro df_grouped */
            color: #4CAF50;  /* Color verde para el nombre */
            font-weight: bold; /* Negrita */
            text-align: center; /* Centrado */
        }

        /* Estilo para la tabla filtrada (df_filtrado) */
        .stDataFrame {
            width: 100% !important;
            margin: auto;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
