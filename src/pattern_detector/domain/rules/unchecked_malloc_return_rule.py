"""C Unchecked Malloc Return Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class UncheckedMallocReturnRule(BasePatternRule):
    """Detects malloc/calloc/realloc calls without null-pointer checks before dereferencing."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.UNCHECKED_MALLOC_RETURN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        null_check_indicators = (
            "if (!", "if (", "if(", "assert(", "ASSERT(", "CHECK(", "abort(", "exit(",
            "? :", "goto "
        )

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                has_alloc = "malloc(" in body or "calloc(" in body or "realloc(" in body
                if not has_alloc:
                    continue

                # Pass-through allocators / factory wrappers that return malloc result directly
                is_direct_return = bool(
                    re.search(r"return\s+(?:\([^)]*\)\s*)?(?:malloc|calloc|realloc)\s*\(", body)
                )
                if is_direct_return:
                    continue

                has_null_check = any(k in body for k in null_check_indicators)
                if not has_null_check:
                    evidences = [
                        Evidence(
                            description=f"Memory Safety Risk: Function '{fn.id_str}' in '{f.file_path}' calls malloc/calloc without validating pointer against NULL, risking null-pointer dereference crash",
                            weight=0.85,
                            rule_code="UNCHECKED_MALLOC_RETURN",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="unsafe_malloc_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
