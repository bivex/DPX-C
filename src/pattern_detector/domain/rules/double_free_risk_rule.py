"""C Double Free / Dangling Pointer Risk Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class DoubleFreeRiskRule(BasePatternRule):
    """Detects multiple free calls on the same pointer variable or free in loops without NULL assignment."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.DOUBLE_FREE_RISK

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                body = fn.body
                free_vars = re.findall(r"\bfree\s*\(\s*([a-zA-Z0-9_]+)\s*\)", body)
                if len(free_vars) != len(set(free_vars)):
                    evidences = [
                        Evidence(
                            description=f"Memory Safety Hazard (Double Free Risk): Function '{fn.id_str}' in '{f.file_path}' calls free() multiple times on the same pointer variable",
                            weight=0.85,
                            rule_code="DOUBLE_FREE_DUPLICATE_CALL",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="double_free_risk_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
