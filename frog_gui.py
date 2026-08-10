#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FROG KERNEL v2.0 - SISTEMA DE CONTROL SINTRÓPICO & AUDITORÍA EN TIEMPO REAL
Arquitectura SACI / Protocolo FROG - Dashboard de Alta Precisión
"""

import math
import random
import statistics
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dataclasses import dataclass
from typing import List

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FROG Kernel | Control Sintrópico",
    page_icon="🐸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS estilo Consola de Control
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; }
    .stAlert { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MODELO DE DATOS Y LÓGICA CORE
# -----------------------------------------------------------------------------
@dataclass
class SensorSYTEC:
    id: int
    ruido_base: float
    fase: float = 0.0
    delta_local: float = 0.0
    k_actual: float = 0.0
    estado: str = "SINTRÓPICO"

class KernelFROGCore:
    def __init__(self, num_sensores: int = 100):
        self.num_sensores = num_sensores
        
        if "sensors" not in st.session_state:
            st.session_state.sensors = self._inicializar_sensores()
        if "historial" not in st.session_state:
            st.session_state.historial = []
        if "logs" not in st.session_state:
            st.session_state.logs = []
        if "ciclo" not in st.session_state:
            st.session_state.ciclo = 0

    def _inicializar_sensores(self) -> List[SensorSYTEC]:
        sensores = []
        for i in range(1, self.num_sensores + 1):
            ruido = round(5.0 / (i ** 0.5), 4)
            sensores.append(SensorSYTEC(
                id=i,
                ruido_base=ruido,
                fase=round(random.uniform(0, 2 * math.pi), 2),
                k_actual=round(ruido, 4)
            ))
        random.shuffle(sensores)
        return sensores

    def procesar_ciclo(self, factor_sensibilidad: float, umbral_entropia: float):
        st.session_state.ciclo += 1
        ciclo_actual = st.session_state.ciclo
        
        deltas = []
        ks = []
        fases = []

        for sensor in st.session_state.sensors:
            delta_fase = random.uniform(-0.1, 0.1)
            sensor.fase = (sensor.fase + delta_fase) % (2 * math.pi)
            
            perturbacion = sensor.ruido_base * random.uniform(-0.25, 0.25) * factor_sensibilidad
            k_efectivo = abs(sensor.k_actual + perturbacion)
            
            estado_anterior = sensor.estado
            
            if k_efectivo > umbral_entropia or random.random() < 0.05:
                sensor.estado = "ENTRÓPICO"
            else:
                sensor.estado = "SINTRÓPICO"

            if estado_anterior != sensor.estado:
                color_log = "🔴" if sensor.estado == "ENTRÓPICO" else "🟢"
                st.session_state.logs.insert(0, f"[{time.strftime('%H:%M:%S')}] Ciclo {ciclo_actual}: Sensor #{sensor.id:02d} cambió a {sensor.estado} {color_log}")

            sensor.k_actual = round(k_efectivo, 4)
            sensor.delta_local = round(abs(k_efectivo - (sum(ks)/len(ks) if ks else 0.5)), 4)

            deltas.append(sensor.delta_local)
            ks.append(sensor.k_actual)
            fases.append(sensor.fase)

        k_prom = round(statistics.mean(ks), 4)
        delta_prom = round(statistics.mean(deltas), 4)
        coherencia_fase = round(abs(sum(math.cos(f) for f in fases)) / self.num_sensores, 4)
        sintropia_global = round(1.0 / (1.0 + delta_prom), 4)

        st.session_state.historial.append({
            "Ciclo": ciclo_actual,
            "K_Promedio": k_prom,
            "Delta_Global": delta_prom,
            "Coherencia_Fase": coherencia_fase,
            "Sintropia_Indice": sintropia_global,
            "Sensores_Entropicos": sum(1 for s in st.session_state.sensors if s.estado == "ENTRÓPICO")
        })

    def reiniciar(self):
        st.session_state.sensors = self._inicializar_sensores()
        st.session_state.historial = []
        st.session_state.logs = []
        st.session_state.ciclo = 0

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO
# -----------------------------------------------------------------------------
kernel = KernelFROGCore()

# BANNER ENCABEZADO
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.title("🐸")
with col_title:
    st.title("FROG KERNEL — CONTROL SINTRÓPICO")
    st.caption("Middleware SACI | Auditoría y Visualización en Tiempo Real | 100 Sensores SYTEC")

# SECCIÓN EXPLICATIVA DESPLEGABLE
with st.expander("ℹ️ **¿Qué es, para qué sirve, qué hace y qué podría hacer este Kernel?**", expanded=False):
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        ### 🧠 ¿Qué es?
        Es un **middleware y centro de control sintrópico** diseñado bajo la arquitectura **SACI**. Funciona como un motor informático que monitorea y procesa patrones de orden, ruido y sincronía en redes compuestas por múltiples nodos o sensores (Matriz SYTEC).

        ### ⚙️ ¿Para qué sirve?
        Sirve para **auditar, visualizar y corregir la estabilidad de sistemas dinámicos en tiempo real**. Permite detectar rápidamente cuando un nodo sufre variaciones de entropía (desorden o ruido elevado) antes de que afecte la red global.
        """)
        
    with col_b:
        st.markdown("""
        ### 🔄 ¿Qué hace actualmente?
        1. **Monitorea 100 sensores SYTEC** organizados en una matriz interactiva 10x10.
        2. **Mide coeficientes sintrópicos (K) y deltas de ruido** en cada ciclo de simulación.
        3. **Calcula la coherencia de fase global** y la sincronía entre nodos.
        4. **Registra eventos y alertas** en vivo cuando un nodo pasa a estado entrópico (🔴).
        5. **Exporta métricas históricas** en formato CSV para análisis posterior.
        """)

    st.markdown("---")
    st.markdown("""
    ### 🚀 ¿Qué podría hacer en el futuro? (Potencial de Escalabilidad)
    * **Integración con Hardware Real:** Conectarse directamente a redes físicas de sensores IoT, antenas o nodos de red mediante protocolos WebSockets o APIs REST.
    * **Consenso Algorítmico Descentralizado:** Aplicar las métricas de coherencia de fase para validar transacciones o estados en redes entre pares (P2P).
    * **Clonación de Fase Automática:** Implementar algoritmos de autocorrección activa para reequilibrar nodos desajustados de forma autónoma.
    * **Machine Learning / Predicción Entrópica:** Anticipar fallas en los sensores mediante análisis predictivo de series temporales.
    """)

