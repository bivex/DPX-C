"""Domain value objects for the Pure C Pattern Detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PatternCategory(str, Enum):
    """Broad classification of C design patterns, memory idioms, and safety rules."""

    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    CONCURRENCY_EVENT = "concurrency_event"
    KERNEL_IDIOM = "kernel_idiom"
    RESILIENCE_CLEANUP = "resilience_cleanup"
    PRINCIPLE = "principle"
    MEMORY_SAFETY = "memory_safety"


class PatternType(str, Enum):
    """Specific C design pattern, idiomatic pattern, and vulnerability identifiers."""

    # Creational
    OPAQUE_POINTER_ADT = "opaque_pointer_adt"
    SINGLETON_MODULE = "singleton_module"
    OBJECT_POOL_ALLOCATOR = "object_pool_allocator"
    BUILDER_CONFIG_STRUCT = "builder_config_struct"

    # Structural
    VTABLE_INTERFACE = "vtable_interface"
    INTRUSIVE_LIST_TREE = "intrusive_list_tree"
    ADAPTER_WRAPPER = "adapter_wrapper"
    FACADE_HEADER = "facade_header"
    DECORATOR_HOOK = "decorator_hook"
    FLYWEIGHT_INTERN = "flyweight_intern"
    COMPOSITE_TREE = "composite_tree"

    # Behavioral
    OBSERVER_CALLBACK_REGISTRY = "observer_callback_registry"
    STRATEGY_FUNCTION_POINTER = "strategy_function_pointer"
    COMMAND_DISPATCH_TABLE = "command_dispatch_table"
    STATE_MACHINE_TABLE = "state_machine_table"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    ITERATOR_CURSOR = "iterator_cursor"

    # Concurrency, System & Idioms
    REACTOR_EVENT_LOOP = "reactor_event_loop"
    GOTO_CLEANUP_IDIOM = "goto_cleanup_idiom"

    # Resilience, Principles & Memory Safety
    UNCHECKED_MALLOC_RETURN = "unchecked_malloc_return"
    UNSAFE_STRING_FUNCTION = "unsafe_string_function"
    MEMORY_LEAK_MISSING_FREE = "memory_leak_missing_free"
    DOUBLE_FREE_RISK = "double_free_risk"
    GOD_C_FILE_SRP = "god_c_file_srp"
    CYCLOMATIC_COMPLEXITY_KISS = "cyclomatic_complexity_kiss"
    DUPLICATE_CODE_DRY = "duplicate_code_dry"
    CIRCULAR_HEADER_INCLUDE = "circular_header_include"


class ConfidenceLevel(str, Enum):
    """Categorical confidence rating for a pattern detection."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

    @classmethod
    def from_score(cls, score: float) -> ConfidenceLevel:
        if score >= 0.85:
            return cls.VERY_HIGH
        if score >= 0.70:
            return cls.HIGH
        if score >= 0.50:
            return cls.MEDIUM
        return cls.LOW


@dataclass(frozen=True)
class SourceLocation:
    """Represents a precise location in a C source or header file (.c / .h)."""

    file_path: str
    line: int = 1
    column: int = 1
    end_line: int | None = None
    end_column: int | None = None

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Evidence:
    """A single piece of heuristic evidence supporting a pattern detection."""

    description: str
    weight: float
    rule_code: str
    location: SourceLocation | None = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(f"Evidence weight must be between 0.0 and 1.0, got {self.weight}")


@dataclass(frozen=True)
class Confidence:
    """Aggregated confidence score computed from multiple pieces of evidence."""

    score: float
    level: ConfidenceLevel = field(init=False)

    def __post_init__(self) -> None:
        clamped = max(0.0, min(1.0, self.score))
        object.__setattr__(self, "score", clamped)
        object.__setattr__(self, "level", ConfidenceLevel.from_score(clamped))

    @classmethod
    def from_evidences(cls, evidences: list[Evidence]) -> Confidence:
        if not evidences:
            return cls(0.0)
        complement_product = 1.0
        for ev in evidences:
            complement_product *= (1.0 - ev.weight)
        return cls(1.0 - complement_product)

    @property
    def percentage_str(self) -> str:
        return f"{int(self.score * 100)}%"
