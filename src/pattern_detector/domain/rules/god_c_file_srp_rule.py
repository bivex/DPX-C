"""C Single Responsibility (God C File) Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class GodCFileSrpRule(BasePatternRule):
    """Detects God C Files (excessive global functions ≥30 or LOC ≥1000)."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.GOD_C_FILE_SRP

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            fn_count = len(f.functions)
            line_count = f.raw_source.count("\n") + 1

            if fn_count >= 30 or line_count >= 1200:
                evidences = [
                    Evidence(
                        description=f"SRP Violation (God C File): File '{f.file_path}' defines {fn_count} functions across {line_count} lines of code, indicating multiple mixed domain responsibilities",
                        weight=0.85,
                        rule_code="SRP_GOD_C_FILE",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="god_c_file",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
