#include <iostream>
#include <chrono>
#include <cstdlib>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
using namespace std;

#define NUM_PROCS 4
#define AT(M,i,j,n) ((M)[(i)*(n)+(j)])

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
    int* A = new int[n * n];
    int* B = new int[n * n];
    int* C = shared_alloc(n * n);

    for (int i = 0; i < n * n; i++) {
        A[i] = rand() % 9 + 1;
        B[i] = rand() % 9 + 1;
        C[i] = 0;
    }

    auto t0 = chrono::steady_clock::now();

    pid_t pids[NUM_PROCS];
    for (int p = 0; p < NUM_PROCS; p++) {
        pids[p] = fork();
        if (pids[p] == 0) {
            int fila_ini = (p * n) / NUM_PROCS;
            int fila_fin = ((p + 1) * n) / NUM_PROCS;
            for (int i = fila_ini; i < fila_fin; i++)
                for (int j = 0; j < n; j++) {
                    int suma = 0;
                    for (int k = 0; k < n; k++)
                        suma += AT(A, i, k, n) * AT(B, k, j, n);
                    AT(C, i, j, n) = suma;
                }
            exit(0);
        }
    }

    for (int p = 0; p < NUM_PROCS; p++)
        waitpid(pids[p], nullptr, 0);

    auto t1 = chrono::steady_clock::now();
    double ms = chrono::duration<double, milli>(t1 - t0).count();
    cout << ms << endl;

    delete[] A; delete[] B;
    munmap(C, n * n * sizeof(int));
    return 0;
}
