"""Tests for C Design Pattern and Safety Rules."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_c_parser_adapter import NativeCParserAdapter
from pattern_detector.domain.rules.goto_cleanup_idiom_rule import GotoCleanupIdiomRule
from pattern_detector.domain.rules.intrusive_list_tree_rule import IntrusiveListTreeRule
from pattern_detector.domain.rules.opaque_pointer_adt_rule import OpaquePointerAdtRule
from pattern_detector.domain.rules.unchecked_malloc_return_rule import UncheckedMallocReturnRule
from pattern_detector.domain.rules.unsafe_string_function_rule import UnsafeStringFunctionRule
from pattern_detector.domain.rules.vtable_interface_rule import VTableInterfaceRule


def test_detect_vtable_and_intrusive_list():
    sources = {
        "include/driver.h": """
        struct file_operations {
            int (*read)(void* buf, size_t len);
            int (*write)(const void* buf, size_t len);
        };
        """,
        "src/list.c": """
        #include <stddef.h>
        struct list_head {
            struct list_head *next, *prev;
        };
        #define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
        """,
    }
    parser = NativeCParserAdapter()
    model = parser.parse_sources(sources)

    vtables = VTableInterfaceRule().detect(model)
    assert len(vtables) >= 1
    assert vtables[0].target_name == "file_operations"

    intrusives = IntrusiveListTreeRule().detect(model)
    assert len(intrusives) >= 1


def test_detect_safety_hazards():
    source = """
    #include <stdlib.h>
    #include <string.h>

    void vulnerable_func(const char* input) {
        char buffer[64];
        strcpy(buffer, input);

        int* ptr = (int*)malloc(100 * sizeof(int));
        ptr[0] = 42; // Unchecked malloc dereference
    }

    int safe_cleanup_func(int condition) {
        char* mem = (char*)malloc(128);
        if (!mem) goto err_out;

        if (condition < 0) goto err_cleanup;

        free(mem);
        return 0;

    err_cleanup:
        free(mem);
    err_out:
        return -1;
    }
    """
    parser = NativeCParserAdapter()
    model = parser.parse_sources({"src/vuln.c": source})

    unsafe_str = UnsafeStringFunctionRule().detect(model)
    assert len(unsafe_str) == 1

    unchecked_malloc = UncheckedMallocReturnRule().detect(model)
    assert len(unchecked_malloc) == 1

    goto_clean = GotoCleanupIdiomRule().detect(model)
    assert len(goto_clean) == 1
