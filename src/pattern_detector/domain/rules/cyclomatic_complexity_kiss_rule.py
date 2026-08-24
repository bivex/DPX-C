"""C KISS Rule (High Cyclomatic Complexity)."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class CyclomaticComplexityKissRule(BasePatternRule):
    """Detects KISS violations in C (functions with branch complexity ≥12)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CYCLOMATIC_COMPLEXITY_KISS

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                if fn.cyclomatic_complexity >= 12:
                    evidences = [
                        Evidence(
                            description=f"KISS Violation (High Complexity): Function '{fn.id_str}' in '{f.file_path}' has cyclomatic complexity of {fn.cyclomatic_complexity}; refactor nested branches or use table dispatch",
                            weight=0.75,
                            rule_code="KISS_HIGH_CYCLOMATIC_COMPLEXITY",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="complex_c_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
