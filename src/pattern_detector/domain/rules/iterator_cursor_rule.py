"""C Iterator / Cursor Pattern Rule."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class IteratorCursorRule(BasePatternRule):
    """Detects Iterator / Cursor structs and traversal functions in C."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.ITERATOR_CURSOR

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            iter_fns = [fn for fn in f.functions.values() if "iter" in fn.name or "cursor" in fn.name]
            has_next = any("next" in fn.name for fn in iter_fns)
            has_has_next = any("has_next" in fn.name or "valid" in fn.name for fn in iter_fns)

            if (has_next and len(iter_fns) >= 2) or (has_next and has_has_next):
                evidences = [
                    Evidence(
                        description=f"File '{f.file_path}' implements Iterator / Cursor pattern providing sequential collection traversal ({', '.join(fn.name for fn in iter_fns[:3])})",
                        weight=0.80,
                        rule_code="ITERATOR_CURSOR_TRAVERSAL",
                        location=f.location,
                    )
                ]
                det = self._create_detection(
                    target_name=f.file_path,
                    target_kind="iterator_module",
                    evidences=evidences,
                    location=f.location,
                )
                detections.append(det)

        return detections
