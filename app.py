import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Ventas", layout="wide", page_icon="🚀")

# --- CONEXIÓN A BASE DE DATOS ---
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    st.error("⚠️ No se encontró DATABASE_URL.")
    st.stop()

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    st.error(f"Error conectando a BD: {e}")
    st.stop()

# --- ESTADO DE LA SESIÓN ---
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = -1 

# --- FUNCIÓN MÁGICA: STATUS -> PROGRESO ---
# Esta función decide qué porcentaje lleva el lead según su texto de estatus
def calcular_progreso_automatico(df):
    # Definimos las reglas del juego
    reglas = {
        'Nuevo': 10,
        'Correo Recibido': 20,
        'Analizando': 30,
        'Contactado': 50,
        'En Negociación': 75,
        'Cerrado': 100
    }
    
    # 1. Si el status está en las reglas, usa ese número.
    # 2. Si no, usa un valor por defecto (ej. 5%).
    # map() busca el valor, fillna(5) pone 5 si no encuentra el texto
    df['progress'] = df['status_step'].map(reglas).fillna(5)
    return df

# --- SIMULADOR EN BARRA LATERAL (PARA PROBAR QUE SE MUEVE) ---
with st.sidebar:
    st.header("🎮 Control de Prueba")
    st.write("Presiona para avanzar el estatus del último lead y ver subir la barra:")
    
    if st.button("Subir Nivel del Último Lead 🆙"):
        # Esto hace un UPDATE real a tu base de datos solo al último lead
        with engine.connect() as conn:
            # Subimos el estatus artificialmente para probar
            conn.execute(text("""
                UPDATE leads 
                SET status_step = 'En Negociación' 
                WHERE id = (SELECT id FROM leads ORDER BY created_at DESC LIMIT 1)
            """))
            conn.commit()
            st.toast("¡Lead actualizado a 'En Negociación'!", icon="📈")
            time.sleep(1) # Espera pequeña para recargar

st.title("🚀 Monitor de Leads en Tiempo Real")
st.markdown("---")

placeholder = st.empty()

while True:
    try:
        # 1. CONSULTAR DATOS
        query = "SELECT * FROM leads ORDER BY created_at DESC LIMIT 100"
        df = pd.read_sql(query, engine)
        
        # --- APLICAMOS LA LÓGICA DE PROGRESO AQUÍ ---
        # Sobrescribimos la columna 'progress' de la BD con nuestro cálculo en vivo
        if not df.empty:
            df = calcular_progreso_automatico(df)

        current_count = len(df)

        # 2. DETECTAR SI LLEGÓ ALGO NUEVO
        if current_count > st.session_state.last_row_count:
            with placeholder.container():
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
                
                st.markdown("<h3 style='text-align: center;'>🤖 Actualizando Pipeline...</h3>", unsafe_allow_html=True)
                time.sleep(1.5)

            st.session_state.last_row_count = current_count
            st.toast('¡Dashboard actualizado!', icon='✅')

        # 3. MOSTRAR EL DASHBOARD
        with placeholder.container():
            
            # --- SECCIÓN 1: RESÚMENES ---
            st.subheader("📊 Distribución de Leads")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Por Estado**")
                if not df.empty:
                    df_status = df['status_step'].value_counts().reset_index()
                    df_status.columns = ['Estado', 'Total']
                    st.dataframe(df_status, hide_index=True, use_container_width=True,
                        column_config={"Total": st.column_config.ProgressColumn("Volumen", format="%d", min_value=0, max_value=int(df_status['Total'].max()))})

            with col2:
                st.markdown("**Por Vendedor**")
                if not df.empty:
                    df_vendor = df['vendedor_asignado'].value_counts().reset_index()
                    df_vendor.columns = ['Vendedor', 'Asignados']
                    st.dataframe(df_vendor, hide_index=True, use_container_width=True,
                         column_config={"Asignados": st.column_config.ProgressColumn("Carga", format="%d", min_value=0, max_value=int(df_vendor['Asignados'].max()))})

            with col3:
                st.markdown("**Por Clasificación IA**")
                if not df.empty:
                    df_class = df['clasificacion_ia'].value_counts().reset_index()
                    df_class.columns = ['Clasificación', 'Total']
                    st.dataframe(df_class, hide_index=True, use_container_width=True)

            st.divider()

            # --- SECCIÓN 2: BITÁCORA DETALLADA ---
            st.subheader("📋 Bitácora de Entrada Reciente")
            
            # Mostramos las primeras 10
            st.dataframe(
                df[['created_at', 'nombre', 'clasificacion_ia', 'vendedor_asignado', 'status_step', 'progress']].head(10),
                column_config={
                    "created_at": st.column_config.DatetimeColumn("Creación", format="D MMM, h:mm a"),
                    "nombre": "Cliente",
                    "clasificacion_ia": "IA",
                    "vendedor_asignado": "Vendedor",
                    "status_step": "Estado",
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
        with placeholder.container():
            st.warning("⏳ Esperando datos...")
            # st.write(e)
    
    time.sleep(2)
