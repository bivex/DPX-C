# ⚡ DPX-C: Hexagonal Architecture, OOP in C & Memory Safety Pattern Detector

<p align="center">
  <img src="https://img.shields.io/badge/Language-C89%20%7C%20C99%20%7C%20C11%20%7C%20C17%20%7C%20C23-blue.svg?style=for-the-badge&logo=c" alt="C" />
  <img src="https://img.shields.io/badge/Architecture-Hexagonal%20Ports%20%26%20Adapters-blueviolet.svg?style=for-the-badge" alt="Hexagonal" />
  <img src="https://img.shields.io/badge/Rules-27%20Patterns-success.svg?style=for-the-badge" alt="Rules" />
  <img src="https://img.shields.io/badge/Output-SARIF%20%7C%20HTML%20%7C%20JSON%20%7C%20Markdown-orange.svg?style=for-the-badge" alt="Outputs" />
</p>

---

## 📖 Overview

**DPX-C** is a static analysis and software design pattern detection engine designed for **Pure C projects** (C89, C99, C11, C17, C23).

Built on **Hexagonal Architecture (Ports and Adapters)** and **Domain-Driven Design (DDD)** principles, DPX-C identifies OOP in C idioms, VTable function pointer interfaces, Opaque Pointer ADT encapsulation, Linux-kernel style intrusive containers (`container_of`), Reactor event loops (`epoll`/`kqueue`), and critical memory safety hazards (unchecked `malloc` returns, buffer-unsafe string manipulation, double frees, and resource leaks).

---

## 🔷 Catalog of 27 Supported C Patterns & Safety Rules

