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


def test_composite_tree_distinguishes_lists_and_trees():
    from pattern_detector.domain.rules.composite_tree_rule import CompositeTreeRule

    sources = {
        "include/ast.h": """
        struct ast_node {
            int token_type;
            struct ast_node* left;
            struct ast_node* right;
            struct ast_node* parent;
        };
        struct json_val {
            int type;
            struct json_val* child;
            struct json_val* next;
            struct json_val* prev;
        };
        """,
        "include/list.h": """
        struct list_node {
            int val;
            struct list_node* prev;
            struct list_node* next;
        };
        """,
    }
    parser = NativeCParserAdapter()
    model = parser.parse_sources(sources)

    detections = CompositeTreeRule().detect(model)
    detected_names = {d.target_name for d in detections}

    assert "ast_node" in detected_names
    assert "json_val" in detected_names
    assert "list_node" not in detected_names


def test_double_free_ignores_error_branch_returns():
    from pattern_detector.domain.rules.double_free_risk_rule import DoubleFreeRiskRule

    sources = {
        "src/cleanup.c": """
        int safe_branches(int fd, size_t len) {
            char* data = (char*)malloc(len);
            if (fd < 0) {
                free(data);
                return -1;
            }
            if (len > 1000) {
                free(data);
                return -2;
            }
            free(data);
            return 0;
        }

        void actual_double_free(char* p) {
            free(p);
            free(p);
        }
        """
    }
    parser = NativeCParserAdapter()
    model = parser.parse_sources(sources)

    detections = DoubleFreeRiskRule().detect(model)
    assert len(detections) == 1
    assert detections[0].target_name == "src/cleanup.c:actual_double_free"


def test_facade_header_ignores_standard_c_includes():
    from pattern_detector.domain.rules.facade_header_rule import FacadeHeaderRule

    sources = {
        "include/std_only.h": """
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <stdint.h>
        #include <unistd.h>
        """,
        "include/facade.h": """
        #include "subsystem/parser.h"
        #include "subsystem/lexer.h"
        #include "subsystem/ast.h"
        #include "subsystem/codegen.h"
        """,
    }
    parser = NativeCParserAdapter()
    model = parser.parse_sources(sources)

    detections = FacadeHeaderRule().detect(model)
    assert len(detections) == 1
    assert detections[0].target_name == "include/facade.h"
