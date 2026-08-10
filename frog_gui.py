#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FROG KERNEL v2.5 - SISTEMA DE CONTROL SINTRÓPICO & AUDITORÍA EN TIEMPO REAL
Arquitectura SACI / Protocolo FROG - Dashboard Multilingüe + Whitepaper
Hecho en Costa Rica | JHA CR 506
"""

import math
import random
import statistics
import time
import pandas as pd
import numpy as np
import plotly.express as px
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
    .footer-stamp {
        text-align: center;
        padding: 20px 0 10px 0;
        color: #8b949e;
        font-size: 0.9em;
        border-top: 1px solid #30363d;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DICCIONARIO DE TRADUCCIÓN (MULTILINGÜE)
# -----------------------------------------------------------------------------
I18N = {
    "ES": {
        "title": "FROG KERNEL — CONTROL SINTRÓPICO",
        "subtitle": "Middleware SACI | Auditoría y Visualización en Tiempo Real | 100 Sensores SYTEC",
        "expander_title": "ℹ️ **¿Qué es, para qué sirve, qué hace y qué podría hacer este Kernel?**",
        "what_is": "### 🧠 ¿Qué es?\nEs un **middleware y centro de control sintrópico** diseñado bajo la arquitectura **SACI**. Funciona como un motor informático que monitorea y procesa patrones de orden, ruido y sincronía en redes compuestas por múltiples nodos (Matriz SYTEC).",
        "what_for": "### ⚙️ ¿Para qué sirve?\nSirve para **auditar, visualizar y corregir la estabilidad de sistemas dinámicos en tiempo real**, detectando fluctuaciones entrópicas antes de que afecten la red global.",
        "what_does": "### 🔄 ¿Qué hace actualmente?\n1. **Monitorea 100 sensores SYTEC** en matriz 10x10.\n2. **Mide coeficientes sintrópicos (K)** y deltas de ruido.\n3. **Calcula la coherencia de fase global** y sincronía.\n4. **Registra eventos y alertas** en vivo.\n5. **Exporta métricas históricas** en CSV.",
        "what_could": "### 🚀 Potencial Futuro\n* **Integración IoT / Hardware Real** mediante WebSockets.\n* **Consenso Algorítmico Descentralizado (P2P)**.\n* **Clonación de Fase Automática** para autocorrección de nodos.",
        "sidebar_control": "🕹️ Panel de Comando",
        "auto_run": "⚡ Ejecución Automática",
        "interval": "Intervalo de Refresco (s)",
        "kernel_params": "⚙️ Parámetros del Kernel",
        "sensitivity": "Factor de Perturbación",
        "threshold": "Umbral Entrópico Crítico",
        "step_btn": "▶️ Paso Manual",
        "reset_btn": "🔄 Reiniciar",
        "m_cycle": "Ciclo Kernel",
        "m_sintropy": "Índice Sintropía",
        "m_k_avg": "K Promedio Global",
        "m_phase": "Coherencia de Fase",
        "m_entropic": "Nodos Entrópicos",
        "tab_matrix": "🎛️ Matriz 2D",
        "tab_trends": "📊 Tendencias",
        "tab_inspector": "🔍 Inspector Nodo",
        "tab_logs": "📜 Terminal Logs",
        "tab_whitepaper": "📄 Whitepaper",
        "export_csv": "📥 Exportar Métricas (CSV)",
        "download_wp": "📥 Descargar Whitepaper (.md)"
    },
    "EN": {
        "title": "FROG KERNEL — SYNTROPIC CONTROL",
        "subtitle": "SACI Middleware | Real-time Audit & Visualization | 100 SYTEC Sensors",
        "expander_title": "ℹ️ **What is it, what is it for, what does it do, and what could it do?**",
        "what_is": "### 🧠 What is it?\nIt is a **syntropic control middleware** built under the **SACI** architecture. It operates as a computing engine that monitors and processes patterns of order, noise, and synchrony across multi-node networks (SYTEC Matrix).",
        "what_for": "### ⚙️ What is it for?\nIt serves to **audit, visualize, and stabilize dynamic systems in real-time**, detecting entropic fluctuations before they compromise global consensus.",
        "what_does": "### 🔄 What does it do now?\n1. **Monitors 100 SYTEC sensors** in a 10x10 grid.\n2. **Measures syntropic coefficients (K)** and noise deltas.\n3. **Calculates global phase coherence** and node sync.\n4. **Logs live events and alerts**.\n5. **Exports historical metrics** to CSV.",
        "what_could": "### 🚀 Future Potential\n* **IoT & Real Hardware Integration** via WebSockets.\n* **Decentralized Algorithmic Consensus (P2P)**.\n* **Automated Phase Cloning** for node self-healing.",
        "sidebar_control": "🕹️ Command Panel",
        "auto_run": "⚡ Auto Execution",
        "interval": "Refresh Interval (s)",
        "kernel_params": "⚙️ Kernel Parameters",
        "sensitivity": "Perturbation Factor",
        "threshold": "Critical Entropic Threshold",
        "step_btn": "▶️ Manual Step",
        "reset_btn": "🔄 Reset",
        "m_cycle": "Kernel Cycle",
        "m_sintropy": "Syntropy Index",
        "m_k_avg": "Global Avg K",
        "m_phase": "Phase Coherence",
        "m_entropic": "Entropic Nodes",
        "tab_matrix": "🎛️ 2D Grid",
        "tab_trends": "📊 Trends",
        "tab_inspector": "🔍 Node Inspector",
        "tab_logs": "📜 Event Terminal",
        "tab_whitepaper": "📄 Whitepaper",
        "export_csv": "📥 Export Metrics (CSV)",
        "download_wp": "📥 Download Whitepaper (.md)"
    },
    "DE": {
        "title": "FROG KERNEL — SYNTROPISCHE STEUERUNG",
        "subtitle": "SACI-Middleware | Echtzeit-Auditierung & Visualisierung | 100 SYTEC-Sensoren",
        "expander_title": "ℹ️ **Was ist das, wozu dient es, was tut es und was könnte es tun?**",
        "what_is": "### 🧠 Was ist das?\nEs ist eine **syntropische Steuerungs-Middleware**, die unter der **SACI**-Architektur entwickelt wurde. Sie fungiert als Rechen-Engine zur Überwachung von Ordnung, Rauschen und Synchronität in Netzwerken.",
        "what_for": "### ⚙️ Wozu dient es?\nEs dient dazu, **dynamische Systeme in Echtzeit zu auditieren, zu visualisieren und zu stabilisieren**, um entropische Abweichungen frühzeitig zu erkennen.",
        "what_does": "### 🔄 Was tut es derzeit?\n1. **Überwacht 100 SYTEC-Sensoren** in einem 10x10-Raster.\n2. **Misst syntropische Koeffizienten (K)** und Rausch-Deltas.\n3. **Berechnet globale Phasenkohärenz** und Synchronisation.\n4. **Protokolliert Live-Ereignisse und Warnungen**.\n5. **Exportiert historische Daten** als CSV.",
        "what_could": "### 🚀 Zukunftspotenzial\n* **IoT & Hardware-Integration** über WebSockets.\n* **Dezentraler algorithmischer Konsens (P2P)**.\n* **Automatische Phasenklonung** zur Knoten-Selbstheilung.",
        "sidebar_control": "🕹️ Bedienfeld",
        "auto_run": "⚡ Automatische Ausführung",
        "interval": "Aktualisierungsintervall (s)",
        "kernel_params": "⚙️ Kernel-Parameter",
        "sensitivity": "Störungsfaktor",
        "threshold": "Kritischer Entropiewert",
        "step_btn": "▶️ Manueller Schritt",
        "reset_btn": "🔄 Zurücksetzen",
        "m_cycle": "Kernel-Zyklus",
        "m_sintropy": "Syntropie-Index",
        "m_k_avg": "Globales Durchschnitts-K",
        "m_phase": "Phasenkohärenz",
        "m_entropic": "Entropische Knoten",
        "tab_matrix": "🎛️ 2D-Raster",
        "tab_trends": "📊 Trends",
        "tab_inspector": "🔍 Knoten-Inspektor",
        "tab_logs": "📜 Ereignis-Terminal",
        "tab_whitepaper": "📄 Whitepaper",
        "export_csv": "📥 Metriken exportieren (CSV)",
        "download_wp": "📥 Whitepaper herunterladen (.md)"
    }
}

# -----------------------------------------------------------------------------
# CONTENIDO DEL WHITEPAPER
# -----------------------------------------------------------------------------
WHITEPAPER_TEXT = r"""
# 📄 WHITEPAPER: PROTOCOLO FROG & ARQUITECTURA SACI
**Versión:** 2.5 | **Estado:** Implementación Middleware | **Autor:** JHA CR (Costa Rica 🇨🇷 506)

