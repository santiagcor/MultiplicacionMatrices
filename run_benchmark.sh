#!/bin/bash
# Benchmark: 9 versiones x 3 tamanos x 10 repeticiones
# Correcciones: llaves cerradas, warm-up, validacion de tiempos, REPS=10

REPS=10
SIZES="1000 2000 3000"
OUT="resultados.csv"

echo "version,n,rep,tiempo_ms" > $OUT

compilar() {
    echo "Compilando todas las versiones..."
    g++ -O0    -o matmul_O0        matmul_seq.cpp
    g++ -O1    -o matmul_O1        matmul_seq.cpp
    g++ -O2    -o matmul_O2        matmul_seq.cpp
    g++ -O3    -o matmul_O3        matmul_seq.cpp
    g++ -Os    -o matmul_Os        matmul_seq.cpp
    g++ -Ofast -o matmul_Ofast     matmul_seq.cpp
    g++ -O3    -o matmul_transpose matmul_transpose.cpp
    g++ -O3    -o matmul_pthreads  matmul_pthreads.cpp -lpthread
    g++ -O3    -o matmul_fork      matmul_fork.cpp
    echo "Compilacion completa."
}

medir() {
    local bin=$1
    local version=$2
    for n in $SIZES; do
        echo "  [$version] n=$n  (warm-up + $REPS reps)..."
        # Warm-up: 1 ejecucion descartada para estabilizar cache y CPU
        ./$bin $n > /dev/null 2>&1
        # Repeticiones reales
        for rep in $(seq 1 $REPS); do
            t=$(./$bin $n 2>/dev/null)
            # Validar que el tiempo es un numero positivo
            if echo "$t" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
                echo "$version,$n,$rep,$t" >> $OUT
            else
                echo "  ADVERTENCIA: tiempo invalido ($t) en $version n=$n rep=$rep" >&2
            fi
        done
    done
}

compilar
echo ""
echo "IMPORTANTE: cierra navegador, VS Code y otros programas antes de continuar."
echo "Presiona ENTER para comenzar..."
read

echo "Corriendo benchmarks... (puede tardar 30-50 minutos)"
echo "------------------------------------------------------"

medir matmul_O0        "seq_O0"
medir matmul_O1        "seq_O1"
medir matmul_O2        "seq_O2"
medir matmul_O3        "seq_O3"
medir matmul_Os        "seq_Os"
medir matmul_Ofast     "seq_Ofast"
medir matmul_transpose "transpose"
medir matmul_pthreads  "pthreads"
medir matmul_fork      "fork"

echo ""
echo "Listo. Resultados guardados en $OUT"
echo "Filas generadas: $(( $(wc -l < $OUT) - 1 ))"
echo ""
echo "Ejecuta ahora: python3 plot_results.py"
