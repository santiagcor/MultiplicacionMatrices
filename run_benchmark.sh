#!/bin/bash
# Benchmark: corre cada versión 10 veces por cada N, guarda resultados en CSV

REPS=10
SIZES="500 1000 1500 2000 3000"
OUT="resultados.csv"

echo "version,n,rep,tiempo_ms" > $OUT

compilar() {
    g++ -O0    -o matmul_O0    matmul_seq.cpp
    g++ -O1    -o matmul_O1    matmul_seq.cpp
    g++ -O2    -o matmul_O2    matmul_seq.cpp
    g++ -O3    -o matmul_O3    matmul_seq.cpp
    g++ -Os    -o matmul_Os    matmul_seq.cpp
    g++ -Ofast -o matmul_Ofast matmul_seq.cpp
    g++ -O3    -o matmul_transpose matmul_transpose.cpp
    g++ -O3    -o matmul_pthreads  matmul_pthreads.cpp -lpthread
    g++ -O3    -o matmul_fork      matmul_fork.cpp
}


medir() {
    local bin=$1
    local version=$2
    for n in $SIZES; do
        echo "  $version n=$n..."
        for rep in $(seq 1 $REPS); do
            t=$(./$bin $n 2>/dev/null)
            echo "$version,$n,$rep,$t" >> $OUT
        done
    done
}

compilar
echo "Corriendo benchmarks..."
medir matmul_O0        "seq_O0"
medir matmul_O1        "seq_O1"
medir matmul_O2        "seq_O2"
medir matmul_O3        "seq_O3"
medir matmul_Os        "seq_Os"
medir matmul_Ofast     "seq_Ofast"
medir matmul_transpose "transpose"
medir matmul_pthreads  "pthreads"
medir matmul_fork      "fork"

echo "Listo. Resultados en $OUT"
