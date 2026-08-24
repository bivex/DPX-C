"""C Potential Memory Leak Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class MemoryLeakMissingFreeRule(BasePatternRule):
    """Detects functions that allocate memory without corresponding free on error paths."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.MEMORY_LEAK_MISSING_FREE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                if ("malloc(" in body or "fopen(" in body) and not ("free(" in body or "fclose(" in body or "return " in fn.return_type or "*" in fn.return_type):
                    evidences = [
                        Evidence(
                            description=f"Memory Safety Risk (Potential Leak): Function '{fn.id_str}' in '{f.file_path}' allocates local resources without deallocating them or returning them to caller",
                            weight=0.75,
                            rule_code="LOCAL_ALLOCATION_WITHOUT_FREE",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="potential_leak_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