---

## 1. RESUMEN EJECUTIVO (EXECUTIVE SUMMARY)
El **Protocolo FROG** (Frequency Resonant Order Governance) junto a la **Arquitectura SACI** constituye una infraestructura informática diseñada para el monitoreo, evaluación y estabilización sintrópica de redes dinámicas complejas. En entornos con alto nivel de interferencia o ruido estocástico, el FROG Kernel actúa como una capa de abstracción middleware capaz de transformar variaciones entrópicas ($K$) en métricas deterministas de coherencia de fase.

---

## 2. FUNDAMENTOS MATEMÁTICOS DEL KERNEL

### 2.1 Coeficiente Sintrópico ($K$)
Cada nodo $i$ dentro de la matriz de sensores SYTEC genera un valor efectivo de perturbación $K_{efectivo}$ determinado por la fórmula:

$$K_{efectivo} = | K_{actual} + \sigma \cdot \xi |$$

Donde:
* $K_{actual}$: Estado previo del coeficiente sintrópico.
* $\sigma$: Factor de sensibilidad al ruido base $R_i = \frac{5.0}{\sqrt{i}}$.
* $\xi$: Perturbación estocástica uniforme $\xi \sim U(-0.25, 0.25)$.

### 2.2 Coherencia de Fase Global ($\Phi$)
La sincronización armónica global entre los 100 sensores se cuantifica mediante la media de componentes sinusoidales de fase $\theta_i$:

