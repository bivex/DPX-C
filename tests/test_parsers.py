"""Tests for Native C Parser Adapter."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_c_parser_adapter import NativeCParserAdapter


def test_parse_c_struct_and_functions():
    source = """
    #include <stdio.h>
    #include <stdlib.h>

    typedef struct device_ops {
        int (*open)(const char* name, int flags);
        ssize_t (*read)(void* buf, size_t count);
        void (*close)(void);
    } device_ops_t;

    static int dev_open(const char* name, int flags) {
        if (!name) return -1;
        printf("Opening device %s\\n", name);
        return 0;
    }
    """
    parser = NativeCParserAdapter()
    model = parser.parse_sources({"src/dev.c": source})

    assert "src/dev.c" in model.files
    f = model.files["src/dev.c"]
    assert "stdio.h" in f.includes
    assert "device_ops" in f.structs or "device_ops_t" in f.structs
    st = f.structs.get("device_ops") or f.structs.get("device_ops_t")
    assert st is not None
    assert st.has_function_pointers is True
    assert len(st.function_pointer_members) == 3

    assert "dev_open" in f.functions
    fn = f.functions["dev_open"]
    assert fn.is_static is True
    assert len(fn.params) == 2


def test_parse_function_pointer_params():
    source = """
    void sort_array(int* arr, size_t len, int (*cmp)(const void*, const void*)) {
        qsort(arr, len, sizeof(int), cmp);
    }
    """
    parser = NativeCParserAdapter()
    model = parser.parse_sources({"src/sort.c": source})

    f = model.files["src/sort.c"]
    fn = f.functions["sort_array"]
    assert len(fn.params) == 3
    assert fn.params[2].is_function_pointer is True
