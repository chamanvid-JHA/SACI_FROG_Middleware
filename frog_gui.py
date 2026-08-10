#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FROG KERNEL - INTERFAZ GRÁFICA DE CONTROL SINTRÓPICO + LOGGER
Visualizador en tiempo real para 100 sensores, clonación de fase y exportación CSV.
"""

import math
import random
import statistics
import csv
import os
import streamlit as at 
# import tkinter as tk
# from tkinter import messagebox, filedialog
from dataclasses import dataclass
from typing import List

@dataclass
class SensorSYTEC:
    id: int
    ruido_base: float
    delta_local: float = 0.0
    k_actual: float = 0.0
    estado: str = "SINTRÓPICO"

class KernelFROGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FROG Kernel - Monitor y Logger de Sintropía Global")
        self.root.geometry("1000x780")
        self.root.configure(bg="#0b0f19")

        # Configuración del motor
        self.num_sensores = 100
        self.delta_global = 0.0
        self.sensores: List[SensorSYTEC] = []
        self.ciclo_actual = 0
        self.is_running = False
        self.historial_metricas = []

        self._inicializar_sensores()
        self._crear_interfaz()

    def _inicializar_sensores(self):
        self.sensores.clear()
        for i in range(self.num_sensores):
            rank = i + 1
            ruido = 5.0 / (rank ** 0.5)
            self.sensores.append(SensorSYTEC(id=i, ruido_base=ruido))
        random.shuffle(self.sensores)

    def _crear_interfaz(self):
        titulo = tk.Label(
            self.root, text="🐸 SISTEMA SYTEC: KERNEL FROG [AUDITORÍA Y CONTROL]",
            font=("Consolas", 15, "bold"), fg="#00ffcc", bg="#0b0f19"
        )
        titulo.pack(pady=8)

        # Marco de Estadísticas Globales
        frame_stats = tk.Frame(self.root, bg="#161b22", bd=2, relief="groove")
        frame_stats.pack(fill="x", padx=20, pady=5)

        self.lbl_ciclo = tk.Label(frame_stats, text="Ciclo: 0", font=("Consolas", 11), fg="#ffffff", bg="#161b22")
        self.lbl_ciclo.pack(side="left", padx=12, pady=8)

        self.lbl_k_prom = tk.Label(frame_stats, text="K Promedio: 0.00", font=("Consolas", 11), fg="#00ffcc", bg="#161b22")
        self.lbl_k_prom.pack(side="left", padx=12, pady=8)

        self.lbl_delta = tk.Label(frame_stats, text="Δ Global: 0.0000", font=("Consolas", 11), fg="#ff00ff", bg="#161b22")
        self.lbl_delta.pack(side="left", padx=12, pady=8)

        self.lbl_entropicos = tk.Label(frame_stats, text="Entrópicos: 0/100", font=("Consolas", 11), fg="#ff4444", bg="#161b22")
        self.lbl_entropicos.pack(side="left", padx=12, pady=8)

        # Canvas para la matriz de 100 sensores (10x10)
        frame_canvas = tk.Frame(self.root, bg="#0b0f19")
        frame_canvas.pack(pady=5)

        self.canvas_size = 380
        self.canvas = tk.Canvas(frame_canvas, width=self.canvas_size, height=self.canvas_size, bg="#0d1117", highlightthickness=1, highlightbackground="#30363d")
        self.canvas.pack()

        self.rects = {}
        cols = 10
        cell_size = self.canvas_size / cols
        for i, sensor in enumerate(self.sensores):
            r = i // cols
            c = i % cols
            x1 = c * cell_size + 3
            y1 = r * cell_size + 3
            x2 = (c + 1) * cell_size - 3
            y2 = (r + 1) * cell_size - 3
            
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#238636", outline="")
            self.rects[sensor.id] = rect

        # Panel de Botones de Control
        frame_btns = tk.Frame(self.root, bg="#0b0f19")
        frame_btns.pack(pady=10)

        self.btn_iniciar = tk.Button(frame_btns, text="▶ Iniciar", font=("Consolas", 10, "bold"), fg="#ffffff", bg="#238636", activebackground="#2ea043", bd=0, padx=12, pady=6, command=self.toggle_simulacion)
        self.btn_iniciar.grid(row=0, column=0, padx=6)

        btn_paso = tk.Button(frame_btns, text="⏭ Ciclo", font=("Consolas", 10, "bold"), fg="#ffffff", bg="#1f6feb", activebackground="#388bfd", bd=0, padx=12, pady=6, command=self.ejecutar_ciclo)
        btn_paso.grid(row=0, column=1, padx=6)

        btn_exportar = tk.Button(frame_btns, text="💾 Exportar CSV", font=("Consolas", 10, "bold"), fg="#ffffff", bg="#8957e5", activebackground="#a371f7", bd=0, padx=12, pady=6, command=self.exportar_csv)
        btn_exportar.grid(row=0, column=2, padx=6)

        btn_reiniciar = tk.Button(frame_btns, text="🔄 Reiniciar", font=("Consolas", 10, "bold"), fg="#ffffff", bg="#da3633", activebackground="#f85149", bd=0, padx=12, pady=6, command=self.reiniciar_sistema)
        btn_reiniciar.grid(row=0, column=3, padx=6)

        lbl_leyenda = tk.Label(self.root, text="🟢 Nodo Sintrópico (K >= 15)  |  🔴 Nodo Entrópico (K < 15)  |  🧬 Clonación Activa", font=("Consolas", 9), fg="#8b949e", bg="#0b0f19")
        lbl_leyenda.pack(pady=5)

    def ejecutar_ciclo(self):
        self.ciclo_actual += 1
        k_list = []
        contador_entropico = 0

        for sensor in self.sensores:
            t_base = 1.0  
            perturbacion = sensor.ruido_base * random.gauss(1.0, 0.2)
            t_efectivo = t_base + 0.1 * perturbacion + sensor.delta_local

            k = abs(10.0 * math.sin(t_efectivo + self.delta_global) + 15.0)
            sensor.k_actual = k
            k_list.append(k)

            if k >= 15.0:
                sensor.estado = "SINTRÓPICO"
            else:
                sensor.estado = "ENTRÓPICO"
                contador_entropico += 1

            error = 25.0 - k
            sensor.delta_local += 0.01 * error * 0.1

        mejor_sensor = max(self.sensores, key=lambda s: s.k_actual)
        for sensor in self.sensores:
            if sensor.estado == "ENTRÓPICO":
                sensor.delta_local = 0.8 * sensor.delta_local + 0.2 * mejor_sensor.delta_local

        peso_total = sum(k_list)
        if peso_total > 0:
            delta_ponderado = sum(k * s.delta_local for k, s in zip(k_list, self.sensores)) / peso_total
        else:
            delta_ponderado = self.delta_global

        self.delta_global = 0.9 * self.delta_global + 0.1 * delta_ponderado

        avg_k = statistics.mean(k_list)
        
        # Guardar en historial interno para auditoría
        self.historial_metricas.append({
            "ciclo": self.ciclo_actual,
            "k_promedio": round(avg_k, 4),
            "delta_global": round(self.delta_global, 6),
            "entropicos": contador_entropico
        })

        self.lbl_ciclo.config(text=f"Ciclo: {self.ciclo_actual}")
        self.lbl_k_prom.config(text=f"K Promedio: {avg_k:.2f}")
        self.lbl_delta.config(text=f"Δ Global: {self.delta_global:.4f}")
        self.lbl_entropicos.config(text=f"Entrópicos: {contador_entropico}/{self.num_sensores}")

        for sensor in self.sensores:
            color = "#238636" if sensor.estado == "SINTRÓPICO" else "#da3633"
            self.canvas.itemconfig(self.rects[sensor.id], fill=color)

        if self.is_running:
            self.root.after(300, self.ejecutar_ciclo)

    def toggle_simulacion(self):
        if not self.is_running:
            self.is_running = True
            self.btn_iniciar.config(text="⏸ Pausar", bg="#9e6a03")
            self.ejecutar_ciclo()
        else:
            self.is_running = False
            self.btn_iniciar.config(text="▶ Iniciar", bg="#238636")

    def exportar_csv(self):
        if not self.historial_metricas:
            messagebox.showwarning("Advertencia", "No hay datos de simulación para exportar todavía.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            initialfile="frog_metrics.csv"
        )
        if archivo:
            try:
                with open(archivo, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["ciclo", "k_promedio", "delta_global", "entropicos"])
                    writer.writeheader()
                    writer.writerows(self.historial_metricas)
                messagebox.showinfo("Éxito", f"Métricas exportadas correctamente en:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def reiniciar_sistema(self):
        self.is_running = False
        self.btn_iniciar.config(text="▶ Iniciar", bg="#238636")
        self.ciclo_actual = 0
        self.delta_global = 0.0
        self.historial_metricas.clear()
        self._inicializar_sensores()
        self.lbl_ciclo.config(text="Ciclo: 0")
        self.lbl_k_prom.config(text="K Promedio: 0.00")
        self.lbl_delta.config(text="Δ Global: 0.0000")
        self.lbl_entropicos.config(text="Entrópicos: 0/100")
        for sensor in self.sensores:
            self.canvas.itemconfig(self.rects[sensor.id], fill="#238636")

if __name__ == "__main__":
    root = tk.Tk()
    app = KernelFROGApp(root)
    root.mainloop()
