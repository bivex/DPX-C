"""C Facade Header Subsystem Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class FacadeHeaderRule(BasePatternRule):
    """Detects Facade headers aggregating multiple internal subsystem headers."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FACADE_HEADER

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            if f.is_header and len(f.includes) >= 4 and len(f.functions) == 0:
                evidences = [
                    Evidence(
                        description=f"Header '{f.file_path}' serves as a Subsystem Facade aggregating {len(f.includes)} internal module headers into a single public interface",
                        weight=0.75,
                        rule_code="FACADE_HEADER_AGGREGATOR",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="facade_header",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
