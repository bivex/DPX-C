#include "buffer_adt.h"
#include <stdlib.h>
#include <string.h>

struct buffer_s {
    char* data;
    size_t size;
    size_t capacity;
};

buffer_t* buffer_create(size_t initial_capacity) {
    buffer_t* buf = (buffer_t*)malloc(sizeof(buffer_t));
    if (!buf) return NULL;

    buf->data = (char*)malloc(initial_capacity);
    if (!buf->data) {
        free(buf);
        return NULL;
    }
    buf->size = 0;
    buf->capacity = initial_capacity;
    return buf;
}

void buffer_destroy(buffer_t* buf) {
    if (buf) {
        if (buf->data) {
            free(buf->data);
            buf->data = NULL;
        }
        free(buf);
    }
}
