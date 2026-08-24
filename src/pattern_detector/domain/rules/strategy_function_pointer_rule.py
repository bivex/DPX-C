"""C Strategy Function Pointer Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class StrategyFunctionPointerRule(BasePatternRule):
    """Detects Strategy pattern algorithm delegation via function pointer arguments."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.STRATEGY_FUNCTION_POINTER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                func_ptrs = [p for p in fn.params if p.is_function_pointer]
                if func_ptrs and not fn.name.startswith("register_") and not fn.name.startswith("add_"):
                    evidences = [
                        Evidence(
                            description=f"Function '{fn.id_str}' accepts strategy function pointer parameter '{func_ptrs[0].name}' for dynamic algorithm injection",
                            weight=0.75,
                            rule_code="STRATEGY_FUNCTION_POINTER_PARAM",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="strategy_delegator_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
