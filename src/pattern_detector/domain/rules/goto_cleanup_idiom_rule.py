"""C Goto Error Cleanup (RAII in C) Rule."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BasePatternRule
from pattern_detector.domain.value_objects import Evidence, PatternType


class GotoCleanupIdiomRule(BasePatternRule):
    """Detects Linux-kernel standard multi-level goto error cleanup idiom."""

    @property
    def pattern_type(self) -> PatternType:
        return PatternType.GOTO_CLEANUP_IDIOM

    def detect(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []

        for f in model.all_files():
            for fn in f.functions.values():
                if fn.has_goto and ("cleanup:" in fn.body or "error:" in fn.body or "err:" in fn.body or "out:" in fn.body or "fail:" in fn.body):
                    evidences = [
                        Evidence(
                            description=f"Function '{fn.id_str}' adopts idiomatic Kernel single-exit Goto Error Cleanup (RAII in C) ensuring unified resource deallocation",
                            weight=0.80,
                            rule_code="GOTO_CLEANUP_RESOURCE_RELEASE",
                            location=fn.location or f.location,
                        )
                    ]
                    det = self._create_detection(
                        target_name=f"{f.file_path}:{fn.name}",
                        target_kind="goto_cleanup_function",
                        evidences=evidences,
                        location=fn.location or f.location,
                    )
                    detections.append(det)

        return detections
