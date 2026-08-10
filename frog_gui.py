import streamlit as st
import numpy as np
import pandas as pd
import time

# ==========================================
# KERNEL FROG v2.1 // ESCALA EXPANSIVA (16x16 / 256 sensores)
# ==========================================
N_FILAS = 16
N_COLUMNAS = 16
TOTAL_SENSORES = N_FILAS * N_COLUMNAS

st.set_page_config(
    page_title="Kernel FROG v2.1 // 256 Nodos",
    page_icon="🐸",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #262730; }
    </style>
""", unsafe_allow_html=True)

st.title("🐸 KERNEL FROG v2.1 // ML WEB DASHBOARD (256 SENSORES)")

# Inicialización de Estados escalados a 16x16
if 'fases' not in st.session_state:
    st.session_state.fases = np.random.uniform(0, 2 * np.pi, TOTAL_SENSORES)
if 'historial' not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=['Ciclo', 'Actual', 'Prediccion_ML'])
if 'ciclo_actual' not in st.session_state:
    st.session_state.ciclo_actual = 0
if 'eventos' not in st.session_state:
    st.session_state.eventos = []

# Sidebar / Panel de Control
with st.expander("ℹ️ ¿Qué es y para qué sirve el KERNEL FROG?", expanded=False):
    st.markdown(f"""
    Es una syntropische Steuerungs-Middleware desarrollada bajo la arquitectura SACI. 
    Monitoreo activo de **{TOTAL_SENSORES} sensores SYTEC** distribuidos en matriz de {N_FILAS}x{N_COLUMNAS}. 
    Permite auditar sistemas dinámicos en tiempo real, visualizar entropía y controlar la sincronía (K).
    """)

tab_fundamentos, tab_lab = st.tabs(["Fundamentación Técnica", "Laboratorio de Pruebas"])

with tab_lab:
    k_slider = st.slider("Intensidad de sincronía (K)", min_value=0.0, max_value=2.0, value=0.5, step=0.01)
    st.info(f"Variable K ajustada a {k_slider:.2f}. El sistema reconfigurará la fase de los {TOTAL_SENSORES} osciladores.")

st.subheader("Panel de Operador")
if st.button("🚨 FORZAR REBALANCEO DE KERNEL"):
    st.session_state.fases = np.random.uniform(0, 2 * np.pi, TOTAL_SENSORES)
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.eventos.insert(0, f"> {timestamp} | Rebalanceo forzado ejecutado en {TOTAL_SENSORES} sensores.")

# Lógica Dinámica adaptada a 256 sensores
st.session_state.ciclo_actual += 1
dt = 0.1
omega = np.random.normal(1.0, 0.2, TOTAL_SENSORES)
coherence = np.mean(np.exp(1j * st.session_state.fases))
sintropia = np.abs(coherence)
delta_ruido = np.std(np.sin(st.session_state.fases))

st.session_state.fases += dt * (omega + k_slider * sintropia * np.sin(st.session_state.fases - np.mean(st.session_state.fases)))

# Registro de datos y predicción ML simulada
val_actual = float(np.clip(sintropia + np.random.normal(0, 0.05), 0, 1))
val_ml = float(np.clip(val_actual + np.random.normal(0, 0.02), 0, 1))

nuevo_registro = pd.DataFrame({
    'Ciclo': [st.session_state.ciclo_actual],
    'Actual': [val_actual],
    'Prediccion_ML': [val_ml]
})
st.session_state.historial = pd.concat([st.session_state.historial, nuevo_registro], ignore_index=True)

if len(st.session_state.historial) > 30:
    st.session_state.historial = st.session_state.historial.iloc[-30:]

# Métricas Principales (incluyendo conteo de sensores activos)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Sensores Activos", value=TOTAL_SENSORES)
with col2:
    st.metric(label="Ciclo Actual", value=st.session_state.ciclo_actual)
with col3:
    st.metric(label="Promedio K Global", value=f"{k_slider:.2f}")
with col4:
    st.metric(label="Delta Global (Ruido)", value=f"{delta_ruido:.4f}")

st.divider()

# Osciloscopio y Gráfica ML
st.subheader("Osciloscopio // Resonancia del Sistema")
df_chart = st.session_state.historial.set_index('Ciclo')[['Actual', 'Prediccion_ML']]
st.line_chart(df_chart)

# Mapa de Calor de Entropía (Escalado a la matriz de 16 columnas)
st.subheader("📊 Mapa de Calor de Entropía del Sistema (Matriz 16x16)")
matriz_calor = np.random.uniform(0, 1, (16, 16))
df_calor = pd.DataFrame(matriz_calor)
st.dataframe(df_calor.style.background_gradient(cmap='inferno'), use_container_width=True)

# Eventos de Autocuración
st.subheader("⚡ Eventos de Autocuración")
timestamp_live = time.strftime("%H:%M:%S")
if not st.session_state.eventos or st.session_state.ciclo_actual % 5 == 0:
    st.session_state.eventos.insert(0, f"> {timestamp_live} | Sistema Operativo estable ({TOTAL_SENSORES} nodos) | Sincronía R: {sintropia:.4f} | ML: {val_ml:.2f}")

if len(st.session_state.eventos) > 5:
    st.session_state.eventos = st.session_state.eventos[:5]

for evento in st.session_state.eventos:
    st.text(evento)

st.markdown("---")
st.caption("FROG Kernel V2.1 // Hecho en Costa Rica 🇨🇷 JHA 506")