$$\Phi = \frac{1}{N} \left| \sum_{i=1}^{N} \cos(\theta_i) \right|$$

---

## 3. ARQUITECTURA DEL MIDDLEWARE (SACI)
La arquitectura SACI se divide en tres niveles estandarizados:
1. **Capa de Captura (SYTEC Matrix):** Colección de 100 nodos ordenados dinámicamente.
2. **Capa de Procesamiento Sintrópico (FROG Core):** Cálculo en bucle cerrado de deltas locales y métricas globales.
3. **Capa de Presentación & Auditoría (Dashboard Streamlit):** Interfaz Web adaptativa multi-idioma para control manual o automatizado.

---

## 4. HOJA DE RUTA Y ESCALABILIDAD (ROADMAP)
* **Fase I (Completada):** Simulación de motor en tiempo real y visualizador matricial Plotly 2D.
* **Fase II (En desarrollo):** Integración de sockets bidireccionales para hardware IoT real.
* **Fase III:** Mecanismos de consenso algorítmico P2P descentralizado sin dependencia de autoridad central.

---
*Hecho con precisión en Costa Rica 🇨🇷 — JHA CR 506*
"""

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
                st.session_state.logs.insert(0, f"[{time.strftime('%H:%M:%S')}] Cycle {ciclo_actual}: Sensor #{sensor.id:02d} -> {sensor.estado} {color_log}")

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
# INTERFAZ Y NAVEGACIÓN MULTI-IDIOMA
# -----------------------------------------------------------------------------
kernel = KernelFROGCore()

# SELECTOR DE IDIOMA EN SIDEBAR
st.sidebar.markdown("### 🌐 Language / Idioma / Sprache")
lang = st.sidebar.selectbox("Select Language:", ["ES", "EN", "DE"], index=0, label_visibility="collapsed")
t = I18N[lang]

# BANNER ENCABEZADO
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.title("🐸")
with col_title:
    st.title(t["title"])
    st.caption(t["subtitle"])

# SECCIÓN EXPLICATIVA
with st.expander(t["expander_title"], expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(t["what_is"])
        st.markdown(t["what_for"])
    with col_b:
        st.markdown(t["what_does"])
    st.markdown("---")
    st.markdown(t["what_could"])

st.divider()

# SIDEBAR CONTROLES
st.sidebar.header(t["sidebar_control"])

run_auto = st.sidebar.toggle(t["auto_run"], value=False)
intervalo = st.sidebar.slider(t["interval"], 0.1, 2.0, 0.5, step=0.1)

st.sidebar.subheader(t["kernel_params"])
sensibilidad = st.sidebar.slider(t["sensitivity"], 0.1, 3.0, 1.0, step=0.1)
umbral_critico = st.sidebar.slider(t["threshold"], 0.5, 5.0, 2.5, step=0.1)

col_b1, col_b2 = st.sidebar.columns(2)
if col_b1.button(t["step_btn"], use_container_width=True):
    kernel.procesar_ciclo(sensibilidad, umbral_critico)

if col_b2.button(t["reset_btn"], use_container_width=True):
    kernel.reiniciar()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("🇨🇷 **Hecho en Costa Rica**\n\n**JHA CR 506**")

# MÉTRICAS
hist = st.session_state.historial
ultimo = hist[-1] if hist else {"Ciclo": 0, "K_Promedio": 0.0, "Delta_Global": 0.0, "Coherencia_Fase": 0.0, "Sintropia_Indice": 1.0, "Sensores_Entropicos": 0}

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(t["m_cycle"], ultimo["Ciclo"])
m2.metric(t["m_sintropy"], f"{ultimo['Sintropia_Indice']:.4f}")
m3.metric(t["m_k_avg"], f"{ultimo['K_Promedio']:.4f}")
m4.metric(t["m_phase"], f"{ultimo['Coherencia_Fase']:.4f}")
m5.metric(t["m_entropic"], ultimo["Sensores_Entropicos"], delta_color="inverse")

st.divider()

# PESTAÑAS (INCLUYENDO WHITEPAPER)
tab_matriz, tab_analisis, tab_inspector, tab_logs, tab_wp = st.tabs([
    t["tab_matrix"], 
    t["tab_trends"], 
    t["tab_inspector"], 
    t["tab_logs"],
    t["tab_whitepaper"]
])

# TAB 1: MATRIZ PLOTLY
with tab_matriz:
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
    fig_heatmap.update_traces(hovertemplate="%{customdata}<extra></extra>", customdata=estado_matrix)
    fig_heatmap.update_layout(height=550, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_heatmap, use_container_width=True)

# TAB 2: TENDENCIAS Y EXPORTACIÓN
with tab_analisis:
    if len(hist) > 0:
        df_hist = pd.DataFrame(hist)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_k = px.line(df_hist, x="Ciclo", y=["K_Promedio", "Delta_Global"], title="K & Delta", color_discrete_sequence=["#00CC96", "#EF553B"])
            fig_k.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_k, use_container_width=True)
        with col_g2:
            fig_fase = px.area(df_hist, x="Ciclo", y="Coherencia_Fase", title="Phase Coherence", color_discrete_sequence=["#636EFA"])
            fig_fase.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_fase, use_container_width=True)
            
        csv_bytes = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(t["export_csv"], data=csv_bytes, file_name="kernel_frog_metrics.csv", mime="text/csv")
    else:
        st.info("Ejecuta la simulación para generar datos.")

# TAB 3: INSPECTOR NODO
with tab_inspector:
    sensor_ids = [s.id for s in st.session_state.sensors]
    selected_id = st.selectbox("Sensor ID:", sorted(sensor_ids))
    s_target = next(s for s in st.session_state.sensors if s.id == selected_id)
    c_i1, c_i2, c_i3, c_i4 = st.columns(4)
    c_i1.metric("ID", f"#{s_target.id}")
    c_i2.metric("Estado", s_target.estado)
    c_i3.metric("K Actual", f"{s_target.k_actual:.4f}")
    c_i4.metric("Fase", f"{s_target.fase:.2f} rad")

# TAB 4: LOGS
with tab_logs:
    if st.session_state.logs:
        st.code("\n".join(st.session_state.logs[:50]), language="bash")
    else:
        st.text("No logs yet.")

# TAB 5: WHITEPAPER
with tab_wp:
    st.markdown(WHITEPAPER_TEXT)
    st.download_button(
        label=t["download_wp"],
        data=WHITEPAPER_TEXT.encode('utf-8'),
        file_name="FROG_Protocol_Whitepaper.md",
        mime="text/markdown"
    )

# PIE DE PÁGINA CON FIRMA
st.markdown("""
    <div class="footer-stamp">
        <strong>FROG KERNEL & PROTOCOLO SACI</strong><br>
        Hecho en Costa Rica 🇨🇷 — <strong>JHA CR 506</strong>
    </div>
""", unsafe_allow_html=True)

# LOOP AUTO-REFRESCO
if run_auto:
    kernel.procesar_ciclo(sensibilidad, umbral_critico)
    time.sleep(intervalo)
    st.rerun()
