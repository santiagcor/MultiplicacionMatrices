#!/bin/bash
# Benchmark: corre cada versión 10 veces por cada N, guarda resultados en CSV

REPS=10
SIZES="100 200 400 600 800 1000"
OUT="resultados.csv"

echo "version,n,rep,tiempo_ms" > $OUT

compilar() {
    echo "Compilando..."
    g++ -O0 -o matmul_seq        matmul_seq.cpp
    g++ -O3 -o matmul_seq_O3     matmul_seq.cpp
    g++ -O3 -o matmul_transpose  matmul_transpose.cpp
    g++ -O3 -o matmul_pthreads   matmul_pthreads.cpp -lpthread
    g++ -O3 -o matmul_fork       matmul_fork.cpp
    echo "Compilado OK"
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
medir matmul_seq        "seq_O0"
medir matmul_seq_O3     "seq_O3"
medir matmul_transpose  "transpose_O3"
medir matmul_pthreads   "pthreads_O3"
medir matmul_fork       "fork_O3"

echo "Listo. Resultados en $OUT"