| Category | Pattern / Rule | Rule Code | Description |
|---|---|---|---|
| **Creational** | **Opaque Pointer (ADT)** | `OPAQUE_POINTER_ADT` | Incomplete struct declaration in headers with paired constructor/destructor functions. |
| **Creational** | **Singleton Module** | `SINGLETON_MODULE` | Module-wide private static state with synchronized `pthread_once` or init guards. |
| **Creational** | **Object Pool / Slab** | `OBJECT_POOL_ALLOCATOR` | Pre-allocated contiguous memory pools with free-list recycling. |
| **Creational** | **Builder Config Struct** | `BUILDER_CONFIG_STRUCT` | Config struct initialization pattern passed to subsystem init factories. |
| **Structural** | **VTable Interface** | `VTABLE_INTERFACE` | Dynamic polymorphism via structs of function pointers (e.g. `struct file_operations`). |
| **Kernel Idiom** | **Intrusive Data Structure** | `INTRUSIVE_LIST_TREE` | Zero-allocation intrusive linked lists/trees resolved via `container_of` / `offsetof`. |
| **Structural** | **Adapter / HAL Wrapper** | `ADAPTER_WRAPPER` | Platform Abstraction Layer (PAL/HAL) uniform OS wrappers. |
| **Structural** | **Facade Header** | `FACADE_HEADER` | Top-level header aggregating internal subsystem headers. |
| **Structural** | **Decorator Hook** | `DECORATOR_HOOK` | Interception / wrapper function pointer hooks. |
| **Structural** | **Flyweight Interning** | `FLYWEIGHT_INTERN` | String / symbol interning hash table for immutable token sharing. |
| **Structural** | **Composite Tree Node** | `COMPOSITE_TREE` | Recursive AST / DOM tree nodes with child pointers. |
| **Behavioral** | **Observer Callback Registry** | `OBSERVER_CALLBACK_REGISTRY` | Callback registration arrays with opaque context pointers (`void* user_data`). |
| **Behavioral** | **Strategy Function Pointer** | `STRATEGY_FUNCTION_POINTER` | Dynamic algorithm strategy injection via function pointer arguments. |
| **Behavioral** | **Command Dispatch Table** | `COMMAND_DISPATCH_TABLE` | Static lookup tables mapping commands to handler function pointers. |
| **Behavioral** | **State Machine Transition Table**| `STATE_MACHINE_TABLE` | Finite State Machine (FSM) 2D transition matrices. |
| **Behavioral** | **Chain of Responsibility** | `CHAIN_OF_RESPONSIBILITY` | Singly-linked list filter chains with `next` delegation. |
| **Behavioral** | **Iterator / Cursor** | `ITERATOR_CURSOR` | Cursor structs with sequential collection traversal. |
| **Concurrency & System** | **Reactor Event Loop** | `REACTOR_EVENT_LOOP` | Non-blocking event demultiplexer loops (`epoll_wait`, `kevent`, `poll`). |
| **Resilience & Cleanup**| **Goto RAII Cleanup** | `GOTO_CLEANUP_IDIOM` | Single-exit multi-level resource release idiom (`goto cleanup;`). |
| **Memory Safety** | **Unchecked Malloc Return** | `UNCHECKED_MALLOC_RETURN` | Dereferencing `malloc`/`calloc` return without NULL check. |
| **Memory Safety** | **Unsafe C String API** | `UNSAFE_STRING_FUNCTION` | Using buffer overflow prone legacy functions (`strcpy`, `strcat`, `sprintf`, `gets`). |
| **Memory Safety** | **Potential Memory Leak** | `MEMORY_LEAK_MISSING_FREE` | Allocating local resources without freeing on error paths. |
| **Memory Safety** | **Double Free Risk** | `DOUBLE_FREE_RISK` | Duplicate `free(ptr)` calls on the same pointer variable. |
| **Quality & Principles** | **God C File (SRP)** | `GOD_C_FILE_SRP` | Monolithic C files with excessive global functions (≥30 functions). |
| **Quality & Principles** | **KISS Complexity** | `CYCLOMATIC_COMPLEXITY_KISS` | Deeply nested conditionals or massive switch branches (≥12 complexity). |
| **Quality & Principles** | **Don't Repeat Yourself (DRY)** | `DUPLICATE_CODE_DRY` | Duplicated C function implementations across files. |
| **Quality & Principles** | **Circular Header Include** | `CIRCULAR_HEADER_INCLUDE` | Mutual `#include` header cycles. |

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/bivex/DPX-C.git
cd DPX-C
uv sync
```

### Usage

```bash
# Terminal scan with rich formatting
uv run dpx-c scan /path/to/c_project

# Generate interactive dark Semantic UI HTML dashboard
uv run dpx-c scan /path/to/c_project -H reports/dashboard.html

# Generate SARIF for GitHub Code Scanning
uv run dpx-c scan /path/to/c_project -S reports/security.sarif

