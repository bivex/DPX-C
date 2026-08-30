"""C Circular Header Include Dependency Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class CircularHeaderIncludeRule(BasePatternRule):
    """Detects cyclic #include dependencies between C header files."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.CIRCULAR_HEADER_INCLUDE

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        cycles = model.find_circular_includes()

        for cycle in cycles:
            cycle_str = " ➔ ".join(cycle) + " ➔ " + cycle[0]
            first_file = model.find_file(cycle[0])
            if not first_file:
                for f_path, f_model in model.files.items():
                    if f_path.endswith("/" + cycle[0]) or f_path == cycle[0] or os.path.basename(f_path) == cycle[0]:
                        first_file = f_model
                        break
            loc = first_file.location if first_file else None

            evidences = [
                Evidence(
                    description=f"Circular Header Include Dependency detected: {cycle_str}",
                    weight=0.85,
                    rule_code="CIRCULAR_HEADER_CYCLE",
                    location=loc,
                )
            ]
            det = self._create_detection(
                target_name=" ⇄ ".join(cycle),
                target_kind="header_cycle",
                evidences=evidences,
                location=loc,
            )
            detections.append(det)

        return detections
