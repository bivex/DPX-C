"""C Chain of Responsibility Filter Chain Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class ChainOfResponsibilityRule(BasePatternRule):
    """Detects Chain of Responsibility middleware / filter chains in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CHAIN_OF_RESPONSIBILITY

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for s_name, st in f.structs.items():
                if ("filter" in s_name or "handler" in s_name or "interceptor" in s_name or "middleware" in s_name) and any(m.name == "next" for m in st.members) and st.has_function_pointers:
                    evidences = [
                        Evidence(
                            description=f"Struct '{s_name}' implements Chain of Responsibility delegating processing to successive `next` filter handlers",
                            weight=0.85,
                            rule_code="CHAIN_OF_RESPONSIBILITY_STRUCT",
                            location=st.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=s_name,
                        target_kind="filter_chain_struct",
                        evidences=evidences,
                        location=st.location or f.location,
                    )
                    detections.append(det)

        return detections
