#include <iostream>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <sys/mman.h>   // mmap
#include <sys/wait.h>   // waitpid
#include <unistd.h>     // fork
using namespace std;

#define NUM_PROCS 4
#define AT(M,i,j,n) ((M)[(i)*(n)+(j)])

// Reserva memoria compartida entre padre e hijos via mmap
int* shared_alloc(int elementos) {
    return (int*)mmap(nullptr, elementos * sizeof(int),
                      PROT_READ | PROT_WRITE,
                      MAP_SHARED | MAP_ANONYMOUS, -1, 0);
}

int main(int argc, char* argv[]) {
    if (argc != 2) { cerr << "Uso: " << argv[0] << " <n>\n"; return 1; }
    int n = atoi(argv[1]);
    if (n <= 0) { cerr << "n debe ser positivo\n"; return 1; }

    srand(42);

    // A y B en memoria normal (solo lectura por hijos)
    // C en memoria COMPARTIDA para que hijos escriban
    int* A = new int[n * n];
    int* B = new int[n * n];
    int* C = shared_alloc(n * n); // memoria compartida

    for (int i = 0; i < n * n; i++) {
        A[i] = rand() % 9 + 1;
        B[i] = rand() % 9 + 1;
        C[i] = 0;
    }

    auto inicio = chrono::high_resolution_clock::now();

    pid_t pids[NUM_PROCS];

    // Crear procesos hijo (fork)
    for (int p = 0; p < NUM_PROCS; p++) {
        pids[p] = fork();
        if (pids[p] == 0) {
            // Proceso hijo: calcula su bloque de filas
            int fila_ini = (p * n) / NUM_PROCS;
            int fila_fin = ((p + 1) * n) / NUM_PROCS;

            for (int i = fila_ini; i < fila_fin; i++)
                for (int j = 0; j < n; j++) {
                    int suma = 0;
                    for (int k = 0; k < n; k++)
                        suma += AT(A, i, k, n) * AT(B, k, j, n);
                    AT(C, i, j, n) = suma;
                }
            exit(0); // hijo termina
        }
    }

    // Padre espera a todos los hijos (join implícito)
    for (int p = 0; p < NUM_PROCS; p++)
        waitpid(pids[p], nullptr, 0);

    auto fin = chrono::high_resolution_clock::now();
    double ms = chrono::duration<double, milli>(fin - inicio).count();
    cout << ms << endl;

    delete[] A; delete[] B;
    munmap(C, n * n * sizeof(int));
    return 0;
}
