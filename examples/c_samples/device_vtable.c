#include <stdio.h>
#include <stdlib.h>

typedef struct device_s device_t;

/* VTable Function Pointer Interface */
struct device_operations {
    int (*open)(device_t* dev, const char* name);
    ssize_t (*read)(device_t* dev, void* buf, size_t len);
    ssize_t (*write)(device_t* dev, const void* buf, size_t len);
    void (*close)(device_t* dev);
};

struct device_s {
    const struct device_operations* ops;
    void* driver_data;
};

/* Strategy / Callback Delegation */
ssize_t device_transfer(device_t* dev, void* buf, size_t len, int (*filter_strategy)(const void*, size_t)) {
    if (filter_strategy && filter_strategy(buf, len) != 0) {
        return -1;
    }
    return dev->ops->read(dev, buf, len);
}
