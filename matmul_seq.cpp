#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <chrono>
using namespace std;
using Matriz = vector<vector<int>>;

Matriz crearAleatoria(int n) {
    Matriz M(n, vector<int>(n));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            M[i][j] = rand() % 9 + 1;
    return M;
}

Matriz multiplicar(const Matriz& A, const Matriz& B, int n) {
    Matriz C(n, vector<int>(n, 0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    return C;
}

int main(int argc, char* argv[]) {
    if (argc != 2) { cerr << "Uso: " << argv[0] << " <n>\n"; return 1; }
    int n = atoi(argv[1]);
    if (n <= 0) { cerr << "n debe ser positivo\n"; return 1; }

    srand(42); // semilla fija para resultados reproducibles
    Matriz A = crearAleatoria(n);
    Matriz B = crearAleatoria(n);

    auto inicio = chrono::high_resolution_clock::now();
    Matriz C = multiplicar(A, B, n);
    auto fin   = chrono::high_resolution_clock::now();

    double ms = chrono::duration<double, milli>(fin - inicio).count();
    cout << ms << endl; // imprime solo el tiempo (para benchmarking)
    return 0;
}
