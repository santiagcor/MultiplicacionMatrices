import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("resultados.csv")
df = df[df["tiempo_ms"] > 0]

df_clean = df.copy()
for (ver, n_size), grupo in df.groupby(["version", "n"]):
    media_g = grupo["tiempo_ms"].mean()
    std_g   = grupo["tiempo_ms"].std()
    if std_g > 0:
        mask = (df_clean["version"] == ver) & (df_clean["n"] == n_size)
        df_clean = df_clean[~(mask & (df_clean["tiempo_ms"] > media_g + 3 * std_g))]

resumen = df_clean.groupby(["version", "n"])["tiempo_ms"].mean().reset_index()
resumen.columns = ["version", "n", "media_ms"]

sizes     = sorted(resumen["n"].unique())
versiones = ["seq_O0", "seq_O3", "transpose", "pthreads", "fork"]
base      = "seq_O0"
pivot     = resumen.pivot(index="n", columns="version", values="media_ms")

colores = {
    "seq_O0":    "gray",
    "seq_O1":    "steelblue",
    "seq_O2":    "royalblue",
    "seq_O3":    "blue",
    "seq_Os":    "purple",
    "seq_Ofast": "darkblue",
    "transpose": "green",
    "pthreads":  "red",
    "fork":      "orange"
}

# FIGURA 1 ─ 4 subgraficas
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Analisis de Rendimiento - Multiplicacion de Matrices",
             fontsize=14, fontweight="bold")

# Grafica 1: Tiempos absolutos
ax1 = axes[0][0]
for v in versiones:
    if v in pivot.columns:
        ax1.plot(sizes, pivot[v], marker="o", label=v, color=colores[v])
ax1.set_title("Tiempos de Ejecucion")
ax1.set_xlabel("Tamano n")
ax1.set_ylabel("Tiempo (ms)")
ax1.legend()
ax1.grid(True)

# Grafica 2: Speedup vs seq_O0
ax2 = axes[0][1]
for v in versiones:
    if v != base and v in pivot.columns and base in pivot.columns:
        sp = pivot[base] / pivot[v]
        ax2.plot(sizes, sp, marker="o", label="Speedup " + v, color=colores[v])
ax2.axhline(y=1, color="gray", linestyle="--")
ax2.set_title("Speedup vs Secuencial -O0")
ax2.set_xlabel("Tamano n")
ax2.set_ylabel("Speedup")
ax2.legend()
ax2.grid(True)

# Grafica 3: Speedup pthreads y fork vs seq_O3
ax3 = axes[1][0]
for v in ["pthreads", "fork"]:
    if v in pivot.columns and "seq_O3" in pivot.columns:
        sp = pivot["seq_O3"] / pivot[v]
        ax3.plot(sizes, sp, marker="s", label="Speedup " + v, color=colores[v])
ax3.axhline(y=1, color="gray", linestyle="--", label="base seq_O3")
ax3.set_title("Speedup Hilos y Procesos vs seq_O3")
ax3.set_xlabel("Tamano n")
ax3.set_ylabel("Speedup")
ax3.legend()
ax3.grid(True)

# Grafica 4: Eficiencia
ax4 = axes[1][1]
NUM_WORKERS = 4
for v in ["pthreads", "fork"]:
    if v in pivot.columns and "seq_O3" in pivot.columns:
        ef = (pivot["seq_O3"] / pivot[v]) / NUM_WORKERS
        ax4.plot(sizes, ef, marker="^", label="Eficiencia " + v, color=colores[v])
ax4.axhline(y=1.0, color="gray", linestyle="--", label="Eficiencia ideal")
ax4.set_title("Eficiencia (Speedup / 4 hilos)")
ax4.set_xlabel("Tamano n")
ax4.set_ylabel("Eficiencia")
ax4.legend()
ax4.grid(True)

plt.tight_layout()
plt.savefig("graficas_rendimiento.png", dpi=150, bbox_inches="tight")
print("Guardado: graficas_rendimiento.png")
plt.close()

# FIGURA 2 ─ Barras comparativas a n=3000
N_BAR        = 3000
orden_vers   = ["seq_O0","seq_O1","seq_O2","seq_O3","seq_Os","seq_Ofast","transpose","pthreads","fork"]
etiquetas    = ["-O0","-O1","-O2","-O3","-Os","-Ofast","transpose","pthreads","fork"]
bar_colores  = ["gray","steelblue","royalblue","blue","purple","darkblue","green","red","orange"]

if N_BAR in pivot.index:
    tiempos = []
    for v in orden_vers:
        if v in pivot.columns:
            tiempos.append(pivot.loc[N_BAR, v])
        else:
            tiempos.append(0)

    fig2, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(etiquetas, tiempos, color=bar_colores, edgecolor="white", width=0.6)

    for bar, val in zip(bars, tiempos):
        lbl = str(round(val/1000, 1)) + "s" if val >= 1000 else str(round(val)) + "ms"
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(tiempos) * 0.01,
                lbl, ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_title("Comparacion de Tiempos a n=3000 - Todas las versiones",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Version / Flag de compilacion", fontsize=11)
    ax.set_ylabel("Tiempo promedio (ms)", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig("grafica_barras_n3000.png", dpi=150, bbox_inches="tight")
    print("Guardado: grafica_barras_n3000.png")
    plt.close()
else:
    print("AVISO: No hay datos para n=3000 en el CSV")

# TABLA RESUMEN EN CONSOLA
print()
print("=== TABLA RESUMEN (ms promedio, outliers removidos) ===")
print("Version       ", end="")
for n in sizes:
    print("  n=" + str(n), end="")
print()
print("-" * (14 + 9 * len(sizes)))
for v in orden_vers:
    if v in pivot.columns:
        print(v.ljust(14), end="")
        for n in sizes:
            val = pivot.loc[n, v] if n in pivot.index else float("nan")
            print(("  " + str(round(val, 1)).rjust(7)), end="")
        print()
print()
print("Listo.")
