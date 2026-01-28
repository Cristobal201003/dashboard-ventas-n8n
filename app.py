import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# Configuración de página
st.set_page_config(page_title="Dashboard Ventas", layout="wide")

# CONEXIÓN A BASE DE DATOS
# EasyPanel nos pasará esto como variable de entorno oculta
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    st.error("⚠️ No se encontró la variable DATABASE_URL. Configúrala en EasyPanel.")
    st.stop()

# Conectar
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    st.error(f"Error conectando a BD: {e}")
    st.stop()

st.title("🚀 Monitor de Leads en Tiempo Real")

# Simulación de auto-refresco
placeholder = st.empty()

while True:
    with placeholder.container():
        # Consultar últimos 10 leads
        try:
            df = pd.read_sql("SELECT * FROM leads ORDER BY created_at DESC LIMIT 10", engine)
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", len(df))
            
            hot_count = len(df[df['clasificacion_ia'] == 'Hot'])
            col2.metric("🔥 Hot Leads", hot_count)
            
            # Tabla Principal
            st.subheader("Bitácora de Asignación")
            
            # Formatear tabla para que se vea profesional
            st.dataframe(
                df[['created_at', 'nombre', 'clasificacion_ia', 'vendedor_asignado', 'status_step', 'progress']],
                column_config={
                    "progress": st.column_config.ProgressColumn("Progreso", format="%d%%", min_value=0, max_value=100),
                    "vendedor_asignado": "Vendedor",
                    "clasificacion_ia": "Clasificación"
                },
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.warning("Esperando datos... (Asegúrate que la tabla 'leads' exista en la BD)")
            st.write(e)

    time.sleep(2) # Refrescar cada 2 segundos
