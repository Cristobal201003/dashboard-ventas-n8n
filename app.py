import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Ventas", layout="wide", page_icon="🚀")

# --- CONEXIÓN A BASE DE DATOS ---
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    st.error("⚠️ No se encontró la variable DATABASE_URL.")
    st.stop()

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    st.error(f"Error conectando a BD: {e}")
    st.stop()

# --- ESTADO DE LA SESIÓN ---
# Inicializamos en -1 para que la primera vez SIEMPRE haga la animación de "Cargando sistema"
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = -1 

st.title("🚀 Monitor de Leads en Tiempo Real")
st.markdown("---")

# Contenedor principal
placeholder = st.empty()

while True:
    try:
        # 1. CONSULTAR DATOS REALES (Siempre consultamos lo más fresco)
        query = "SELECT * FROM leads ORDER BY created_at DESC LIMIT 10"
        df = pd.read_sql(query, engine)
        current_count = len(df)

        # 2. DETECTAR SI LLEGÓ ALGO NUEVO
        # Comparamos lo que acabamos de leer con lo que teníamos guardado
        if current_count > st.session_state.last_row_count:
            
            # --- ZONA DE DRAMA (Solo ocurre si cambió la BD) ---
            
            # Limpiamos el contenedor para mostrar solo la animación
            with placeholder.container():
                
                # Diseño del "Correo Entrante"
                st.markdown("""
                <div style="text-align: center; padding: 50px;">
                    <h1 style='font-size: 60px;'>📨</h1>
                    <h2>Nuevo Correo Detectado...</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Barra de progreso simulada
                bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01) # Simula velocidad de carga
                    bar.progress(i + 1)
                
                st.markdown("<h3 style='text-align: center;'>🤖 Extrayendo datos con IA...</h3>", unsafe_allow_html=True)
                time.sleep(1.5) # Retraso extra para leer el mensaje

            # Actualizamos el estado para que no se repita hasta el próximo correo real
            st.session_state.last_row_count = current_count
            
            # Notificación
            st.toast('¡Base de datos actualizada!', icon='✅')

        # 3. MOSTRAR LA TABLA (Estado Normal)
        # Esto sobrescribe la animación y muestra los datos finales
        with placeholder.container():
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", f"{current_count}")
            hot_count = len(df[df['clasificacion_ia'] == 'Hot'])
            col2.metric("🔥 Hot Leads", hot_count)
            col3.metric("📡 Estado", "Esperando nuevos correos...")

            st.subheader("📋 Bitácora de Asignación Reciente")
            
            st.dataframe(
                df[['created_at', 'nombre', 'clasificacion_ia', 'vendedor_asignado', 'status_step', 'progress']],
                column_config={
                    "created_at": st.column_config.DatetimeColumn(
                        "Creación",
                        format="D MMM YYYY, h:mm a"
                    ),
                    "nombre": "Nombre del Cliente",
                    "clasificacion_ia": st.column_config.TextColumn("Clasificación IA"),
                    "vendedor_asignado": "Vendedor",
                    "status_step": "Estatus Actual",
                    "progress": st.column_config.ProgressColumn(
                        "Progreso", format="%d%%", min_value=0, max_value=100
                    ),
                },
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        with placeholder.container():
            st.warning("⏳ Esperando conexión a la base de datos...")
    
    # Espera 2 segundos antes de volver a consultar a la BD
    time.sleep(2)
