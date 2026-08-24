"""Pattern metadata, catalog definitions, and architectural descriptions for Pure C."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from pattern_detector.domain.value_objects import PatternCategory, PatternType


@dataclass(frozen=True)
class PatternCatalogEntry:
    """Catalog entry describing a C design pattern, memory idiom, or rule."""

    pattern_type: PatternType
    category: PatternCategory
    name: str
    description: str
    idiomatic_example: str


PATTERN_CATALOG: Mapping[PatternType, PatternCatalogEntry] = {
    # Creational
    PatternType.OPAQUE_POINTER_ADT: PatternCatalogEntry(
        pattern_type=PatternType.OPAQUE_POINTER_ADT,
        category=PatternCategory.CREATIONAL,
        name="Opaque Pointer (ADT Encapsulation)",
        description="Information hiding via incomplete struct declaration in header (`typedef struct foo foo_t;`) and paired constructor/destructor functions.",
        idiomatic_example="typedef struct buffer_s buffer_t;\nbuffer_t* buffer_create(size_t cap);\nvoid buffer_destroy(buffer_t* buf);",
    ),
    PatternType.SINGLETON_MODULE: PatternCatalogEntry(
        pattern_type=PatternType.SINGLETON_MODULE,
        category=PatternCategory.CREATIONAL,
        name="Singleton Module with Static State",
        description="Encapsulates module-wide private static state with synchronized initialization (`pthread_once` or `static bool initialized`).",
        idiomatic_example="static logger_t g_logger;\nvoid logger_init(void) {\n    pthread_once(&g_once, init_internal);\n}",
    ),
    PatternType.OBJECT_POOL_ALLOCATOR: PatternCatalogEntry(
        pattern_type=PatternType.OBJECT_POOL_ALLOCATOR,
        category=PatternCategory.CREATIONAL,
        name="Object Pool / Slab Allocator",
        description="Pre-allocated contiguous memory chunks with free-list recycling to eliminate runtime malloc fragmentation.",
        idiomatic_example="typedef struct pool {\n    void* memory;\n    struct chunk* free_list;\n} pool_t;\nvoid* pool_alloc(pool_t* p);",
    ),
    PatternType.BUILDER_CONFIG_STRUCT: PatternCatalogEntry(
        pattern_type=PatternType.BUILDER_CONFIG_STRUCT,
        category=PatternCategory.CREATIONAL,
        name="Builder Config Struct Idiom",
        description="Config struct initialization with designated initializers passed to entity creation factory functions.",
        idiomatic_example="http_server_config_t cfg = {\n    .port = 8080,\n    .max_conns = 1000\n};\nhttp_server_t* srv = http_server_create(&cfg);",
    ),

    # Structural
    PatternType.VTABLE_INTERFACE: PatternCatalogEntry(
        pattern_type=PatternType.VTABLE_INTERFACE,
        category=PatternCategory.STRUCTURAL,
        name="VTable Function Pointer Polymorphism",
        description="Dynamic polymorphism in C achieved through structs containing function pointer method tables (e.g. `struct file_operations`).",
        idiomatic_example="struct device_ops {\n    int (*open)(device_t* dev);\n    ssize_t (*read)(device_t* dev, void* buf, size_t len);\n    void (*close)(device_t* dev);\n};",
    ),
    PatternType.INTRUSIVE_LIST_TREE: PatternCatalogEntry(
        pattern_type=PatternType.INTRUSIVE_LIST_TREE,
        category=PatternCategory.KERNEL_IDIOM,
        name="Intrusive Data Structure (container_of)",
        description="Linux kernel style intrusive linked list/tree node embedded inside domain structs resolved via `container_of` / `offsetof`.",
        idiomatic_example="struct list_head {\n    struct list_head *next, *prev;\n};\n#define list_entry(ptr, type, member) container_of(ptr, type, member)",
    ),
    PatternType.ADAPTER_WRAPPER: PatternCatalogEntry(
        pattern_type=PatternType.ADAPTER_WRAPPER,
        category=PatternCategory.STRUCTURAL,
        name="Adapter / HAL Platform Wrapper",
        description="Platform Abstraction Layer (PAL/HAL) adapting OS-specific sockets, threads, or hardware APIs into a uniform interface.",
        idiomatic_example="int hal_socket_read(hal_sock_t* s, void* buf, size_t len) {\n    return posix_read(s->fd, buf, len);\n}",
    ),
    PatternType.FACADE_HEADER: PatternCatalogEntry(
        pattern_type=PatternType.FACADE_HEADER,
        category=PatternCategory.STRUCTURAL,
        name="Facade Header Subsystem",
        description="Single top-level public header aggregating internal subsystem headers into a clean external client API.",
        idiomatic_example="#include <my_lib/core.h>\n#include <my_lib/net.h>\n#include <my_lib/crypto.h>",
    ),
    PatternType.DECORATOR_HOOK: PatternCatalogEntry(
        pattern_type=PatternType.DECORATOR_HOOK,
        category=PatternCategory.STRUCTURAL,
        name="Decorator Function Pointer Hook",
        description="Intercepts or decorates function executions via wrapper function pointers or hook chains.",
        idiomatic_example="typedef void (*hook_fn_t)(void* ctx);\nvoid register_pre_exec_hook(hook_fn_t fn);",
    ),
    PatternType.FLYWEIGHT_INTERN: PatternCatalogEntry(
        pattern_type=PatternType.FLYWEIGHT_INTERN,
        category=PatternCategory.STRUCTURAL,
        name="Flyweight String/Symbol Interning",
        description="Shared global intern table mapping identical immutable string literals/symbols to unique pointer addresses.",
        idiomatic_example="const char* atom_intern(const char* str) {\n    return hash_table_lookup_or_insert(&g_intern_table, str);\n}",
    ),
    PatternType.COMPOSITE_TREE: PatternCatalogEntry(
        pattern_type=PatternType.COMPOSITE_TREE,
        category=PatternCategory.STRUCTURAL,
        name="Composite Tree Node (AST/DOM)",
        description="Hierarchical tree node structure containing array or linked list of child node pointers of the same struct type.",
        idiomatic_example="typedef struct ast_node {\n    int type;\n    struct ast_node** children;\n    size_t child_count;\n} ast_node_t;",
    ),

    # Behavioral
    PatternType.OBSERVER_CALLBACK_REGISTRY: PatternCatalogEntry(
        pattern_type=PatternType.OBSERVER_CALLBACK_REGISTRY,
        category=PatternCategory.BEHAVIORAL,
        name="Observer Callback Registry",
        description="Pub/Sub event notification system allowing listeners to register function pointers with opaque context (`void* user_data`).",
        idiomatic_example="void event_emitter_on(emitter_t* em, event_type_t ev, event_callback_t cb, void* user_data);",
    ),
    PatternType.STRATEGY_FUNCTION_POINTER: PatternCatalogEntry(
        pattern_type=PatternType.STRATEGY_FUNCTION_POINTER,
        category=PatternCategory.BEHAVIORAL,
        name="Strategy Function Pointer Delegation",
        description="Interchangeable algorithm strategies passed as function pointer arguments (e.g. `qsort(..., cmp_fn)` or custom serializers).",
        idiomatic_example="void sort_records(record_t* arr, size_t n, int (*comparator)(const void*, const void*));",
    ),
    PatternType.COMMAND_DISPATCH_TABLE: PatternCatalogEntry(
        pattern_type=PatternType.COMMAND_DISPATCH_TABLE,
        category=PatternCategory.BEHAVIORAL,
        name="Command Dispatch Table",
        description="Array or lookup table of `{opcode/cmd_name, handler_func_ptr}` eliminating long if-else or switch ladders.",
        idiomatic_example="static const struct cmd_entry dispatch_table[] = {\n    {\"GET\", handle_get},\n    {\"POST\", handle_post},\n    {NULL, NULL}\n};",
    ),
    PatternType.STATE_MACHINE_TABLE: PatternCatalogEntry(
        pattern_type=PatternType.STATE_MACHINE_TABLE,
        category=PatternCategory.BEHAVIORAL,
        name="Finite State Machine Transition Table",
        description="Finite State Machine (FSM) implemented via 2D transition table or state handler function pointer matrix.",
        idiomatic_example="typedef state_t (*state_handler_fn)(event_t ev);\nstatic state_handler_fn state_matrix[STATE_MAX][EVENT_MAX];",
    ),
    PatternType.CHAIN_OF_RESPONSIBILITY: PatternCatalogEntry(
        pattern_type=PatternType.CHAIN_OF_RESPONSIBILITY,
        category=PatternCategory.BEHAVIORAL,
        name="Chain of Responsibility Filter Chain",
        description="Singly-linked list of middleware filters where each node processes request and delegates to `next`.",
        idiomatic_example="struct filter {\n    int (*process)(void* req, struct filter* next);\n    struct filter* next;\n};",
    ),
    PatternType.ITERATOR_CURSOR: PatternCatalogEntry(
        pattern_type=PatternType.ITERATOR_CURSOR,
        category=PatternCategory.BEHAVIORAL,
        name="Iterator / Cursor State Traversal",
        description="Opaque iterator struct providing `iterator_has_next()` and `iterator_next()` traversal.",
        idiomatic_example="iterator_t* it = list_iterator_create(list);\nwhile (iterator_has_next(it)) {\n    void* item = iterator_next(it);\n}",
    ),

    # Concurrency, System & Idioms
    PatternType.REACTOR_EVENT_LOOP: PatternCatalogEntry(
        pattern_type=PatternType.REACTOR_EVENT_LOOP,
        category=PatternCategory.CONCURRENCY_EVENT,
        name="Reactor I/O Event Demultiplexer",
        description="Event-driven Reactor loop leveraging non-blocking OS primitives (`epoll_wait`, `kqueue`, `poll`, `select`).",
        idiomatic_example="while (running) {\n    int n = epoll_wait(epfd, events, MAX_EVENTS, -1);\n    for (int i=0; i<n; i++) dispatch(events[i]);\n}",
    ),
    PatternType.GOTO_CLEANUP_IDIOM: PatternCatalogEntry(
        pattern_type=PatternType.GOTO_CLEANUP_IDIOM,
        category=PatternCategory.RESILIENCE_CLEANUP,
        name="Goto Error Cleanup (RAII in C)",
        description="Kernel standard single-exit multi-level resource release idiom using `goto cleanup` labels.",
        idiomatic_example="if (!res1) goto err_cleanup_res1;\nif (!res2) goto err_cleanup_res2;\nreturn OK;\nerr_cleanup_res2: free(res1);\nreturn ERR;",
    ),

    # Resilience, Principles & Memory Safety
    PatternType.UNCHECKED_MALLOC_RETURN: PatternCatalogEntry(
        pattern_type=PatternType.UNCHECKED_MALLOC_RETURN,
        category=PatternCategory.MEMORY_SAFETY,
        name="Unchecked Malloc Return Dereference",
        description="Calling `malloc`/`calloc`/`realloc` without checking for NULL return before dereferencing pointer.",
        idiomatic_example="Always verify `if (!ptr) { handle_oom_error(); }` immediately after dynamic allocation.",
    ),
    PatternType.UNSAFE_STRING_FUNCTION: PatternCatalogEntry(
        pattern_type=PatternType.UNSAFE_STRING_FUNCTION,
        category=PatternCategory.MEMORY_SAFETY,
        name="Unsafe C String Buffer Overflow Risk",
        description="Using dangerous legacy buffer manipulation routines (`strcpy`, `strcat`, `sprintf`, `gets`) instead of bounds-checked alternatives (`strncpy`, `snprintf`, `strlcpy`).",
        idiomatic_example="Replace `sprintf(buf, ...)` with `snprintf(buf, sizeof(buf), ...)`. ",
    ),
    PatternType.MEMORY_LEAK_MISSING_FREE: PatternCatalogEntry(
        pattern_type=PatternType.MEMORY_LEAK_MISSING_FREE,
        category=PatternCategory.MEMORY_SAFETY,
        name="Potential Resource / Memory Leak",
        description="Function allocates heap memory with `malloc` or opens files with `fopen` but returns on error branches without freeing/closing.",
        idiomatic_example="Ensure all allocated pointers are freed on every return branch or use `goto cleanup;`.",
    ),
    PatternType.DOUBLE_FREE_RISK: PatternCatalogEntry(
        pattern_type=PatternType.DOUBLE_FREE_RISK,
        category=PatternCategory.MEMORY_SAFETY,
        name="Double Free / Dangling Pointer Risk",
        description="Calling `free(ptr)` without resetting `ptr = NULL` in reusable contexts or calling `free()` multiple times on same pointer.",
        idiomatic_example="Use safe free macro: `#define SAFE_FREE(p) do { free(p); (p) = NULL; } while(0)`.",
    ),
    PatternType.GOD_C_FILE_SRP: PatternCatalogEntry(
        pattern_type=PatternType.GOD_C_FILE_SRP,
        category=PatternCategory.PRINCIPLE,
        name="Single Responsibility (God C File)",
        description="Monolithic C source file with excessive global functions (≥30 functions) or lines of code (≥1000 LOC).",
        idiomatic_example="Decompose monolithic `.c` file into modular subsystems with private internal headers.",
    ),
    PatternType.CYCLOMATIC_COMPLEXITY_KISS: PatternCatalogEntry(
        pattern_type=PatternType.CYCLOMATIC_COMPLEXITY_KISS,
        category=PatternCategory.PRINCIPLE,
        name="Keep It Simple (KISS Complexity)",
        description="Function with excessive cyclomatic complexity, deeply nested loops, or massive switch cases (≥12 branches).",
        idiomatic_example="Refactor nested conditionals into table-driven dispatch or smaller static helper routines.",
    ),
    PatternType.DUPLICATE_CODE_DRY: PatternCatalogEntry(
        pattern_type=PatternType.DUPLICATE_CODE_DRY,
        category=PatternCategory.PRINCIPLE,
        name="Don't Repeat Yourself (DRY)",
        description="Duplicated C function logic across multiple files.",
        idiomatic_example="Extract duplicated routines into a shared static inline header or utility module.",
    ),
    PatternType.CIRCULAR_HEADER_INCLUDE: PatternCatalogEntry(
        pattern_type=PatternType.CIRCULAR_HEADER_INCLUDE,
        category=PatternCategory.PRINCIPLE,
        name="Circular Header Include Dependency",
        description="Mutual `#include` header cycles (HeaderA.h -> HeaderB.h -> HeaderA.h).",
        idiomatic_example="Use forward declarations (`struct foo;`) in headers instead of full `#include` cycles.",
    ),
}
