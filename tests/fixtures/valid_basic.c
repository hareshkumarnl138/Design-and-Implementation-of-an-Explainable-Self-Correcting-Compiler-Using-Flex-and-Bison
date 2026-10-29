#include <stdio.h>

/* Compute factorial iteratively. */
int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;   // accumulate
    }
    return result;
}

int main(void) {
    float ratio = 3.14e-2f;
    char c = '\n';
    int mask = 0xFF & 077;
    printf("factorial(5) = %d\n", factorial(5));
    if (mask >= 10 && ratio != 0.5) { c = 'x'; }
    return 0;
}