# Export AI Context prompt for LLM refactoring
uv run dpx-c scan /path/to/c_project --llm
```

---

## 🌐 The DPX Suite Family

Cross-language architectural static analysis across all modern programming languages:

| Repository | Language / Ecosystem | Primary Paradigms & Focus |
|---|---|---|
| **[`DPX-Move`](https://github.com/bivex/DPX-Move)** | **Move** (Move 2024 / Aptos / Sui) | **Linear Resources, Abilities, Sui Objects, Hot Potato, Prover, GoF 23** |
| **[`DPX-Lua`](https://github.com/bivex/DPX-Lua)** | **Lua / Luau** (5.1 - 5.4 / LuaJIT) | **Metatable OOP, Coroutines, LuaJIT FFI, GameDev (Roblox/Neovim), GoF 23** |
| **[`DPX-Solidity`](https://github.com/bivex/DPX-Solidity)** | **Solidity** (0.8.x - 0.8.28+) | **EVM Gas Optimization, Proxies, CEI Reentrancy, Yul, GoF 23, Security** |
| **[`DPX-Zig`](https://github.com/bivex/DPX-Zig)** | **Zig** (0.11 - 0.14+) | **Comptime Generics, Allocator RAII, Defer Cleanup, SIMD, GoF 23** |
| **[`DPX-Gleam`](https://github.com/bivex/DPX-Gleam)** | **Gleam** (1.0 - 1.8+) | **Type-Safe OTP Actors, Algebraic Data Types, Railway Monads, GoF 23** |
| **[`DPX-Mojo`](https://github.com/bivex/DPX-Mojo)** | **Mojo** (24.x - 25.x+) | **SIMD Vectorization, Ownership, Memory Safety, GoF 23, AI Acceleration** |
| **[`DPX-Julia`](https://github.com/bivex/DPX-Julia)** | **Julia** (1.6 - 1.11+) | **Multiple Dispatch, Holy Traits, Metaprogramming, Tasks, GoF 23** |
| **[`DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin)** | **Kotlin** (1.8 - 2.0+) | **Coroutines, Flow, Jetpack Compose, Multiplatform, GoF 23** |
| **[`DPX-Swift`](https://github.com/bivex/DPX-Swift)** | **Swift** (5.5 - 6.0+) | **Protocol-Oriented, Actor Concurrency, SwiftUI, ARC Safety** |
| **[`DPX-CSharp`](https://github.com/bivex/DPX-CSharp)** | **C#** (10 - 13 / .NET 8-9) | **Clean Architecture, CQRS MediatR, Channel Pipelines** |
| **[`DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript)** | **TypeScript / JavaScript** | **Hexagonal DI, Decorator Meta, Reactive Streams, React/NestJS** |
| **[`DPX-Rust`](https://github.com/bivex/DPX-Rust)** | **Rust** (Edition 2021/2024) | **Zero-Cost Abstractions, RAII Lifetimes, Typestate Pattern** |
| **[`DPX-Go`](https://github.com/bivex/DPX-Go)** | **Go** (1.18 - 1.24+) | **Goroutine Channels, CSP Concurrency, Pipeline Streaming** |
| **[`DPX-Py`](https://github.com/bivex/DPX-Py)** | **Python** (3.8 - 3.13+) | **Multi-Paradigm Hexagonal, Data Flow Engine, AsyncIO** |
| **[`DPX-Php`](https://github.com/bivex/DPX-Php)** | **PHP** (8.1 - 8.4+) | **Attribute-driven DDD, Fiber Concurrency, Laravel/Symfony** |
| **[`DPX-Haskell`](https://github.com/bivex/DPX-Haskell)** | **Haskell** (GHC 9.2 - 9.12+) | **Category Theory, Monad Transformers, Free Monads, Optics** |
| **[`DPX-OCaml`](https://github.com/bivex/DPX-OCaml)** | **OCaml** (4.14 - 5.3+ Multicore) | **Functor Modules, Effect Handlers, GADTs, Railway Monads** |
| **[`DPX-Elixir`](https://github.com/bivex/DPX-Elixir)** | **Elixir** (OTP 25 - 27+) | **GenServer, DynamicSupervisor, Actor Fault Tolerance** |
| **[`DPX-Erlang`](https://github.com/bivex/DPX-Erlang)** | **Erlang/OTP** (24 - 27+) | **OTP Behaviors, Supervision Trees, Message Passing** |
| **[`DPX-C`](https://github.com/bivex/DPX-C)** | **C** (C99 - C23) | **Opaque Structs, VTables, MISRA/CERT Safety, Arena Allocators** |
| **[`DPX-Cpp`](https://github.com/bivex/DPX-Cpp)** | **C++** (C++14 - C++20) | **CRTP, Policy-Based Design, RAII Memory Safety, ANTLR4 AST** |
| **[`DPX-Java`](https://github.com/bivex/DPX-Java)** | **Java** (17 - 23+) | **Virtual Threads, Spring Boot / Jakarta EE, GoF Patterns** |
| **[`DPX`](https://github.com/bivex/DPX)** | **Clojure** / Meta Engine | **Pure Functional, Multimethods, Homoiconic Macro Architecture** |
---

## 📄 License

MIT © bivex
