"""Domain Code Model for Pure C (C89, C99, C11, C17, C23) Static Architecture and Pattern Analysis."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Sequence

from pattern_detector.domain.value_objects import SourceLocation


@dataclass
class StructMemberModel:
    """Represents a member field in a C struct or union."""

    name: str
    type_str: str
    is_function_pointer: bool = False
    is_pointer: bool = False
    is_array: bool = False
    func_ptr_params: list[str] = field(default_factory=list)


@dataclass
class StructModel:
    """Represents a C struct, union, or enum definition."""

    name: str
    members: list[StructMemberModel] = field(default_factory=list)
    is_union: bool = False
    is_opaque_forward: bool = False
    location: SourceLocation | None = None

    @property
    def has_function_pointers(self) -> bool:
        return any(m.is_function_pointer for m in self.members)

    @property
    def function_pointer_members(self) -> list[StructMemberModel]:
        return [m for m in self.members if m.is_function_pointer]


@dataclass
class TypedefModel:
    """Represents a C typedef declaration (`typedef ... Name;`)."""

    name: str
    target_type: str
    is_function_pointer: bool = False
    location: SourceLocation | None = None


@dataclass
class FunctionParamModel:
    """Represents a parameter in a C function signature."""

    name: str
    type_str: str
    is_function_pointer: bool = False
    is_pointer: bool = False


@dataclass
class FunctionModel:
    """Represents a C function declaration or definition."""

    name: str
    return_type: str
    params: list[FunctionParamModel] = field(default_factory=list)
    is_static: bool = False
    is_inline: bool = False
    is_definition: bool = True
    body: str = ""
    cyclomatic_complexity: int = 1
    calls: list[str] = field(default_factory=list)  # Function names called
    has_goto: bool = False
    has_malloc: bool = False
    has_free: bool = False
    has_unsafe_str: bool = False
    location: SourceLocation | None = None

    @property
    def id_str(self) -> str:
        return f"{self.name}()"

    @property
    def arity(self) -> int:
        return len(self.params)


@dataclass
class MacroModel:
    """Represents a C preprocessor macro (`#define ...`)."""

    name: str
    params: list[str] = field(default_factory=list)
    definition: str = ""
    is_function_like: bool = False
    location: SourceLocation | None = None


@dataclass
class FileModel:
    """Represents a C source (.c) or header (.h) file."""

    file_path: str
    is_header: bool = False
    includes: list[str] = field(default_factory=list)
    structs: dict[str, StructModel] = field(default_factory=dict)
    typedefs: dict[str, TypedefModel] = field(default_factory=dict)
    functions: dict[str, FunctionModel] = field(default_factory=dict)
    macros: dict[str, MacroModel] = field(default_factory=dict)
    raw_source: str = ""
    location: SourceLocation | None = None

    def find_function(self, name: str) -> FunctionModel | None:
        return self.functions.get(name)


@dataclass
class CodeModel:
    """Aggregated semantic domain model of a C project or library."""

    files: dict[str, FileModel] = field(default_factory=dict)
    project_path: str = ""

    def all_files(self) -> list[FileModel]:
        return list(self.files.values())

    def all_functions(self) -> list[FunctionModel]:
        res = []
        for f in self.files.values():
            res.extend(f.functions.values())
        return res

    def all_structs(self) -> list[StructModel]:
        res = []
        for f in self.files.values():
            res.extend(f.structs.values())
        return res

    def find_file(self, path: str) -> FileModel | None:
        return self.files.get(path)

    # -------------------------------------------------------------------------
    # Circular Header Include Dependency Graph
    # -------------------------------------------------------------------------

    def _resolve_include_target(self, current_file: str, inc: str) -> str | None:
        # Ignore system angle bracket style headers like <stdio.h>
        if inc.endswith(".h") and ("/" not in inc or inc.startswith("sys/") or inc.startswith("mach/") or inc.startswith("arpa/")):
            if inc in ("stdio.h", "stdlib.h", "string.h", "stdint.h", "stddef.h", "limits.h", "errno.h", "unistd.h", "fcntl.h", "windows.h", "winsock2.h"):
                return None

        cur_dir = os.path.dirname(current_file)
        rel_candidate = os.path.normpath(os.path.join(cur_dir, inc))
        if rel_candidate in self.files and self.files[rel_candidate].is_header:
            return rel_candidate

        if inc in self.files and self.files[inc].is_header:
            return inc

        norm_inc = "/" + inc.lstrip("/")
        matching_candidates = [
            f_path for f_path, f_model in self.files.items()
            if f_model.is_header and (f_path.endswith(norm_inc) or f_path.endswith("/" + inc) or f_path == inc)
        ]
        if matching_candidates:
            if len(matching_candidates) == 1:
                return matching_candidates[0]
            try:
                matching_candidates.sort(
                    key=lambda p: len(os.path.commonpath([os.path.dirname(current_file), os.path.dirname(p)])),
                    reverse=True
                )
                return matching_candidates[0]
            except ValueError:
                return matching_candidates[0]

        return None

    def build_include_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}
        for file_path, file_model in self.files.items():
            if not file_model.is_header:
                continue
            graph.setdefault(file_path, set())
            for inc in file_model.includes:
                resolved = self._resolve_include_target(file_path, inc)
                if resolved and resolved != file_path and self.files.get(resolved) and self.files[resolved].is_header:
                    graph[file_path].add(resolved)
        return graph

    def find_circular_includes(self, max_depth: int = 8, max_cycles: int = 50) -> list[list[str]]:
        graph = self.build_include_graph()
        cycles: list[list[str]] = []
        visited: set[str] = set()

        def _dfs(current: str, path: list[str], path_set: set[str]) -> None:
            if len(cycles) >= max_cycles:
                return
            path.append(current)
            path_set.add(current)

            for neighbor in sorted(graph.get(current, set())):
                if neighbor == path[0] and len(path) > 1:
                    canonical = tuple(path)
                    rotations = [canonical[i:] + canonical[:i] for i in range(len(canonical))]
                    min_rot = list(min(rotations))
                    # Format as basenames for concise cycle reporting
                    cycle_names = [os.path.basename(p) for p in min_rot]
                    if cycle_names not in cycles:
                        cycles.append(cycle_names)
                elif neighbor not in path_set and neighbor not in visited and len(path) < max_depth:
                    _dfs(neighbor, path, path_set)

            path.pop()
            path_set.remove(current)

        for node in sorted(graph.keys()):
            _dfs(node, [], set())
            visited.add(node)

        return cycles
