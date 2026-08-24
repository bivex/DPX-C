#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void unsafe_buffer_operations(const char* input_str) {
    char local_buf[32];
    /* Buffer overflow vulnerability: strcpy / sprintf */
    strcpy(local_buf, input_str);

    /* Unchecked malloc dereference */
    int* numbers = (int*)malloc(10 * sizeof(int));
    numbers[0] = 100;
}

int double_free_and_leak(int flag) {
    char* chunk = (char*)malloc(128);
    if (!chunk) return -1;

    if (flag) {
        free(chunk);
        /* Potential double free hazard */
        free(chunk);
        return 0;
    }

    return 1; /* Resource leak: chunk not freed */
}
