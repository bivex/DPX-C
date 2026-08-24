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

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                if ("malloc(" in body or "calloc(" in body or "realloc(" in body) and not ("if (!" in body or "if (" in body or "assert(" in body):
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
