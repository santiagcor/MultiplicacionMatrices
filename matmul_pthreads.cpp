#include <iostream>
#include <pthread.h>
#include <chrono>
#include <cstdlib>
using namespace std;

#define NUM_HILOS 4
#define AT(M,i,j,n) ((M)[(i)*(n)+(j)])

struct ArgHilo {
    int  id;
    int  n;
    int* A;
    int* B;
    int* C;
};

void* calcularFilas(void* arg) {
    ArgHilo* a = (ArgHilo*)arg;
    int n      = a->n;
    int inicio = (a->id * n) / NUM_HILOS;
    int fin    = ((a->id + 1) * n) / NUM_HILOS;

    for (int i = inicio; i < fin; i++)
        for (int j = 0; j < n; j++) {
            int suma = 0;
            for (int k = 0; k < n; k++)
                suma += AT(a->A, i, k, n) * AT(a->B, k, j, n);
            AT(a->C, i, j, n) = suma;
        }
    return nullptr;
}

int main(int argc, char* argv[]) {
    if (argc != 2) { cerr << "Uso: " << argv[0] << " <n>\n"; return 1; }
    int n = atoi(argv[1]);
    if (n <= 0) { cerr << "n debe ser positivo\n"; return 1; }

    srand(42);
    int* A = new int[n * n];
    int* B = new int[n * n];
    int* C = new int[n * n]();

    for (int i = 0; i < n * n; i++) {
        A[i] = rand() % 9 + 1;
        B[i] = rand() % 9 + 1;
    }

    pthread_t hilos[NUM_HILOS];
    ArgHilo   args[NUM_HILOS];

    auto t0 = chrono::steady_clock::now();

    for (int t = 0; t < NUM_HILOS; t++) {
        args[t] = {t, n, A, B, C};
        pthread_create(&hilos[t], nullptr, calcularFilas, &args[t]);
    }
    for (int t = 0; t < NUM_HILOS; t++)
        pthread_join(hilos[t], nullptr);

    auto t1 = chrono::steady_clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();
    cout << ms << endl;

    delete[] A; delete[] B; delete[] C;
    return 0;
}
