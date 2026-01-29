import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Ventas", layout="wide", page_icon="🚀")

# --- CONEXIÓN A BASE DE DATOS ---
DATABASE_URL = os.getenv('DATABASE_URL')

# Manejo de error si no hay URL (para que no crashee feo)
if not DATABASE_URL:
    st.error("⚠️ No se encontró la variable DATABASE_URL. Configúrala en EasyPanel.")
    st.stop()

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    st.error(f"Error conectando a BD: {e}")
    st.stop()

# --- ESTADO DE LA SESIÓN (MEMORIA) ---
# Usamos esto para recordar cuántos leads teníamos la última vez y comparar
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = 0

# --- TÍTULO PRINCIPAL ---
st.title("🚀 Monitor de Leads en Tiempo Real")
st.markdown("---")

# Contenedor principal que se refrescará
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # 1. CONSULTAR DATOS
            query = "SELECT * FROM leads ORDER BY created_at DESC LIMIT 10"
            df = pd.read_sql(query, engine)
            
            current_count = len(df)

            # 2. LÓGICA DE SIMULACIÓN DE CORREO
            # Si hay más filas ahora que la última vez, simulamos la llegada
            if current_count > st.session_state.last_row_count and st.session_state.last_row_count > 0:
                
                # Simulación visual de espera (como si estuviera leyendo el correo)
                with st.spinner('📨 Recibiendo nuevo correo... Analizando datos con IA...'):
                    time.sleep(2) # Pausa dramática de 2 segundos
                
                # Notificación flotante
                st.toast('¡Nuevo Lead detectado y procesado!', icon='✅')
            
            # Actualizamos el contador en memoria
            st.session_state.last_row_count = current_count

            # 3. MÉTRICAS
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Leads", f"{current_count}")
            
            hot_count = len(df[df['clasificacion_ia'] == 'Hot'])
            col2.metric("🔥 Hot Leads", hot_count)
            
            # Ejemplo de métrica extra para diseño
            col3.metric("📡 Estado del Sistema", "Activo")

            # 4. TABLA PRINCIPAL CON DISEÑO MEJORADO
            st.subheader("📋 Bitácora de Asignación Reciente")
            
            st.dataframe(
                df[['created_at', 'nombre', 'clasificacion_ia', 'vendedor_asignado', 'status_step', 'progress']],
                column_config={
                    "created_at": st.column_config.DatetimeColumn(
                        "Creación",   # <--- CAMBIO DE NOMBRE AQUÍ
                        format="D MMM YYYY, h:mm a"
                    ),
                    "nombre": "Nombre del Cliente",
                    "clasificacion_ia": st.column_config.TextColumn(
                        "Clasificación IA",
                        help="Clasificación basada en el sentimiento del correo"
                    ),
                    "vendedor_asignado": "Vendedor",
                    "status_step": "Estatus Actual",
                    "progress": st.column_config.ProgressColumn(
                        "Progreso", 
                        format="%d%%", 
                        min_value=0, 
                        max_value=100
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.warning("⏳ Esperando conexión o datos... (Asegúrate que la tabla 'leads' exista)")
            # st.write(e) # Descomentar para ver el error técnico si falla

    # Intervalo de actualización (Polling)
    time.sleep(2)
