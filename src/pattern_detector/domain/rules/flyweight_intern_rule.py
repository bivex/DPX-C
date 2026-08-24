"""C Flyweight String / Symbol Interning Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class FlyweightInternRule(BasePatternRule):
    """Detects String and Symbol Flyweight interning tables in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.FLYWEIGHT_INTERN

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            src = f.raw_source
            if "intern(" in src or "string_pool" in src or "atom_table" in src or "symbol_intern" in src:
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Flyweight String/Symbol Interning to optimize memory sharing across duplicate immutable tokens",
                        weight=0.80,
                        rule_code="FLYWEIGHT_STRING_INTERN_POOL",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="flyweight_pool_file",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
