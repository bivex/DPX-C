#ifndef BUFFER_ADT_H
#define BUFFER_ADT_H

#include <stddef.h>
#include <stdbool.h>

/* Opaque pointer definition (ADT encapsulation) */
typedef struct buffer_s buffer_t;

buffer_t* buffer_create(size_t initial_capacity);
void buffer_destroy(buffer_t* buf);
bool buffer_append(buffer_t* buf, const char* data, size_t len);
const char* buffer_get_data(const buffer_t* buf);

#endif /* BUFFER_ADT_H */