st.divider()

# SIDEBAR: PANEL DE COMANDO
st.sidebar.header("🕹️ Panel de Comando")

run_auto = st.sidebar.toggle("⚡ Ejecución Automática", value=False)
intervalo = st.sidebar.slider("Intervalo de Refresco (s)", 0.1, 2.0, 0.5, step=0.1)

st.sidebar.subheader("⚙️ Parámetros del Kernel")
sensibilidad = st.sidebar.slider("Factor de Perturbación", 0.1, 3.0, 1.0, step=0.1)
umbral_critico = st.sidebar.slider("Umbral Entrópico Crítico", 0.5, 5.0, 2.5, step=0.1)

col_b1, col_b2 = st.sidebar.columns(2)
if col_b1.button("▶️ Paso Manual", use_container_width=True):
    kernel.procesar_ciclo(sensibilidad, umbral_critico)

if col_b2.button("🔄 Reiniciar", use_container_width=True):
    kernel.reiniciar()
    st.rerun()

# MÉTRICAS TOP
hist = st.session_state.historial
ultimo = hist[-1] if hist else {"Ciclo": 0, "K_Promedio": 0.0, "Delta_Global": 0.0, "Coherencia_Fase": 0.0, "Sintropia_Indice": 1.0, "Sensores_Entropicos": 0}

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Ciclo Kernel", ultimo["Ciclo"])
m2.metric("Índice Sintropía", f"{ultimo['Sintropia_Indice']:.4f}")
m3.metric("K Promedio Global", f"{ultimo['K_Promedio']:.4f}")
m4.metric("Coherencia de Fase", f"{ultimo['Coherencia_Fase']:.4f}")
m5.metric("Nodos Entrópicos", ultimo["Sensores_Entropicos"], delta_color="inverse")

