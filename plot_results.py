import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("resultados.csv")

# Media por version y n
media = df.groupby(["version", "n"])["tiempo_ms"].mean().reset_index()
media.columns = ["version", "n", "media_ms"]

sizes = sorted(media["n"].unique())
versiones = ["seq_O0", "seq_O3", "transpose_O3", "pthreads_O3", "fork_O3"]
base = "seq_O0"

# Pivot para calcular speedup
pivot = media.pivot(index="n", columns="version", values="media_ms")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Análisis de Rendimiento - Multiplicación de Matrices", fontsize=14, fontweight="bold")

colores = {"seq_O0": "gray", "seq_O3": "blue", "transpose_O3": "green",
           "pthreads_O3": "red", "fork_O3": "orange"}

# ── Gráfica 1: Tiempos absolutos ──
ax1 = axes[0][0]
for v in versiones:
    if v in pivot.columns:
        ax1.plot(sizes, pivot[v], marker="o", label=v, color=colores[v])
ax1.set_title("Tiempos de Ejecución")
ax1.set_xlabel("Tamaño n"); ax1.set_ylabel("Tiempo (ms)")
ax1.legend(); ax1.grid(True)

# ── Gráfica 2: Speedup general ──
ax2 = axes[0][1]
for v in versiones:
    if v != base and v in pivot.columns:
        speedup = pivot[base] / pivot[v]
        ax2.plot(sizes, speedup, marker="o", label=f"Speedup {v}", color=colores[v])
ax2.axhline(y=1, color="gray", linestyle="--")
ax2.set_title("Speedup vs Secuencial -O0")
ax2.set_xlabel("Tamaño n"); ax2.set_ylabel("Speedup")
ax2.legend(); ax2.grid(True)

# ── Gráfica 3: Speedup hilos vs procesos ──
ax3 = axes[1][0]
for v in ["pthreads_O3", "fork_O3"]:
    if v in pivot.columns:
        speedup = pivot["seq_O3"] / pivot[v]
        ax3.plot(sizes, speedup, marker="s", label=f"Speedup {v}", color=colores[v])
ax3.axhline(y=1, color="gray", linestyle="--", label="base seq_O3")
ax3.set_title("Speedup Hilos y Procesos vs seq_O3")
ax3.set_xlabel("Tamaño n"); ax3.set_ylabel("Speedup")
ax3.legend(); ax3.grid(True)

# ── Gráfica 4: Eficiencia (Speedup / NUM_HILOS) ──
ax4 = axes[1][1]
NUM = 4
for v in ["pthreads_O3", "fork_O3"]:
    if v in pivot.columns:
        eficiencia = (pivot["seq_O3"] / pivot[v]) / NUM
        ax4.plot(sizes, eficiencia, marker="^", label=f"Eficiencia {v}", color=colores[v])
ax4.axhline(y=1.0, color="gray", linestyle="--", label="Eficiencia ideal")
ax4.set_title("Eficiencia (Speedup / 4 hilos)")
ax4.set_xlabel("Tamaño n"); ax4.set_ylabel("Eficiencia")
ax4.legend(); ax4.grid(True)

plt.tight_layout()
plt.savefig("graficas_rendimiento.png", dpi=150, bbox_inches="tight")
print("Gráficas guardadas en graficas_rendimiento.png")
