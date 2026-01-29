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
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = -1 

st.title("🚀 Monitor de Leads en Tiempo Real")
st.markdown("---")

placeholder = st.empty()

while True:
    try:
        # 1. CONSULTAR DATOS (Aumentamos el límite para tener estadística real)
        # Traemos los últimos 100 para que las gráficas tengan sentido
        query = "SELECT * FROM leads ORDER BY created_at DESC LIMIT 100"
        df = pd.read_sql(query, engine)
        current_count = len(df)

        # 2. DETECTAR SI LLEGÓ ALGO NUEVO (Lógica de animación)
        if current_count > st.session_state.last_row_count:
            
            with placeholder.container():
                # --- ANIMACIÓN DE CORREO ENTRANTE ---
                st.markdown("""
                <div style="text-align: center; padding: 50px;">
                    <h1 style='font-size: 60px;'>📨</h1>
                    <h2>Nuevo Correo Detectado...</h2>
                </div>
                """, unsafe_allow_html=True)
                
                bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    bar.progress(i + 1)
                
                st.markdown("<h3 style='text-align: center;'>🤖 Clasificando y Asignando...</h3>", unsafe_allow_html=True)
                time.sleep(1.5)

            st.session_state.last_row_count = current_count
            st.toast('¡Dashboard actualizado!', icon='✅')

        # 3. MOSTRAR EL DASHBOARD (Estado Normal)
        with placeholder.container():
            
            # --- SECCIÓN 1: RESÚMENES (PRIORIDAD) ---
            st.subheader("📊 Distribución de Leads (Últimos 100)")
            
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

            # TABLA A: LEADS POR ESTADO (Status Step)
            with col_kpi1:
                st.markdown("**Por Estado**")
                if not df.empty:
                    df_status = df['status_step'].value_counts().reset_index()
                    df_status.columns = ['Estado', 'Total']
                    st.dataframe(
                        df_status, 
                        hide_index=True, 
                        use_container_width=True,
                        column_config={
                            "Total": st.column_config.ProgressColumn(
                                "Volumen", 
                                format="%d", 
                                min_value=0, 
                                max_value=int(df_status['Total'].max())
                            )
                        }
                    )

            # TABLA B: LEADS POR VENDEDOR
            with col_kpi2:
                st.markdown("**Por Vendedor**")
                if not df.empty:
                    df_vendor = df['vendedor_asignado'].value_counts().reset_index()
                    df_vendor.columns = ['Vendedor', 'Asignados']
                    st.dataframe(
                        df_vendor, 
                        hide_index=True, 
                        use_container_width=True,
                         column_config={
                            "Asignados": st.column_config.ProgressColumn(
                                "Carga", 
                                format="%d", 
                                min_value=0, 
                                max_value=int(df_vendor['Asignados'].max())
                            )
                        }
                    )

            # TABLA C: LEADS POR CLASIFICACIÓN (HOT/WARM/COLD)
            with col_kpi3:
                st.markdown("**Por Clasificación IA**")
                if not df.empty:
                    df_class = df['clasificacion_ia'].value_counts().reset_index()
                    df_class.columns = ['Clasificación', 'Total']
                    st.dataframe(
                        df_class, 
                        hide_index=True, 
                        use_container_width=True,
                        column_config={
                            "Total": st.column_config.Column(
                                "Cantidad",
                                width="small"
                            )
                        }
                    )

            st.divider()

            # --- SECCIÓN 2: BITÁCORA DETALLADA ---
            st.subheader("📋 Bitácora de Entrada Reciente")
            
            st.dataframe(
                df[['created_at', 'nombre', 'clasificacion_ia', 'vendedor_asignado', 'status_step', 'progress']].head(10), # Solo mostramos 10 en la tabla detallada
                column_config={
                    "created_at": st.column_config.DatetimeColumn("Creación", format="D MMM, h:mm a"),
                    "nombre": "Cliente",
                    "clasificacion_ia": "IA",
                    "vendedor_asignado": "Vendedor",
                    "status_step": "Estado",
                    "progress": st.column_config.ProgressColumn("Progreso", format="%d%%"),
                },
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        with placeholder.container():
            st.warning("⏳ Esperando datos...")
            # st.write(e) # Descomentar para debug
    
    time.sleep(2)