st.divider()

# PESTAÑAS
tab_matriz, tab_analisis, tab_inspector, tab_logs = st.tabs([
    "🎛️ Matriz 2D de Sensores", 
    "📊 Tendencias y Fase", 
    "🔍 Inspector Individual", 
    "📜 Terminal de Logs"
])

# TAB 1: MATRIZ PLOTLY
with tab_matriz:
    st.subheader("Matriz de Calor Sintrópica (10x10)")
    
    k_matrix = np.zeros((10, 10))
    estado_matrix = [["" for _ in range(10)] for _ in range(10)]
    
    for idx, s in enumerate(st.session_state.sensors):
        r, c = divmod(idx, 10)
        k_matrix[r, c] = s.k_actual
        estado_matrix[r][c] = f"S#{s.id:02d} | {s.estado}<br>K: {s.k_actual:.2f}"

    fig_heatmap = px.imshow(
        k_matrix,
        text_auto=False,
        color_continuous_scale="Viridis",
        aspect="equal",
        labels=dict(color="Coeficiente K")
    )
    
    fig_heatmap.update_traces(
        hovertemplate="%{customdata}<extra></extra>",
        customdata=estado_matrix
    )
    
    fig_heatmap.update_layout(
        height=550,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# TAB 2: GRÁFICAS
with tab_analisis:
    st.subheader("Dinámica Temporal del Kernel")
    if len(hist) > 0:
        df_hist = pd.DataFrame(hist)
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            fig_k = px.line(df_hist, x="Ciclo", y=["K_Promedio", "Delta_Global"], 
                            title="Evolución de K Global y Delta",
                            color_discrete_sequence=["#00CC96", "#EF553B"])
            fig_k.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_k, use_container_width=True)
            
        with col_g2:
            fig_fase = px.area(df_hist, x="Ciclo", y="Coherencia_Fase", 
                               title="Sincronización / Coherencia de Fase Global",
                               color_discrete_sequence=["#636EFA"])
            fig_fase.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_fase, use_container_width=True)
            
        csv_bytes = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Datos Registrados (CSV)", data=csv_bytes, file_name="kernel_frog_metrics.csv", mime="text/csv")
    else:
        st.info("Ejecuta la simulación para generar registros de tendencia.")

# TAB 3: INSPECTOR
with tab_inspector:
    st.subheader("Inspección de Nodo SYTEC")
    sensor_ids = [s.id for s in st.session_state.sensors]
    selected_id = st.selectbox("Selecciona un Sensor:", sorted(sensor_ids))
    
    s_target = next(s for s in st.session_state.sensors if s.id == selected_id)
    
    c_i1, c_i2, c_i3, c_i4 = st.columns(4)
    c_i1.metric("ID Sensor", f"#{s_target.id}")
    c_i2.metric("Estado Actual", s_target.estado)
    c_i3.metric("K Actual", f"{s_target.k_actual:.4f}")
    c_i4.metric("Fase Radianes", f"{s_target.fase:.2f} rad")

# TAB 4: LOGS
with tab_logs:
    st.subheader("Consola de Eventos en Vivo")
    if st.session_state.logs:
        st.code("\n".join(st.session_state.logs[:50]), language="bash")
    else:
        st.text("No hay eventos registrados aún.")

# LOOP AUTO-REFRESCO
if run_auto:
    kernel.procesar_ciclo(sensibilidad, umbral_critico)
    time.sleep(intervalo)
    st.rerun()
