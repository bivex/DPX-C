"""Rule catalog registration for Pure C Pattern Detector."""

from __future__ import annotations

from pattern_detector.domain.rules.adapter_wrapper_rule import AdapterWrapperRule
from pattern_detector.domain.rules.base import BasePatternRule, PatternRule
from pattern_detector.domain.rules.builder_config_struct_rule import BuilderConfigStructRule
from pattern_detector.domain.rules.chain_of_responsibility_rule import ChainOfResponsibilityRule
from pattern_detector.domain.rules.circular_header_include_rule import CircularHeaderIncludeRule
from pattern_detector.domain.rules.command_dispatch_table_rule import CommandDispatchTableRule
from pattern_detector.domain.rules.composite_tree_rule import CompositeTreeRule
from pattern_detector.domain.rules.cyclomatic_complexity_kiss_rule import CyclomaticComplexityKissRule
from pattern_detector.domain.rules.decorator_hook_rule import DecoratorHookRule
from pattern_detector.domain.rules.double_free_risk_rule import DoubleFreeRiskRule
from pattern_detector.domain.rules.duplicate_code_dry_rule import DuplicateCodeDryRule
from pattern_detector.domain.rules.facade_header_rule import FacadeHeaderRule
from pattern_detector.domain.rules.flyweight_intern_rule import FlyweightInternRule
from pattern_detector.domain.rules.god_c_file_srp_rule import GodCFileSrpRule
from pattern_detector.domain.rules.goto_cleanup_idiom_rule import GotoCleanupIdiomRule
from pattern_detector.domain.rules.intrusive_list_tree_rule import IntrusiveListTreeRule
from pattern_detector.domain.rules.iterator_cursor_rule import IteratorCursorRule
from pattern_detector.domain.rules.memory_leak_missing_free_rule import MemoryLeakMissingFreeRule
from pattern_detector.domain.rules.object_pool_allocator_rule import ObjectPoolAllocatorRule
from pattern_detector.domain.rules.observer_callback_registry_rule import ObserverCallbackRegistryRule
from pattern_detector.domain.rules.opaque_pointer_adt_rule import OpaquePointerAdtRule
from pattern_detector.domain.rules.reactor_event_loop_rule import ReactorEventLoopRule
from pattern_detector.domain.rules.singleton_module_rule import SingletonModuleRule
from pattern_detector.domain.rules.state_machine_table_rule import StateMachineTableRule
from pattern_detector.domain.rules.strategy_function_pointer_rule import StrategyFunctionPointerRule
from pattern_detector.domain.rules.unchecked_malloc_return_rule import UncheckedMallocReturnRule
from pattern_detector.domain.rules.unsafe_string_function_rule import UnsafeStringFunctionRule
from pattern_detector.domain.rules.vtable_interface_rule import VTableInterfaceRule

DEFAULT_RULES: list[PatternRule] = [
    # Creational (4)
    OpaquePointerAdtRule(),
    SingletonModuleRule(),
    ObjectPoolAllocatorRule(),
    BuilderConfigStructRule(),

    # Structural (7)
    VTableInterfaceRule(),
    IntrusiveListTreeRule(),
    AdapterWrapperRule(),
    FacadeHeaderRule(),
    DecoratorHookRule(),
    FlyweightInternRule(),
    CompositeTreeRule(),

    # Behavioral & Concurrency (8)
    ObserverCallbackRegistryRule(),
    StrategyFunctionPointerRule(),
    CommandDispatchTableRule(),
    StateMachineTableRule(),
    ChainOfResponsibilityRule(),
    IteratorCursorRule(),
    ReactorEventLoopRule(),
    GotoCleanupIdiomRule(),

    # Resilience, Principles & Memory Safety (8)
    UncheckedMallocReturnRule(),
    UnsafeStringFunctionRule(),
    MemoryLeakMissingFreeRule(),
    DoubleFreeRiskRule(),
    GodCFileSrpRule(),
    CyclomaticComplexityKissRule(),
    DuplicateCodeDryRule(),
    CircularHeaderIncludeRule(),
]

__all__ = [
    "BasePatternRule",
    "PatternRule",
    "DEFAULT_RULES",
    "OpaquePointerAdtRule",
    "SingletonModuleRule",
    "ObjectPoolAllocatorRule",
    "BuilderConfigStructRule",
    "VTableInterfaceRule",
    "IntrusiveListTreeRule",
    "AdapterWrapperRule",
    "FacadeHeaderRule",
    "DecoratorHookRule",
    "FlyweightInternRule",
    "CompositeTreeRule",
    "ObserverCallbackRegistryRule",
    "StrategyFunctionPointerRule",
    "CommandDispatchTableRule",
    "StateMachineTableRule",
    "ChainOfResponsibilityRule",
    "IteratorCursorRule",
    "ReactorEventLoopRule",
    "GotoCleanupIdiomRule",
    "UncheckedMallocReturnRule",
    "UnsafeStringFunctionRule",
    "MemoryLeakMissingFreeRule",
    "DoubleFreeRiskRule",
    "GodCFileSrpRule",
    "CyclomaticComplexityKissRule",
    "DuplicateCodeDryRule",
    "CircularHeaderIncludeRule",
]
