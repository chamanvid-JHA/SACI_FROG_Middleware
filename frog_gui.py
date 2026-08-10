#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FROG KERNEL - INTERFAZ WEB DE CONTROL SINTRÓPICO / LOGGER
Visualizador en tiempo real para 100 sensores, clonación de fase y exportación CSV.
"""

import math
import random
import statistics
import csv
import os
import time
import pandas as pd
import streamlit as st
from dataclasses import dataclass
from typing import List


# Configuración general de la página Streamlit
st.set_page_config(
    page_title="FROG Kernel - Monitor Sintrópico",
    page_icon="🐸",
    layout="wide"
)

@dataclass
class SensorSYTEC:
    id: int
    ruido_base: float
    delta_local: float = 0.0
    k_actual: float = 0.0
    estado: str = "SINTRÓPICO"


class KernelFROGApp:
    def __init__(self):
        self.num_sensores = 100
        self.delta_global = 0.0
        self.k_global = 0.0
        self.is_running = False
        
        # Inicializar estado de sesión en Streamlit
        if "sensors" not in st.session_state:
            st.session_state.sensors = self.generar_sensores_iniciales()
        if "historial_metrics" not in st.session_state:
            st.session_state.historial_metrics = []
        if "ciclo_actual" not in st.session_state:
            st.session_state.ciclo_actual = 0

    def generar_sensores_iniciales(self) -> List[SensorSYTEC]:
        sensores = []
        for i in range(self.num_sensores):
            ramk = i + 1
            ruido = 5.0 / (ramk ** 0.5)
            sensores.append(SensorSYTEC(id=ramk, ruido_base=ruido))
        random.shuffle(sensores)
        return sensores

    def ejecutar_paso_simulacion(self):
        st.session_state.ciclo_actual += 1
        
        deltas = []
        ks = []
        
        for sensor in st.session_state.sensors:
            perturbacion = sensor.ruido_base * random.uniform(-0.2, 0.2)
            k_efectivo = abs(sensor.k_actual + perturbacion)
            
            if random.random() < 0.1:
                sensor.estado = "ENTRÓPICO"
            else:
                sensor.estado = "SINTRÓPICO"
                
            sensor.k_actual = round(k_efectivo, 4)
            sensor.delta_local = round(abs(k_efectivo - st.session_state.get("delta_global", 0.0)), 4)
            
            deltas.append(sensor.delta_local)
            ks.append(sensor.k_actual)

        # Actualizar métricas globales
        promedio_delta = round(statistics.mean(deltas), 4) if deltas else 0.0
        promedio_k = round(statistics.mean(ks), 4) if ks else 0.0
        
        st.session_state.delta_global = promedio_delta
        st.session_state.k_global = promedio_k

        # Guardar en historial
        st.session_state.historial_metrics.append({
            "Ciclo": st.session_state.ciclo_actual,
            "K_Promedio": promedio_k,
            "Delta_Global": promedio_delta,
            "Estado": "Sintrópico" if promedio_delta < 0.5 else "Alerta Entrópica"
        })

    def reiniciar_sistema(self):
        st.session_state.sensors = self.generar_sensores_iniciales()
        st.session_state.historial_metrics = []
        st.session_state.ciclo_actual = 0
        st.session_state.delta_global = 0.0
        st.session_state.k_global = 0.0


# Instanciar aplicación
app = KernelFROGApp()

# --- INTERFAZ STREAMLIT ---

st.title("🐸 FROG KERNEL - SISTEMA DE CONTROL SINTRÓPICO")
st.subheader("Visualizador y Logger en Tiempo Real (100 Sensores SYTEC)")

# Panel de control (Sidebar)
st.sidebar.header("🕹️ Panel de Control")

auto_run = st.sidebar.checkbox("Ejecutar Simulación Automática", value=False)
velocidad = st.sidebar.slider("Intervalo de Actualización (seg)", 0.1, 2.0, 0.5)

col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.button("▶️ Paso Manual"):
        app.ejecutar_paso_simulacion()

with col_btn2:
    if st.button("🔄 Reiniciar"):
        app.reiniciar_sistema()
        st.rerun()

# Métricas Globales Top
m1, m2, m3 = st.columns(3)
m1.metric("Ciclo Actual", st.session_state.ciclo_actual)
m2.metric("Promedio K Global", st.session_state.get("k_global", 0.0))
m3.metric("Delta Global (Ruido)", st.session_state.get("delta_global", 0.0))

st.divider()

# Matriz de 100 Sensores SYTEC
st.write("### 🛰️ Matriz de Estado de Sensores SYTEC (10x10)")

# Formatear matriz para visualización rápida
grid_data = []
for i in range(0, 100, 10):
    fila = []
    for s in st.session_state.sensors[i:i+10]:
        icono = "🟢" if s.estado == "SINTRÓPICO" else "🔴"
        fila.append(f"{icono} S{s.id:02d}\nK:{s.k_actual:.2f}")
    grid_data.append(fila)

df_grid = pd.DataFrame(grid_data)
st.dataframe(df_grid, use_container_width=True)

st.divider()

# Historial y Gráficas en tiempo real
if st.session_state.historial_metrics:
    st.write("### 📈 Tendencia Sintrópica Global")
    df_hist = pd.DataFrame(st.session_state.historial_metrics)
    st.line_chart(df_hist.set_index("Ciclo")[["K_Promedio", "Delta_Global"]])

    # Exportación CSV
    st.write("### 💾 Exportar Registros")
    csv_data = df_hist.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Historial CSV",
        data=csv_data,
        file_name="frog_metrics.csv",
        mime="text/csv"
    )

# Bucle de actualización automática
if auto_run:
    app.ejecutar_paso_simulacion()
    time.sleep(velocidad)
    st.rerun()
